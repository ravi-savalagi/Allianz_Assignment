
resource "aws_lambda_function" "ec2_api" {
  function_name    = "ec2-manager-api-lambda"  # New unique name to avoid conflict
  filename         = var.lambda_zip_path
  handler          = "lambda_handler.lambda_handler"
  runtime          = "python3.12"
  role             = aws_iam_role.lambda_exec.arn
  timeout          = 300
  source_code_hash = filebase64sha256(var.lambda_zip_path)

  environment {
    variables = {
      REGION = "us-east-1"
      ami_id = "ami-052064a798f08f0d3"

    }
  }
}


