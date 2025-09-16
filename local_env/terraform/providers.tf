terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }

  backend "s3" {
    bucket = "your-terraform-state-bucket"
    key    = "ecomm-ml-platform/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.region
}