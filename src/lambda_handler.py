import json
import boto3
import os
import time
from botocore.exceptions import ClientError
import uuid


ec2 = boto3.client('ec2', region_name='us-east-1')
secrets = boto3.client('secretsmanager')

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
    except Exception:
        return response(400, {'error': 'Invalid JSON in request body'})

    action = body.get('action')
    name = body.get('name', 'ec2-instance')  # Default name if not provided
    instance_id = body.get('instance_id')
    ami_id = os.getenv('ami_id')  # From Lambda environment variable
    instance_type = 't3.micro'

    if not action:
        return response(400, {'error': 'Action is required'})
    
    key_name = f"{name}-key-{str(uuid.uuid4())[:8]}"
    sg_name = f"{name}-ssh-sg"

    try:
        if action == 'create':
            # Step 1: Create Key Pair
            try:
                key_pair = ec2.create_key_pair(KeyName=key_name)
                private_key = key_pair['KeyMaterial']
                secrets.create_secret(Name=key_name, SecretString=private_key)
            except ClientError as e:
                if 'InvalidKeyPair.Duplicate' in str(e):
                    return response(400, {'error': f"Key '{key_name}' already exists"})
                else:
                    return response(500, {'error': f"Key creation error: {str(e)}"})

            # Step 2: Create Security Group
            try:
                sg_result = ec2.create_security_group(
                    GroupName=sg_name,
                    Description='Allow SSH only',
                    VpcId=get_default_vpc_id()
                )
                sg_id = sg_result['GroupId']
                ec2.authorize_security_group_ingress(
                    GroupId=sg_id,
                    IpPermissions=[{
                        'IpProtocol': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # Replace with user's IP for security
                    }]
                )
            except ClientError as e:
                if 'InvalidGroup.Duplicate' in str(e):
                    sg_id = get_security_group_id(sg_name)
                else:
                    return response(500, {'error': f"Security group error: {str(e)}"})

            # Step 3: Launch EC2 Instance
            try:
                ec2_result = ec2.run_instances(
                    ImageId=ami_id,
                    InstanceType=instance_type,
                    MinCount=1,
                    MaxCount=1,
                    KeyName=key_name,
                    SecurityGroupIds=[sg_id]
                )
                instance_id = ec2_result['Instances'][0]['InstanceId']
                waiter = ec2.get_waiter('instance_running')
                waiter.wait(InstanceIds=[instance_id])
                desc = ec2.describe_instances(InstanceIds=[instance_id])
                public_ip = desc['Reservations'][0]['Instances'][0]['PublicIpAddress']
            except Exception as e:
                return response(500, {'error': f"EC2 launch error: {str(e)}"})

            ssh_command = f"ssh -i <downloaded-key>.pem ec2-user@{public_ip}"
            return response(200, {
                'message': f'Created instance {instance_id}',
                'data': {
                    'instance_id': instance_id,
                    'public_ip': public_ip,
                    'ssh_command': ssh_command,
                    'ssh_key_secret': key_name
                }
            })

        elif action == 'start':
            if not instance_id:
                return response(400, {'error': 'Instance ID is required for start'})
            ec2.start_instances(InstanceIds=[instance_id])
            return response(200, {'message': f'Instance {instance_id} started'})

        elif action == 'stop':
            if not instance_id:
                return response(400, {'error': 'Instance ID is required for stop'})
            ec2.stop_instances(InstanceIds=[instance_id])
            return response(200, {'message': f'Instance {instance_id} stopped'})

        elif action == 'terminate':
            if not instance_id:
                return response(400, {'error': 'Instance ID is required for terminate'})
            desc = ec2.describe_instances(InstanceIds=[instance_id])
            instance = desc['Reservations'][0]['Instances'][0]
            sg_id = instance['SecurityGroups'][0]['GroupId']

            ec2.terminate_instances(InstanceIds=[instance_id])
            while True:
                check_result = ec2.describe_instances(InstanceIds=[instance_id])
                state = check_result['Reservations'][0]['Instances'][0]['State']['Name']
                if state == 'terminated':
                    break
                time.sleep(5)

            ec2.delete_security_group(GroupId=sg_id)
            secrets.delete_secret(SecretId=key_name, ForceDeleteWithoutRecovery=True)
            ec2.delete_key_pair(KeyName=key_name)

            return response(200, {'message': f'Instance {instance_id} terminated and resources cleaned up'})

        elif action == 'list':
            list_result = ec2.describe_instances()
            instances = []
            for reservation in list_result['Reservations']:
                for instance in reservation['Instances']:
                    instances.append({
                        'instance_id': instance['InstanceId'],
                        'state': instance['State']['Name'],
                        'public_ip': instance.get('PublicIpAddress', 'None'),
                        'instance_type': instance['InstanceType']
                    })
            return response(200, {'message': f'Found {len(instances)} instances', 'data': instances})

        else:
            return response(400, {'error': 'Invalid action'})

    except Exception as e:
        return response(500, {'error': f'Error: {str(e)}'})

def get_default_vpc_id():
    vpcs = ec2.describe_vpcs(Filters=[{'Name': 'isDefault', 'Values': ['true']}])
    return vpcs['Vpcs'][0]['VpcId']

def get_security_group_id(group_name):
    sgs = ec2.describe_security_groups(Filters=[{'Name': 'group-name', 'Values': [group_name]}])
    return sgs['SecurityGroups'][0]['GroupId']

def response(status, message):
    return {
        'statusCode': status,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        },
        'body': json.dumps(message)
    }
