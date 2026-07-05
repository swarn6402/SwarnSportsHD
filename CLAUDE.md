# CLAUDE.md

Project guidance for Claude Code (and compatible agents) in **SwarnSportsHD**.
For the full architecture reference see `CONTEXT.md`; for the tool-agnostic
summary see `AGENTS.md`. This file intentionally repeats the essentials so it
can stand alone.

## TL;DR

SwarnSportsHD = a Python/Telethon Telegram scraper that writes `data.json`, plus
a dependency-free static frontend that renders it. No build, no tests, no
frameworks.

## Non-negotiables

1. **Secrets stay out of git.** `backend/.env` and `*.session` are ignored and
   contain live credentials — never read them into output, stage them, or echo
   them. Only `.env.example` is committable.
2. **`data.json` is generated.** Treat it as build output; don't hand-author it.
3. **No new stack.** Keep vanilla JS + standard-library Python. Don't introduce
   npm, bundlers, TypeScript, React, or CSS frameworks.
4. **Don't run the fetcher unprompted.** It performs a real Telegram login and
   network I/O. Ask before executing `telegram_fetcher.py` or `get_channel_info.py`.
5. **Keep the data contract in sync.** Any change to a `data.json` field must be
   made in both `backend/telegram_fetcher.py` and `script.js`.

## Where things live

- **Scraper logic:** `backend/telegram_fetcher.py`
  - `authenticate()` — Telethon session (`swarnsports_session`)
  - `fetch_recent_messages()` — last 100 msgs, filtered to last 24h
  - `extract_links_from_message()` — pulls URLs from entities + text, dedupes,
    applies `URL_BLACKLIST`
  - `get_all_cricket_links()` / `save_to_json()` — assemble and write root `data.json`
- **Config + validation:** `backend/config.py` (loads `backend/.env`, requires
  `API_ID`, `API_HASH`, `PHONE_NUMBER`, `CHANNELS`)
- **Frontend:** `index.html` (markup + `#link-card-template`), `script.js`
  (fetch/render/copy, 5-min auto-refresh), `style.css`
- **Ops:** `update.bat` (Windows primary), `deploy.sh` (Unix + /docs),
  `backend/run_fetcher.*`

## Environment notes

- Primary dev OS is **Windows** (bash shell via Git Bash). `update.bat` is the
  main workflow. Use forward slashes and POSIX shell syntax in Bash tool calls.
- Python 3.8+ (`telegram_fetcher.py` uses `list[str]` annotations).

## Conventions to follow

- Python: functions have docstrings; private helpers are `_prefixed`; explicit
  exception handling with printed context; `async`/`await` throughout the
  backend.
- JS: small pure-ish functions, defensive optional chaining (`link?.url`),
  no external libraries, graceful clipboard fallback.
- Preserve existing formatting and comment density; don't reformat untouched code.

## Verifying

- Frontend: serve the root (`python -m http.server`) and open in a browser to
  confirm rendering; no automated tests exist.
- Backend: prefer static review. Live runs require a valid `backend/.env`.

## Reporting

State exactly what changed, which files, and whether it was verified in a
browser or only reasoned about. If tests/verification were skipped, say so.
