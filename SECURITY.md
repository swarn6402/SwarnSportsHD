# Security policy

## Reporting a vulnerability

Do not publish credentials, private message content, session artifacts, or
exploit details in public issues or pull requests. If the repository offers
GitHub private vulnerability reporting, use **Security → Advisories → Report a
vulnerability**. If that option is unavailable, open an issue containing only
a request for a private reporting channel; do not include the sensitive details.

The maintained code is on `main`; there is no supported-version matrix or
guaranteed response-time policy. This project aggregates third-party links and
does not certify their content, playback, or redirect safety.

## Credentials and public data

The live fetch runs in GitHub Actions. Keep `API_ID`, `API_HASH`, `PHONE_NUMBER`,
`CHANNELS`, and `SESSION_STRING` in repository Actions secrets. The workflow
injects them into the fetch step and stages only root `data.json`.

For optional local runs, use `backend/.env`. Both committed `.env.example`
templates contain placeholders only. Never put a session string in a template.

`.gitignore` excludes `.env` variants, Telethon `*.session` files and
`*.session-*` sidecars, virtual environments, caches, and local editor/agent
settings. Ignore rules do not protect files already tracked or erase history.
Do not force-add ignored files. Before any future commit, review the exact
staged paths and diff; do not use broad staging for generated link updates.

## Historical exposure found during the reorganization

The history audit on 2026-10-30 found values in root `.env.example` matching
local `API_HASH` and `PHONE_NUMBER`, and a previously committed
`backend/swarnsports_session.session-journal`. These must be treated as exposed.
The current template has been sanitized and session sidecars are now ignored.
Existing private local files were not moved or changed.

Credential rotation and session revocation were not verified by the repository
audit. If they have not already been completed, the account owner should: revoke potentially exposed Telegram
sessions, generate a fresh CI session, and update the Actions secrets. Replace
exposed API credentials where the provider permits; a published phone number
cannot be made private by changing an ignore rule. History cleanup, if desired,
requires a separate coordinated change and cannot invalidate copies already
downloaded. No history rewrite or account changes were performed here.

## What the website publishes

Root `data.json` is intentionally public and contains stream URLs, source
channel IDs/names, message text, and posting times. The frontend shows only a
short message preview, but the full JSON is downloadable. Include only source
content you intend to publish. The retained historical JSON in `docs/archive/`
is also part of the public repository. Reorganization does not change this
data contract or remove published message content.

## Link filtering boundaries

The parser and frontend reject known Telegram/WhatsApp/Discord destinations,
the configured common shorteners, malformed HTTP(S) URLs, and URL authorities
containing credentials. Matching uses the destination hostname and its
subdomains, not arbitrary text in a player's path or query. Keep backend
`URL_BLACKLIST` and frontend `blockedLinkHosts` in sync.

New player domains, root pages, signed queries, and extensionless stream links
remain eligible. The parser does not open destinations, follow redirects, or
claim that a syntactically eligible link is a working stream. Unknown promo
sites cannot reliably be identified from their URL alone; add narrow exclusions
only when supported by observed examples. Do not reject an entire mixed post
just because it also contains a join link.

Successful empty reads may clear expired streams. Failed reads from every
channel stop publication instead. Data replacement is atomic, and Actions
serializes fetch runs per branch to reduce conflicting updates.

For a local preview, serve only the public files with a suitable restricted
server or use a temporary copy containing `index.html`, `assets/`, `data.json`,
the root icons/manifest and SEO files. Do not expose a development server
containing local credentials to other devices.
