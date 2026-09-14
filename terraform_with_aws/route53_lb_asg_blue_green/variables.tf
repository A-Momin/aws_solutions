# Variables for Blue-Green Deployment

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "demo-app"
}

variable "existing_vpc_id" {
  description = "ID of the existing VPC"
  type        = string
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "harnesstechtx.com"
}

variable "certificate_arn" {
  description = "ARN of the SSL certificate"
  type        = string
}

variable "ami_id" {
  description = "AMI ID for EC2 instances"
  type        = string
  default     = "ami-053a45fff0a704a47" # Amazon Linux 2023
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "key_pair_name" {
  description = "Name of the EC2 key pair"
  type        = string
}

variable "ssh_cidr_block" {
  description = "CIDR block for SSH access"
  type        = string
  default     = "0.0.0.0/0"
}

variable "health_check_path" {
  description = "Health check path for target groups"
  type        = string
  default     = "/"
}

variable "active_environment" {
  description = "Currently active environment (blue or green)"
  type        = string
  default     = "blue"

  validation {
    condition     = contains(["blue", "green"], var.active_environment)
    error_message = "Active environment must be either 'blue' or 'green'."
  }
}

variable "asg_config" {
  description = "Auto Scaling Group configuration"
  type = object({
    min_size         = number
    max_size         = number
    desired_capacity = number
  })
  default = {
    min_size         = 1
    max_size         = 4
    desired_capacity = 2
  }
}

variable "app_versions" {
  description = "Application versions for blue and green environments"
  type        = map(string)
  default = {
    blue  = "v1.0.0"
    green = "v1.1.0"
  }
}

variable "deployment_config" {
  description = "Deployment configuration"
  type = object({
    enable_auto_rollback = bool
    rollback_threshold   = number
    monitoring_duration  = number
  })
  default = {
    enable_auto_rollback = true
    rollback_threshold   = 5   # percentage of failed requests
    monitoring_duration  = 300 # seconds
  }
}
