from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pymongo import MongoClient
from datetime import datetime, timezone
import json
import os

app = FastAPI(title="GitHub Webhook Receiver")

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["github_events"]
collection = db["events"]

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")


def format_timestamp(dt: datetime) -> str:
    """Format datetime to readable string: 1st April 2021 - 9:30 PM UTC"""
    day = dt.day
    suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return dt.strftime(f"%-d{suffix} %B %Y - %-I:%M %p UTC")


@app.get("/", response_class=HTMLResponse)
async def index():
    return FileResponse("static/index.html")


@app.post("/webhook")
async def receive_webhook(request: Request):
    """Receive GitHub webhook events and store in MongoDB."""
    event_type = request.headers.get("X-GitHub-Event", "")
    payload = await request.json()

    now = datetime.now(timezone.utc)
    timestamp_str = format_timestamp(now)

    document = None

    if event_type == "push":
        author = payload.get("pusher", {}).get("name", "Unknown")
        to_branch = payload.get("ref", "").replace("refs/heads/", "")
        request_id = payload.get("after", "")  # latest commit hash

        document = {
            "request_id": request_id,
            "author": author,
            "action": "PUSH",
            "from_branch": None,
            "to_branch": to_branch,
            "timestamp": timestamp_str,
        }

    elif event_type == "pull_request":
        pr = payload.get("pull_request", {})
        action = payload.get("action", "")

        # Only capture opened/reopened PRs (not merged here — merge handled separately)
        if action in ["opened", "reopened"]:
            author = pr.get("user", {}).get("login", "Unknown")
            from_branch = pr.get("head", {}).get("ref", "")
            to_branch = pr.get("base", {}).get("ref", "")
            request_id = str(pr.get("number", ""))

            document = {
                "request_id": request_id,
                "author": author,
                "action": "PULL_REQUEST",
                "from_branch": from_branch,
                "to_branch": to_branch,
                "timestamp": timestamp_str,
            }

        # Handle merge (brownie points)
        elif action == "closed" and pr.get("merged"):
            author = pr.get("merged_by", {}).get("login", "Unknown")
            from_branch = pr.get("head", {}).get("ref", "")
            to_branch = pr.get("base", {}).get("ref", "")
            request_id = str(pr.get("number", "")) + "-merge"

            document = {
                "request_id": request_id,
                "author": author,
                "action": "MERGE",
                "from_branch": from_branch,
                "to_branch": to_branch,
                "timestamp": timestamp_str,
            }

    if document:
        collection.insert_one(document)
        return {"status": "success", "action": document["action"]}

    return {"status": "ignored", "event": event_type}


@app.get("/events")
async def get_events():
    """Fetch latest events from MongoDB (most recent 20)."""
    events = list(collection.find({}, {"_id": 0}).sort("_id", -1).limit(20))
    return {"events": events}


@app.delete("/events")
async def clear_events():
    """Clear all events (for testing)."""
    collection.delete_many({})
    return {"status": "cleared"}


if __name__ == "__main__":
    import uvicorn

    # Run the app with Uvicorn when executed directly.
    # Adjust host/port or add `reload=True` for development as needed.
    uvicorn.run(app)
