#!/usr/bin/env python3

import boto3
import json
from datetime import datetime
from visualize import generate_timeline_chart

session = boto3.Session(profile_name='breachclock', region_name='us-east-1')
cloudtrail = session.client('cloudtrail')

BUCKET_NAME = 'breachclock-test-demo-1781316300'

def get_all_cloudtrail_events():
    """Fetch all CloudTrail events for the bucket"""
    print(f"[*] Fetching CloudTrail events for {BUCKET_NAME}...\n")
    
    try:
        response = cloudtrail.lookup_events(
            LookupAttributes=[
                {
                    'AttributeKey': 'ResourceName',
                    'AttributeValue': BUCKET_NAME
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

def main():
    print("[*] BreachClock - Exposure Timeline Detector\n")
    
    events = get_all_cloudtrail_events()
    
    if not events:
        print("[-] No events found")
        return
    
    print(f"[+] Found {len(events)} events\n")
    
    print("=" * 70)
    print("EVENT TIMELINE")
    print("=" * 70)
    
    for i, event in enumerate(events, 1):
        print(f"\n{i}. [{event['EventTime']}] {event['EventName']}")
        print(f"   Principal: {event.get('Username', 'unknown')}")
    
    exposure_time = find_exposure_time(events)
    
    if exposure_time:
        current = datetime.now(exposure_time.tzinfo)
        duration = current - exposure_time
        days = duration.days
        hours = (duration.seconds // 3600) % 24
        
        print(f"\n\n[!] EXPOSURE DETECTED")
        print(f"    Became public: {exposure_time}")
        print(f"    Exposed for: {days}d {hours}h")
        print("=" * 70)
        
        # Generate chart
        print("\n[*] Generating timeline chart...")
        generate_timeline_chart(events, exposure_time, 'screenshots/timeline.png')
    else:
        print("\n[-] No public exposure detected")

if __name__ == '__main__':
    main()
