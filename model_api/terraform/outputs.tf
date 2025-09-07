output "api_url" {
  description = "URL of the API"
  value       = "http://${aws_lb.api_alb.dns_name}"
}

output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.model_api.repository_url
}