import boto3
from botocore.exceptions import ClientError

s3 = boto3.client('s3')

try:
    s3.head_bucket(Bucket='my-bucket')
    print("Bucket exists")
except ClientError as e:
    error_code = e.response['Error']['Code']
    if error_code == '404':
        print("Bucket does not exist")
    else:
        print(f"Unexpected error: {error_code}")