resource "aws_mwaa_environment" "airflow" {
  name          = "ecomm-airflow-${var.environment}"
  execution_role_arn = aws_iam_role.mwaa_execution_role.arn

  source_bucket_arn = aws_s3_bucket.airflow_dags.arn
  dag_s3_path       = "dags/"

  network_configuration {
    security_group_ids = [aws_security_group.mwaa_sg.id]
    subnet_ids         = module.vpc.private_subnets
  }

  environment_class = "mw1.small"

  max_workers = 5

  # Airflow configuration options
  airflow_configuration_options = {
    "core.default_timezone" = "utc"
    "core.load_examples"    = "False"
  }

  logging_configuration {
    dag_processing_logs {
      enabled   = true
      log_level = "INFO"
    }

    scheduler_logs {
      enabled   = true
      log_level = "INFO"
    }

    task_logs {
      enabled   = true
      log_level = "INFO"
    }

    webserver_logs {
      enabled   = true
      log_level = "INFO"
    }

    worker_logs {
      enabled   = true
      log_level = "INFO"
    }
  }

  tags = {
    Environment = var.environment
  }
}

# S3 bucket for Airflow DAGs
resource "aws_s3_bucket" "airflow_dags" {
  bucket = "ecomm-airflow-dags-${var.environment}"

  tags = {
    Environment = var.environment
  }
}

# Upload your DAGs to S3
resource "aws_s3_object" "dags" {
  for_each = fileset("${path.module}/../airflow/dags/", "**")

  bucket = aws_s3_bucket.airflow_dags.id
  key    = "dags/${each.value}"
  source = "${path.module}/../airflow/dags/${each.value}"
  etag   = filemd5("${path.module}/../airflow/dags/${each.value}")
}