# Example terraform.tfvars file for Django ECS Deployment

# AWS Configuration
aws_region = "us-east-1"

# Project Configuration
project_name = "django-bookstore"

# Existing Infrastructure
domain_name   = "harnesstechtx.com"
key_pair_name = "general_purpose" # Replace with your key pair name

# ================================================================
# ECS Configuration Variables
# ================================================================
ecs_instance_type     = "t3.medium"
task_cpu              = 1024
task_memory           = 2048
service_desired_count = 2

# Auto Scaling Configuration
asg_config = {
  min_size         = 2
  max_size         = 4
  desired_capacity = 2
}

# Blue-Green Configuration
active_environment = "blue"
app_versions = {
  blue  = "latest"
  green = "latest"
}

# ================================================================
# Environment Variables for Django Application
# ================================================================
# django_settings_module = "bookstore.core.settings.production"
django_settings_module = "core.settings.dev_debug"
django_debug           = false
# django_allowed_hosts=""
# django_cors_allowed_origins="http://localhost:8000,http://localhost:8010,http://127.0.0.1:8000,http://127.0.0.1:8010"