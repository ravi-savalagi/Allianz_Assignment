# resource "aws_iam_role" "lambda_exec" {
#   name = "${var.lambda_name}-role"  # e.g., "ec2-manager-api-role"
#   assume_role_policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [{
#       Action = "sts:AssumeRole"
#       Principal = { Service = "lambda.amazonaws.com" }
#       Effect = "Allow"
#       Sid    = ""  # Optional: Can remove Sid
#     }]
#   })
# }

# # Added: Attach managed basic execution role (standard for CloudWatch Logs)
# resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
#   role       = aws_iam_role.lambda_exec.name
#   policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
# }

# resource "aws_iam_role_policy" "lambda_policy" {
#   name = "${var.lambda_name}-policy"  # e.g., "ec2-manager-api-policy"
#   role = aws_iam_role.lambda_exec.id

#   policy = jsonencode({
#     Version = "2012-10-17",
#     Statement = [
#       {
#         Effect = "Allow",
#         Action = [
#           "ec2:RunInstances",
#           "ec2:DescribeInstances",
#           "ec2:StartInstances",
#           "ec2:StopInstances",
#           "ec2:TerminateInstances",
#           "ec2:CreateKeyPair",
#           "ec2:DeleteKeyPair",  # Optional: If you want Lambda to clean up keys
#           "ec2:DescribeKeyPairs",
#           "ec2:DescribeSecurityGroups",
#           "ec2:CreateSecurityGroup",  # Extra: Allows Lambda to create SG if needed (your handler hardcodes ID)
#           "ec2:AuthorizeSecurityGroupIngress"  # Extra: For inbound rules (e.g., SSH)
#         ],
#         Resource = "*"  # Demo: Restrict to specific ARNs in prod (e.g., "arn:aws:ec2:us-east-1:*:instance/*")
#       }
#       # Removed: SSM:GetParameter (not used in your lambda_handler.py—add back if storing keys in SSM)
#       # Removed: logs:* (now handled by AWSLambdaBasicExecutionRole attachment above)
#     ]
#   })
# }





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
          "ec2:AuthorizeSecurityGroupIngress"
        ],
        Resource = "*"
      }
    ]
  })
}