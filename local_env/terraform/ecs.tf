# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "ecomm-ml-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Environment = var.environment
  }
}

# ECS Task Definitions for each service
module "streamlit_service" {
  source  = "terraform-aws-modules/ecs/aws//modules/service"
  version = "~> 4.0"

  name        = "streamlit"
  cluster_arn = aws_ecs_cluster.main.arn

  cpu    = 512
  memory = 1024

  # Container definition
  container_definitions = {
    "streamlit" = {
      cpu       = 512
      memory    = 1024
      essential = true
      image     = "${aws_ecr_repository.streamlit.repository_url}:latest"
      port_mappings = [
        {
          containerPort = 8501
          hostPort      = 8501
          protocol      = "tcp"
        }
      ]
      environment = [
        {
          name  = "DB_URL"
          value = "postgresql://${var.db_username}:${var.db_password}@${module.db.db_instance_endpoint}/data_warehouse"
        }
      ]
      secrets = [
        {
          name      = "DB_PASSWORD"
          valueFrom = aws_secretsmanager_secret.db_password.arn
        }
      ]
      log_configuration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/streamlit"
          "awslogs-region"        = var.region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  }

  # Security groups
  security_group_ids = [aws_security_group.ecs_sg.id]

  # Network configuration
  network_configuration = {
    subnets          = module.vpc.private_subnets
    security_groups  = [aws_security_group.ecs_sg.id]
    assign_public_ip = false
  }

  # Service discovery
  service_connect_configuration = {
    namespace = aws_service_discovery_http_namespace.main.arn
    service = {
      client_alias = {
        dns_name = "streamlit"
        port     = 8501
      }
      discovery_name = "streamlit"
      port_name      = "streamlit"
    }
  }

  tags = {
    Environment = var.environment
  }
}

# Similar configurations for MLFlow, FastAPI, and other services