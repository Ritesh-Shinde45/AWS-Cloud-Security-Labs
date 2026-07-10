import boto3

s3_client = boto3.client('s3', region_name='ap-south-1')

response = s3_client.list_buckets()

print("All buckets in this account:")
for bucket in response['Buckets']:
    print(f"  {bucket['Name']} - Created: {bucket['CreationDate']}")