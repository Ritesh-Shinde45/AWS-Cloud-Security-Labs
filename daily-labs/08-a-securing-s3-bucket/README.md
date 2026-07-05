# Lab 08-A: Securing S3 Bucket with KMS Encryption

## 1. Overview

This lab covers Phase 8-A of the AWS Cloud Infrastructure project. In Lab 06 I studied how AWS KMS works conceptually. In this lab I actually put it into practice by creating a real KMS key and using it to encrypt an S3 bucket. Every new object uploaded to the bucket from this point will be encrypted automatically using that key.

## 2. Environment Used

* **Cloud Provider:** AWS
* **Region:** Asia Pacific (Mumbai) `ap-south-1`
* **Services:** AWS KMS and Amazon S3
* **KMS Key Alias:** demo-key
* **Bucket:** demo-s3-bucket-908875503206-ap-south-1-an

---

## 3. What I Did

There were two main parts to this lab. First I created a new KMS key. Then I went into the S3 bucket and changed its default encryption to use that key.

---

## 4. Steps

### 4.1 Opening Bucket Encryption Settings

Went into the S3 bucket, opened the **Properties** tab, scrolled down to **Default encryption** and clicked **Edit**. Changed the encryption type from SSE-S3 to **SSE-KMS**. At this point I had no KMS key created yet so the key dropdown was empty. This is where I decided to create a new key.

![S3 edit encryption - SSE-KMS selected](./01-s3-edit-encryption.png)

### 4.2 Creating a New KMS Key - Configure Key

Clicked the **Create a KMS key** button which opened the KMS console in a new tab. On the first step, selected **Symmetric** as the key type since this key will be used for both encrypting and decrypting data inside the same account. Set key usage to **Encrypt and decrypt** and left the key material origin as **KMS** so AWS generates and manages the key material internally.

![KMS configure key](./02-kms-configure-key.png)

### 4.3 Adding Labels

Gave the key an alias of `demo-key` and added a short description. Left tags empty since this was a learning exercise.

![KMS add labels](./03-kms-add-labels.png)

### 4.4 Setting Key Administrative Permissions

Selected the IAM user `suraj` as the key administrator. A key administrator can manage the key itself, things like enabling, disabling, rotating and deleting it. This does not automatically mean they can use the key to encrypt or decrypt data since that is a separate permission set.

![KMS key admin permissions](./04-kms-key-admin-permissions.png)

### 4.5 Setting Key Usage Permissions

Also selected `suraj` as the key user. This allows the user to actually use the key in cryptographic operations like encrypt, decrypt and generate data keys. Both admin and usage permissions were given to the same user here for simplicity in this lab.

![KMS key usage permissions](./05-kms-key-usage-permissions.png)

### 4.6 Reviewing the Key Policy

Before finishing, reviewed the auto-generated key policy JSON. The policy has four statements:

* **Enable IAM User Permissions** - gives the root account full control over the key as a fallback
* **Allow access for Key Administrators** - gives `suraj` permissions to manage the key lifecycle
* **Allow use of the key** - gives `suraj` permission to use the key for encryption and decryption
* **Allow attachment of persistent resources** - lets `suraj` create grants so AWS services like S3 can use the key on their own

```json
{
  "Id": "key-consolepolicy-3",
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Enable IAM User Permissions",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::908875503206:root"
      },
      "Action": "kms:*",
      "Resource": "*"
    },
    {
      "Sid": "Allow access for Key Administrators",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::908875503206:user/suraj"
      },
      "Action": [
        "kms:Create*",
        "kms:Describe*",
        "kms:Enable*",
        "kms:List*",
        "kms:Put*",
        "kms:Update*",
        "kms:Revoke*",
        "kms:Disable*",
        "kms:Get*",
        "kms:Delete*",
        "kms:TagResource",
        "kms:UntagResource",
        "kms:ScheduleKeyDeletion",
        "kms:CancelKeyDeletion",
        "kms:RotateKeyOnDemand"
      ],
      "Resource": "*"
    },
    {
      "Sid": "Allow use of the key",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::908875503206:user/suraj"
      },
      "Action": [
        "kms:Encrypt",
        "kms:Decrypt",
        "kms:ReEncrypt*",
        "kms:GenerateDataKey*",
        "kms:DescribeKey"
      ],
      "Resource": "*"
    },
    {
      "Sid": "Allow attachment of persistent resources",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::908875503206:user/suraj"
      },
      "Action": [
        "kms:CreateGrant",
        "kms:ListGrants",
        "kms:RevokeGrant"
      ],
      "Resource": "*",
      "Condition": {
        "Bool": {
          "kms:GrantIsForAWSResource": "true"
        }
      }
    }
  ]
}
```

![KMS edit key policy](./06-kms-edit-key-policy.png)

### 4.7 Applying the Key to the Bucket

Came back to the S3 Edit default encryption page. The `demo-key` now showed up in the available KMS keys dropdown. Selected it and saved the changes. Also noticed the console automatically checked **Block SSE-C** at the bottom which is a good security practice since SSE-C lets users bring their own keys from outside AWS which is harder to audit and control.

From this point every new object uploaded to the bucket will be encrypted using `demo-key` automatically without needing to do anything extra during upload.

![S3 encryption demo-key applied](./07-key-applied.png)

---

## 5. Key Configuration Summary

| Setting | Value |
|---|---|
| Key type | Symmetric |
| Key spec | SYMMETRIC_DEFAULT |
| Key usage | Encrypt and decrypt |
| Origin | AWS KMS |
| Regionality | Single-Region key |
| Alias | demo-key |
| Key administrator | suraj |
| Key user | suraj |
| Bucket encryption | SSE-KMS |
| SSE-C blocked | Yes |

---

## 6. What I Learned

The difference between SSE-S3 and SSE-KMS became very clear here. With SSE-S3, S3 manages the encryption key itself and you have no control over who can use that key or when. With SSE-KMS, the key lives in KMS and access to it is controlled through a key policy just like any other IAM policy. This means you can restrict which users or services can decrypt objects in the bucket simply by controlling who has access to the KMS key, without touching the bucket policy at all.

The fact that blocking SSE-C gets enforced automatically when you switch to SSE-KMS is also an important detail. It means no one can bypass your KMS-based encryption by uploading objects with their own external key.