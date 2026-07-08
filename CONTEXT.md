# CONTEXT.md — SwarnSportsHD Architecture & Agentic Reference

A thorough, single-source reference for agents (and humans) working on this
codebase. `AGENTS.md` and `CLAUDE.md` are the short operating rules; this file is
the deep documentation.

---

## 1. Purpose & high-level flow

SwarnSportsHD aggregates cricket live-stream links that are posted in Telegram
channels and presents them on a simple public web page.

```
Telegram channels
      │  (Telethon, authenticated user session)
      ▼
backend/telegram_fetcher.py ──writes──►  data.json  ◄──fetch()── script.js ──renders──► index.html (GitHub Pages)
      ▲
backend/config.py (loads backend/.env)
```

- The backend is **pull-based and stateless between runs** (aside from the
  Telethon `.session` file). Each run overwrites `data.json`.
- The frontend is **fully static**: it does an HTTP `GET data.json` on load and
  every 5 minutes; there is no server-side component in production.
- Deployment is **git-push driven**: a fetch produces a new `data.json`, which is
  committed and pushed; GitHub Pages serves the updated file.

---

## 2. Component reference

### 2.1 `backend/config.py`
Loads and validates environment variables from `backend/.env` using
`python-dotenv`.

- Resolves `.env` relative to the file's own directory (robust to CWD).
- Exposes module-level constants: `API_ID` (int), `API_HASH` (str),
  `PHONE_NUMBER` (str), `CHANNELS` (list[int]).
- **Fail-fast validation:**
  - Raises `ValueError` listing any missing required vars.
  - `API_ID` must parse as `int`.
  - `CHANNELS` must be a comma-separated list of ints; empty list is rejected.
- Prints debug lines about which `.env` was loaded (harmless, kept for
  transparency).

### 2.2 `backend/telegram_fetcher.py`
The core scraper. Key elements:

- `URL_BLACKLIST` — substrings that disqualify a URL (`t.me/+`, `t.me/joinchat`)
  to skip Telegram invite links.
- `authenticate()` → `TelegramClient("swarnsports_session", ...)`, starts with
  phone auth. Creates/uses a local `.session` file.
- `_normalize_channel_id_for_peer(channel_id)` — converts Telegram's
  `-100XXXXXXXXXX` supergroup/channel form into the raw id for `PeerChannel`.
  Only strips the `100` prefix when the id begins with `100` after taking abs.
- `_resolve_channel_entity(client, channel_id)` — for negative ids resolves via
  `PeerChannel(normalized_id)`; for non-negative ids resolves directly.
- `fetch_recent_messages(client, channel_id)` — pulls up to 100 messages, keeps
  only those with `date >= now(UTC) - 24h`. Catches `ChannelPrivateError` /
  `ValueError` and returns `[]` on failure (per-channel resilience).
- `extract_links_from_message(message)` — the link-extraction heart:
  1. Reads `message.entities`: takes explicit `entity.url` (text-link entities),
     otherwise slices `text[offset:offset+length]` when it starts with `http`.
  2. Regex-scans the text for `https?://[^\s<>"]+`.
  3. Strips trailing punctuation `)]}>,.;:*'`.
  4. Validates scheme ∈ {http, https} and non-empty netloc via `urlparse`.
  5. Applies `URL_BLACKLIST` and dedupes (order-preserving via a `seen` set).
- `get_all_cricket_links()` — iterates `config.CHANNELS`, resolves each channel's
  title, and builds one record per URL per message. Per-channel `try/except`
  keeps one bad channel from aborting the whole run. Returns
  `{timestamp, links}`. Always disconnects the client in `finally`.
- `save_to_json(data)` — writes to **repo-root** `data.json`
  (`../data.json` relative to `backend/`), `indent=2`, UTF-8. Note the inline
  comment: output deliberately goes to root, not `frontend/`.
- `main()` — orchestrates fetch → save → summary print. Entry via
  `asyncio.run(main())`.

### 2.3 `backend/get_channel_info.py`
Standalone utility. Authenticates, lists all dialogs, filters to broadcasts
(Channel) and megagroups (Supergroup), and prints an ASCII table of
`(title, id, type)`. Use it to discover the numeric ids to put in `CHANNELS`.

### 2.4 Frontend (`index.html`, `script.js`, `style.css`)
- `index.html` — semantic markup with a header/hero (an absolutely-positioned
  `.hero-media` photo layer behind the `.header-content`), a streams section
  containing `#loading-state`, `#empty-state`, `#links-container`, a
  `<template id="link-card-template">` cloned per link, and a footer with social
  links (GitHub, X — inline SVG) plus a content disclaimer. The `<head>` carries
  the SEO/PWA block (see §2.6). Loads Google Fonts and `script.js`.
- `script.js` — no dependencies:
  - `loadLinks()` — fetches `data.json` with `cache: "no-store"`; distinguishes
    HTTP errors vs malformed JSON; shows friendly error text.
  - `displayLinks(data)` — sorts links by `posted_time` desc; empty → empty state.
  - `createLinkCard(link, index)` — clones the template, fills url/channel/
    time/preview (message truncated to 100 chars), wires the Copy button, and
    staggers a CSS entrance animation delay.
  - `copyToClipboard` / `fallbackCopyToClipboard` — Clipboard API with a
    `document.execCommand("copy")` fallback and toast feedback.
  - `formatRelativeTime` / `formatAbsoluteTime` — human-friendly timestamps
    (`en-GB` locale).
  - Auto-refresh: `setInterval(loadLinks, 5 * 60 * 1000)` after DOMContentLoaded.
  - `createToast` uses inline styles; its background color is kept in sync with
    the CSS `--accent` by hand (styling only — not part of the fetch/render logic).
- `style.css` — hand-written responsive styling; premium dark broadcast theme.
  - **Palette:** near-black background (`--bg-primary: #0a0a0a`) with a single
    **electric-blue accent** (`--accent: #3b82f6`, plus `--accent-strong` /
    `--accent-soft` / `--accent-glow` / `--accent-tint`) used sparingly: live dot,
    links, hover glow, Copy CTA, card accent bar.
  - **Type scale:** Plus Jakarta Sans 800 (hero `<h1>`, mixed case), Space Grotesk
    (section headings), Inter (body/meta). One Google Fonts request, `display=swap`.
  - **Hero image:** `.hero-media` paints an Unsplash night-cricket photo behind the
    hero only, layered under a `linear-gradient` dark overlay for text legibility,
    with a `background-color` fallback so a failed image load degrades to solid
    dark (no broken icon, no layout shift). Photographer credited in a CSS comment.
  - **Motion & a11y:** eased 200–300ms transitions, staggered `cardEnter`,
    `livePulse` on the live dot; hover effects scoped to `@media (hover: hover)`
    with `@media (hover: none)` `:active` fallbacks for touch; all animation
    guarded by `prefers-reduced-motion`.
  - **Responsive grid:** 1 col `<768px`, 2 cols `≥768px`, 3 cols `≥1024px`; tap
    targets ≥44px.

### 2.6 SEO & PWA assets
- **In `<head>` (`index.html`):** one concise `<title>`, a `<meta
  name="description">` (<160 chars), `<meta name="theme-color">`, a canonical
  link, Open Graph (`og:type/site_name/title/description/url`) and a Twitter
  `summary` card. **No `og:image`/`twitter:image`** — no suitable image asset
  ships in the repo, so none is fabricated. Keep `<title>` / description / `og:`
  / `twitter:` wording in sync when any of them changes. No JSON-LD (a link
  aggregator isn't an accurate `SportsEvent`), no tracking scripts.
- **Root files:** `robots.txt` (allow all + `Sitemap:` line), `sitemap.xml`
  (single canonical URL), `site.webmanifest` (name `SwarnSports`, dark
  `theme_color`/`background_color` `#0a0a0a`, relative icon `src`s).
- **Favicons (root):** `favicon.ico`, `favicon-16x16.png`, `favicon-32x32.png`,
  `apple-touch-icon.png`, `android-chrome-192x192.png`,
  `android-chrome-512x512.png`, wired via relative-path `<link>` tags.
- **Path rule:** every asset/SEO path is **relative** (no leading `/`) so it
  resolves on the GitHub Pages project subpath
  (`https://swarn6402.github.io/SwarnSportsHD/`), not just at a domain root.
- **External runtime dependencies:** Google Fonts and the Unsplash hero image are
  the only third-party frontend requests. Intentional; don't add more casually.

### 2.5 Ops scripts
- `update.bat` (Windows, **primary**): `cd backend` → run fetcher → `git add
  data.json` → commit `"Update links"` (tolerates no-change) → `git push`.
- `deploy.sh` (Unix): run fetcher → `mkdir -p docs` + `cp -r frontend/* docs/`
  → commit with dated message → `git push origin main`. Supports the "serve from
  /docs" GitHub Pages option.
- `backend/run_fetcher.sh` / `run_fetcher.bat`: thin wrappers to run the fetcher
  with error trapping.

---

## 3. The `data.json` contract

Single interface between backend and frontend. **Changing it means editing both
sides.**

```jsonc
{
  "timestamp": "2026-07-05T12:00:00+00:00",   // ISO-8601 UTC, when the run finished
  "links": [
    {
      "url": "https://example.com/stream",     // cleaned, validated absolute URL
      "source_channel_id": -1002292758419,      // original Telegram id from CHANNELS
      "source_channel_name": "Channel Title",   // resolved entity title (fallback: id)
      "message_text": "raw message body",       // may be empty string
      "posted_time": "2026-07-05T11:58:00+00:00" // ISO-8601 or null
    }
  ]
}
```

Producer: `get_all_cricket_links()` in `telegram_fetcher.py`.
Consumer: `displayLinks` / `createLinkCard` in `script.js`.

Note the **two copies** of `data.json`: root (written by the fetcher, served by
Pages-from-root) and `frontend/data.json` (used by the `deploy.sh` /docs flow).
Be aware which deployment mode is in use before assuming which copy is live.

---

## 4. Environment & configuration

`backend/.env` (git-ignored — never commit real values):

```env
API_ID=12345678                 # integer from https://my.telegram.org
API_HASH=your_api_hash          # paired hash
PHONE_NUMBER=+1234567890         # E.164
CHANNELS=-1001111111111,-1002222222222   # comma-separated channel ids
```

`.env.example` is the committed template. `*.session` files are Telethon auth
artifacts — local only, git-ignored.

Dependencies (`backend/requirements.txt`): `telethon`, `python-dotenv`. Python
3.8+.

---

## 5. Runbook

| Action | Command |
|--------|---------|
| Install deps | `pip install -r backend/requirements.txt` |
| Discover channel ids | `python backend/get_channel_info.py` |
| Run scraper | `python backend/telegram_fetcher.py` |
| Full update (Windows) | `update.bat` |
| Full update (Unix, /docs) | `./deploy.sh` |
| Preview frontend | `python -m http.server` in repo root, open `localhost:8000` |

⚠️ Running the scraper or channel utility triggers a **real Telegram login** and
network activity. Agents should not run these without explicit user approval.

---

## 6. Constraints, gotchas & conventions

- **No test suite / no CI.** Verification is manual (browser for frontend,
  live run for backend).
- **No build tooling.** Do not add npm/bundlers/TypeScript/frameworks.
- **Line endings** are enforced via `.gitattributes`: LF for `.sh/.py/.js/.html/
  .css/.md`, CRLF for `.bat`. Respect this when creating files.
- **Per-channel error isolation** is intentional — preserve the `try/except`
  around each channel loop.
- **Timezone correctness:** all cutoffs use timezone-aware UTC
  (`datetime.timezone.utc`). Keep new time logic UTC-aware.
- **Security posture:** this repo is public; keep credentials, session files,
  and any private channel content out of commits and out of agent output.
- **Editing style:** match existing docstrings, `_private` helper naming, and
  defensive JS optional chaining. Don't reformat untouched code.

---

## 7. Change-impact cheat sheet

- Changing scrape/filter behavior → `telegram_fetcher.py` only (self-contained).
- Adding a config field → `config.py` (validate it) + document in `.env.example`
  + README.
- Changing a `data.json` field → `telegram_fetcher.py` **and** `script.js`
  (+ possibly `index.html` template) together.
- Changing the UI → `index.html` template + `script.js` render fns + `style.css`.
- Changing the accent color / theme → `style.css` `:root` accent variables **and**
  the inline toast color in `script.js` (+ `theme-color` / `site.webmanifest` if
  the base dark tone changes).
- Changing the site title/description → `<title>`, `<meta name="description">`,
  and the matching `og:`/`twitter:` tags in `index.html` together.
- Changing SEO/PWA assets → keep all paths **relative** for the Pages subpath;
  touch `robots.txt` / `sitemap.xml` / `site.webmanifest` / favicon `<link>`s as
  needed.
- Changing deploy behavior → `update.bat` and/or `deploy.sh` (mind the two
  `data.json` copies and the Pages source setting).
