# SwarnSports 🏏

## 1. Project Overview

SwarnSports is a lightweight cricket streaming link aggregator that fetches recent Telegram messages from selected channels, extracts URLs, and publishes them to a simple dark-themed frontend.

### Features
- ✅ Fetches links from multiple Telegram channels/supergroups
- ✅ Filters messages from the last 24 hours
- ✅ Extracts URLs automatically using regex
- ✅ Saves structured output to `frontend/data.json`
- ✅ Responsive, mobile-friendly frontend UI
- ✅ Copy-to-clipboard support for stream links
- ✅ Automation scripts for Windows, Linux, and macOS
- ✅ GitHub Pages friendly deployment flow

## 2. Prerequisites

- Python 3.8+
- Telegram account
- GitHub account (for hosting)

## 3. Setup Instructions

1. **Get Telegram API credentials** from `https://my.telegram.org`.
2. **Clone the repository** and open it in your IDE.
3. **Install dependencies**:

```bash
pip install -r backend/requirements.txt
```

4. **Copy environment template** and fill values:

```bash
cp .env.example .env
```

5. **Verify channels** by listing your available channel IDs:

```bash
python backend/get_channel_info.py
```

6. **Run a fetch test**:

```bash
python backend/telegram_fetcher.py
```

## 4. Getting Your Channel IDs

Use the helper script below to print your channels/supergroups in a table with title, chat ID, and type:

```bash
python backend/get_channel_info.py
```

How to add new channels:
- Copy the channel chat ID from script output.
- Open `.env`.
- Add the ID to `CHANNELS` as a comma-separated list.

Example:

```env
CHANNELS=-2292758419,-2946703793,-2100926631,-2221382924,-1001234567890
```

## 5. Deployment to GitHub Pages

Your repository is already created and linked to your IDE. Use this flow:

1. Create docs folder:

```bash
mkdir docs
```

2. Copy frontend files to docs:

```bash
cp -r frontend/* docs/
```

3. In GitHub repository settings, enable **Pages** from the `/docs` folder.
4. Run update script, then push:

```bash
./update.sh
git push
```

If your project uses `deploy.sh` instead, run:

```bash
./deploy.sh
```

## 6. Automation Setup

### Windows (Task Scheduler) 🪟

1. Open **Task Scheduler** → **Create Basic Task**.
2. Name: `SwarnSports Fetch`.
3. Trigger: `Daily` and set repeat every 1 hour.
4. Action: **Start a program**.
5. Program/script: `cmd.exe`
6. Add arguments:

```bat
/c "C:\path\to\SwarnSports\backend\run_fetcher.bat"
```

### macOS/Linux (cron) 🍎🐧

Edit crontab:

```bash
crontab -e
```

Run every hour:

```cron
0 * * * * cd /path/to/SwarnSports/backend && ./run_fetcher.sh
```

## 7. Usage

- Access site at: `https://username.github.io/swarnsports`
- Manual update:

```bash
./update.sh
git push
```

- Add channels:
  - Update `.env` (`CHANNELS=...`)
  - Re-run fetch/deploy

## 8. Troubleshooting

### Common errors and fixes

- ❌ `Missing required environment variable(s)`
  - Ensure `.env` exists and includes `API_ID`, `API_HASH`, `PHONE_NUMBER`, `CHANNELS`.

- ❌ `API_ID must be a valid integer`
  - Remove quotes/spaces; keep `API_ID` numeric.

- ❌ `Malformed JSON in data.json`
  - Re-run fetch script to regenerate JSON:

```bash
python backend/telegram_fetcher.py
```

### Session file issues

- If authentication breaks, delete old `.session` files and authenticate again.
- Session files are local and should stay out of version control.

### Channel access problems

- Make sure your Telegram account is a member of private channels.
- Some channels may block access or become unavailable.
- Run `python backend/get_channel_info.py` to verify visible channels and IDs.

---

Built for fast cricket link aggregation and simple static hosting. 🚀
