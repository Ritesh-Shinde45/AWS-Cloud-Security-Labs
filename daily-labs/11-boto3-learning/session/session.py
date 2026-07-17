import boto3

# default session, uses default credential chain
s3 = boto3.client('s3')

# explicit session
session = boto3.Session(
    aws_access_key_id='...',
    aws_secret_access_key='...',
    aws_session_token='...',   # optional, only for temp creds
    region_name='ap-south-1',
    profile_name='my-profile'  # cannot mix with explicit keys
)
s3 = session.client('s3')
ec2 = session.resource('ec2')