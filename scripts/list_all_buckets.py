import boto3
from botocore.exceptions import ClientError

def list_all_buckets():
    s3_client = boto3.client('s3')
    
    try:
        response = s3_client.list_buckets()
        
        print("Your Amazon S3 Buckets:")
        print("-----------------------")
        
        for bucket in response['Buckets']:
            print(f"Name: {bucket['Name']}")
            print(f"Created: {bucket['CreationDate']}")
            print("-" * 23)
            
    except ClientError as e:
        print(f"AWS Error: {e.response['Error']['Message']}")

list_all_buckets()