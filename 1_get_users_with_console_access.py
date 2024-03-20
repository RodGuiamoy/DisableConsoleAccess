import boto3
from botocore.exceptions import ClientError
import sys

# Initialize a Boto3 IAM client
iam = boto3.client('iam')

def get_users_with_console_access(excluded_emails):
    excluded_emails = excluded_emails.split(',')  # Split the string into a list of email addresses
    users_with_access = []  # This list will hold the usernames of users with console access

    # Paginator to handle the case where there are more users than can be returned in a single AWS API call
    paginator = iam.get_paginator('list_users')
    for response in paginator.paginate():
        for user in response['Users']:
            user_name = user['UserName']
            try:
                # Attempt to get the login profile for the user, indicating console access
                iam.get_login_profile(UserName=user_name)
                
                # Login profile exists, now check if the user has an 'email' tag and if it's in the excluded list
                tags_response = iam.list_user_tags(UserName=user_name)
                user_tags = {tag['Key']: tag['Value'] for tag in tags_response['Tags']}
                user_email = user_tags.get('email', None)  # Default to None if 'email' tag doesn't exist
                
                if not user_email or (user_email and user_email not in excluded_emails):
                    # Include user if no email tag exists or if their email is not in the excluded list
                    users_with_access.append(user_name)
            except ClientError as error:
                # Ignore errors related to missing login profile, as we only want users with console access
                if error.response['Error']['Code'] != 'NoSuchEntity':
                    print(f"Error processing user {user_name}: {error}")

    return ','.join(users_with_access)

try:
    # Attempt to retrieve excluded users from the command line argument
    excluded_emails = sys.argv[1]
except IndexError:
    # No argument provided, so no excluded users
    excluded_emails = ""

users_with_console_access_str = get_users_with_console_access(excluded_emails)
print(users_with_console_access_str)
