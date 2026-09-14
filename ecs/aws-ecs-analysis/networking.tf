

# ------------------------
# Security Groups
# ------------------------
resource "aws_security_group" "alb_sg" {
  name_prefix = "${var.project_name}-alb-"
  description = "Security group for Application Load Balancer"
  vpc_id      = var.vpc_id

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

  tags = merge(local.common_tags, { Name = "${var.project_name}-alb-sg" })

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "ecs_sg" {
  name_prefix = "${var.project_name}-ecs-"
  description = "Security group for ECS tasks"
  vpc_id      = var.vpc_id

  ingress {
    description     = "HTTP from ALB"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }

  ingress {
    description = "HTTP from ALB"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.vpc_cidr_block != null ? [var.vpc_cidr_block] : []
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-ecs-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "endpoint_sg" {
  name_prefix = "${var.project_name}-vpc-ep-"
  description = "Allow inbound 443 from ECS tasks/instances to VPC Endpoints"
  vpc_id      = var.vpc_id

  # Inbound rule: Allow HTTPS from the ECS Security Group
  ingress {
    description = "HTTPS from ECS instances/tasks"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    # Allow traffic originating from the security group attached to the ECS instances/tasks
    security_groups = [aws_security_group.ecs_sg.id]
  }

  # Outbound rule: Endpoints don't generally initiate connections, but default all egress is fine.
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-vpc-endpoint-sg"
  })
}

# ECS Endpoint (for agent registration/communication)
resource "aws_vpc_endpoint" "ecs_endpoint" {
  vpc_id              = var.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.ecs"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = var.private_subnets
  security_group_ids  = [aws_security_group.endpoint_sg.id] # Need to create a specific SG for Endpoints
  private_dns_enabled = true
}

# ECR API Endpoint (for registry credentials)
resource "aws_vpc_endpoint" "ecr_api_endpoint" {
  vpc_id              = var.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.ecr.api"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = var.private_subnets
  security_group_ids  = [aws_security_group.endpoint_sg.id]
  private_dns_enabled = true
}

# ECR Docker Endpoint (for image pulling)
resource "aws_vpc_endpoint" "ecr_dkr_endpoint" {
  vpc_id              = var.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.ecr.dkr"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = var.private_subnets
  security_group_ids  = [aws_security_group.endpoint_sg.id]
  private_dns_enabled = true
}

# CloudWatch Logs Endpoint (for task logging)
resource "aws_vpc_endpoint" "logs_endpoint" {
  vpc_id              = var.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.logs"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = var.private_subnets
  security_group_ids  = [aws_security_group.endpoint_sg.id]
  private_dns_enabled = true
}