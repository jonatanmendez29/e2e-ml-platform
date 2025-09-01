output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.analytics_dashboard.repository_url
}

output "dashboard_url" {
  description = "URL of the analytics dashboard"
  value       = "http://${aws_ecs_service.analytics_dashboard.load_balancer[0].dns_name}:8501"
}