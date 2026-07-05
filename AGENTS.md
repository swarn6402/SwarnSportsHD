# AGENTS.md

Guidance for AI coding agents working in the **SwarnSportsHD** repository. This
file is the portable, tool-agnostic entry point (see also `CLAUDE.md` for
Claude Code specifics and `CONTEXT.md` for deep architecture notes).

## What this project is

SwarnSportsHD is a two-part app:

1. **Backend** (`backend/`, Python + Telethon) — logs into a Telegram account,
   reads recent messages from configured channels, extracts stream URLs, and
   writes them to `data.json` at the repository root.
2. **Frontend** (root `index.html` / `script.js` / `style.css`, vanilla JS) — a
   static GitHub Pages site that fetches `data.json` and renders link cards.

There is **no build step, no framework, no package manager for the frontend, and
no test suite.** Keep it that way unless explicitly asked otherwise.

## Golden rules

- **Never commit secrets.** `backend/.env` (real credentials) and `*.session`
  (Telethon auth) are git-ignored. Do not stage, print, or paste their contents.
  `.env.example` is the only env file that belongs in git.
- **`data.json` is generated output**, not source. Do not hand-edit it to add
  features; it is overwritten by `telegram_fetcher.py` on every run.
- **Match the existing style.** No TypeScript, no bundlers, no JS frameworks, no
  CSS preprocessors. Plain ES modules-free `<script>`, standard library Python.
- **Keep changes small and dependency-free.** Only `telethon` and
  `python-dotenv` are backend dependencies. Adding a new dependency needs a
  clear justification.
- **Do not run the fetcher without permission.** It performs a real Telegram
  login and network calls. Prefer static reasoning; ask before executing it.

## Repository map

```
SwarnSportsHD/
├── index.html            # Frontend markup + link-card <template>
├── script.js             # Frontend logic: fetch data.json, render, copy-to-clipboard
├── style.css             # Frontend styling
├── data.json             # GENERATED output consumed by the frontend (root copy)
├── frontend/data.json    # Secondary copy used by deploy.sh /docs workflow
├── update.bat            # Windows: fetch + git add/commit/push (primary workflow)
├── deploy.sh             # Linux/macOS: fetch + copy to docs/ + push
├── .env.example          # Template for credentials (safe to commit)
├── backend/
│   ├── config.py             # Loads & validates env vars from backend/.env
│   ├── telegram_fetcher.py   # Main scraper → writes root data.json
│   ├── get_channel_info.py   # Utility: list channel/supergroup IDs for the account
│   ├── requirements.txt      # telethon, python-dotenv
│   ├── run_fetcher.sh        # Linux/macOS wrapper to run the fetcher
│   └── run_fetcher.bat       # Windows wrapper
└── README.md             # User-facing setup/usage docs
```

## Common tasks

| Goal | Where to work |
|------|---------------|
| Change how links are scraped/filtered | `backend/telegram_fetcher.py` (`extract_links_from_message`, `URL_BLACKLIST`) |
| Add/validate a config option | `backend/config.py` |
| Change the rendered card / UI | `index.html` (`#link-card-template`) + `script.js` (`createLinkCard`) + `style.css` |
| Change the `data.json` shape | Backend `get_all_cricket_links` **and** frontend `displayLinks`/`createLinkCard` must stay in sync |
| Change deploy/commit flow | `update.bat` (Windows) / `deploy.sh` (Unix) |

## The data contract (keep both sides in sync)

`data.json` is the single interface between backend and frontend:

```json
{
  "timestamp": "ISO-8601 UTC string",
  "links": [
    {
      "url": "https://...",
      "source_channel_id": -100...,
      "source_channel_name": "Channel title",
      "message_text": "raw message text",
      "posted_time": "ISO-8601 string or null"
    }
  ]
}
```

If you alter any key here, update **both** the producer
(`telegram_fetcher.py`) and the consumer (`script.js`).

## Verifying changes

- **Frontend:** open `index.html` in a browser (or `python -m http.server` from
  root) and confirm cards render against the current `data.json`. There is no
  automated test harness.
- **Backend:** prefer reasoning + reading. If a live run is required and
  authorized, use `python backend/telegram_fetcher.py` (needs a valid
  `backend/.env` and Telegram login).

## Git / deployment

- Default branch: `main`. GitHub Pages serves from the repo root.
- Commit only when asked. Real commit history uses messages like
  `Update links`. Do not commit `data.json` churn unless that is the task.
- End work by summarizing what changed and whether it was verified.
