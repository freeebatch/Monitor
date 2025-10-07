# Website Monitor Bot (Telegram + Dashboard)

Monitors multiple websites asynchronously and alerts via Telegram if any go down or recover.
Deployable on Render (worker + web service).

## Files
- monitor.py          : Async monitor that sends Telegram alerts
- dashboard.py        : Flask app with simple status page and API
- config.json         : List of websites to monitor
- .env.sample         : Example environment variables
- requirements.txt
- render.yaml         : Render deployment configuration

## Setup (locally)
1. Copy `.env.sample` to `.env` and fill BOT_TOKEN and CHAT_ID (or set ENV vars).
2. Install deps: `pip install -r requirements.txt`
3. Run the monitor (in one terminal): `python monitor.py`
4. Run dashboard (in another terminal): `python dashboard.py`
5. Open http://localhost:8000 for the dashboard.

## Deploy to Render
1. Push this repo to GitHub.
2. In Render, create a Web Service (dashboard) and a Worker (monitor) or let render.yaml handle both.
3. Add environment variables in Render: BOT_TOKEN, CHAT_ID, CHECK_INTERVAL
4. Deploy.

## Notes
- This is a minimal production-ready starting point. For more reliability, consider adding persistent storage
  (e.g., PostgreSQL), structured logging, and graceful shutdown handling.
