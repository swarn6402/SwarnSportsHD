<div align="center">
  <img src="assets/icons/android-chrome-512x512.png" alt="SwarnSports logo" width="112" height="112" />

# SwarnSportsHD

Cricket stream links from Telegram, published through GitHub Actions and served by GitHub Pages.

[![Fetch Links](https://github.com/swarn6402/SwarnSportsHD/actions/workflows/fetch-links.yml/badge.svg?branch=main)](https://github.com/swarn6402/SwarnSportsHD/actions/workflows/fetch-links.yml)
[![Source Checks](https://github.com/swarn6402/SwarnSportsHD/actions/workflows/checks.yml/badge.svg?branch=main)](https://github.com/swarn6402/SwarnSportsHD/actions/workflows/checks.yml)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](backend/requirements.txt)
[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[Live site](https://swarn6402.github.io/SwarnSportsHD/) · [Operations](docs/OPERATIONS.md) · [Architecture](docs/CONTEXT.md) · [Contributing](CONTRIBUTING.md)

</div>

SwarnSports is a static link aggregator. A Python/Telethon process reads configured
Telegram channels and writes root `data.json`; the browser displays that file as
copyable link cards. There is no frontend framework, package manager, build step,
database service, or application server to deploy.

## Automation and publishing

The primary operational workflow is [Fetch Links](.github/workflows/fetch-links.yml).
Run it from **Actions → Fetch Links → Run workflow**, selecting `main`. It can be
started from GitHub on the web or mobile; local batch files are not part of the
normal update process.

The workflow:

1. Checks out the selected branch's latest commit and sets up Python 3.12.
2. Installs `telethon` and `python-dotenv` from `backend/requirements.txt`.
3. Injects repository Actions secrets into the fetch step and requires a
   `SESSION_STRING` for headless authentication.
4. Reads recent channel messages, extracts eligible URLs, and replaces
   `data.json` atomically. If every channel fails, it preserves the previous file.
5. Commits and pushes **only `data.json`**, skipping the commit when unchanged.

Concurrency is limited per branch so fetch jobs do not publish simultaneously.
The workflow is manual: there is no scheduled acquisition. GitHub Pages serves
the repository-root site; publication should be confirmed from its separate
**pages build and deployment** run and the published data timestamp.

[Source Checks](.github/workflows/checks.yml) runs separately on pull requests to
`main` and source pushes to `main`. It checks Python, JavaScript, and shell syntax,
JSON structure, the data contract, and local HTML/manifest asset paths without
Telegram credentials or installing backend packages. Data-only pushes skip it.
These are lightweight static checks, not a behavioral test suite or proof that
streams play. See the [operations guide](docs/OPERATIONS.md) for setup, deployment
verification, failure handling, and release checks.

## Link handling

- Reads up to the latest 100 messages per channel and retains messages from the
  preceding 24 hours, using UTC timestamps.
- Uses raw message text, UTF-16 entity offsets, and hidden hyperlink targets;
  formatting entities cannot produce partial URLs.
- Excludes configured Telegram, WhatsApp, Discord, and common-shortener
  destinations by hostname. A mixed post can retain its player URLs while its
  join links are discarded.
- Accepts new player domains, extensionless pages, and signed query strings.
  There is no stream-domain allowlist or media-file-extension requirement.
- Deduplicates URLs across channels. The sport heuristic excludes posts matching
  football keywords only when no cricket or F1 keyword is present; ambiguous
  posts remain eligible. Channel names do not decide the sport.
- Handles individual channel failures without discarding results from other
  readable channels. A successful read with no matching links may publish an
  empty list.

Filtering does not establish that a destination plays video or that its redirects
are safe. Unknown promo sites cannot reliably be recognized from their URLs alone.
Read the [security policy](SECURITY.md) before configuring sources or sharing data.

## Frontend

The site uses vanilla HTML, CSS, and JavaScript, with a responsive dark theme,
copy-to-clipboard controls, empty/error states, and relative asset paths for the
GitHub Pages project subpath. Metadata, a web manifest, and icon assets are
included. There is no service worker or offline-caching guarantee.

The browser requests `data.json` on load and every five minutes. **Polling does
not run Telegram acquisition or remove stale records**: freshness depends on the
last successful manual fetch. Google Fonts and the hero photograph are external
runtime resources; the photograph has a solid-color fallback.

## Visitor statistics

Cloudflare Web Analytics is embedded once in `index.html` for free traffic and
page-performance statistics. Sign in to [Cloudflare Web Analytics](https://dash.cloudflare.com/?to=/:account/web-analytics)
and select `swarn6402.github.io` to view visits and page views. Counts start
after installation; visits are not an exact count of unique people. Browser
blocking and disabled JavaScript can reduce recorded traffic.

The snippet's site token is intentionally public; account credentials and API
keys do not belong in Git. Hosting and DNS remain on GitHub Pages. See the
[analytics runbook](docs/OPERATIONS.md#visitor-analytics) for verification and
removal, and [SECURITY.md](SECURITY.md#visitor-analytics) for data boundaries.

## Preview locally

Python 3.12 matches the Actions runtime. A frontend preview needs no Telegram
credentials or installed backend packages.

```bash
git clone https://github.com/swarn6402/SwarnSportsHD.git
cd SwarnSportsHD
python -m http.server --bind 127.0.0.1 8000
```

Open `http://127.0.0.1:8000/`. Use HTTP rather than `file://` so the JSON request
works. Stop the server after previewing. Serving the repository also makes local
files reachable to local clients; do not bind it to other interfaces or expose
it through a tunnel. For a public preview, use a copy containing public assets
only, as described in [operations](docs/OPERATIONS.md#local-preview).

## Optional local backend setup

For maintainers who explicitly need local Telegram access:

```bash
python -m pip install -r backend/requirements.txt
cp .env.example backend/.env
```

In PowerShell, use `Copy-Item .env.example backend/.env` for the copy step. Fill
in `API_ID`, `API_HASH`, `PHONE_NUMBER`, and comma-separated `CHANNELS`. The root
template is canonical; `backend/.env.example` is a retained compatibility
template. Neither contains a session token.

Run local helpers **from `backend/`** so they share the existing on-disk session:

```bash
cd backend
python telegram_fetcher.py
```

The first run may request a Telegram code and 2FA password. These are real account
and network operations, not verification commands. Normal site updates should
continue to use Actions. [Configuration and session setup](docs/OPERATIONS.md#configuration)
documents the full process, including GitHub's five required secrets.

## Repository layout

```text
SwarnSportsHD/
├── index.html / data.json          # Pages entry point and generated live output
├── assets/
│   ├── css/style.css
│   ├── js/script.js
│   └── icons/
├── backend/                       # Fetcher, configuration, login helpers
├── .github/
│   ├── workflows/                 # Manual Fetch Links and offline Source Checks
│   └── pull_request_template.md
├── scripts/
│   ├── check.py                   # Offline source and site checks
│   ├── local/                     # Optional fetch-only wrappers
│   └── legacy/                    # Unused manual publishers
├── docs/
│   ├── CONTEXT.md                 # Architecture and data contract
│   ├── OPERATIONS.md              # Setup, verification, publishing, recovery
│   └── archive/                   # Retained historical secondary JSON
├── AGENTS.md / CLAUDE.md           # Agent instructions
├── CONTRIBUTING.md / SECURITY.md
└── README.md / LICENSE
```

Root `favicon.ico`, `robots.txt`, `sitemap.xml`, and `site.webmanifest` are retained
at their conventional public paths. The historical JSON in `docs/archive/` is
not an input to the live site. `data.json` is generated; do not hand-edit it or
mix link refreshes into source changes.

## Contributing and security

Read [CONTRIBUTING.md](CONTRIBUTING.md) for focused changes and verification, and
[SECURITY.md](SECURITY.md) for credential handling, public-data boundaries,
vulnerability reporting, and historical exposure requiring account-owner review.
Real `.env` files, Telegram sessions and sidecars, virtual environments, caches,
and local settings do not belong in commits.

## Credits and license

Hero photograph: [Zoshua Colah via Unsplash](https://unsplash.com/photos/66X4NgftbrA).
Fonts: Plus Jakarta Sans, Space Grotesk, and Inter via Google Fonts.
Code is licensed under [MIT](LICENSE); third-party media retains its own terms.

SwarnSportsHD does not host or own the linked streams. Source configuration and
use of third-party content must respect applicable rights and service terms.
The software license does not grant rights to third-party streams or messages.
