<div align="center">

<img src="android-chrome-512x512.png" alt="SwarnSports logo" width="120" height="120" />

# SwarnSports

**Live cricket streaming links — aggregated from Telegram, served on a fast, dependency-free web page.**

[![Live site](https://img.shields.io/badge/live-swarn6402.github.io-3b82f6.svg)](https://swarn6402.github.io/SwarnSportsHD/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Frontend: Vanilla JS](https://img.shields.io/badge/frontend-vanilla%20JS-f7df1e.svg)](#-frontend)
[![No build step](https://img.shields.io/badge/build-none-brightgreen.svg)](#-frontend)

</div>

---

SwarnSports is a two-part project: a **Python + Telethon scraper** that collects cricket
stream links posted in Telegram channels into a `data.json` file, and a **static, framework-free
web frontend** that renders those links as clean, copyable cards — auto-refreshing every few
minutes. No build tooling, no server, no database.

> **Click a link to watch. Copy a link to share.** That's the whole interaction.

## ✨ Features

**Frontend**
- ⚡ **Zero build, zero framework** — hand-written HTML, CSS, and vanilla JS. Loads instantly.
- 🎨 **Premium broadcast UI** — dark, near-black theme with a single electric-blue accent, a
  cinematic cricket hero image, and clean modern typography (Plus Jakarta Sans / Space Grotesk / Inter).
- 🔄 **Auto-refresh** — pulls the latest `data.json` every 5 minutes, no reload needed.
- 📋 **One-tap copy** — copy any stream link to the clipboard with graceful fallbacks + toast feedback.
- 📱 **Fully responsive** — 1 → 2 → 3 column grid, ≥44px tap targets, hover effects that degrade
  gracefully to touch, and `prefers-reduced-motion` support.
- 🔍 **SEO & PWA ready** — canonical URL, Open Graph / Twitter cards, `robots.txt`, `sitemap.xml`,
  a web manifest, and a full favicon set.

**Backend**
- 🤖 **Telethon-powered** — reads recent messages from configured channels as an authenticated user.
- 🧹 **Smart link extraction** — pulls URLs from message entities *and* text, validates schemes,
  strips trailing punctuation, deduplicates globally, and blacklist-filters invite links.
- 🏏 **Sport filtering** — the same channels sometimes post football; a conservative per-message
  classifier drops clear football posts while always keeping cricket (and letting F1 through).
- ⏱️ **24-hour window** — keeps only fresh links (last 100 messages, filtered to the past 24h, UTC-aware).
- 🛡️ **Per-channel resilience** — one unreachable channel never aborts the whole run.
- 📲 **Two ways to run** — a local Windows `update.bat`, or a manual **GitHub Actions** button you
  can tap from the GitHub mobile app (no laptop needed).

## 🌐 Live site

**→ [swarn6402.github.io/SwarnSportsHD](https://swarn6402.github.io/SwarnSportsHD/)**

## 🧭 How it works

```
Telegram channels ──▶ telegram_fetcher.py ──▶ data.json ──▶ index.html (static site)
     (Telethon)          (scrape + filter)      (output)       (fetch + render)
```

1. The backend logs into Telegram via [Telethon](https://docs.telethon.dev/), reads the last 100
   messages from each configured channel, and keeps only those from the past 24 hours.
2. It skips messages that are clearly football (cricket and F1 posts always pass), then extracts
   `http/https` links from message entities and text, and validates, deduplicates, and
   blacklist-filters them.
3. Results are written to `data.json` at the repository root.
4. The static frontend fetches `data.json` and renders link cards, auto-refreshing every 5 minutes.

The fetch can be triggered locally (`update.bat`) **or** remotely by tapping *Run workflow* on the
GitHub Actions "Fetch Links" job — handy from a phone.

There is **no build step, no framework, and no server** — just Python standard library + Telethon
on the backend, and vanilla HTML/CSS/JS on the frontend.

## 🧰 Tech stack

| Layer      | Tools                                                                 |
| ---------- | --------------------------------------------------------------------- |
| Backend    | Python 3.8+, [Telethon](https://docs.telethon.dev/), python-dotenv    |
| Frontend   | Vanilla HTML / CSS / JavaScript (no framework, no bundler)            |
| Fonts      | Plus Jakarta Sans, Space Grotesk, Inter (Google Fonts, `display=swap`)|
| Hosting    | GitHub Pages (static, served from repo root)                          |

## 🚀 Quick start

```bash
# 1. Clone the repository
git clone https://github.com/swarn6402/SwarnSportsHD.git
cd SwarnSportsHD

# 2. Install the backend dependencies
pip install -r backend/requirements.txt

# 3. Make the configuration file
cp .env.example backend/.env      # on Windows: copy .env.example backend\.env
```

Open `backend/.env` in an editor. Set these values:

```env
API_ID=12345678
API_HASH=your_api_hash
PHONE_NUMBER=+1234567890
CHANNELS=-1001111111111,-1002222222222
```

Start the scraper:

```bash
python backend/telegram_fetcher.py
```

On the first run, Telegram sends a login code to your account. Type this code when the scraper asks for it.

To see the site on your computer, start a local server:

```bash
python -m http.server        # then open http://localhost:8000
```

## ⚙️ Configuration

Write all configuration in `backend/.env`. At startup, `backend/config.py` does a check of these values:

| Variable       | Description                                              |
| -------------- | ------------------------------------------------------- |
| `API_ID`       | Telegram API ID (integer)                               |
| `API_HASH`     | Telegram API hash                                       |
| `PHONE_NUMBER` | Account phone in E.164 format (e.g. `+1234567890`)      |
| `CHANNELS`     | Comma-separated channel/chat IDs (negative integers)    |

To find the channel IDs, run the helper: `python backend/get_channel_info.py`.

The **headless / GitHub Actions** path uses one more variable: `SESSION_STRING`. This is a Telethon
[StringSession](https://docs.telethon.dev/en/stable/concepts/sessions.html). Do not set it on your
computer. On your computer, the scraper uses the `.session` file on the disk. For CI, set
`SESSION_STRING` as a GitHub **secret**. Refer to [Publishing](#-publishing-github-pages) below.

## 📄 Data contract

`data.json` is **generated output** — do not edit it by hand. Any field change must be mirrored in
both `backend/telegram_fetcher.py` (producer) and `script.js` (consumer).

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

## 🎨 Frontend

The frontend is intentionally simple to host and hack on — three files, no toolchain.

- **Theme:** premium dark (`#0a0a0a` base) with a single electric-blue accent (`#3b82f6`) used
  sparingly — the live indicator, links, hover glow, the Copy button, and the card accent bar.
- **Typography:** Plus Jakarta Sans 800 for the hero headline, Space Grotesk for section headings,
  Inter for body and meta text — loaded in a single `display=swap` request.
- **Hero:** a cinematic night-cricket photo sits behind the header under a dark gradient overlay,
  with a solid-color fallback so a failed image load never breaks the layout.
- **Motion & accessibility:** eased micro-interactions, a staggered card entrance, a pulsing live
  dot, hover effects that fall back to tap states on touch, and full `prefers-reduced-motion` support.

Editing the card layout means touching `index.html` (`#link-card-template`) + `script.js`
(`createLinkCard`) + `style.css` together.

## 📦 Publishing (GitHub Pages)

The site is fully static and can be served straight from the repo.

- **From root:** commit the frontend files + `data.json`, then set
  *Settings → Pages → Deploy from a branch → `main` / `(root)`*.
- **From `/docs`:** run `deploy.sh` (copies `frontend/*` into `docs/`), then point Pages at `main` / `/docs`.

Convenience scripts to fetch-and-publish in one step:

- `update.bat` — Windows: runs the scraper, then `git add data.json` + commit + push.
- `deploy.sh` — Linux/macOS: runs the scraper, copies to `docs/`, commits, and pushes.

### Fetching from your phone (GitHub Actions)

`.github/workflows/fetch-links.yml` runs the exact same scraper on GitHub's servers, triggered
**manually** (`workflow_dispatch`) — so you can update the site from the GitHub mobile app with no
laptop. It installs deps, runs the fetcher using repository **secrets**, and commits/pushes
`data.json`. There is intentionally **no schedule** — it only runs when you tap *Run workflow*.

One-time setup:

1. Make a reusable login token. Headless runs cannot do the interactive phone-code step.
   ```bash
   cd backend && python generate_session.py
   ```
   Copy the `SESSION_STRING` that the script shows.

   > ⚠️ **WARNING: The `SESSION_STRING` gives full access to your Telegram account. Keep it safe, as you keep a password.**
2. In the repository, go to *Settings → Secrets and variables → Actions*. Add these **Actions secrets**:
   `API_ID`, `API_HASH`, `PHONE_NUMBER`, `CHANNELS` (the same values as in your `.env`), and `SESSION_STRING`.
3. Go to *Actions → Fetch Links → Run workflow* (web or mobile app). Push *Run workflow* to start the fetch.

The local `update.bat` flow does not change. It does not use `SESSION_STRING`.

> **Note on paths:** all asset and SEO paths are **relative** (no leading `/`) so they resolve on
> the GitHub Pages project subpath, not just at a domain root.

## 🗂️ Project structure

```
SwarnSportsHD/
├── index.html            # Frontend markup + link-card template + hero + footer
├── style.css             # Styling (dark broadcast theme, electric-blue accent)
├── script.js             # Fetch, render, copy, 5-min auto-refresh
├── data.json             # Generated output (scraper writes this)
├── robots.txt            # SEO: allow all + sitemap reference
├── sitemap.xml           # SEO: canonical URL
├── site.webmanifest      # PWA manifest (name, icons, dark theme colors)
├── favicon.ico           # + favicon-16/32, apple-touch-icon, android-chrome icons
├── .github/workflows/
│   └── fetch-links.yml   # Manual GitHub Actions fetch (run from web/mobile)
├── backend/
│   ├── telegram_fetcher.py   # Scraper: fetch, sport-filter, extract, save
│   ├── config.py             # Loads + validates backend/.env
│   ├── get_channel_info.py   # Helper to list channel IDs
│   ├── generate_session.py   # One-time: make a SESSION_STRING for CI
│   └── requirements.txt
├── update.bat            # Windows fetch + publish
└── deploy.sh             # Unix fetch + publish to /docs
```

## 🩺 Troubleshooting

| Message                                          | Fix                                                             |
| ------------------------------------------------ | -------------------------------------------------------------- |
| `Missing required environment variable(s)`       | Ensure all four keys are set in `backend/.env`.                |
| `API_ID must be a valid integer`                 | Use a plain number, no quotes.                                 |
| `CHANNELS must be a comma-separated list...`      | Each ID must be an integer, comma-separated.                   |
| `Malformed JSON in data.json`                     | Re-run the scraper to regenerate the file.                     |
| Channel fetch errors                             | Confirm your account can access the channel and the ID is right. |

## 🔒 Security

- `backend/.env` and `*.session` files hold live credentials and are **git-ignored** — never commit
  them. Only `.env.example` belongs in version control.
- Do not share your `API_HASH`, phone number, or Telethon session file.
- `SESSION_STRING` is a full-access login token — store it **only** as a GitHub Actions secret,
  never in `.env.example`, code, or logs. Regenerate it with `generate_session.py` if exposed.

## 🤝 Contributing

Issues and pull requests are welcome. Please keep the stack as-is — standard-library Python +
Telethon on the backend, vanilla JS on the frontend (no npm, bundlers, or CSS frameworks) — and
keep the `data.json` contract in sync across backend and frontend.

## 🙏 Credits

- Hero photograph by [Zoshua Colah](https://unsplash.com/photos/66X4NgftbrA) via
  [Unsplash](https://unsplash.com/) (Unsplash License).
- Fonts: [Plus Jakarta Sans](https://fonts.google.com/specimen/Plus+Jakarta+Sans),
  [Space Grotesk](https://fonts.google.com/specimen/Space+Grotesk), and
  [Inter](https://fonts.google.com/specimen/Inter) via Google Fonts.

## ⚖️ Disclaimer

SwarnSportsHD does **not** host, own, or claim rights to any streams or content. All links are
aggregated from publicly available third-party sources for convenience only. This project is
intended for personal and educational use. Users are responsible for complying with the terms of
service of Telegram and any linked services, as well as applicable copyright law.

## 📜 License

MIT — see [LICENSE](LICENSE).
