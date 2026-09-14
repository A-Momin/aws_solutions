#!/bin/bash
# Blue-Green Deployment Script
# This script automates the blue-green deployment process

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TERRAFORM_DIR="$PROJECT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if terraform is installed
    if ! command -v terraform &> /dev/null; then
        error "Terraform is not installed or not in PATH"
        exit 1
    fi
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        error "AWS CLI is not installed or not in PATH"
        exit 1
    fi
    
    # Check if jq is installed
    if ! command -v jq &> /dev/null; then
        error "jq is not installed or not in PATH"
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        error "AWS credentials not configured or invalid"
        exit 1
    fi
    
    success "Prerequisites check passed"
}

# Function to get current active environment
get_active_environment() {
    cd "$TERRAFORM_DIR"
    terraform output -raw active_environment 2>/dev/null || echo "blue"
}

# Function to get inactive environment
get_inactive_environment() {
    local active_env="$1"
    if [ "$active_env" = "blue" ]; then
        echo "green"
    else
        echo "blue"
    fi
}

# Function to check target group health
check_target_group_health() {
    local tg_arn="$1"
    local environment="$2"
    local timeout="${3:-300}"
    
    log "Checking health of $environment target group..."
    
    local start_time=$(date +%s)
    local end_time=$((start_time + timeout))
    
    while [ $(date +%s) -lt $end_time ]; do
        local healthy_count=$(aws elbv2 describe-target-health \
            --target-group-arn "$tg_arn" \
            --query 'TargetHealthDescriptions[?TargetHealth.State==`healthy`] | length(@)' \
            --output text)
        
        local total_count=$(aws elbv2 describe-target-health \
            --target-group-arn "$tg_arn" \
            --query 'TargetHealthDescriptions | length(@)' \
            --output text)
        
        log "Health check: $healthy_count/$total_count targets healthy"
        
        if [ "$healthy_count" -gt 0 ] && [ "$healthy_count" -eq "$total_count" ]; then
            success "$environment environment is healthy"
            return 0
        fi
        
        sleep 10
    done
    
    error "Timeout waiting for $environment environment to become healthy"
    return 1
}

# Function to run smoke tests
run_smoke_tests() {
    local test_url="$1"
    local environment="$2"
    
    log "Running smoke tests for $environment environment..."
    
    # Test 1: Basic connectivity
    local http_status=$(curl -s -o /dev/null -w "%{http_code}" "$test_url" || echo "000")
    if [ "$http_status" != "200" ]; then
        error "Smoke test failed: HTTP status $http_status"
        return 1
    fi
    
    # Test 2: Check if correct environment is responding
    local response=$(curl -s "$test_url/version" || echo "{}")
    local env_from_response=$(echo "$response" | jq -r '.environment // "unknown"')
    
    if [ "$env_from_response" != "$environment" ]; then
        error "Smoke test failed: Expected environment '$environment', got '$env_from_response'"
        return 1
    fi
    
    # Test 3: Health endpoint
    local health_status=$(curl -s "$test_url/health" | jq -r '.status // "unknown"')
    if [ "$health_status" != "healthy" ]; then
        error "Smoke test failed: Health status is '$health_status'"
        return 1
    fi
    
    success "Smoke tests passed for $environment environment"
    return 0
}

# Function to switch traffic
switch_traffic() {
    local new_active_env="$1"
    local listener_arn="$2"
    local target_group_arn="$3"
    
    log "Switching traffic to $new_active_env environment..."
    
    # Update the default action of the listener
    aws elbv2 modify-listener \
        --listener-arn "$listener_arn" \
        --default-actions Type=forward,TargetGroupArn="$target_group_arn" \
        > /dev/null
    
    success "Traffic switched to $new_active_env environment"
}

# Function to scale environment
scale_environment() {
    local environment="$1"
    local desired_capacity="$2"
    local asg_name="$3"
    
    log "Scaling $environment environment to $desired_capacity instances..."
    
    aws autoscaling update-auto-scaling-group \
        --auto-scaling-group-name "$asg_name" \
        --desired-capacity "$desired_capacity" \
        > /dev/null
    
    # Wait for scaling to complete
    local timeout=600  # 10 minutes
    local start_time=$(date +%s)
    local end_time=$((start_time + timeout))
    
    while [ $(date +%s) -lt $end_time ]; do
        local current_capacity=$(aws autoscaling describe-auto-scaling-groups \
            --auto-scaling-group-names "$asg_name" \
            --query 'AutoScalingGroups[0].Instances[?LifecycleState==`InService`] | length(@)' \
            --output text)
        
        log "Scaling progress: $current_capacity/$desired_capacity instances in service"
        
        if [ "$current_capacity" -eq "$desired_capacity" ]; then
            success "$environment environment scaled to $desired_capacity instances"
            return 0
        fi
        
        sleep 15
    done
    
    error "Timeout waiting for $environment environment to scale"
    return 1
}

# Function to rollback deployment
rollback() {
    local current_active="$1"
    local previous_active="$2"
    
    warning "Initiating rollback from $current_active to $previous_active..."
    
    cd "$TERRAFORM_DIR"
    
    # Get infrastructure details
    local listener_arn=$(terraform output -raw listener_arn)
    local previous_tg_arn=$(terraform output -raw "${previous_active}_target_group_arn")
    local current_asg_name=$(terraform output -raw "${current_active}_asg_name")
    local previous_asg_name=$(terraform output -raw "${previous_active}_asg_name")
    
    # Scale up previous environment
    scale_environment "$previous_active" 2 "$previous_asg_name"
    
    # Wait for health checks
    if check_target_group_health "$previous_tg_arn" "$previous_active" 300; then
        # Switch traffic back
        switch_traffic "$previous_active" "$listener_arn" "$previous_tg_arn"
        
        # Scale down current environment
        scale_environment "$current_active" 0 "$current_asg_name"
        
        success "Rollback completed successfully"
    else
        error "Rollback failed - previous environment is not healthy"
        return 1
    fi
}

# Function to monitor deployment
monitor_deployment() {
    local environment="$1"
    local test_url="$2"
    local duration="${3:-300}"
    
    log "Monitoring $environment environment for $duration seconds..."
    
    local start_time=$(date +%s)
    local end_time=$((start_time + duration))
    local error_count=0
    local total_checks=0
    
    while [ $(date +%s) -lt $end_time ]; do
        total_checks=$((total_checks + 1))
        
        local http_status=$(curl -s -o /dev/null -w "%{http_code}" "$test_url" || echo "000")
        
        if [ "$http_status" != "200" ]; then
            error_count=$((error_count + 1))
            warning "Health check failed: HTTP $http_status (Error $error_count/$total_checks)"
        else
            log "Health check passed: HTTP $http_status"
        fi
        
        # Calculate error rate
        local error_rate=$((error_count * 100 / total_checks))
        
        # Check if error rate exceeds threshold (5%)
        if [ "$error_rate" -gt 5 ] && [ "$total_checks" -gt 10 ]; then
            error "Error rate ($error_rate%) exceeds threshold (5%)"
            return 1
        fi
        
        sleep 10
    done
    
    local final_error_rate=$((error_count * 100 / total_checks))
    log "Monitoring completed: $error_count errors out of $total_checks checks ($final_error_rate% error rate)"
    
    if [ "$final_error_rate" -le 5 ]; then
        success "Deployment monitoring passed"
        return 0
    else
        error "Deployment monitoring failed"
        return 1
    fi
}

# Main deployment function
deploy() {
    local new_version="$1"
    local skip_tests="${2:-false}"
    
    log "Starting blue-green deployment..."
    
    cd "$TERRAFORM_DIR"
    
    # Get current state
    local current_active=$(get_active_environment)
    local new_active=$(get_inactive_environment "$current_active")
    
    log "Current active environment: $current_active"
    log "Deploying to environment: $new_active"
    log "New version: $new_version"
    
    # Get infrastructure details
    local listener_arn=$(terraform output -raw listener_arn)
    local new_tg_arn=$(terraform output -raw "${new_active}_target_group_arn")
    local current_asg_name=$(terraform output -raw "${current_active}_asg_name")
    local new_asg_name=$(terraform output -raw "${new_active}_asg_name")
    local new_test_url=$(terraform output -raw "${new_active}_test_url")
    local production_url=$(terraform output -raw production_url)
    
    # Update app version for new environment
    log "Updating application version for $new_active environment..."
    terraform apply -auto-approve \
        -var="app_versions={\"$current_active\"=\"$(terraform output -json app_versions | jq -r ".$current_active")\",\"$new_active\"=\"$new_version\"}" \
        > /dev/null
    
    # Scale up new environment
    if ! scale_environment "$new_active" 2 "$new_asg_name"; then
        error "Failed to scale up $new_active environment"
        return 1
    fi
    
    # Wait for new environment to be healthy
    if ! check_target_group_health "$new_tg_arn" "$new_active" 600; then
        error "New environment failed health checks"
        scale_environment "$new_active" 0 "$new_asg_name"
        return 1
    fi
    
    # Run smoke tests
    if [ "$skip_tests" != "true" ]; then
        if ! run_smoke_tests "$new_test_url" "$new_active"; then
            error "Smoke tests failed"
            scale_environment "$new_active" 0 "$new_asg_name"
            return 1
        fi
    fi
    
    # Switch traffic
    switch_traffic "$new_active" "$listener_arn" "$new_tg_arn"
    
    # Monitor deployment
    if ! monitor_deployment "$new_active" "$production_url" 300; then
        warning "Deployment monitoring failed, initiating rollback..."
        rollback "$new_active" "$current_active"
        return 1
    fi
    
    # Scale down old environment
    scale_environment "$current_active" 0 "$current_asg_name"
    
    # Update Terraform state
    terraform apply -auto-approve \
        -var="active_environment=$new_active" \
        > /dev/null
    
    success "Blue-green deployment completed successfully!"
    log "New active environment: $new_active"
    log "Production URL: $production_url"
}

# Function to show status
show_status() {
    cd "$TERRAFORM_DIR"
    
    local current_active=$(get_active_environment)
    local inactive_env=$(get_inactive_environment "$current_active")
    
    echo "=== Blue-Green Deployment Status ==="
    echo "Active Environment: $current_active"
    echo "Inactive Environment: $inactive_env"
    echo ""
    
    # Get target group health
    local blue_tg_arn=$(terraform output -raw blue_target_group_arn)
    local green_tg_arn=$(terraform output -raw green_target_group_arn)
    
    echo "Blue Environment Health:"
    aws elbv2 describe-target-health --target-group-arn "$blue_tg_arn" \
        --query 'TargetHealthDescriptions[*].[Target.Id,TargetHealth.State]' \
        --output table
    
    echo ""
    echo "Green Environment Health:"
    aws elbv2 describe-target-health --target-group-arn "$green_tg_arn" \
        --query 'TargetHealthDescriptions[*].[Target.Id,TargetHealth.State]' \
        --output table
    
    echo ""
    echo "URLs:"
    echo "Production: $(terraform output -raw production_url)"
    echo "Blue Test: $(terraform output -raw blue_test_url)"
    echo "Green Test: $(terraform output -raw green_test_url)"
}

# Main script logic
case "${1:-}" in
    "deploy")
        check_prerequisites
        if [ -z "${2:-}" ]; then
            error "Version number required for deployment"
            echo "Usage: $0 deploy <version> [skip-tests]"
            exit 1
        fi
        deploy "$2" "${3:-false}"
        ;;
    "rollback")
        check_prerequisites
        current_active=$(get_active_environment)
        previous_active=$(get_inactive_environment "$current_active")
        rollback "$current_active" "$previous_active"
        ;;
    "status")
        show_status
        ;;
    "test")
        check_prerequisites
        cd "$TERRAFORM_DIR"
        blue_url=$(terraform output -raw blue_test_url)
        green_url=$(terraform output -raw green_test_url)
        
        echo "Testing Blue Environment:"
        run_smoke_tests "$blue_url" "blue"
        echo ""
        echo "Testing Green Environment:"
        run_smoke_tests "$green_url" "green"
        ;;
    *)
        echo "Usage: $0 {deploy|rollback|status|test}"
        echo ""
        echo "Commands:"
        echo "  deploy <version> [skip-tests]  - Deploy new version to inactive environment"
        echo "  rollback                       - Rollback to previous environment"
        echo "  status                         - Show current deployment status"
        echo "  test                           - Run smoke tests on both environments"
        echo ""
        echo "Examples:"
        echo "  $0 deploy v1.2.0"
        echo "  $0 deploy v1.2.0 skip-tests"
        echo "  $0 rollback"
        echo "  $0 status"
        exit 1
        ;;
esac