import boto3
from botocore.exceptions import ClientError
import argparse

# Initialize a Boto3 IAM client
iam = boto3.client('iam')

def parseArguments():
    # Create argument parser
    parser = argparse.ArgumentParser()

    # Positional mandatory arguments
    parser.add_argument('--excluded_emails', dest='excluded_emails', nargs='?', default='', help='Excluded emails')
    parser.add_argument('--excluded_users', dest='excluded_users', nargs='?', default='', help='Excluded usernames')
    
    # Parse arguments
    args = parser.parse_args()

    return args

def get_users_with_console_access(excluded_emails, excluded_usernames):
    # Initialize to empty lists regardless of input
    excluded_emails = excluded_emails.lower().split(',') if excluded_emails else []
    excluded_usernames = excluded_usernames.lower().split(',') if excluded_usernames else []
    users_with_access = []  # This list will hold the usernames of users with console access
    
    # Assuming iam is a configured AWS IAM client
    paginator = iam.get_paginator('list_users')
    for response in paginator.paginate():
        for user in response['Users']:
            user_name = user['UserName']
            
            tags_response = iam.list_user_tags(UserName=user_name)
            user_tags = {tag['Key']: tag['Value'] for tag in tags_response['Tags']} 
            user_email = user_tags.get('email', None)  # Default to None if 'email' tag doesn't exist
            employee_ID = user_tags.get('employeeID', None) # Default to None if 'employeeID' tag doesn't exist
            
            if employee_ID == 'service-account':
                continue
                
            try:
                # Attempt to get the login profile for the user, indicating console access
                iam.get_login_profile(UserName=user_name)
                
                # Check if the user's email or username is in the excluded lists
                if (not user_email or user_email.lower() not in excluded_emails) and user_name.lower() not in excluded_usernames:
                    users_with_access.append(user_name)
            except ClientError as error:
                # Log the exception and move on
                pass

    return ','.join(users_with_access)

# Parse the arguments
args = parseArguments()

users_with_console_access_str = get_users_with_console_access(args.excluded_emails, args.excluded_users)
print(users_with_console_access_str)