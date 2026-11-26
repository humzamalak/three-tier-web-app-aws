resource "aws_db_subnet_group" "this" {
  name       = var.name
  subnet_ids = aws_subnet.db[*].id
}

resource "aws_db_parameter_group" "this" {
  name   = "${var.name}-pg16"
  family = "postgres16"

  parameter {
    name  = "rds.force_ssl"
    value = "1"
  }

  parameter {
    name  = "log_min_duration_statement"
    value = "500"
  }
}

resource "aws_db_instance" "this" {
  #checkov:skip=CKV_AWS_157:Multi-AZ is a variable (db_multi_az); off by default to halve demo cost.
  #checkov:skip=CKV_AWS_293:Deletion protection is a variable; off by default so the demo can be destroyed.
  #checkov:skip=CKV_AWS_354:Performance Insights uses the AWS-managed key in this demo.
  #checkov:skip=CKV_AWS_118:Enhanced monitoring is out of scope for the demo.
  #checkov:skip=CKV_AWS_161:The app uses the managed master secret; IAM DB auth is a later step.
  #checkov:skip=CKV2_AWS_60:Copy tags to snapshots is set.
  identifier     = var.name
  engine         = "postgres"
  engine_version = "16"
  instance_class = var.db_instance_class

  db_name  = "app"
  username = "app"
  # RDS creates the password and keeps it in Secrets Manager (with rotation).
  manage_master_user_password = true

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp3"
  storage_encrypted     = true

  db_subnet_group_name   = aws_db_subnet_group.this.name
  vpc_security_group_ids = [aws_security_group.db.id]
  parameter_group_name   = aws_db_parameter_group.this.name
  publicly_accessible    = false
  multi_az               = var.db_multi_az

  backup_retention_period         = 7
  copy_tags_to_snapshot           = true
  auto_minor_version_upgrade      = true
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  performance_insights_enabled    = true
  deletion_protection             = var.db_deletion_protection
  skip_final_snapshot             = !var.db_deletion_protection
  final_snapshot_identifier       = var.db_deletion_protection ? "${var.name}-final" : null
  apply_immediately               = true
}
