import boto3

ec2 = boto3.client("ec2")

response = ec2.describe_instances()

print("Running EC2 Instance IDs:")

for reservation in response["Reservations"]:
    for instance in reservation["Instances"]:
        if instance["State"]["Name"] == "running":
            print(instance["InstanceId"])