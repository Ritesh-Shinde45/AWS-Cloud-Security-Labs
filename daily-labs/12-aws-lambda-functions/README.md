# Lab 12: AWS Lambda Functions

## 1. Overview

This was a concept study session on AWS Lambda. Before this, all the compute I worked with was EC2, where you manage a full virtual machine. Lambda is a completely different model where you just write a function, upload it and AWS runs it for you without any server to manage.

---

## 2. What Lambda Actually Is

Lambda is a serverless compute service. The word serverless does not mean there are no servers. It means you do not see or manage any servers. AWS handles provisioning, scaling, patching and availability entirely on its own. You only write the function code and define what should trigger it.

You are billed only for the time your function actually runs, measured in milliseconds. If your function runs for 200ms, you pay for 200ms. When the function is not running you pay nothing. This is very different from EC2 where the instance costs money whether it is doing anything or not.

---

## 3. Concepts Learned

### 3.1 How Lambda Works

When a trigger fires, AWS spins up an execution environment, loads your function code into it, runs the handler function and then either keeps the environment warm for a short time (in case another trigger comes in soon) or shuts it down.

**Execution environment lifecycle:**

1. AWS creates a new execution environment (this takes a small amount of time called a cold start)
2. Your deployment package (code and dependencies) is downloaded and loaded
3. Any initialization code outside the handler runs once
4. The handler function runs for this specific event
5. The environment stays alive for a while waiting for the next invocation
6. If no invocation comes, AWS shuts it down

**Cold start vs warm start:**

* A **cold start** happens when AWS has to create a fresh environment. This adds a few hundred milliseconds of latency on top of your actual function runtime.
* A **warm start** happens when a previous execution environment is still alive and gets reused. This is much faster since the environment is already set up.

Cold starts matter more for latency-sensitive applications. For background jobs and security automation they usually do not matter.

---

### 3.2 Key Lambda Concepts

**Handler:**
The entry point function that Lambda calls when your function is invoked. In Python it looks like this:

```python
def lambda_handler(event, context):
    print("Function triggered")
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda'
    }
```

* `event` is a dictionary containing the data passed to the function by the trigger. The structure of this dictionary depends on which service triggered the function.
* `context` is an object with runtime information like the function name, memory limit, remaining execution time and request ID.

**Deployment package:**
Your function code and any dependencies packaged together. For simple Python functions with no external libraries, you can write code directly in the Lambda console. For anything that uses third-party packages like Boto3 (beyond the version pre-installed by AWS), you zip the code and dependencies together and upload the zip.

**Layers:**
A Lambda layer is a zip file containing shared code or dependencies that multiple functions can use. Instead of packaging the same library into every function separately, you put it in a layer and attach the layer to each function. This keeps deployment packages small and makes dependency updates easier.

**Memory and timeout:**

* You configure how much memory a function gets, anywhere from 128 MB to 10 GB.
* CPU is allocated proportionally to memory. More memory means more CPU.
* Timeout sets the maximum time a function can run before AWS kills it. Maximum is 15 minutes. For most use cases functions should complete in seconds.

**Concurrency:**
Lambda can run many instances of the same function at the same time. If 100 events come in at once, Lambda spins up 100 execution environments and runs them in parallel. This is automatic and requires no configuration. There is an account-level concurrency limit (default 1000 across all functions) that can be raised if needed.

---

### 3.3 Triggers

A trigger is what causes a Lambda function to run. Lambda integrates with almost every AWS service as a trigger source.

| Trigger | What Happens |
|---|---|
| **API Gateway** | An HTTP request hits an endpoint and Lambda handles it |
| **S3** | A file is uploaded, deleted or modified in a bucket |
| **CloudWatch Events / EventBridge** | A scheduled cron job or an AWS service event fires |
| **SNS** | A message is published to a topic |
| **SQS** | A message appears in a queue |
| **DynamoDB Streams** | A record is inserted, updated or deleted in a table |
| **CloudTrail** | An API call is made in the account (via EventBridge) |

For security automation the most useful triggers are S3 events, CloudTrail via EventBridge and scheduled CloudWatch Events for periodic checks.

---

### 3.4 IAM Role for Lambda

Every Lambda function needs an IAM execution role. This role defines what AWS services and resources the function is allowed to interact with. When the function runs, it assumes this role and gets temporary credentials automatically, the same way an EC2 instance uses an instance profile.

The minimum role needed for any Lambda function is the `AWSLambdaBasicExecutionRole` managed policy, which only allows the function to write logs to CloudWatch. Any additional permissions, like reading from S3 or calling KMS, have to be added explicitly following the principle of least privilege.

**Example:** A Lambda function that scans S3 buckets for public access settings needs:
* `s3:ListAllMyBuckets`
* `s3:GetBucketPublicAccessBlock`
* `logs:CreateLogGroup`
* `logs:CreateLogStream`
* `logs:PutLogEvents`

Nothing else. Not `s3:PutObject`, not `s3:DeleteObject`, not anything it does not actually need.

---

### 3.5 Environment Variables

Lambda supports environment variables that your code can read at runtime. This is how you pass configuration like bucket names, region settings or feature flags without hardcoding them in the function code.

```python
import os

BUCKET_NAME = os.environ['BUCKET_NAME']
REGION = os.environ.get('REGION', 'ap-south-1')
```

Sensitive values like API keys should be stored in AWS Secrets Manager or SSM Parameter Store and fetched by the function at runtime, not put directly into environment variables where they show up in plain text in the Lambda console.

---

### 3.6 Lambda Pricing

Lambda pricing has two components:

* **Number of requests:** First 1 million requests per month are free. After that it is a very small amount per million requests.
* **Duration:** Charged based on how long the function runs multiplied by the memory allocated. The free tier includes 400,000 GB-seconds per month.

For the kind of security automation scripts this portfolio is building, Lambda costs are effectively zero because the functions run infrequently and finish in a few seconds.

---

### 3.7 Lambda vs EC2 - When to Use Which

| | Lambda | EC2 |
|---|---|---|
| **Best for** | Short tasks triggered by events | Long-running processes or always-on services |
| **Max runtime** | 15 minutes | Unlimited |
| **Scaling** | Automatic and instant | Manual or Auto Scaling setup required |
| **Cost model** | Pay per execution | Pay per hour the instance is running |
| **Server management** | None | You manage OS, patches and updates |
| **Use in security** | Automated checks, alerts, remediation on events | Security tools that run continuously like log collectors |

---

### 3.8 Lambda in a Security Context

Lambda is extremely useful for security automation because it lets you react to events in real time without running a dedicated server.

**Real world security use cases:**

* **Automatic remediation:** A CloudTrail event fires when someone creates a public S3 bucket. An EventBridge rule catches it and triggers a Lambda function that immediately sets Block Public Access back on.
* **Scheduled security scans:** A CloudWatch scheduled event runs a Lambda function every night that checks all IAM users for missing MFA and sends a report via SNS.
* **Alert on suspicious API calls:** CloudTrail detects a root account login. EventBridge triggers Lambda which sends an immediate alert to a Slack channel or email via SNS.
* **Quarantine a compromised instance:** A GuardDuty finding triggers Lambda which automatically isolates the EC2 instance by moving it to a restricted security group with no outbound access.

---

## 4. Key Takeaways

* Lambda runs your code in response to a trigger without any server to manage or pay for when idle
* Cold starts add a small latency penalty the first time a function runs after a period of inactivity
* Every function needs an IAM execution role and that role should only have the permissions the function actually needs
* The event dictionary tells the function what triggered it and carries all the relevant data from the trigger source
* For security engineering Lambda is the right tool for event-driven automation like automatic remediation, scheduled scans and real-time alerts
* Lambda is not a replacement for EC2 when something needs to run for more than 15 minutes or needs to be always listening on a port