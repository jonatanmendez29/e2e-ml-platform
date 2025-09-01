output "rds_endpoint" {
  description = "The endpoint of the RDS instance"
  value       = aws_db_instance.data_warehouse.endpoint
}

output "s3_bucket_name" {
  description = "The name of the S3 bucket"
  value       = aws_s3_bucket.data_lake.bucket
}