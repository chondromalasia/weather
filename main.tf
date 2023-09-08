provider "aws" {
  region = "eu-central-1"
}

resource "aws_instance" "vps" {
  ami           = "ami-07c27171ff332e277"
  instance_type = "t4g.micro"

  tags = {
    Name = "weather-vps"
  }
}

resource "aws_s3_bucket" "terraform_state" {
  bucket = "weather-state"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_versioning" "enabled" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "default" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "public_access" {
  bucket                  = aws_s3_bucket.terraform_state.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_dynamodb_table" "terraform_locks" {
  name         = "weather_locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"
  attribute {
    name = "LockID"
    type = "S"
  }
}

terraform {
  backend "s3" {
    bucket = "weather-state"
    key    = "global/s3/terraform.tfstate"
    region = "eu-central-1"

    dynamodb_table = "weather_locks"
    encrypt        = true
  }
}
