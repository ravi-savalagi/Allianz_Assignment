resource "aws_iam_role" "lambda_exec" {
  name = "ec2-manager-api-lambda-role"  # New, unique, and descriptive
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Principal = { Service = "lambda.amazonaws.com" }
      Effect = "Allow"
      Sid    = ""
    }]
  })
}

# Attach AWS managed policy for basic Lambda execution (CloudWatch Logs)
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Custom inline policy for EC2 management
resource "aws_iam_role_policy" "lambda_policy" {
  name = "ec2-manager-api-lambda-policy"  # Matches role name for clarity
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "ec2:RunInstances",
          "ec2:DescribeInstances",
          "ec2:StartInstances",
          "ec2:StopInstances",
          "ec2:TerminateInstances",
          "ec2:CreateKeyPair",
          "ec2:DeleteKeyPair",
          "ec2:DescribeKeyPairs",
          "ec2:DescribeSecurityGroups",
          "ec2:CreateSecurityGroup",
          "ec2:AuthorizeSecurityGroupIngress",
          "ec2:DeleteSecurityGroup"
        ],
        Resource = "*"
      }
    ]
  })
}