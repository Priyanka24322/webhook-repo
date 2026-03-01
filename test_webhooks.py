"""
Test script to simulate GitHub webhook events locally.
Run your FastAPI server first: uvicorn app:app --port 5000
Then run: python test_webhooks.py
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def send_push_event():
    payload = {
        "ref": "refs/heads/staging",
        "after": "abc123def456",
        "pusher": {"name": "Travis"}
    }
    headers = {"X-GitHub-Event": "push", "Content-Type": "application/json"}
    r = requests.post(f"{BASE_URL}/webhook", json=payload, headers=headers)
    print("PUSH:", r.json())

def send_pull_request_event():
    payload = {
        "action": "opened",
        "pull_request": {
            "number": 42,
            "user": {"login": "Travis"},
            "head": {"ref": "staging"},
            "base": {"ref": "master"},
        }
    }
    headers = {"X-GitHub-Event": "pull_request", "Content-Type": "application/json"}
    r = requests.post(f"{BASE_URL}/webhook", json=payload, headers=headers)
    print("PULL_REQUEST:", r.json())

def send_merge_event():
    payload = {
        "action": "closed",
        "pull_request": {
            "number": 42,
            "merged": True,
            "merged_by": {"login": "Travis"},
            "head": {"ref": "dev"},
            "base": {"ref": "master"},
        }
    }
    headers = {"X-GitHub-Event": "pull_request", "Content-Type": "application/json"}
    r = requests.post(f"{BASE_URL}/webhook", json=payload, headers=headers)
    print("MERGE:", r.json())

def get_events():
    r = requests.get(f"{BASE_URL}/events")
    events = r.json().get("events", [])
    print(f"\n=== {len(events)} Events in DB ===")
    for e in events:
        print(f"  [{e['action']}] {e['author']} | {e.get('from_branch','—')} → {e['to_branch']} | {e['timestamp']}")

if __name__ == "__main__":
    send_push_event()
    send_pull_request_event()
    send_merge_event()
    get_events()