
# EC2-AUTOMATION_JEN: Complete EC2 Lifecycle Automation

## 📦 Project Structure

```
EC2-AUTOMATION_JEN/
├── terraform/                # Terraform IaC files
│   ├── api.tf                # API Gateway setup
│   ├── iam.tf                # IAM roles and policies
│   ├── lambda.tf             # Lambda function configuration
│   ├── outputs.tf            # Terraform outputs
│   ├── provider.tf           # AWS provider setup
│   ├── variables.tf          # Input variables
├── app.py                    # Flask UI for EC2 control
├── lambda_api_runner.py      # Jenkins runner script
├── lambda_handler.py         # Lambda function code
├── lambda.zip                # Packaged Lambda deployment
├── screenshots
├── Readme.md
```

---

## 🛠️ Prerequisites

- AWS CLI configured with credentials
- Terraform installed
- Python 3.12
- Jenkins installed and configured
- IAM user with EC2, Lambda, Secrets Manager permissions

---

## 🚀 How It Works

### Lambda Function
- Handles EC2 actions: create, start, stop, terminate, list
- Stores SSH private key in Secrets Manager
- Returns public IP and SSH command

### API Gateway
- HTTP API with POST and OPTIONS routes
- Forwards requests to Lambda using AWS_PROXY integration

### Terraform
- Provisions Lambda, API Gateway, IAM roles
- Auto-deploys changes with `$default` stage

### Flask UI
- Web interface to trigger EC2 actions
- Displays instance details and SSH command

### Jenkins
- Automates API calls using `lambda_api_runner.py`
- Can be triggered manually or on GitHub push

---

## ⚙️ Setup Instructions

### 1. Deploy Infrastructure with Terraform
```bash
cd terraform
terraform init
terraform apply
```

### 2. Package Lambda Function
```bash
zip lambda.zip lambda_handler.py
```

### 3. Run Flask UI
```bash
python app.py
```
Access at: `http://127.0.0.1:5000/ec2`

---

## 🧪 API Payload Examples

### Create Instance
```json
{ "body": "{"action": "create", "name": "demo-instance"}" }
```

### Start Instance
```json
{ "body": "{"action": "start", "instance_id": "i-xxxxxxxxxxxxxxxxx"}" }
```

### Stop Instance
```json
{ "body": "{"action": "stop", "instance_id": "i-xxxxxxxxxxxxxxxxx"}" }
```

### Terminate Instance
```json
{ "body": "{"action": "terminate", "instance_id": "i-xxxxxxxxxxxxxxxxx"}" }
```

### List Instances
```json
{ "body": "{"action": "list"}" }
```

---

## 🔐 IAM Permissions

Attach these to Lambda role:
```json
{
  "Effect": "Allow",
  "Action": [
    "ec2:*",
    "secretsmanager:CreateSecret",
    "secretsmanager:GetSecretValue",
    "secretsmanager:DeleteSecret",
    "secretsmanager:PutSecretValue",
    "secretsmanager:UpdateSecret",
    "secretsmanager:ListSecrets"
  ],
  "Resource": "*"
}
```
Also attach: `AWSLambdaBasicExecutionRole`

---

## 🧰 Jenkins Pipeline Configuration

### Sample Jenkinsfile
```groovy
pipeline {
  agent any
  environment {
    ENDPOINT = 'https://<your-api-id>.execute-api.us-east-1.amazonaws.com'
    MY_IP = '167.103.6.167/32'
  }
  stages {
    stage('Run Lambda API') {
      steps {
        bat 'python lambda_api_runner.py'
      }
    }
  }
}
```

---

## 🔑 SSH Key Retrieval

```bash
aws secretsmanager get-secret-value --secret-id demo-instance-key-xxxx --query SecretString --output text > demo-instance-key.pem
chmod 400 demo-instance-key.pem
ssh -i demo-instance-key.pem ec2-user@<public-ip>
```

---

