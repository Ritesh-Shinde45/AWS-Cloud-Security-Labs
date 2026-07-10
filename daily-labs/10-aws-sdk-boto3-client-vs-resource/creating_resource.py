import boto3


s3_resource = boto3.resource('s3', region_name='ap-south-1')


print("All buckets in this account:")
for bucket in s3_resource.buckets.all():
    print(f"  {bucket.name}")