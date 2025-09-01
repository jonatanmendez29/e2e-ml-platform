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

# Create a VPC
resource "aws_vpc" "data_pipeline_vpc" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "DataPipelineVPC"
  }
}

# Create a subnet
resource "aws_subnet" "data_pipeline_subnet" {
  vpc_id            = aws_vpc.data_pipeline_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"

  tags = {
    Name = "DataPipelineSubnet"
  }
}

# Create an Internet Gateway
resource "aws_internet_gateway" "data_pipeline_igw" {
  vpc_id = aws_vpc.data_pipeline_vpc.id

  tags = {
    Name = "DataPipelineIGW"
  }
}

# Create a route table
resource "aws_route_table" "data_pipeline_rt" {
  vpc_id = aws_vpc.data_pipeline_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.data_pipeline_igw.id
  }

  tags = {
    Name = "DataPipelineRouteTable"
  }
}

# Associate route table with subnet
resource "aws_route_table_association" "data_pipeline_rta" {
  subnet_id      = aws_subnet.data_pipeline_subnet.id
  route_table_id = aws_route_table.data_pipeline_rt.id
}

# Create a security group for RDS
resource "aws_security_group" "rds_sg" {
  name        = "rds-security-group"
  description = "Allow inbound traffic to RDS"
  vpc_id      = aws_vpc.data_pipeline_vpc.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "RDSSecurityGroup"
  }
}

# Create an RDS PostgreSQL instance
resource "aws_db_instance" "data_warehouse" {
  identifier             = "data-warehouse"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  engine                 = "postgres"
  engine_version         = "13.7"
  username               = "admin"
  password               = var.db_password
  db_name                = "data_warehouse"
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  publicly_accessible    = true
  skip_final_snapshot    = true

  tags = {
    Name = "DataWarehouse"
  }
}

# Create an S3 bucket for data storage
resource "aws_s3_bucket" "data_lake" {
  bucket = "ecommerce-data-lake-${random_id.bucket_suffix.hex}"

  tags = {
    Name = "EcommerceDataLake"
  }
}

resource "random_id" "bucket_suffix" {
  byte_length = 8
}

# Output the RDS endpoint and S3 bucket name
output "rds_endpoint" {
  value = aws_db_instance.data_warehouse.endpoint
}

output "s3_bucket_name" {
  value = aws_s3_bucket.data_lake.bucket
}