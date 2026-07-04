# Lab 07: S3 Permission Policies and IAM vs Bucket Policies

## 1. Overview

This lab covers Phase 7 of the AWS Cloud Infrastructure project. This was a concept study session focused on how access control works in S3. In the previous lab I learned how KMS protects encryption keys. This session goes one level up and focuses on who is allowed to access S3 resources in the first place and how that permission is written and applied.

---

## 2. Concepts Learned

### 2.1 Permission Policies and JSON

A permission policy is a document written in JSON that tells AWS what actions are allowed or denied on which resources and under what conditions.

**Basic structure of a policy:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```

Each statement inside a policy has four main parts:

* **Effect:** either `Allow` or `Deny`
* **Action:** what operation is being allowed or denied, like `s3:GetObject` or `s3:PutObject`
* **Resource:** which bucket or object the statement applies to, written as an ARN
* **Condition (optional):** extra rules that must be true for the effect to apply, like checking a tag value or an IP address

### 2.2 IAM Policies vs S3 Bucket Policies

Both IAM policies and S3 bucket policies control access to S3 but they work from different directions. Understanding the difference matters a lot when figuring out why access is being allowed or blocked.

| | IAM Policy | S3 Bucket Policy |
|---|---|---|
| **Attached to** | A user, group or role | The S3 bucket itself |
| **Controls** | What the identity can do across AWS services | Who can access this specific bucket and what they can do |
| **Written in** | JSON | JSON |
| **Use case** | Give a developer access to multiple AWS services including S3 | Allow a specific external account or service to access just this bucket |
| **Scope** | Works across your whole AWS account | Works only on the bucket it is attached to |

**When both exist at the same time:**

If an IAM policy and a bucket policy both apply to the same request, AWS evaluates both together. The request is allowed only if neither policy has an explicit Deny and at least one of them has an explicit Allow. An explicit Deny always wins over any Allow.

### 2.3 When to Use Which

* Use **IAM policies** when you are managing your own users and roles inside your AWS account and want to control what they can do across multiple services.
* Use **S3 bucket policies** when you need to give access to someone outside your account, a specific AWS service like CloudFront, or when you want to enforce rules at the bucket level regardless of what IAM says.
* Use **both together** when you need fine grained control, for example allowing a user broad S3 access through IAM but restricting them to a specific bucket prefix through the bucket policy.

### 2.4 S3 Object Tagging

Object tagging lets you attach key-value labels to any object inside a bucket. For example you could tag an object with `env: production` or `department: finance`. Tags can also be used inside permission policies as a condition, for example only letting a finance team access objects tagged with `department: finance`. They are also useful for cost tracking since AWS Billing can break down costs per tag.

---

## 3. Key Takeaways

* Every permission policy is JSON with the same structure: Effect, Action, Resource and optional Condition
* IAM policies follow the identity, bucket policies follow the bucket
* An explicit Deny anywhere always overrides an Allow no matter which policy it comes from
* Knowing which policy type to reach for and why is one of the most practical IAM skills in real cloud work
* Object tags can extend policies with extra conditions and help track costs at the object level