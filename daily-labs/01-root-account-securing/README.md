# Lab 01: AWS Root Account Hardening & Security Baseline

## Objective
The goal of this lab is to establish a secure foundation for a new AWS account by eliminating the daily use of the root user, enforcing strict authentication controls, and initializing an administrative identity based on the principle of least privilege. 

According to the AWS Well-Architected Framework (Security Pillar), using the root account for daily operational tasks is a severe vulnerability. This lab mitigates that risk entirely.

---

## Security Actions Taken 

### 1. Enforced Multi-Factor Authentication (MFA) on Root
To shield the primary billing and account ownership credentials from credential stuffing and brute-force attacks, I implemented hardware-isolated virtual token authentication.
* **Service Used:** AWS Identity and Access Management (IAM)
* **Implementation:** Configured a Virtual MFA device linked to a mobile authenticator app.
* **Verification:** Root login now strictly requires the primary password plus a time-based one-time password (TOTP).

### 2. Audited and Eliminated Root Access Keys
Access keys grant unrestricted programmatic API and CLI access to the entire AWS account. Leaving root access keys active introduces catastrophic risk if accidentally exposed (e.g., leaked via code repositories).
* **Action:** Audited the root credentials dashboard. 
* **Resolution:** Permanently **Deleted** all active root access keys. Programmatic access will now be handled exclusively by heavily restricted IAM users.

### 3. Created a Dedicated IAM Administrator User Group & User
To completely abstract daily operations away from the root account, I built a professional, group-based identity hierarchy.
* **User Created:** `suraj`
* **Group Created:** `admin`
* **Permissions Strategy:** Attached the AWS-managed policy `AdministratorAccess` to the `admin` group, then added the `suraj` user to that group. 
* *Security Note: Assigning permissions via groups rather than inline directly to a user is an enterprise IAM best practice.*

### 4. Enforced MFA on the New Administrator User
* **Action:** Logged out of the root user completely.
* **Action:** Logged into the unique AWS account console alias as `suraj`.
* **Action:** Immediately configured an independent Virtual MFA device for this new administrative identity.

---

## Verification & Key Takeaways

* **IAM Credential Report:** The AWS IAM security status dashboard now displays full green checkmarks for **"MFA added for root user"** and **"Eliminated root access keys"**.
* **Attack Surface Reduction:** By removing root access keys, the attack surface for programmatic API exploits on the root account is officially reduced to **zero**.
* **Operational Shift:** Moving forward, the root account credentials will be securely locked away and used *only* for account closure, changing billing plans, or modifying root settings.

---

