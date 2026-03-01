# webhook-repo

A FastAPI-based GitHub webhook receiver that captures **Push**, **Pull Request**, and **Merge** events, stores them in MongoDB, and displays them in a clean real-time UI.

---

## Project Structure

```
webhook-repo/
├── main.py              # FastAPI application
├── requirements.txt
├── cloudflared.exe      # Cloudflare tunnel binary (Windows)
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

**Option A — Local MongoDB:**
```powershell
mongod
```

**Option B — MongoDB Atlas (recommended):** Create a free cluster at [mongodb.com/atlas](https://www.mongodb.com/atlas), then set the connection string as an environment variable:

```powershell
$env:MONGO_URI = "mongodb+srv://<user>:<pass>@cluster.mongodb.net/"
```

### 3. Run the FastAPI server

```powershell
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

The app will be available at `http://localhost:5000`.

---

## Exposing to the Internet (for GitHub Webhooks)

GitHub needs a public URL to send webhooks to. We use **Cloudflare Tunnel** for this.

### 1. Download Cloudflared

Download the **Windows 64-bit** binary from:
[developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/)

Place `cloudflared.exe` inside your `webhook-repo` folder.

### 2. Start the tunnel

Open a **new PowerShell terminal** and run:

```powershell
.\cloudflared.exe tunnel --url http://localhost:5000
```

You'll see a public URL like:
```
https://funk-encounter3762-hurricane-ministers.trycloudflare.com
```

Copy this URL — you'll need it for the GitHub webhook configuration.

> **Note:** No account needed for quick tunnels. The URL changes every time you restart cloudflared, so update your GitHub webhook URL accordingly.

---

## Configuring GitHub Webhook on `action-repo`

1. Go to your **action-repo** on GitHub
2. Navigate to **Settings → Webhooks → Add webhook**
3. Fill in:
   - **Payload URL**: `https://<your-cloudflare-url>/webhook`
   - **Content type**: `application/json`
   - **Secret**: *(leave blank)*
   - **SSL verification**: Disable it
   - **Which events?**: Select **individual events** and check:
     - ✅ Pushes
     - ✅ Pull requests
4. Click **Add webhook**

GitHub will send a ping request — check **Recent Deliveries** to confirm it shows a green ✅.

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

| Field        | Type             | Details                                                    |
|--------------|------------------|------------------------------------------------------------|
| `_id`        | ObjectId         | MongoDB default ID                                         |
| `request_id` | string           | Git commit hash (Push) or PR number (PR/Merge)             |
| `author`     | string           | GitHub username performing the action                      |
| `action`     | string           | Enum: `"PUSH"`, `"PULL_REQUEST"`, `"MERGE"`                |
| `from_branch`| string           | Source branch (null for Push)                              |
| `to_branch`  | string           | Target branch                                              |
| `timestamp`  | string(datetime) | UTC formatted string, e.g. `1st April 2021 - 9:30 PM UTC` |

---

## UI

The frontend (`/`) auto-polls `/events` every **15 seconds** and renders:

- **Push**: `"Travis" pushed to "staging" on 1st April 2021 - 9:30 PM UTC`
- **Pull Request**: `"Travis" submitted a pull request from "staging" to "master" on ...`
- **Merge**: `"Travis" merged branch "dev" to "master" on ...`

---

## Testing Locally (Without GitHub)

To simulate webhook events without pushing to GitHub, run:

```powershell
python test_webhooks.py
```

This sends fake Push, Pull Request, and Merge payloads directly to your local server and prints the results.

---

## action-repo Setup

The `action-repo` is just any regular GitHub repository — no special code is needed there. GitHub sends webhooks automatically based on the webhook configuration above.

Simply create a repo named `action-repo`, configure the webhook pointing to your `webhook-repo` endpoint, and start making commits and pull requests.