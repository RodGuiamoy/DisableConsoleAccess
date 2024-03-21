import boto3
from botocore.exceptions import ClientError
import sys

# Initialize a Boto3 IAM client
iam = boto3.client('iam')

# List of IAM usernames whose console access you want to disable
user_names = sys.argv[1].split(',')

for user_name in user_names:
    try:
        # Remove the IAM user's login profile
        iam.delete_login_profile(UserName=user_name)
        print(f"Console access removed for user: {user_name}")
    except ClientError as error:
        if error.response['Error']['Code'] == 'NoSuchEntity':
            print(f"The user {user_name} does not have a console login profile.")
        else:
            print(f"Failed to remove console access for user: {user_name}. Error: {error}")
