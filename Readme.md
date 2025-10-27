# EC2 Automation Project

## 1. Project Overview
This project automates Amazon EC2 instance management using:
- AWS Lambda (serverless function to perform EC2 actions)
- API Gateway (to expose Lambda as an HTTP API)
- Terraform (to create AWS resources automatically)
- Flask Web App (to provide a user-friendly interface)
- Jenkins (to automate API calls when code changes)

Supported actions:
- Create a new EC2 instance
- Start an existing instance
- Stop an instance
- Terminate an instance
- List all instances


## 2. Project Structure
```
EC2-AUTOMATION_JEN/
│
├── terraform/                # Terraform configs for AWS resources
│   ├── api.tf                # Creates API Gateway and routes
│   ├── iam.tf                # Creates IAM role and policies for Lambda
│   ├── lambda.tf             # Creates Lambda function
│   ├── outputs.tf            # Outputs API endpoint after deployment
│   ├── provider.tf           # AWS provider configuration
│   ├── variables.tf          # Variables for Lambda name and zip path
│
├── app.py                    # Flask web app for EC2 control
├── lambda_handler.py         # Lambda function logic for EC2 actions
├── lambda_api_runner.py      # Script to call API (used in Jenkins)
├── lambda.zip                # Packaged Lambda code for deployment
├── aws_ass.pem               # SSH key for EC2 access

├──screenshots
```

## 3. Why Terraform?
Terraform automates AWS resource creation:
- Creates Lambda function, API Gateway, and IAM roles
- Ensures repeatable, consistent deployments
- Tracks changes in version control

## 4. What Each Terraform File Does
- provider.tf: Configures AWS provider and region
- variables.tf: Defines reusable variables (Lambda name, zip path)
- lambda.tf: Creates Lambda function and sets environment variables
- iam.tf: Creates IAM role and attaches policies for EC2 actions
- api.tf: Creates API Gateway, routes, and integrates with Lambda
- outputs.tf: Displays API endpoint after deployment

## 5. Prerequisites
- AWS account
- AWS CLI installed and configured:
  ```bash
  aws configure --profile personal
  ```
- Terraform installed
- Python 3.12 installed
- Install dependencies:
  ```bash
  pip install boto3 requests Flask requests-aws4auth
  ```

## 6. Step-by-Step Setup
### Step 1: Configure AWS Credentials
```bash
aws configure --profile personal
```
Stores your AWS Access Key and Secret Key locally for Terraform and boto3.

### Step 2: Package Lambda Code
```bash
zip lambda.zip lambda_handler.py
```
Bundles Lambda code for deployment via Terraform.

### Step 3: Deploy Infrastructure with Terraform
```bash
cd terraform
terraform init
terraform plan
terraform apply
```
- terraform init: Downloads AWS provider
- terraform plan: Shows resources to create
- terraform apply: Creates resources in AWS

### Step 4: Get API Endpoint
```bash
terraform output api_endpoint
```
Displays API Gateway URL (e.g., https://xxxx.execute-api.us-east-1.amazonaws.com)

### Step 5: Test Lambda API Using curl
Run these commands in your terminal:

#### Create Instance
```bash
curl -X POST https://<API-ENDPOINT>/ -H "Content-Type: application/json" -d '{"action": "create"}'
```

#### Start Instance
```bash
curl -X POST https://<API-ENDPOINT>/ -H "Content-Type: application/json" -d '{"action": "start", "instance_id": "i-xxxxxxxx"}'
```

#### Stop Instance
```bash
curl -X POST https://<API-ENDPOINT>/ -H "Content-Type: application/json" -d '{"action": "stop", "instance_id": "i-xxxxxxxx"}'
```

#### Terminate Instance
```bash
curl -X POST https://<API-ENDPOINT>/ -H "Content-Type: application/json" -d '{"action": "terminate", "instance_id": "i-xxxxxxxx"}'
```

#### List Instances
```bash
curl -X POST https://<API-ENDPOINT>/ -H "Content-Type: application/json" -d '{"action": "list"}'
```

### Step 5: Run Flask App
```bash
python app.py
```
Open browser at: http://127.0.0.1:5000/ec2

## 8. Jenkins Automation
Automate EC2 actions when code changes in GitHub.

### Steps:
1. Install Jenkins and required plugins (Git, Python)
2. Create a Jenkins pipeline job:
   - Pull code from GitHub
   - Run:
     ```bash
     python lambda_api_runner.py
     ```
     with environment variables:
     ```bash
     ACTION=create
     INSTANCE_ID=i-xxxxxxxx
     ```
3. Configure GitHub webhook to trigger Jenkins job on push

### Pipeline Script Example
```
pipeline {
    agent any
    environment {
        ACTION = "create"
        INSTANCE_ID = ""
    }
    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/your-repo.git'
            }
        }
        stage('Run Lambda API') {
            steps {
                sh 'python lambda_api_runner.py'
            }
        }
    }
}
```

## 9. Testing
```bash
python lambda_api_runner.py ACTION=create
python lambda_api_runner.py ACTION=stop INSTANCE_ID=i-xxxxxxxx
```
Expected output:
```json
{
  "message": "Stopped instance i-xxxxxxxx"
}
```


