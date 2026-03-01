# webhook-repo

A FastAPI-based GitHub webhook receiver that captures **Push**, **Pull Request**, and **Merge** events, stores them in MongoDB, and displays them in a clean real-time UI.

---

## Project Structure

```
webhook-repo/
├── app.py               # FastAPI application
├── requirements.txt
├── static/
│   └── index.html       # Frontend UI (polls every 15s)
└── README.md
```

---

## Setup & Run

### 1. Clone & install dependencies

```bash
git clone https://github.com/<your-username>/webhook-repo.git
cd webhook-repo
pip install -r requirements.txt
```

### 2. Start MongoDB

Make sure MongoDB is running locally:
```bash
mongod --dbpath /data/db
```
Or use a MongoDB Atlas URI by setting the environment variable:
```bash
export MONGO_URI="mongodb+srv://<user>:<pass>@cluster.mongodb.net/"
```

### 3. Run the FastAPI server

```bash
uvicorn app:app --host 0.0.0.0 --port 5000 --reload
```

The app will be available at `http://localhost:5000`.

---

## Exposing to the Internet (for GitHub Webhooks)

GitHub needs a public URL to send webhooks to. Use **ngrok** during development:

```bash
ngrok http 5000
```

Copy the HTTPS URL it gives you (e.g., `https://abc123.ngrok.io`).

---

## Configuring GitHub Webhook on `action-repo`

1. Go to your **action-repo** on GitHub
2. Navigate to **Settings → Webhooks → Add webhook**
3. Fill in:
   - **Payload URL**: `https://<your-ngrok-url>/webhook`
   - **Content type**: `application/json`
   - **Secret**: *(leave blank for now or add verification)*
   - **Which events?**: Select **individual events** and check:
     - ✅ Pushes
     - ✅ Pull requests
4. Click **Add webhook**

---

## API Endpoints

| Method | Endpoint   | Description                        |
|--------|------------|------------------------------------|
| POST   | `/webhook` | Receives GitHub webhook payloads   |
| GET    | `/events`  | Returns latest 20 events as JSON   |
| GET    | `/`        | Serves the frontend UI             |
| DELETE | `/events`  | Clears all events (for testing)    |

---

## MongoDB Schema

| Field       | Type             | Details                                              |
|-------------|------------------|------------------------------------------------------|
| `_id`       | ObjectId         | MongoDB default ID                                   |
| `request_id`| string           | Git commit hash (Push) or PR number (PR/Merge)       |
| `author`    | string           | GitHub username performing the action                |
| `action`    | string           | Enum: `"PUSH"`, `"PULL_REQUEST"`, `"MERGE"`          |
| `from_branch`| string          | Source branch (null for Push)                        |
| `to_branch` | string           | Target branch                                        |
| `timestamp` | string(datetime) | UTC formatted string, e.g. `1st April 2021 - 9:30 PM UTC` |

---

## UI

The frontend (`/`) auto-polls `/events` every **15 seconds** and renders:

- **Push**: `"Travis" pushed to "staging" on 1st April 2021 - 9:30 PM UTC`
- **Pull Request**: `"Travis" submitted a pull request from "staging" to "master" on ...`
- **Merge**: `"Travis" merged branch "dev" to "master" on ...`

---

## action-repo Setup

The `action-repo` is just any regular GitHub repository. No special code is needed there — GitHub sends webhooks automatically based on the webhook configuration above.

Simply create a repo named `action-repo`, configure the webhook pointing to your `webhook-repo` endpoint, and start making commits and pull requests.