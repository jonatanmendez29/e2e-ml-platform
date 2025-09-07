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

# S3 Bucket for storing analysis results
resource "aws_s3_bucket" "causal_analysis_results" {
  bucket = "causal-analysis-results-${random_id.bucket_suffix.hex}"

  tags = {
    Name = "CausalAnalysisResults"
  }
}

resource "random_id" "bucket_suffix" {
  byte_length = 8
}

# SageMaker Notebook Instance for causal analysis
resource "aws_sagemaker_notebook_instance" "causal_analysis" {
  name          = "causal-analysis-notebook"
  role_arn      = aws_iam_role.sagemaker_role.arn
  instance_type = "ml.t3.medium"

  tags = {
    Name = "CausalAnalysisNotebook"
  }
}

# IAM Role for SageMaker
resource "aws_iam_role" "sagemaker_role" {
  name = "sagemaker-causal-analysis-role"

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

# Output the notebook URL
output "notebook_url" {
  value = "https://${aws_sagemaker_notebook_instance.causal_analysis.id}.notebook.${var.region}.sagemaker.aws"
}

output "s3_bucket_name" {
  value = aws_s3_bucket.causal_analysis_results.bucket
}