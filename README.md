# SwarnSportsHD

> A Telegram-to-web cricket stream link aggregator: a Python scraper that collects links from Telegram channels into `data.json`, and a dependency-free static site that renders them.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![No build step](https://img.shields.io/badge/frontend-vanilla%20JS-f7df1e.svg)](#frontend)

## How it works

```
Telegram channels ──▶ telegram_fetcher.py ──▶ data.json ──▶ index.html (static site)
     (Telethon)          (scrape + filter)      (output)       (fetch + render)
```

1. The backend logs into Telegram via [Telethon](https://docs.telethon.dev/), reads the last 100 messages from each configured channel, and keeps only those from the past 24 hours.
2. It extracts `http/https` links from message entities and text, then validates, deduplicates (globally), and blacklist-filters them.
3. Results are written to `data.json` at the repository root.
4. The static frontend fetches `data.json` and renders link cards, auto-refreshing every 5 minutes.

There is **no build step, no framework, and no server** — just Python standard library + Telethon on the backend, and vanilla HTML/CSS/JS on the frontend.

## Requirements

- Python 3.8+
- A Telegram account with API credentials (`API_ID`, `API_HASH`) from [my.telegram.org](https://my.telegram.org)
- Git (for the publish workflow)
- Python packages: `telethon`, `python-dotenv` (see `backend/requirements.txt`)

## Quick start

```bash
# 1. Clone
git clone https://github.com/swarn6402/SwarnSportsHD.git
cd SwarnSportsHD

# 2. Install backend dependencies
pip install -r backend/requirements.txt

# 3. Configure credentials
cp .env.example backend/.env      # on Windows: copy .env.example backend\.env
```

Edit `backend/.env`:

```env
API_ID=12345678
API_HASH=your_api_hash
PHONE_NUMBER=+1234567890
CHANNELS=-1001111111111,-1002222222222
```

Run the scraper (prompts for a Telegram login code on first run):

```bash
python backend/telegram_fetcher.py
```

Preview the site locally:

```bash
python -m http.server        # then open http://localhost:8000
```

## Configuration

All config lives in `backend/.env` and is validated on startup by `backend/config.py`:

| Variable       | Description                                              |
| -------------- | ------------------------------------------------------- |
| `API_ID`       | Telegram API ID (integer)                               |
| `API_HASH`     | Telegram API hash                                       |
| `PHONE_NUMBER` | Account phone in E.164 format (e.g. `+1234567890`)      |
| `CHANNELS`     | Comma-separated channel/chat IDs (negative integers)    |

To find channel IDs, use the helper: `python backend/get_channel_info.py`.

## Data contract

`data.json` is **generated output** — do not edit it by hand. Any field change must be mirrored in both `backend/telegram_fetcher.py` and `script.js`.

```json
{
  "timestamp": "2026-07-05T14:29:31+00:00",
  "links": [
    {
      "url": "https://example.com/stream",
      "source_channel_id": -1001748820600,
      "source_channel_name": "Channel Name",
      "message_text": "Match A vs Match B\n...",
      "posted_time": "2026-07-05T13:35:11+00:00"
    }
  ]
}
```

## Publishing (GitHub Pages)

The site is fully static and can be served straight from the repo.

- **From root:** commit `index.html`, `style.css`, `script.js`, `data.json`, then set
  *Settings → Pages → Deploy from a branch → `main` / `(root)`*.
- **From `/docs`:** run `deploy.sh` (copies `frontend/*` into `docs/`), then point Pages at `main` / `/docs`.

Convenience scripts to fetch-and-publish in one step:

- `update.bat` — Windows: runs the scraper, then `git add data.json` + commit + push.
- `deploy.sh` — Linux/macOS: runs the scraper, copies to `docs/`, commits, and pushes.

## Project structure

```
SwarnSportsHD/
├── index.html            # Frontend markup + link-card template
├── style.css             # Styling (dark theme, no framework)
├── script.js             # Fetch, render, copy, 5-min auto-refresh
├── data.json             # Generated output (scraper writes this)
├── backend/
│   ├── telegram_fetcher.py   # Scraper: fetch, extract, filter, save
│   ├── config.py             # Loads + validates backend/.env
│   ├── get_channel_info.py   # Helper to list channel IDs
│   └── requirements.txt
├── update.bat            # Windows fetch + publish
└── deploy.sh             # Unix fetch + publish to /docs
```

## Troubleshooting

| Message                                          | Fix                                                             |
| ------------------------------------------------ | -------------------------------------------------------------- |
| `Missing required environment variable(s)`       | Ensure all four keys are set in `backend/.env`.                |
| `API_ID must be a valid integer`                 | Use a plain number, no quotes.                                 |
| `CHANNELS must be a comma-separated list...`      | Each ID must be an integer, comma-separated.                   |
| `Malformed JSON in data.json`                     | Re-run the scraper to regenerate the file.                     |
| Channel fetch errors                             | Confirm your account can access the channel and the ID is right. |

## Security

- `backend/.env` and `*.session` files hold live credentials and are **git-ignored** — never commit them. Only `.env.example` belongs in version control.
- Do not share your `API_HASH`, phone number, or Telethon session file.

## Contributing

Issues and pull requests are welcome. Please keep the stack as-is (standard-library Python + Telethon on the backend, vanilla JS on the frontend — no npm, bundlers, or CSS frameworks) and keep the `data.json` contract in sync across backend and frontend.

## Disclaimer

This project is a tool for aggregating publicly posted links and is intended for personal and educational use. It does not host, stream, or distribute any content. Users are responsible for complying with the terms of service of Telegram and any linked services, as well as applicable copyright law.

## License

MIT — see [LICENSE](LICENSE).
