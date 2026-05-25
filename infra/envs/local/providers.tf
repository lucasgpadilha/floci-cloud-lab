provider "aws" {
  region                      = var.aws_region
  access_key                  = "test"
  secret_key                  = "test"
  s3_use_path_style           = true
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  endpoints {
    s3         = var.aws_endpoint_url
    dynamodb   = var.aws_endpoint_url
    logs       = var.aws_endpoint_url
    cloudwatch = var.aws_endpoint_url
    iam        = var.aws_endpoint_url
    sts        = var.aws_endpoint_url
  }
}
