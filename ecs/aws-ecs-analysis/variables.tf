variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "django-bookstore"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "vpc_id" {
  description = "The VPC object"
  type        = string
  default     = "vpc-043506b8f2a3086b7"
}

variable "vpc_cidr_block" {
  description = "The VPC object"
  type        = string
  default     = "20.20.0.0/16"
}

variable "public_subnets" {
  description = "Map of public subnet IDs"
  type        = set(string)
  default     = ["subnet-0923d23cbcc79dc9c", "subnet-07910447c7be16a94"]
}

variable "private_subnets" {
  description = "Map of private subnet IDs"
  type        = set(string)
  default     = ["subnet-080856a486501be0f", "subnet-0760170ed6f75b8eb"]

  #   # If you only need a few fields (e.g., `id` and `availability_zone`), you can define a smaller object:
  #   type = map(object({
  #     id                = string
  #     availability_zone = string
  #   }))
}

# ================================================================
# Route53 Configuration Variables
# ================================================================
variable "r53_hosted_zone_name" {
  description = "The domain name of the Route53 hosted zone"
  type        = string
  default     = "harnesstechtx.com"
}

variable "r53_hosted_zone_id" {
  description = "The id of the Route53 hosted zone"
  type        = string
  default     = "Z01482622Y718COFL2WJT"
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "harnesstechtx.com" # Expires: February 11, 2026
}

variable "subject_alternative_names" {
  description = "List of Subject Alternative Names (SANs) for the ACM certificate"
  type        = list(string)
  default     = ["www.harnesstechtx.com", "blue.harnesstechtx.com", "green.harnesstechtx.com"]
}


# variable "certificate_arn" {
#   description = "ARN of the SSL certificate"
#   type        = string
# }

# ================================================================
# ECS Configuration Variables
# ================================================================
variable "active_environment" {
  description = "Currently active environment (blue or green)"
  type        = string
  default     = "blue"

  validation {
    condition     = contains(["blue", "green"], var.active_environment)
    error_message = "Active environment must be either 'blue' or 'green'."
  }
}

variable "service_desired_count" {
  description = "Desired number of tasks"
  type        = number
  default     = 2
}

variable "ecs_instance_type" {
  description = "EC2 instance type for ECS"
  type        = string
  default     = "t3.medium"
}

variable "task_cpu" {
  description = "CPU units for the task"
  type        = number
  default     = 512
}

variable "task_memory" {
  description = "Memory for the task"
  type        = number
  default     = 1024
}

variable "app_versions" {
  description = "Application versions for blue and green environments"
  type        = map(string)
  default = {
    blue  = "latest"
    green = "latest"
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
    min_size         = 2
    max_size         = 6
    desired_capacity = 2
  }
}

variable "container_port" {
  description = "Port on which the container listens"
  type        = number
  default     = 8000
}

variable "ecr_repository_url" {
  description = "ecr_repository_url"
  type        = string
  default     = "530976901147.dkr.ecr.us-east-1.amazonaws.com/bookstore-ecr-repo"
}

variable "key_pair_name" {
  description = "Name of the EC2 key pair"
  type        = string
  default     = "general_purpose"
}

# variable "dockerhub_image_name" {
#   description = "The full name of the image on Docker Hub (e.g., username/repo)."
#   type        = string
#   default     = "bbcredcap3/harness"
# }

# ================================================================
# Environment Variables for Django Application
# ================================================================
variable "django_settings_module" {
  description = "Django settings module"
  type        = string
  default     = "core.settings.dev_debug"
}

variable "django_static_root" {
  description = "Django settings module"
  type        = string
  default     = ""
}

variable "django_debug" {
  description = "Django debug mode"
  type        = bool
  default     = false
}

variable "django_secret_key" {
  description = ""
  type        = string
  sensitive   = true # Mark as sensitive to prevent output in logs/state
}

variable "django_stripe_secret_key" {
  description = ""
  type        = string
  sensitive   = true # Mark as sensitive to prevent output in logs/state
}

variable "django_stripe_endpoint_secret" {
  description = ""
  type        = string
  sensitive   = true # Mark as sensitive to prevent output in logs/state
}

