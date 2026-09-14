# Blue-Green Deployment Infrastructure for Demo Application
# This configuration creates infrastructure to support blue-green deployments

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Data sources for existing infrastructure
data "aws_vpc" "existing" {
  id = var.existing_vpc_id
}

data "aws_subnets" "public" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.existing.id]
  }

  filter {
    name   = "tag:Name"
    values = ["*public*"]
  }
}

data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.existing.id]
  }

  filter {
    name   = "tag:Name"
    values = ["*private*"]
  }
}

data "aws_route53_zone" "existing" {
  name = var.domain_name
}

# Local values for environment management
locals {
  environments = ["blue", "green"]

  common_tags = {
    Project     = var.project_name
    Environment = "blue-green"
    ManagedBy   = "terraform"
  }
}

# ------------------------
# Security Groups
# ------------------------
resource "aws_security_group" "alb_sg" {
  name_prefix = "${var.project_name}-alb-bg-"
  description = "Security group for Blue-Green ALB"
  vpc_id      = data.aws_vpc.existing.id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-alb-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "web_sg" {
  name_prefix = "${var.project_name}-web-bg-"
  description = "Security group for Blue-Green web servers"
  vpc_id      = data.aws_vpc.existing.id

  ingress {
    description     = "HTTP from ALB"
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_cidr_block]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-web-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# ------------------------
# Application Load Balancer
# ------------------------
resource "aws_lb" "main" {
  name               = "${var.project_name}-bg-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = data.aws_subnets.public.ids

  enable_deletion_protection = false

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-bg-alb"
  })
}

# ------------------------
# Target Groups (Blue and Green)
# ------------------------
resource "aws_lb_target_group" "environments" {
  for_each = toset(local.environments)

  name     = "${var.project_name}-${each.key}-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = data.aws_vpc.existing.id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = var.health_check_path
    matcher             = "200"
    port                = "traffic-port"
    protocol            = "HTTP"
  }

  tags = merge(local.common_tags, {
    Name        = "${var.project_name}-${each.key}-tg"
    Environment = each.key
  })

  lifecycle {
    create_before_destroy = true
  }
}

# ------------------------
# ALB Listeners
# ------------------------
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }

  tags = local.common_tags
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-Res-2021-06"
  certificate_arn   = var.certificate_arn

  # Default action points to the active environment (initially blue)
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.environments["blue"].arn
  }

  tags = local.common_tags
}

# ------------------------
# Launch Templates
# ------------------------
resource "aws_launch_template" "environments" {
  for_each = toset(local.environments)

  name_prefix   = "${var.project_name}-${each.key}-"
  image_id      = var.ami_id
  instance_type = var.instance_type
  key_name      = var.key_pair_name

  vpc_security_group_ids = [aws_security_group.web_sg.id]

  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    environment = each.key
    app_version = var.app_versions[each.key]
  }))

  tag_specifications {
    resource_type = "instance"
    tags = merge(local.common_tags, {
      Name        = "${var.project_name}-${each.key}-instance"
      Environment = each.key
    })
  }

  lifecycle {
    create_before_destroy = true
  }
}

# ------------------------
# Auto Scaling Groups
# ------------------------
resource "aws_autoscaling_group" "environments" {
  for_each = toset(local.environments)

  name                      = "${var.project_name}-${each.key}-asg"
  vpc_zone_identifier       = data.aws_subnets.private.ids
  target_group_arns         = [aws_lb_target_group.environments[each.key].arn]
  health_check_type         = "ELB"
  health_check_grace_period = 300

  min_size         = var.asg_config.min_size
  max_size         = var.asg_config.max_size
  desired_capacity = each.key == var.active_environment ? var.asg_config.desired_capacity : 0

  launch_template {
    id      = aws_launch_template.environments[each.key].id
    version = "$Latest"
  }

  # Instance refresh configuration for rolling updates
  instance_refresh {
    strategy = "Rolling"
    preferences {
      min_healthy_percentage = 50
      instance_warmup        = 300
    }
  }

  tag {
    key                 = "Name"
    value               = "${var.project_name}-${each.key}-asg"
    propagate_at_launch = false
  }

  tag {
    key                 = "Project"
    value               = var.project_name
    propagate_at_launch = true
  }

  tag {
    key                 = "Environment"
    value               = each.key
    propagate_at_launch = true
  }

  lifecycle {
    create_before_destroy = true
    ignore_changes        = [desired_capacity]
  }
}

# ------------------------
# Auto Scaling Policies
# ------------------------
resource "aws_autoscaling_policy" "scale_up" {
  for_each = toset(local.environments)

  name                   = "${var.project_name}-${each.key}-scale-up"
  scaling_adjustment     = 1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.environments[each.key].name
}

resource "aws_autoscaling_policy" "scale_down" {
  for_each = toset(local.environments)

  name                   = "${var.project_name}-${each.key}-scale-down"
  scaling_adjustment     = -1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.environments[each.key].name
}

# ------------------------
# CloudWatch Alarms
# ------------------------
resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  for_each = toset(local.environments)

  alarm_name          = "${var.project_name}-${each.key}-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors ec2 cpu utilization"
  alarm_actions       = [aws_autoscaling_policy.scale_up[each.key].arn]

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.environments[each.key].name
  }

  tags = merge(local.common_tags, {
    Environment = each.key
  })
}

resource "aws_cloudwatch_metric_alarm" "low_cpu" {
  for_each = toset(local.environments)

  alarm_name          = "${var.project_name}-${each.key}-low-cpu"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "10"
  alarm_description   = "This metric monitors ec2 cpu utilization"
  alarm_actions       = [aws_autoscaling_policy.scale_down[each.key].arn]

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.environments[each.key].name
  }

  tags = merge(local.common_tags, {
    Environment = each.key
  })
}

# ------------------------
# Route53 Records for Testing
# ------------------------
resource "aws_route53_record" "blue" {
  zone_id = data.aws_route53_zone.existing.zone_id
  name    = "blue.${var.domain_name}"
  type    = "A"

  alias {
    name                   = aws_lb.main.dns_name
    zone_id                = aws_lb.main.zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "green" {
  zone_id = data.aws_route53_zone.existing.zone_id
  name    = "green.${var.domain_name}"
  type    = "A"

  alias {
    name                   = aws_lb.main.dns_name
    zone_id                = aws_lb.main.zone_id
    evaluate_target_health = true
  }
}

# ------------------------
# ALB Listener Rules for Testing
# ------------------------
resource "aws_lb_listener_rule" "blue_test" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.environments["blue"].arn
  }

  condition {
    host_header {
      values = ["blue.${var.domain_name}"]
    }
  }

  tags = merge(local.common_tags, {
    Environment = "blue"
  })
}

resource "aws_lb_listener_rule" "green_test" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 101

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.environments["green"].arn
  }

  condition {
    host_header {
      values = ["green.${var.domain_name}"]
    }
  }

  tags = merge(local.common_tags, {
    Environment = "green"
  })
}

# ------------------------
# S3 Bucket for Deployment Artifacts
# ------------------------
resource "aws_s3_bucket" "deployment_artifacts" {
  bucket = "${var.project_name}-bg-deployment-artifacts-${random_id.bucket_suffix.hex}"

  tags = local.common_tags
}

resource "aws_s3_bucket_versioning" "deployment_artifacts" {
  bucket = aws_s3_bucket.deployment_artifacts.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "deployment_artifacts" {
  bucket = aws_s3_bucket.deployment_artifacts.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# ------------------------
# IAM Role for CodeDeploy (Optional)
# ------------------------
resource "aws_iam_role" "codedeploy_role" {
  name = "${var.project_name}-codedeploy-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "codedeploy.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "codedeploy_role" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSCodeDeployRole"
  role       = aws_iam_role.codedeploy_role.name
}

# ------------------------
# CloudWatch Dashboard
# ------------------------
resource "aws_cloudwatch_dashboard" "blue_green" {
  dashboard_name = "${var.project_name}-blue-green-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", aws_lb.main.arn_suffix],
            [".", "RequestCount", ".", "."],
            [".", "HTTPCode_Target_2XX_Count", ".", "."],
            [".", "HTTPCode_Target_4XX_Count", ".", "."],
            [".", "HTTPCode_Target_5XX_Count", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "ALB Metrics"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/ApplicationELB", "HealthyHostCount", "TargetGroup", aws_lb_target_group.environments["blue"].arn_suffix],
            [".", "UnHealthyHostCount", ".", "."],
            [".", "HealthyHostCount", "TargetGroup", aws_lb_target_group.environments["green"].arn_suffix],
            [".", "UnHealthyHostCount", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Target Group Health"
          period  = 300
        }
      }
    ]
  })
}
