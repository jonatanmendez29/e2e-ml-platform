module "db" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 5.0"

  identifier = "ecomm-ml-db"

  engine               = "postgres"
  engine_version       = "13.7"
  instance_class       = "db.t3.medium"
  allocated_storage    = 20

  db_name  = "data_warehouse"
  username = var.db_username
  password = var.db_password
  port     = "5432"

  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  subnet_ids             = module.vpc.private_subnets

  maintenance_window = "Mon:00:00-Mon:03:00"
  backup_window      = "03:00-06:00"

  # Enhanced monitoring
  monitoring_interval = 30
  monitoring_role_arn = aws_iam_role.rds_monitoring.arn

  # Disable public access
  publicly_accessible = false

  # Enable deletion protection
  deletion_protection = true

  tags = {
    Environment = var.environment
  }
}

# Create separate databases for each service
resource "postgresql_database" "airflow_metadata" {
  name  = "airflow_metadata"
  owner = var.db_username
}

resource "postgresql_database" "mlflow_tracking" {
  name  = "mlflow_tracking"
  owner = var.db_username
}

resource "postgresql_database" "data_warehouse" {
  name  = "data_warehouse"
  owner = var.db_username
}