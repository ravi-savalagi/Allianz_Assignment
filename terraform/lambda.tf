# resource "aws_lambda_function" "ec2_api" {  # Renamed resource to match var.lambda_name for consistency
#   function_name    = var.lambda_name
#   filename         = var.lambda_zip_path
#   handler          = "lambda_handler.lambda_handler"  # Matches your lambda_handler.py
#   runtime          = "python3.12"  # Updated: Matches your local Python 3.12 (better than 3.9; boto3 compatible)
#   role             = aws_iam_role.lambda_exec.arn
#   timeout          = 300  # Good: Allows waiter.wait() in create action (up to 5 min)
#   source_code_hash = filebase64sha256(var.lambda_zip_path)  # Detects zip changes

#   environment {  # Added: For flexibility (your handler hardcodes us-east-1, but useful for multi-region)
#     variables = {
#       REGION = "us-east-1"
#     }
#   }
# }


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
    }
  }
}