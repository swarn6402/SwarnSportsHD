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
   them. Only `.env.example` is committable. `SESSION_STRING` (the CI
   StringSession) is a full-access credential too — it lives only in GitHub
   Actions secrets; never print it or add it to `.env.example`.
2. **`data.json` is generated.** Treat it as build output; don't hand-author it.
3. **No new stack.** Keep vanilla JS + standard-library Python. Don't introduce
   npm, bundlers, TypeScript, React, or CSS frameworks.
4. **Don't run the fetcher unprompted.** It performs a real Telegram login and
   network I/O. Ask before executing `telegram_fetcher.py`, `get_channel_info.py`,
   or `generate_session.py`.
5. **Keep the data contract in sync.** Any change to a `data.json` field must be
   made in both `backend/telegram_fetcher.py` and `script.js`.

## Where things live

- **Scraper logic:** `backend/telegram_fetcher.py`
  - `authenticate()` — Telethon session: `StringSession(SESSION_STRING)` when that
    env var is set (headless/CI), else the on-disk `swarnsports_session` file
  - `fetch_recent_messages()` — last 100 msgs, filtered to last 24h
  - `_is_football_message()` — sport gate; drops clear football posts but keeps
    cricket and F1 (keep-by-default via `CRICKET_KEYWORDS` / `F1_KEYWORDS` /
    `FOOTBALL_KEYWORDS`). Bias: never miss a cricket stream.
  - `extract_links_from_message()` — pulls URLs from entities + text, dedupes,
    applies `URL_BLACKLIST`
  - `get_all_cricket_links()` / `save_to_json()` — assemble and write root `data.json`
- **CI session helper:** `backend/generate_session.py` — one-time local script to
  mint a `SESSION_STRING` for GitHub Actions (do not run unprompted; it logs in).
- **Config + validation:** `backend/config.py` (loads `backend/.env`, requires
  `API_ID`, `API_HASH`, `PHONE_NUMBER`, `CHANNELS`)
- **Frontend:** `index.html` (markup + `#link-card-template` + `.hero-media`
  layer + footer social/disclaimer), `script.js` (fetch/render/copy, 5-min
  auto-refresh), `style.css`
- **SEO / PWA assets (root):** `robots.txt`, `sitemap.xml`, `site.webmanifest`,
  and the favicon set (`favicon.ico`, `favicon-16x16.png`, `favicon-32x32.png`,
  `apple-touch-icon.png`, `android-chrome-192x192.png`,
  `android-chrome-512x512.png`). All referenced with **relative** paths so they
  resolve on the GitHub Pages project subpath.
- **Ops:** `update.bat` (Windows primary), `deploy.sh` (Unix + /docs),
  `backend/run_fetcher.*`, and `.github/workflows/fetch-links.yml` (manual
  `workflow_dispatch` headless fetch — runnable from the GitHub mobile app; auths
  via the `SESSION_STRING` secret, no schedule)

## Frontend design system

- **Theme:** premium dark, broadcast-style. Rich near-black background
  (`--bg-primary: #0a0a0a`); one **electric-blue accent** (`--accent: #3b82f6`,
  `--accent-strong`, `--accent-soft`) used *sparingly* — live dot, links, hover
  glow, Copy CTA, card accent bar. Don't turn the accent into a fill wash.
- **Typography (Google Fonts, one request, `display=swap`):** hero `<h1>` uses
  **Plus Jakarta Sans 800** (mixed case — no `text-transform`); section headings
  use **Space Grotesk**; body/meta use **Inter**. Load only weights in use.
- **Hero image:** `.hero-media` renders an Unsplash night-cricket photo *behind
  the hero only*, under a dark gradient overlay for legibility, with
  `background-color` fallback so a failed load degrades to solid dark (no broken
  icon, no layout shift). Keep that fallback if you touch it.
- **Motion:** 200–300ms eased transitions, staggered card entrance (JS sets
  `animationDelay`), `livePulse` on the live dot; all guarded by
  `prefers-reduced-motion`. Hover effects live in `@media (hover: hover)` with
  `:active` fallbacks under `@media (hover: none)` — preserve that split so touch
  degrades gracefully.
- **External runtime deps:** Google Fonts + the Unsplash hero image are fetched
  from CDNs at page load. They're intentional, but they are the *only* third-party
  frontend requests — don't add more without a reason.
- **Toast color** in `script.js` is inline styling kept in sync with `--accent`
  by hand; updating that one color string is styling, not logic.

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
