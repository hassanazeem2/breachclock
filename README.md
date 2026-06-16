# 🕐 BreachClock

> **Quantifies cloud exposure timelines** — transforming abstract security risks into concrete dwell-time metrics that correlate with breach cost.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![AWS](https://img.shields.io/badge/AWS-Cloud-orange.svg)](https://aws.amazon.com)

---

## The Problem

Most cloud security tools answer: **"What's wrong?"**

BreachClock answers: **"Since when?"**

According to IBM's Cost of a Data Breach report, **dwell time is the single largest driver of breach cost**. Yet most CSPM tools focus on *what* is misconfigured, not *how long* it's been exposed.

BreachClock fills this gap by reconstructing the exact exposure timeline from CloudTrail history.

---

## Key Features

✅ **Exposure Timeline Detection** — Identifies the precise moment a resource became public  
✅ **Dwell Time Calculation** — Quantifies exposure duration down to the minute  
✅ **Unauthorized Access Tracking** — Counts real access attempts during exposure window  
✅ **Visual Timeline Reports** — Matplotlib-generated charts showing event history  
✅ **CloudTrail Integration** — Queries native AWS logs for 100% audit coverage  
✅ **Zero Setup Overhead** — Works with existing CloudTrail data (no agents needed)  

---

## How It Works

```
CloudTrail History
       ↓
   Parse Events
       ↓
Find "PutBucketPolicy" with Principal: "*"
       ↓
Mark Exposure Start Time
       ↓
Query GetObject attempts after exposure
       ↓
Calculate Duration & Access Count
       ↓
Generate Timeline Visualization
```

### Example Output

```
[*] BreachClock - Exposure Timeline Detector

[+] Found 4 events

EVENT TIMELINE
1. [2026-06-12 21:05:01] CreateBucket
   Principal: hazeem-admin

2. [2026-06-12 21:19:20] PutBucketPolicy
   Principal: hazeem-admin

3. [2026-06-12 21:19:36] PutBucketPublicAccessBlock
   Principal: hazeem-admin

4. [2026-06-12 21:19:42] PutBucketPolicy
   Principal: hazeem-admin


[!] EXPOSURE DETECTED
    Became public: 2026-06-12 21:19:20
    Exposed for: 47d 14h
    
[*] Generating timeline chart...
[+] Chart saved to screenshots/timeline.png
```

---

## Screenshots

### Timeline Visualization
![Exposure Timeline](screenshots/timeline.png)

*The chart displays the full event history with exposure window clearly marked. Red events indicate public access configuration, blue indicates administrative actions.*

---

## Installation

### Prerequisites
- Python 3.8+
- AWS account with CloudTrail enabled
- AWS CLI configured

### Setup

```bash
# Clone repo
git clone https://github.com/hassanazeem2/breachclock.git
cd breachclock

# Install dependencies
pip install -r requirements.txt

# Configure AWS credentials
aws configure --profile breachclock
```

### Quick Start

```bash
# Run against your S3 bucket
python3 breachclock.py

# Output: Event timeline + exposure metrics + visualization chart
```

---

## Real-World Impact

**Scenario:** A company discovers an S3 bucket is public.

### Without BreachClock:
❌ "Our bucket is public" — no timeline, no quantified impact

### With BreachClock:
✅ "Our bucket has been public for **47 days** with **340+ unauthorized reads** — estimated **2.3GB of data accessed**"

**Cost Implications:**
- Dwell time of 47 days = ~$4.5M average breach cost (IBM data)
- Early detection (47 days → 2 days) = potential **$2M+ savings**

---

## Usage

Run with the default demo configuration:

```bash
python3 breachclock.py
```

Analyze a specific bucket and export a JSON report:

```bash
python3 breachclock.py \
  --bucket your-bucket-name \
  --profile breachclock \
  --region us-east-1 \
  --chart screenshots/timeline.png \
  --report reports/exposure-report.json
```

The JSON report includes the analyzed bucket, exposure start time, dwell time in
seconds, public access change count, and the CloudTrail event timeline.

## Architecture

### Data Flow
```
AWS CloudTrail (audit logs)
          ↓
boto3 lookup_events()
          ↓
Parse PutBucketPolicy events
          ↓
Identify Principal: "*" (public access)
          ↓
Calculate exposure window
          ↓
Query GetObject attempts in window
          ↓
Matplotlib visualization
          ↓
Optional JSON report export
```

### How Exposure Detection Works

BreachClock reconstructs the exposure timeline by:

1. **Querying CloudTrail** for all S3 management events
2. **Finding PutBucketPolicy** calls that set Principal to `"*"`
3. **Recording the exact timestamp** of public access enablement
4. **Calculating exposure duration** from that moment to now
5. **Correlating data events** (GetObject) to quantify unauthorized access
6. **Optionally exporting JSON** for incident response handoff or automation

---

## Use Cases

### 1. Incident Response
Quickly quantify blast radius and dwell time during a security incident.

### 2. Compliance Audits
Demonstrate exposure timeline for post-breach investigations and regulatory reporting.

### 3. Risk Quantification
Convert abstract "data exposure" into concrete "47-day dwell time" metrics for stakeholders.

### 4. Breach Cost Analysis
Estimate potential breach cost using dwell time × sensitivity of exposed data.

### 5. Security Posture Improvement
Identify patterns in exposure duration to improve detection and response times.

---

## Configuration

Edit `breachclock.py` to monitor different buckets:

```python
BUCKET_NAME = 'your-bucket-name'
```

### AWS Requirements

Ensure your IAM user/role has these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudtrail:LookupEvents",
        "s3:GetBucketPolicy",
        "s3:GetBucketAcl",
        "config:GetResourceConfigHistory"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## Roadmap

- [ ] Multi-bucket scanning
- [ ] Cross-account support
- [ ] EBS snapshot exposure detection
- [ ] RDS backup exposure detection
- [ ] Blast radius scoring (how much data was accessible)
- [ ] Slack/email alert integration
- [ ] HTML report generation
- [ ] Web dashboard
- [ ] Cost impact calculator

---

## Why This Matters

**Dwell time directly correlates with breach cost.**

IBM's 2023 Cost of a Data Breach Report found:
- **Short dwell time (< 30 days):** $3.8M average breach cost
- **Long dwell time (> 200 days):** $5.7M average breach cost
- **Difference:** $1.9M+ per breach

BreachClock helps you:
1. Detect dwell time early
2. Quantify exposure impact
3. Accelerate incident response
4. Reduce breach cost
5. Demonstrate security maturity to stakeholders

---

## Requirements

```
boto3>=1.26.0
matplotlib>=3.5.0
```

---

## Files

- `breachclock.py` — Main exposure detection script
- `visualize.py` — Timeline chart generation
- `requirements.txt` — Python dependencies
- `screenshots/` — Example outputs and charts

---

## License

MIT License — See LICENSE for details

---

## Author

Built by [@hassanazeem2](https://github.com/hassanazeem2)

Part of a cloud security portfolio demonstrating expertise in AWS security, incident response, and threat timeline analysis.

---

## Contact

📧 Email: hassan@hazeem.org  
💼 Portfolio: [hazeem.org](https://hazeem.org)  
🔗 GitHub: [@hassanazeem2](https://github.com/hassanazeem2)

---

## Disclaimer

BreachClock is designed for authorized security professionals and incident responders. Ensure you have proper authorization before analyzing cloud infrastructure. Unauthorized access to AWS resources may violate terms of service and applicable laws.
