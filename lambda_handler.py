import json
import boto3
from botocore.exceptions import ClientError

ec2 = boto3.client('ec2', region_name='us-east-1')

def lambda_handler(event, context):
    # Parse event for API Gateway v2.0 (wrapped 'body' string) or direct console/CLI tests
    try:
        if 'body' in event and isinstance(event['body'], str):
            # API call: Unwrap the body string (e.g., from curl/app.py)
            body = json.loads(event['body'])
        else:
            # Direct test: Use event as-is (e.g., Lambda console raw JSON)
            body = event

        action = body.get('action')
        instance_id = body.get('instance_id')
    except json.JSONDecodeError:
        return response(400, {'error': 'Invalid JSON in request body. Use {"action": "create"} or similar.'})
    except Exception as e:
        return response(500, {'error': f'Failed to parse request: {str(e)}'})

    try:
        if action == 'start':
            if not instance_id:
                return response(400, {'error': 'Missing "instance_id" for start'})

            # Check current state
            desc = ec2.describe_instances(InstanceIds=[instance_id])
            state = desc['Reservations'][0]['Instances'][0]['State']['Name']

            if state == 'stopped':
                ec2.start_instances(InstanceIds=[instance_id])
                # Wait for running (like in create)
                waiter = ec2.get_waiter('instance_running')
                waiter.wait(InstanceIds=[instance_id])
                return response(200, {'message': f'Started instance {instance_id}'})
            elif state == 'running':
                return response(200, {'message': f'Instance {instance_id} is already running'})
            elif state == 'stopping':
                return response(202, {'message': f"Instance {instance_id} is currently stopping. Please try starting it again shortly."})

            elif state in ['shutting-down', 'terminated']:
                return response(400, {'error': f"Cannot start instance {instance_id} because it is in state: {state}"})
            else:
                return response(400, {'error': f"Cannot start instance in state: {state}"})

        elif action == 'stop':
            if not instance_id:
                return response(400, {'error': 'Missing "instance_id" for stop'})

            try:
                desc = ec2.describe_instances(InstanceIds=[instance_id])
                state = desc['Reservations'][0]['Instances'][0]['State']['Name']

                if state == 'running':
                    ec2.stop_instances(InstanceIds=[instance_id])
                    # Wait for stopped
                    waiter = ec2.get_waiter('instance_stopped')
                    waiter.wait(InstanceIds=[instance_id])
                    return response(200, {'message': f'Stopped instance {instance_id}'})
                elif state == 'stopped':
                    return response(200, {'message': f'Instance {instance_id} is already stopped'})
                elif state == 'terminated':
                    return response(400, {'error': f'Cannot stop instance {instance_id} because it is terminated'})
                else:
                    return response(400, {'error': f'Cannot stop instance in state: {state}'})
            except Exception as e:
                return response(500, {'error': f'Error: {str(e)}'})

        elif action == 'terminate':
            if not instance_id:
                return response(400, {'error': 'Missing "instance_id" for terminate'})

            try:
                desc = ec2.describe_instances(InstanceIds=[instance_id])
                state = desc['Reservations'][0]['Instances'][0]['State']['Name']

                if state == 'terminated':
                    return response(400, {'error': f'Instance {instance_id} is already terminated'})
                else:
                    ec2.terminate_instances(InstanceIds=[instance_id])
                    # Wait for terminated
                    waiter = ec2.get_waiter('instance_terminated')
                    waiter.wait(InstanceIds=[instance_id])
                    return response(200, {'message': f'Terminated instance {instance_id}'})
            except Exception as e:
                return response(500, {'error': f'Error: {str(e)}'})

        elif action == 'create':
            key_name = 'my_keypair'
            new_instance = ec2.run_instances(
                ImageId='ami-052064a798f08f0d3',  # Verify/update: Amazon Linux 2 in us-east-1
                InstanceType='t3.micro',
                MinCount=1,
                MaxCount=1,
                KeyName=key_name,
                SecurityGroupIds=['sg-0f66c9807f2d88f49']  # <-- REPLACE WITH YOUR SG ID (e.g., sg-0abc123def456)
            )
            instance = new_instance['Instances'][0]
            instance_id = instance['InstanceId']

            # Wait for instance to be running and get public IP
            waiter = ec2.get_waiter('instance_running')
            waiter.wait(InstanceIds=[instance_id])

            # Fetch instance details
            desc = ec2.describe_instances(InstanceIds=[instance_id])
            public_ip = desc['Reservations'][0]['Instances'][0].get('PublicIpAddress')
            ssh_command = f"ssh -i my_keypair.pem ec2-user@{public_ip}"  # Hardcoded key name
            ssh_info = {
                "instance_id": instance_id,
                "public_ip": public_ip,
                "username": "ec2-user",  
                "key_name": "my_keypair",
                "ssh_command": ssh_command
            }

            return response(200, {'message': f'Created instance {instance_id}', 'data': ssh_info})

        elif action == 'list':  # New: List all instances (optional; remove if not needed)
            describe_response = ec2.describe_instances()
            instances = []
            for reservation in describe_response['Reservations']:
                for instance in reservation['Instances']:
                    instances.append({
                        'instance_id': instance['InstanceId'],
                        'state': instance['State']['Name'],
                        'public_ip': instance.get('PublicIpAddress', 'None'),
                        'instance_type': instance['InstanceType']
                    })
            return response(200, {'message': f'Found {len(instances)} instances', 'data': instances})

        else:
            return response(400, {'error': 'Invalid action. Use start, stop, terminate, create, or list.'})

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if 'InvalidKeyPair.NotFound' in error_code:
            return response(400, {'error': 'Key pair "my_keypair" not found. Create it in EC2 Console > Key Pairs.'})
        elif 'InvalidGroup.NotFound' in error_code:
            return response(400, {'error': 'Security group ID invalid. Update in code and re-deploy.'})
        else:
            return response(500, {'error': f'AWS Error ({error_code}): {e.response["Error"]["Message"]}'})
    except Exception as e:
        return response(500, {'error': f'Error: {str(e)}'})

def response(status, message):
    return {
        'statusCode': status,
        'headers': {  # Added CORS for API Gateway + app.py/browser
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  # Allow all for demo (restrict in prod)
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        },
        'body': json.dumps(message)
    }