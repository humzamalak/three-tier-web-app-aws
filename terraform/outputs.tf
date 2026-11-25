output "app_url" {
  description = "Open this in a browser."
  value       = "${local.https ? "https" : "http"}://${aws_lb.this.dns_name}"
}

output "ecr_repositories" {
  value = { for k, r in aws_ecr_repository.this : k => r.repository_url }
}

output "ecs_cluster" {
  value = aws_ecs_cluster.this.name
}

output "db_endpoint" {
  value = aws_db_instance.this.address
}

output "db_secret_arn" {
  description = "Secrets Manager secret that holds the database password (managed by RDS)."
  value       = local.db_secret_arn
}

output "github_deploy_role_arn" {
  description = "Set this as the AWS_DEPLOY_ROLE_ARN repository variable in GitHub."
  value       = local.deploy_enabled ? aws_iam_role.deploy[0].arn : null
}
