terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# S3 Bucket for MLflow Artifacts
resource "aws_s3_bucket" "mlflow_artifacts" {
  bucket = "mlflow-artifacts-${random_id.bucket_suffix.hex}"

  tags = {
    Name = "MLflowArtifacts"
  }
}

resource "random_id" "bucket_suffix" {
  byte_length = 8
}

# RDS for MLflow Metadata
resource "aws_db_instance" "mlflow_metadata" {
  identifier             = "mlflow-metadata"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  engine                 = "postgres"
  engine_version         = "13.7"
  username               = "mlflow"
  password               = var.mlflow_db_password
  db_name                = "mlflow"
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  publicly_accessible    = true
  skip_final_snapshot    = true

  tags = {
    Name = "MLflowMetadata"
  }
}

# ECS Cluster for MLflow Server
resource "aws_ecs_cluster" "mlflow_cluster" {
  name = "mlflow-cluster"
}

# ECS Task Definition for MLflow
resource "aws_ecs_task_definition" "mlflow_server" {
  family                   = "mlflow-server"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([{
    name      = "mlflow-server"
    image     = "mlflow-server:latest"  # You would push your custom image to ECR
    essential = true
    portMappings = [{
      containerPort = 5000
      hostPort      = 5000
      protocol      = "tcp"
    }]
    environment = [
      {
        name  = "MLFLOW_TRACKING_URI"
        value = "http://localhost:5000"
      },
      {
        name  = "MLFLOW_BACKEND_STORE_URI"
        value = "postgresql://mlflow:${var.mlflow_db_password}@${aws_db_instance.mlflow_metadata.endpoint}/mlflow"
      },
      {
        name  = "MLFLOW_ARTIFACT_ROOT"
        value = "s3://${aws_s3_bucket.mlflow_artifacts.bucket}"
      }
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/ecs/mlflow-server"
        "awslogs-region"        = var.region
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])
}

# SageMaker Endpoint for Churn Prediction (Example)
resource "aws_sagemaker_endpoint" "churn_prediction" {
  name = "churn-prediction-endpoint"

  endpoint_config_name = aws_sagemaker_endpoint_configuration.churn_prediction.name
}

resource "aws_sagemaker_endpoint_configuration" "churn_prediction" {
  name = "churn-prediction-config"

  production_variants {
    variant_name           = "primary"
    model_name             = aws_sagemaker_model.churn_prediction.name
    initial_instance_count = 1
    instance_type          = "ml.t2.medium"
  }
}

resource "aws_sagemaker_model" "churn_prediction" {
  name               = "churn-prediction-model"
  execution_role_arn = aws_iam_role.sagemaker_role.arn

  primary_container {
    image = "${aws_ecr_repository.ml_models.repository_url}:churn-prediction"
    mode  = "SingleModel"
  }
}

# IAM Roles
resource "aws_iam_role" "sagemaker_role" {
  name = "sagemaker-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "sagemaker.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "sagemaker_s3" {
  role       = aws_iam_role.sagemaker_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}