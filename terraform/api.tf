resource "aws_apigatewayv2_api" "http_api" {
  name          = "${var.lambda_name}-httpapi"  # e.g., "ec2-manager-api-httpapi"
  protocol_type = "HTTP"
  description   = "HTTP API for EC2 automation via Lambda"  # Optional: For clarity in AWS Console
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id                 = aws_apigatewayv2_api.http_api.id
  integration_type       = "AWS_PROXY"  # Passes event/body directly to your lambda_handler (e.g., event.get('action'))
  integration_uri        = aws_lambda_function.ec2_api.invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"  # Modern format for Lambda events (JSON body preserved)
}

resource "aws_apigatewayv2_route" "default_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /"  # Matches curl/Flask/app.py calls (e.g., POST https://.../ with {"action": "create"})
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

# OPTIONS route for CORS preflight (handles browser/Flask OPTIONS requests; no parameters needed)
# Your lambda_handler.py returns CORS headers (e.g., Access-Control-Allow-Origin: *), so API Gateway passes them back
resource "aws_apigatewayv2_route" "options_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "OPTIONS /{proxy+}"  # Catches OPTIONS requests to any path (e.g., OPTIONS / for preflight)
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"  # Same Lambda integration (returns empty 200 with CORS headers)

  api_key_required = false
  # Removed: request_parameter blocks (unnecessary for basic CORS; causes syntax errors in HTTP API v2)
  # Lambda response handles headers like Allow-Origin, Allow-Methods (POST, OPTIONS), Allow-Headers (Content-Type, Authorization)
}

resource "aws_apigatewayv2_stage" "default_stage" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default"  # Default stage (no custom name needed)
  auto_deploy = true  # Auto-deploys changes (e.g., after terraform apply)
}

resource "aws_lambda_permission" "apigw_allow" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ec2_api.function_name  # e.g., "ec2-manager-api"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"  # Allows POST and OPTIONS methods on all routes
}