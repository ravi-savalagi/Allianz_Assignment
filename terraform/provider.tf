terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  profile = "personal"  # Added: Uses your IAM user creds (from aws configure --profile personal)
  region  = "us-east-1"
}