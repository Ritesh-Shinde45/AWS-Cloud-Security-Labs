# Lab 09: CloudWatch Metrics and Logs Architecture

## 1. Overview

This lab covers Phase 9 of the AWS Cloud Infrastructure project. This was a deep concept study session on Amazon CloudWatch. Before this I had used CloudWatch briefly in the security simulation lab to observe network spikes. This session goes much deeper into how CloudWatch actually works under the hood, what the difference between metrics and logs is and how the whole monitoring architecture fits together in a real AWS environment.

---

## 2. Concepts Learned

### 2.1 What CloudWatch Actually Is

CloudWatch is AWS's built-in monitoring and observability service. It collects data from almost every AWS service automatically and gives you a single place to watch what is happening across your entire infrastructure. Without something like CloudWatch you would have no way to know if your EC2 instance is running out of memory, if your S3 bucket is getting too many access denied errors or if your Lambda function is throwing exceptions.

There are two main types of data CloudWatch deals with: **metrics** and **logs**. These are different things and they serve different purposes.

---

### 2.2 CloudWatch Metrics

A metric is a numeric measurement collected over time. Think of it as a number that gets recorded at a regular interval.

**Examples of metrics:**
* EC2 CPU utilization percentage every 5 minutes
* Number of S3 GetObject requests per hour
* RDS database connection count per minute
* Number of errors returned by a Lambda function

**Key concepts around metrics:**

* **Namespace:** Metrics are grouped into namespaces. AWS services each have their own namespace, for example `AWS/EC2`, `AWS/S3`, `AWS/Lambda`. Custom metrics you publish yourself go into a namespace you define.
* **Dimensions:** A dimension is a key-value pair that identifies a specific resource within a namespace. For example `InstanceId: i-1234abcd` inside the `AWS/EC2` namespace. Without dimensions you would not know which EC2 instance a CPU metric belongs to.
* **Resolution:** By default most AWS metrics are published at 5-minute intervals (standard resolution). You can enable detailed monitoring on EC2 to get 1-minute intervals. For custom metrics you can go as low as 1-second intervals with high-resolution metrics.
* **Retention:** CloudWatch stores metrics at different granularities depending on age. Data points under 60 seconds are kept for 3 hours, 1-minute data for 15 days, 5-minute data for 63 days and 1-hour data for 15 months.

---

### 2.3 CloudWatch Alarms

An alarm watches a single metric over a time period and performs an action when the metric crosses a threshold.

**Three states an alarm can be in:**
* **OK** - the metric is within the defined threshold
* **ALARM** - the metric has breached the threshold
* **INSUFFICIENT_DATA** - not enough data points yet to evaluate

**What an alarm can trigger:**
* Send a notification through SNS (email, SMS, HTTP endpoint)
* Auto Scaling action to add or remove EC2 instances
* EC2 action like stopping, rebooting or terminating an instance
* Systems Manager OpsItem for incident tracking

**Real example:** Set an alarm on EC2 CPU utilization. If it stays above 80% for two consecutive 5-minute periods, send an email alert and trigger an Auto Scaling policy to launch another instance.

---

### 2.4 CloudWatch Logs

Logs are text-based records of events that happened inside a system. Where a metric tells you a number changed, a log tells you exactly what happened and when.

**Core structure of CloudWatch Logs:**

* **Log Group:** A container for log streams from the same source or application. For example all Lambda function logs go into a log group named `/aws/lambda/function-name`.
* **Log Stream:** A sequence of log events from a single source inside a log group. For example each EC2 instance sends its logs to its own stream inside a shared log group.
* **Log Event:** A single record with a timestamp and a message string.

**Where logs come from:**

* EC2 instances using the CloudWatch Agent installed on the instance
* Lambda functions automatically send logs without any setup
* API Gateway access logs
* VPC Flow Logs for network traffic records
* CloudTrail logs forwarded to CloudWatch for real-time analysis
* Application code publishing custom log events using the SDK

---

### 2.5 CloudWatch Logs Insights

Logs Insights is a query engine built into CloudWatch that lets you search and analyze log data using a simple query language. Instead of scrolling through thousands of raw log lines you can write a query to filter, count, sort and visualize specific patterns.

**Example query to find the top 10 most frequent error messages:**

```
fields @timestamp, @message
| filter @message like /ERROR/
| stats count(*) as errorCount by @message
| sort errorCount desc
| limit 10
```

This is useful for things like finding which Lambda errors are happening most often, spotting unusual API call patterns or identifying which IP addresses are hitting your load balancer the most.

---

### 2.6 CloudWatch Agent

By default CloudWatch only collects metrics that AWS services report automatically. EC2 gives you CPU, network and disk I/O by default, but it does not give you memory usage or disk space because those live inside the operating system and AWS has no visibility into the OS level.

The CloudWatch Agent is a software process you install on an EC2 instance (or on-premises server) that collects:
* **System-level metrics:** Memory utilization, swap usage, disk space used
* **Custom application logs:** Any log file on the instance, for example `/var/log/httpd/access_log` from Apache

The agent reads a config file that tells it which metrics to collect and which log files to tail, then ships everything to CloudWatch.

---

### 2.7 CloudWatch Dashboards

Dashboards are customizable visual panels in the CloudWatch console where you can pin graphs of any metrics or alarm states. You can create a single dashboard that shows EC2 CPU across all your instances, S3 request counts, Lambda error rates and active alarms all in one view.

---

### 2.8 How Everything Fits Together

```
AWS Services / EC2 Agent
        |
        v
  CloudWatch Metrics  ──────────────>  Alarms  ──>  SNS / Auto Scaling
        |
  CloudWatch Logs
        |
        v
  Logs Insights (query and analyze)
        |
        v
  Dashboards (visualize everything)
```

A typical real-world monitoring setup looks like this:

1. EC2 instances run the CloudWatch Agent to send memory and disk metrics plus application logs
2. Alarms watch CPU and memory thresholds and notify the team via SNS when something looks wrong
3. VPC Flow Logs and CloudTrail logs stream into CloudWatch Logs for security analysis
4. Logs Insights queries run periodically to look for anomalies or failed login attempts
5. A dashboard gives the team a live overview of the whole environment

---

## 3. Key Takeaways

* Metrics are numbers over time, logs are text records of events. Both are needed for full observability.
* Every metric needs a namespace and at least one dimension to be meaningful, otherwise you cannot tell which resource it came from.
* CloudWatch only sees inside your EC2 instance if you install the CloudWatch Agent. Without it, memory and disk space are invisible to AWS.
* Logs Insights turns raw log data into something you can actually query and reason about instead of scrolling through lines manually.
* Alarms are the action layer on top of metrics. A metric alone just shows you data, an alarm is what actually responds to it.
