terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # For a team, keep state in S3 with locking:
  # backend "s3" {
  #   bucket       = "<state-bucket>"
  #   key          = "three-tier-web-app/terraform.tfstate"
  #   region       = "eu-west-2"
  #   use_lockfile = true
  # }
}

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project   = var.name
      ManagedBy = "terraform"
    }
  }
}

data "aws_caller_identity" "current" {}
data "aws_partition" "current" {}
data "aws_availability_zones" "available" {
  #checkov:skip=CKV_AWS_394:Only the first az_count zones are used (slice in network.tf).
  state = "available"
}
