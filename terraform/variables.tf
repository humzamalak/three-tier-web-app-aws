variable "name" {
  description = "Name prefix for all resources."
  type        = string
  default     = "three-tier"
}

variable "region" {
  type    = string
  default = "eu-west-2"
}

variable "vpc_cidr" {
  type    = string
  default = "10.20.0.0/16"
}

variable "az_count" {
  description = "Number of availability zones (2 or 3)."
  type        = number
  default     = 2

  validation {
    condition     = var.az_count >= 2 && var.az_count <= 3
    error_message = "az_count must be 2 or 3."
  }
}

variable "single_nat_gateway" {
  description = "One NAT gateway for all AZs (cheaper) instead of one per AZ (highly available)."
  type        = bool
  default     = true
}

variable "image_tag" {
  description = "Image tag for the first deploy. Later deploys are done by GitHub Actions."
  type        = string
  default     = "latest"
}

variable "web_desired_count" {
  type    = number
  default = 2
}

variable "api_desired_count" {
  type    = number
  default = 2
}

variable "api_max_count" {
  description = "Upper limit for API auto scaling."
  type        = number
  default     = 6
}

variable "db_instance_class" {
  type    = string
  default = "db.t4g.micro"
}

variable "db_multi_az" {
  description = "Standby RDS instance in a second AZ. Doubles the database cost."
  type        = bool
  default     = false
}

variable "db_deletion_protection" {
  description = "Set to true for anything that is not a short-lived demo."
  type        = bool
  default     = false
}

variable "certificate_arn" {
  description = "ACM certificate ARN for HTTPS on the ALB. Leave empty to serve HTTP only (demo)."
  type        = string
  default     = ""
}

variable "github_repository" {
  description = "owner/repo allowed to deploy through GitHub OIDC. Leave empty to skip the deploy role."
  type        = string
  default     = ""
}

variable "create_github_oidc_provider" {
  description = "Create the GitHub OIDC provider. Set to false if the account already has one."
  type        = bool
  default     = true
}

variable "log_retention_days" {
  type    = number
  default = 30
}
