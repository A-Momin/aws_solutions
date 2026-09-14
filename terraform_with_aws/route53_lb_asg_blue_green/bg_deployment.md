# Blue-Green Deployment Guide

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Initial Setup](#initial-setup)
5. [Deployment Process](#deployment-process)
6. [Traffic Management](#traffic-management)
7. [Monitoring and Rollback](#monitoring-and-rollback)
8. [Advanced Scenarios](#advanced-scenarios)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

---

## Overview

Blue-Green deployment is a technique that reduces downtime and risk by running two identical production environments called Blue and Green. At any time, only one of the environments is live, with the other serving as a staging environment for the next release.

### Benefits
- **Zero-downtime deployments**
- **Instant rollback capability**
- **Reduced deployment risk**
- **Easy testing in production-like environment**
- **Simplified disaster recovery**

### How It Works
1. **Blue environment** serves production traffic
2. **Green environment** is prepared with new version
3. Traffic is switched from Blue to Green
4. Blue environment becomes the standby

---

## Architecture

### Infrastructure Components

```
Internet → Route53 → ALB → Target Groups → Auto Scaling Groups → EC2 Instances
                      ├── Blue Target Group → Blue ASG → Blue Instances
                      └── Green Target Group → Green ASG → Green Instances
```

### Key Resources
- **Application Load Balancer (ALB)**: Routes traffic between environments
- **Target Groups**: Blue and Green target groups for health checks
- **Auto Scaling Groups**: Separate ASGs for each environment
- **Launch Templates**: Environment-specific configurations
- **Route53**: DNS management and testing subdomains
- **CloudWatch**: Monitoring and alerting
- **S3**: Deployment artifacts storage

---

## Prerequisites

### Required Tools
```bash
# Install required tools
brew install terraform awscli jq  # macOS
# or
sudo apt-get install terraform awscli jq  # Ubuntu
# or
sudo yum install terraform awscli jq  # Amazon Linux
```

### AWS Permissions
Ensure your AWS user/role has permissions for:
- EC2 (instances, security groups, load balancers)
- Auto Scaling
- Route53
- CloudWatch
- S3
- IAM (for service roles)

### Existing Infrastructure
- VPC with public and private subnets
- SSL certificate in ACM
- Route53 hosted zone
- EC2 key pair for SSH access

---

## Initial Setup

### Step 1: Clone and Configure

```bash
# Clone the configuration
git clone <your-repo>
cd blue-green-deployment

# Copy and edit variables
cp terraform.tfvars.example terraform.tfvars
```

### Step 2: Update terraform.tfvars

```hcl
# terraform.tfvars
aws_region = "us-east-1"
project_name = "demo-app"

# Replace with your actual values
existing_vpc_id = "vpc-xxxxxxxxx"
certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/xxxxxxxx"
domain_name = "harnesstechtx.com"
key_pair_name = "your-key-pair"

# Application versions
app_versions = {
  blue  = "v1.0.0"
  green = "v1.1.0"
}
```

### Step 3: Initialize and Deploy

```bash
# Initialize Terraform
terraform init

# Plan the deployment
terraform plan

# Apply the configuration
terraform apply
```

### Step 4: Verify Initial Setup

```bash
# Check status
./scripts/deploy.sh status

# Test both environments
./scripts/deploy.sh test
```

---

## Deployment Process

### Standard Blue-Green Deployment

#### Step 1: Prepare New Version

```bash
# Deploy new version to inactive environment
./scripts/deploy.sh deploy v1.2.0
```

**What happens:**
1. Script identifies inactive environment (e.g., Green)
2. Updates Green environment with new version
3. Scales up Green Auto Scaling Group
4. Waits for instances to become healthy
5. Runs smoke tests on Green environment
6. Switches traffic from Blue to Green
7. Monitors deployment for 5 minutes
8. Scales down Blue environment if successful

#### Step 2: Monitor Deployment

The script automatically monitors the deployment:
- **Health Checks**: Verifies target group health
- **Smoke Tests**: Tests critical application endpoints
- **Error Rate Monitoring**: Tracks HTTP error rates
- **Automatic Rollback**: Triggers if error rate exceeds 5%

#### Step 3: Verify Success

```bash
# Check deployment status
./scripts/deploy.sh status

# Manual verification
curl https://your-domain.com/version
curl https://your-domain.com/health
```

### Manual Deployment Steps

If you prefer manual control:

#### Step 1: Scale Up New Environment

```bash
# Get current active environment
ACTIVE_ENV=$(terraform output -raw active_environment)
NEW_ENV=$([ "$ACTIVE_ENV" = "blue" ] && echo "green" || echo "blue")

# Scale up new environment
aws autoscaling update-auto-scaling-group \
    --auto-scaling-group-name "demo-app-${NEW_ENV}-asg" \
    --desired-capacity 2
```

#### Step 2: Wait for Health Checks

```bash
# Monitor target group health
TG_ARN=$(terraform output -raw "${NEW_ENV}_target_group_arn")

aws elbv2 describe-target-health \
    --target-group-arn "$TG_ARN" \
    --query 'TargetHealthDescriptions[*].[Target.Id,TargetHealth.State]' \
    --output table
```

#### Step 3: Test New Environment

```bash
# Test the new environment
TEST_URL=$(terraform output -raw "${NEW_ENV}_test_url")
curl "$TEST_URL/health"
curl "$TEST_URL/version"
```

#### Step 4: Switch Traffic

```bash
# Switch all traffic to new environment
./scripts/switch-traffic.sh switch $NEW_ENV
```

#### Step 5: Scale Down Old Environment

```bash
# Scale down old environment
aws autoscaling update-auto-scaling-group \
    --auto-scaling-group-name "demo-app-${ACTIVE_ENV}-asg" \
    --desired-capacity 0
```

---

## Traffic Management

### Instant Traffic Switch

```bash
# Switch all traffic to blue
./scripts/switch-traffic.sh switch blue

# Switch all traffic to green
./scripts/switch-traffic.sh switch green
```

### Weighted Traffic Distribution

```bash
# 80% blue, 20% green
./scripts/switch-traffic.sh weighted 80 20

# 50% blue, 50% green
./scripts/switch-traffic.sh weighted 50 50
```

### Canary Deployment

```bash
# Send 10% traffic to green for 5 minutes
./scripts/switch-traffic.sh canary green 10 300
```

**Canary Process:**
1. Routes specified percentage to canary environment
2. Monitors for specified duration
3. Prompts for decision: promote, rollback, or maintain
4. Executes chosen action

### Gradual Traffic Shift

```bash
# Gradually shift traffic to blue in 5 steps over 5 minutes
./scripts/switch-traffic.sh gradual blue 5 60
```

**Gradual Shift Process:**
- Step 1: 20% blue, 80% green
- Step 2: 40% blue, 60% green
- Step 3: 60% blue, 40% green
- Step 4: 80% blue, 20% green
- Step 5: 100% blue, 0% green

---

## Monitoring and Rollback

### Monitoring Dashboard

Access the CloudWatch dashboard:
```bash
# Get dashboard URL
terraform output cloudwatch_dashboard_url
```

**Key Metrics:**
- Target group health (healthy/unhealthy hosts)
- ALB request count and response times
- HTTP status code distribution
- Auto Scaling Group metrics

### Health Check Endpoints

Each environment provides health endpoints:

```bash
# Health check
curl https://blue.your-domain.com/health
curl https://green.your-domain.com/health

# Version information
curl https://blue.your-domain.com/version
curl https://green.your-domain.com/version
```

### Automatic Rollback

The deployment script includes automatic rollback:
- **Triggers**: Error rate > 5%, health check failures
- **Process**: Scales up previous environment, switches traffic back
- **Notification**: Logs rollback reason and actions taken

### Manual Rollback

```bash
# Immediate rollback to previous environment
./scripts/deploy.sh rollback
```

**Rollback Process:**
1. Identifies current and previous environments
2. Scales up previous environment
3. Waits for health checks to pass
4. Switches traffic back
5. Scales down current environment

---

## Advanced Scenarios

### Feature Flags with Blue-Green

Combine feature flags with blue-green deployment:

```bash
# Deploy with feature flag disabled
./scripts/deploy.sh deploy v1.3.0-feature-disabled

# Test with small percentage
./scripts/switch-traffic.sh canary green 5 600

# Enable feature flag in green environment
# (application-specific implementation)

# Gradually increase traffic
./scripts/switch-traffic.sh gradual green 10 300
```

### Database Migration Scenarios

#### Backward-Compatible Changes

```bash
# 1. Deploy database changes (backward compatible)
# 2. Deploy new application version
./scripts/deploy.sh deploy v1.4.0

# 3. Switch traffic
# 4. Remove old database structures (optional)
```

#### Breaking Database Changes

```bash
# 1. Deploy migration scripts
# 2. Run data migration
# 3. Deploy new application version
./scripts/deploy.sh deploy v2.0.0

# 4. Test thoroughly before switching
./scripts/deploy.sh test

# 5. Switch traffic
./scripts/switch-traffic.sh switch green
```

### Multi-Region Blue-Green

For multi-region deployments:

```bash
# Deploy to region 1
AWS_REGION=us-east-1 ./scripts/deploy.sh deploy v1.5.0

# Deploy to region 2
AWS_REGION=us-west-2 ./scripts/deploy.sh deploy v1.5.0

# Update Route53 weighted routing
# (implementation depends on your DNS setup)
```

---

## Troubleshooting

### Common Issues

#### 1. Health Check Failures

**Symptoms:**
- Instances showing as unhealthy in target group
- Deployment script fails during health check phase

**Solutions:**
```bash
# Check instance logs
aws logs get-log-events \
    --log-group-name "/aws/ec2/demoapp/blue/httpd/error" \
    --log-stream-name "i-1234567890abcdef0"

# Check security group rules
aws ec2 describe-security-groups \
    --group-ids sg-xxxxxxxxx

# Verify application is running
ssh -i your-key.pem ec2-user@instance-ip
sudo systemctl status httpd
```

#### 2. Traffic Not Switching

**Symptoms:**
- Traffic switch command succeeds but traffic still goes to old environment
- DNS resolution issues

**Solutions:**
```bash
# Verify listener configuration
LISTENER_ARN=$(terraform output -raw listener_arn)
aws elbv2 describe-listeners --listener-arns "$LISTENER_ARN"

# Check DNS propagation
dig your-domain.com
nslookup your-domain.com

# Clear DNS cache
sudo dscacheutil -flushcache  # macOS
sudo systemctl restart systemd-resolved  # Ubuntu
```

#### 3. Auto Scaling Issues

**Symptoms:**
- Instances not launching
- Scaling operations timing out

**Solutions:**
```bash
# Check Auto Scaling Group status
aws autoscaling describe-auto-scaling-groups \
    --auto-scaling-group-names "demo-app-blue-asg"

# Check launch template
aws ec2 describe-launch-templates \
    --launch-template-names "demo-app-blue-lt"

# Review Auto Scaling activities
aws autoscaling describe-scaling-activities \
    --auto-scaling-group-name "demo-app-blue-asg"
```

#### 4. SSL Certificate Issues

**Symptoms:**
- HTTPS connections failing
- Certificate validation errors

**Solutions:**
```bash
# Verify certificate status
aws acm describe-certificate \
    --certificate-arn "your-certificate-arn"

# Test SSL connection
openssl s_client -connect your-domain.com:443 -servername your-domain.com

# Check ALB listener configuration
aws elbv2 describe-listeners \
    --load-balancer-arn "your-alb-arn"
```

### Debugging Commands

```bash
# Get comprehensive status
./scripts/deploy.sh status

# Test both environments
./scripts/deploy.sh test

# Check traffic distribution
./scripts/switch-traffic.sh status

# View recent deployments
aws logs filter-log-events \
    --log-group-name "/aws/ec2/demoapp" \
    --start-time $(date -d '1 hour ago' +%s)000
```

---

## Best Practices

### Deployment Best Practices

#### 1. Pre-Deployment Checklist

- [ ] Database migrations tested and backward compatible
- [ ] Feature flags configured appropriately
- [ ] Monitoring and alerting in place
- [ ] Rollback plan documented
- [ ] Team notified of deployment window

#### 2. Testing Strategy

```bash
# Automated testing pipeline
./scripts/deploy.sh deploy v1.6.0

# Manual verification checklist
curl https://green.your-domain.com/health
curl https://green.your-domain.com/version
curl https://green.your-domain.com/api/status

# Load testing (optional)
ab -n 1000 -c 10 https://green.your-domain.com/
```

#### 3. Monitoring During Deployment

```bash
# Monitor key metrics
watch -n 5 './scripts/switch-traffic.sh status'

# Watch error rates
aws logs filter-log-events \
    --log-group-name "/aws/applicationelb/demo-app-bg-alb" \
    --filter-pattern "ERROR" \
    --start-time $(date -d '5 minutes ago' +%s)000
```

### Security Best Practices

#### 1. Network Security

```hcl
# Restrict SSH access
variable "ssh_cidr_block" {
  description = "CIDR block for SSH access"
  type        = string
  default     = "10.0.0.0/8"  # Internal network only
}
```

#### 2. IAM Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "autoscaling:UpdateAutoScalingGroup",
        "elbv2:ModifyListener",
        "elbv2:DescribeTargetHealth"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": "us-east-1"
        }
      }
    }
  ]
}
```

#### 3. Secrets Management

```bash
# Use AWS Systems Manager Parameter Store
aws ssm put-parameter \
    --name "/demoapp/database/password" \
    --value "your-secure-password" \
    --type "SecureString"

# Reference in user data
DB_PASSWORD=$(aws ssm get-parameter \
    --name "/demoapp/database/password" \
    --with-decryption \
    --query 'Parameter.Value' \
    --output text)
```

### Cost Optimization

#### 1. Instance Management

```bash
# Use Spot instances for non-production
# (Configure in launch template)

# Right-size instances based on metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/EC2 \
    --metric-name CPUUtilization \
    --dimensions Name=AutoScalingGroupName,Value=demo-app-blue-asg \
    --start-time $(date -d '7 days ago' -u +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 3600 \
    --statistics Average
```

#### 2. Resource Cleanup

```bash
# Automated cleanup of old environments
# (Add to deployment script)

# Clean up unused AMIs
aws ec2 describe-images \
    --owners self \
    --query 'Images[?CreationDate<=`2023-01-01`].[ImageId,CreationDate]' \
    --output table
```

### Operational Best Practices

#### 1. Documentation

- Maintain deployment runbooks
- Document rollback procedures
- Keep architecture diagrams updated
- Record deployment decisions and lessons learned

#### 2. Team Communication

```bash
# Slack notification example
curl -X POST -H 'Content-type: application/json' \
    --data '{"text":"🚀 Blue-Green deployment started: v1.6.0 → Green environment"}' \
    YOUR_SLACK_WEBHOOK_URL
```

#### 3. Compliance and Auditing

```bash
# Log all deployment activities
echo "$(date): Deployment v1.6.0 started by $(whoami)" >> /var/log/deployments.log

# Tag resources for compliance
aws ec2 create-tags \
    --resources i-1234567890abcdef0 \
    --tags Key=DeploymentVersion,Value=v1.6.0 \
           Key=Environment,Value=green \
           Key=DeployedBy,Value=$(whoami)
```

---

## Conclusion

This Blue-Green deployment setup provides:

- **Zero-downtime deployments** with instant rollback capability
- **Comprehensive monitoring** and automated health checks
- **Flexible traffic management** with canary and gradual deployment options
- **Production-ready security** and compliance features
- **Cost-optimized** resource management

The combination of Terraform infrastructure-as-code and automated deployment scripts ensures consistent, reliable deployments while maintaining the flexibility to handle various deployment scenarios.

For additional support or questions, refer to the troubleshooting section or consult the AWS documentation for specific services.