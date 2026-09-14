# Outputs for Blue-Green Deployment

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "Zone ID of the Application Load Balancer"
  value       = aws_lb.main.zone_id
}

output "blue_target_group_arn" {
  description = "ARN of the blue target group"
  value       = aws_lb_target_group.environments["blue"].arn
}

output "green_target_group_arn" {
  description = "ARN of the green target group"
  value       = aws_lb_target_group.environments["green"].arn
}

output "blue_asg_name" {
  description = "Name of the blue Auto Scaling Group"
  value       = aws_autoscaling_group.environments["blue"].name
}

output "green_asg_name" {
  description = "Name of the green Auto Scaling Group"
  value       = aws_autoscaling_group.environments["green"].name
}

output "blue_test_url" {
  description = "URL for testing blue environment"
  value       = "https://blue.${var.domain_name}"
}

output "green_test_url" {
  description = "URL for testing green environment"
  value       = "https://green.${var.domain_name}"
}

output "production_url" {
  description = "Production URL"
  value       = "https://${var.domain_name}"
}

output "deployment_bucket" {
  description = "S3 bucket for deployment artifacts"
  value       = aws_s3_bucket.deployment_artifacts.bucket
}

output "cloudwatch_dashboard_url" {
  description = "URL to CloudWatch dashboard"
  value       = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.blue_green.dashboard_name}"
}

output "listener_arn" {
  description = "ARN of the HTTPS listener"
  value       = aws_lb_listener.https.arn
}

output "security_group_ids" {
  description = "Security group IDs"
  value = {
    alb = aws_security_group.alb_sg.id
    web = aws_security_group.web_sg.id
  }
}
