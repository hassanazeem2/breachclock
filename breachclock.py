#!/usr/bin/env python3

import argparse
import boto3
import json
from datetime import datetime, timezone
from pathlib import Path
from visualize import generate_timeline_chart

BUCKET_NAME = 'breachclock-test-demo-1781316300'
DEFAULT_PROFILE = 'breachclock'
DEFAULT_REGION = 'us-east-1'
DEFAULT_CHART_PATH = 'screenshots/timeline.png'


def parse_args():
    """Parse command-line options while preserving the demo defaults."""
    parser = argparse.ArgumentParser(
        description='Quantify S3 public exposure timelines from CloudTrail history.'
    )
    parser.add_argument(
        '--bucket',
        default=BUCKET_NAME,
        help=f'S3 bucket to analyze (default: {BUCKET_NAME})'
    )
    parser.add_argument(
        '--profile',
        default=DEFAULT_PROFILE,
        help=f'AWS profile name (default: {DEFAULT_PROFILE})'
    )
    parser.add_argument(
        '--region',
        default=DEFAULT_REGION,
        help=f'AWS region for CloudTrail lookup (default: {DEFAULT_REGION})'
    )
    parser.add_argument(
        '--chart',
        default=DEFAULT_CHART_PATH,
        help=f'Path for the timeline chart (default: {DEFAULT_CHART_PATH})'
    )
    parser.add_argument(
        '--report',
        help='Optional path to write a JSON exposure report.'
    )
    return parser.parse_args()


def get_all_cloudtrail_events(cloudtrail, bucket_name):
    """Fetch all CloudTrail events for the bucket"""
    print(f"[*] Fetching CloudTrail events for {bucket_name}...\n")
    
    try:
        response = cloudtrail.lookup_events(
            LookupAttributes=[
                {
                    'AttributeKey': 'ResourceName',
                    'AttributeValue': bucket_name
                }
            ],
            MaxResults=50
        )
        
        events = response.get('Events', [])
        return sorted(events, key=lambda x: x['EventTime'])
    
    except Exception as e:
        print(f"[-] Error: {e}")
        return []

def find_exposure_time(events):
    """Find when bucket became public"""
    for event in events:
        if event['EventName'] in ['PutBucketPolicy', 'PutBucketAcl']:
            try:
                ct_event = json.loads(event.get('CloudTrailEvent', '{}'))
                request_params = ct_event.get('requestParameters', {})
                
                if 'bucketPolicy' in request_params:
                    policy = request_params['bucketPolicy']
                    if isinstance(policy, str):
                        policy = json.loads(policy)
                    
                    statements = policy.get('Statement', [])
                    for stmt in statements:
                        principal = stmt.get('Principal')
                        if principal == '*':
                            return event['EventTime']
            except:
                pass
    
    return None


def format_duration(duration):
    """Return a compact day/hour/minute duration string."""
    days = duration.days
    hours = (duration.seconds // 3600) % 24
    minutes = (duration.seconds // 60) % 60
    return f"{days}d {hours}h {minutes}m"


def isoformat(value):
    """Serialize datetimes for JSON reports."""
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def build_exposure_report(bucket_name, events, exposure_time, generated_at):
    """Create a machine-readable exposure summary."""
    duration = generated_at - exposure_time if exposure_time else None
    exposure_events = [
        event for event in events
        if event['EventName'] in ['PutBucketPolicy', 'PutBucketAcl']
    ]

    return {
        'bucket': bucket_name,
        'generated_at': generated_at.isoformat(),
        'event_count': len(events),
        'exposure_detected': exposure_time is not None,
        'exposure_started_at': isoformat(exposure_time),
        'exposure_duration_seconds': int(duration.total_seconds()) if duration else None,
        'exposure_duration': format_duration(duration) if duration else None,
        'public_access_change_count': len(exposure_events),
        'events': [
            {
                'time': isoformat(event.get('EventTime')),
                'name': event.get('EventName'),
                'principal': event.get('Username', 'unknown'),
            }
            for event in events
        ],
    }


def write_report(report, output_path):
    """Write the exposure report to disk as formatted JSON."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + '\n')
    print(f"[+] JSON report saved to {path}")


def main():
    args = parse_args()
    print("[*] BreachClock - Exposure Timeline Detector\n")
    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    cloudtrail = session.client('cloudtrail')
    
    events = get_all_cloudtrail_events(cloudtrail, args.bucket)
    
    if not events:
        print("[-] No events found")
        if args.report:
            report = build_exposure_report(args.bucket, events, None, datetime.now(timezone.utc))
            write_report(report, args.report)
        return
    
    print(f"[+] Found {len(events)} events\n")
    
    print("=" * 70)
    print("EVENT TIMELINE")
    print("=" * 70)
    
    for i, event in enumerate(events, 1):
        print(f"\n{i}. [{event['EventTime']}] {event['EventName']}")
        print(f"   Principal: {event.get('Username', 'unknown')}")
    
    exposure_time = find_exposure_time(events)
    current = datetime.now(exposure_time.tzinfo if exposure_time else timezone.utc)
    
    if exposure_time:
        duration = current - exposure_time
        
        print(f"\n\n[!] EXPOSURE DETECTED")
        print(f"    Became public: {exposure_time}")
        print(f"    Exposed for: {format_duration(duration)}")
        print("=" * 70)
        
        # Generate chart
        print("\n[*] Generating timeline chart...")
        generate_timeline_chart(events, exposure_time, args.chart)
    else:
        print("\n[-] No public exposure detected")

    if args.report:
        report = build_exposure_report(args.bucket, events, exposure_time, current)
        write_report(report, args.report)

if __name__ == '__main__':
    main()
