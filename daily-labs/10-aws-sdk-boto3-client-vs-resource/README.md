# Lab 10: AWS SDK and Boto3 Client vs Resource

## 1. Overview

This lab covers Phase 10 of the AWS Cloud Infrastructure project. This was a concept study session on the AWS SDK for Python, which is called Boto3. Up to this point I have been using the AWS console to interact with services. Boto3 is how you do the same things through code, which is the foundation for writing automation scripts, security scanners and any kind of infrastructure tooling in Python.

---

## 2. Concepts Learned

### 2.1 What the AWS SDK Is

An SDK (Software Development Kit) is a library that lets your code talk to AWS services directly without going through the console. AWS provides SDKs for several languages including Python, JavaScript, Java, Go and others. The Python one is called Boto3.

When you write a script using Boto3, it sends HTTP requests to the AWS API on your behalf, handles authentication automatically using your configured credentials and returns the response as a Python dictionary or object. Without the SDK you would have to build those HTTP requests manually and handle signing and authentication yourself, which is complex.

**Where credentials come from (in order of priority Boto3 checks):**
* Environment variables (`AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`)
* AWS credentials file (`~/.aws/credentials`)
* IAM role attached to an EC2 instance or Lambda function (recommended for production)

The IAM role approach is the cleanest because there are no keys to store or rotate manually. The SDK picks up the temporary credentials from the instance metadata automatically.

---

### 2.2 Setting Up Boto3

Install with pip:

```bash
pip install boto3
```

Configure credentials using the AWS CLI (only needed for local development, not on EC2 with an IAM role):

```bash
aws configure
```

This stores your access key, secret key and default region in `~/.aws/credentials` and `~/.aws/config`.

---

### 2.3 Client vs Resource - The Core Difference

Boto3 gives you two different ways to interact with AWS services: **client** and **resource**. This is the most important thing to understand when starting with Boto3 because both exist and choosing the wrong one can make code harder to write than it needs to be.

| | Client | Resource |
|---|---|---|
| **Level** | Low level | High level |
| **Maps to** | AWS API directly | Python objects |
| **Response format** | Raw JSON dictionary | Python object with attributes and methods |
| **Coverage** | Every AWS service and every API action | Only some services (S3, EC2, IAM, DynamoDB, SQS, SNS) |
| **Control** | Full, explicit | Simpler but less control |
| **When to use** | When you need precise API control or the service has no resource interface | When you want cleaner code for supported services |

---

### 2.4 Client

A client is a direct, low-level interface to the AWS API. Every method on a client maps exactly to one AWS API call. The response always comes back as a Python dictionary that mirrors the raw JSON from the API.

**Creating a client:**

```python
import boto3

s3_client = boto3.client('s3', region_name='ap-south-1')
```

**Listing buckets with a client:**

```python
response = s3_client.list_buckets()
# response is a raw dictionary
for bucket in response['Buckets']:
    print(bucket['Name'])
```

**Uploading a file with a client:**

```python
s3_client.upload_file(
    Filename='local-file.txt',
    Bucket='my-bucket',
    Key='remote-file.txt'
)
```

The client gives you full access to every parameter the AWS API supports. If you need to set specific headers, use pagination tokens or call an API that is not supported by the resource interface, the client is the right choice.

**Pagination:** Some API calls return results in pages if there are too many items. With a client you handle this manually using paginators:

```python
paginator = s3_client.get_paginator('list_objects_v2')
pages = paginator.paginate(Bucket='my-bucket')

for page in pages:
    for obj in page.get('Contents', []):
        print(obj['Key'])
```

---

### 2.5 Resource

A resource is a high-level, object-oriented interface. Instead of getting raw dictionaries back, you get Python objects that have attributes and methods attached to them. This makes code read more naturally and hides some of the lower-level details.

**Creating a resource:**

```python
import boto3

s3_resource = boto3.resource('s3', region_name='ap-south-1')
```

**Listing buckets with a resource:**

```python
for bucket in s3_resource.buckets.all():
    print(bucket.name)
```

Compare this to the client version above. The resource version reads much more like plain Python. `bucket.name` instead of `bucket['Name']`, and no need to dig into a response dictionary.

**Uploading a file with a resource:**

```python
bucket = s3_resource.Bucket('my-bucket')
bucket.upload_file('local-file.txt', 'remote-file.txt')
```

**Accessing a specific object:**

```python
obj = s3_resource.Object('my-bucket', 'remote-file.txt')
print(obj.content_type)
print(obj.last_modified)
```

The resource automatically handles things like lazy loading, meaning it does not fetch all the data about an object until you actually access an attribute. This can be more efficient in some cases.

---

### 2.6 When to Use Which

* **Use client when:**
  * The service does not have a resource interface (CloudTrail, GuardDuty, KMS, CloudWatch and most security services are client-only)
  * You need access to a specific API parameter that the resource abstraction does not expose
  * You are writing something that needs precise control over the exact API call being made
  * You are handling paginated responses and want explicit control over pagination

* **Use resource when:**
  * You are working with S3, EC2, IAM, DynamoDB, SQS or SNS
  * You want cleaner and more readable code
  * You are doing straightforward CRUD operations on objects or buckets

In practice, most real scripts end up using both. You might use a resource to iterate over S3 objects cleanly and then switch to a client to call a specific API action that is not available on the resource interface.

---

### 2.7 Common Boto3 Patterns

**Error handling:**

```python
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
```

**Using a session (useful when working with multiple accounts or regions):**

```python
session = boto3.Session(
    region_name='ap-south-1',
    profile_name='my-profile'
)
s3 = session.client('s3')
```

---

### 2.8 How Boto3 Fits Into Security Work

For cloud security engineering, Boto3 is how you write tools that check your own infrastructure. Instead of clicking through the console to verify security settings, you write a script that:

* Lists all S3 buckets and checks if any have public access enabled
* Scans IAM users and flags anyone without MFA
* Pulls CloudTrail events and looks for suspicious API calls
* Checks all EC2 security groups for port 22 open to `0.0.0.0/0`

These are the kinds of scripts that make up a real security scanner, which is what the upcoming project labs will build on top of these Boto3 foundations.

---

## 3. Key Takeaways

* Boto3 is the Python SDK for AWS and handles authentication, request signing and response parsing automatically
* Client is low level and returns raw dictionaries, resource is high level and returns Python objects with attributes
* Client covers every AWS service, resource only covers a handful of the common ones
* Most real scripts use both depending on what they need to do
* For cloud security work, Boto3 is the foundation for writing automated checks and scanners instead of doing everything manually through the console