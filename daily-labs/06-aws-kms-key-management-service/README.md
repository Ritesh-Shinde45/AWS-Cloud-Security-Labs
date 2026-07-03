# Lab 06: AWS Key Management Service (KMS)

## 1. Overview

This lab covers Phase 6 of the AWS Cloud Infrastructure project. This was a concept study session focused on AWS KMS. Before this I had a rough idea that encryption exists but never understood where the encryption keys themselves are stored or what happens if those keys get stolen. This session cleared that up completely.

---

## 2. The Core Problem KMS Solves

When you store sensitive data like credit card numbers or login tokens in a database, you have to encrypt it first. But that creates one big question: where do you keep the encryption key?

* **Store it in the same database?** If someone breaks into the database they get the encrypted data and the key to unlock it at the same time.
* **Store it in a `.env` file or hardcode it?** If someone gets access to the server or the code, the key is exposed.

KMS solves this by acting as a separate, dedicated and highly secured system that manages keys for you. Your application server never has to store raw keys anywhere permanently.

---

## 3. Concepts Learned

### 3.1 Envelope Encryption

This is the core mechanism KMS uses to encrypt data without creating performance problems.

**How it works:**

1. Your server asks KMS for a data key
2. KMS sends back two things: a plain text data key and an encrypted version of that same data key
3. The server uses the plain text key to encrypt the data
4. The server stores the encrypted data together with the encrypted data key in the database
5. The server then immediately destroys the plain text key from memory
6. When the server needs to read the data later, it sends the encrypted data key back to KMS
7. KMS decrypts it using its internal master key and hands the plain text key back temporarily
8. The server uses it to decrypt the data and then destroys it again

The master key never leaves KMS at any point in this flow.

### 3.2 Reducing Blast Radius

Instead of using one single key to encrypt millions of records, the server requests a new data key every few thousand records. If one key ever gets stolen, only a small portion of data is at risk instead of everything. This limits the damage from any single leak.

### 3.3 Master Key Rotation

KMS automatically rotates the internal master key every 90 to 180 days. This makes it very hard for an attacker to exploit a key even if they somehow got close to it, because the key changes before they can do anything useful with it.

### 3.4 Why KMS is Hard to Hack

A common question is: if your server needs credentials to talk to KMS, can't a hacker just steal those credentials? AWS handles this in a few ways:

* **IAM Integration:** Because the EC2 instance and KMS are both inside the same AWS account, AWS handles authentication automatically. No usernames or passwords are hardcoded anywhere.
* **Short-lived RAM tokens:** AWS injects a temporary token directly into the server's RAM and rotates it every hour. There is no file to steal.
* **Private network:** KMS runs on private IPs that are not reachable from the public internet. Only authorized servers inside the account can reach it.
* **Minimal code surface:** KMS does exactly one job. Less code means fewer bugs and fewer ways for an attacker to find a weakness.

### 3.5 Real World Use Case

This same KMS setup can be used to securely store third party API keys like OpenAI keys or database connection strings. Instead of leaving them in a `.env` file or a repository, they get encrypted with KMS and only decrypted at runtime when the server actually needs them.

---

## 4. Key Takeaways

* Your data is only as secure as the keys used to encrypt it
* Storing encryption keys in the same place as encrypted data defeats the purpose of encrypting at all
* Envelope encryption lets you encrypt large amounts of data without sending everything through KMS every time
* Blast radius reduction and key rotation are two simple strategies that limit how much damage a key leak can actually cause
* AWS handles authentication between your server and KMS automatically so there are no credentials to steal or hardcode