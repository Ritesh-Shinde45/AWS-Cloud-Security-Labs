# Boto3 Sessions & Credential Chains

## What is a Session

A boto3.Session holds config state: credentials, region, profile. If you never
create one yourself, boto3 quietly creates a default session the first time
you make a client or resource.

```python
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
```

## Why This Matters for Security Work

- Keep credentials isolated per thread. Session objects are not thread safe,
  so create a new one per thread if scripting concurrent scans.
- Assume different IAM roles for different accounts, useful for cross account
  audits.
- Prevents one account's creds from leaking into calls meant for another
  account.



## Credential Resolution Chain (order matters)

boto3 checks these in order, first match wins:

1. Explicit params passed directly to Session() or client()
2. Environment variables
   - AWS_ACCESS_KEY_ID
   - AWS_SECRET_ACCESS_KEY
   - AWS_SESSION_TOKEN
3. Shared credentials file, ~/.aws/credentials
4. AWS config file, ~/.aws/config (needs AWS_SDK_LOAD_CONFIG=1 in older setups)
5. Assume role config in ~/.aws/config using role_arn + source_profile
6. Legacy boto2 config, /etc/boto.cfg or ~/.boto (rarely seen now)
7. Instance metadata / container credentials
   - ECS task role via AWS_CONTAINER_CREDENTIALS_RELATIVE_URI
   - EKS IRSA via AWS_WEB_IDENTITY_TOKEN_FILE + AWS_ROLE_ARN
   - EC2 instance profile via IMDSv2



## Things to remember

- Never hardcode access_key_id / secret_access_key in scripts that go into
  source control.
- Prefer instance profiles, IRSA, or lambda execution roles over long lived
  IAM user keys.
- Set DurationSeconds low on assume_role calls to limit blast radius.
- Use ExternalId on cross account assume role calls, protects against the
  confused deputy problem.
- If doing IR work, treat any static creds found via get_frozen_credentials()
  as something to rotate immediately.