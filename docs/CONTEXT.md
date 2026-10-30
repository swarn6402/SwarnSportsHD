# Architecture and data contract

SwarnSportsHD has two runtime components: an acquisition process in `backend/`
and a static site at the repository root. Start with [README.md](../README.md)
for the public overview and [OPERATIONS.md](OPERATIONS.md) for commands and
publication procedures. [AGENTS.md](../AGENTS.md) contains the coding rules.

## Data flow

The manual Fetch Links workflow reads Telegram through Telethon, writes
`data.json`, and commits that generated file. GitHub Pages serves `index.html`
and the public assets; `assets/js/script.js` fetches the published JSON and
renders cards. There is no frontend build or backend application server.

The browser reads JSON on load and every five minutes. Acquisition runs only
when manually requested. The browser does not fetch Telegram or locally remove
rows when their source messages become older than 24 hours. A stale published
snapshot remains until an update is successfully acquired and deployed.

## Backend

### Configuration

`backend/config.py` loads `backend/.env` relative to its own file using
`python-dotenv`, independently of the process working directory. Existing
environment variables take precedence over the file. Required values are
`API_ID`, `API_HASH`, `PHONE_NUMBER`, and `CHANNELS`.

Validation checks presence, parses the API ID as an integer, and parses a
nonempty comma-separated list of channel IDs as integers. It does not establish
that credentials are valid, a phone is authorized, or a channel is accessible.
Startup diagnostics show the configuration path/existence and success status;
they must never show credential values.

### Authentication and sessions

`authenticate()` uses `StringSession(SESSION_STRING)` when that environment value
is present. Otherwise it uses the on-disk session name `swarnsports_session`.
The latter is relative to the **process working directory**, so optional local
helpers should run from `backend/` or through the wrappers that enter it.
Actions already runs the fetch step inside `backend/` and requires its session
secret before starting Python.

`backend/generate_session.py` performs a one-time interactive login and prints a
reusable session credential for the operator to store in Actions secrets. It is
never part of the ordinary fetch job. `backend/get_channel_info.py` lists
accessible broadcast/supergroup dialogs and their entity IDs. Both are live
account operations and require explicit authorization.

### Channel resolution and collection

`_normalize_channel_id_for_peer()` strips the `-100` channel prefix where
applicable. `_resolve_channel_entity()` uses `PeerChannel` for negative channel
IDs and direct lookup for non-negative values.

`fetch_recent_messages()` reads at most 100 messages per configured channel and
keeps messages dated within the preceding 24 hours. Cutoffs use timezone-aware
UTC. This is a bounded recent-message window, not exhaustive channel history.
Known read errors are logged and re-raised rather than returned as empty data.

`get_all_cricket_links()` resolves source titles, applies the sport heuristic,
and deduplicates extracted URLs across messages/channels. Each unreadable
channel is isolated so others can contribute. If no channel can be read and
resolved, the function raises before saving. Successful reads with no eligible
URLs can legitimately produce an empty list. Collection disconnects its client
in `finally`.

The sport heuristic is conservative: `_is_football_message()` returns true only
when a football keyword is present and no configured cricket/F1 keyword is
present. Unknown and mixed posts remain eligible. The source channel's name is
not used for classification. This is a keyword heuristic, not a semantic or
exhaustive guarantee that every result is a live cricket stream.

### URL extraction and filtering

`extract_links_from_message()` follows these steps:

1. `_message_text()` reads unformatted message text. Telegram entity offsets
   refer to raw text and count UTF-16 units, including surrogate pairs for emoji.
2. `MessageEntityTextUrl` supplies its hidden destination. `MessageEntityUrl`
   supplies a bounded raw-text slice in UTF-16 units. Formatting entities such
   as bold, italic, and code never define URL boundaries.
3. Text already covered by an actual link entity is not extracted again. The
   visible text of a hidden link is not an additional destination. Explicit
   entity targets keep their exact paths and query strings.
4. A case-insensitive HTTP(S) regex handles text not covered by link entities.
   `_clean_text_url()` removes prose/Markdown punctuation while preserving
   balanced brackets. Bare-domain URL entities receive an HTTPS prefix,
   including hosts with explicit ports.
5. `_normalize_stream_url()` validates the scheme, hostname, and port. It rejects
   malformed targets, embedded whitespace/backslashes, and credential-bearing
   URL authorities. A malformed candidate does not discard valid neighbors.
6. `URL_BLACKLIST` matches exact destination domains and their subdomains,
   case-insensitively. It covers configured Telegram, WhatsApp, Discord, and
   common-shortener destinations, without scanning arbitrary words in a
   player's path/query. Accepted URLs are deduplicated in order.

There is no stream-host allowlist, media-extension requirement, or positive
cricket-keyword requirement for every post. New player pages remain eligible.
Filtering does not open destinations, validate playback, or follow redirects.
Keep the frontend `blockedLinkHosts` list synchronized with the backend policy.

This handling follows [Telegram's entity specification](https://core.telegram.org/api/entities)
and [Telethon's raw-text model](https://docs.telethon.dev/en/stable/quick-references/objects-reference.html).
It avoids the prior bug where slicing formatted text for non-URL entities could
create a truncated URL alongside the complete player link.

### Output and failure behavior

`save_to_json()` writes **root `data.json`**, resolved relative to the backend
file rather than the current directory. It serializes UTF-8 JSON with two-space
indentation into a same-directory temporary file, flushes/syncs it, and calls
`os.replace`. A serialization/write/replacement failure leaves the prior file
intact. Temporary files are cleaned up and ignored by Git.

`main()` performs collection before saving, so all-channel acquisition failure
does not publish a successful-looking empty snapshot. Individual-channel
failure may still reduce coverage in an otherwise successful result.

## Data contract

Root `data.json` is the sole interface between producer and consumer. Example
values below are illustrative, not live records:

```json
{
  "timestamp": "2026-01-01T12:00:00+00:00",
  "links": [
    {
      "url": "https://player.example/watch?id=match&lang=en",
      "source_channel_id": -1001111111111,
      "source_channel_name": "Example channel",
      "message_text": "Raw source message text",
      "posted_time": "2026-01-01T11:45:00+00:00"
    }
  ]
}
```

`timestamp` is the UTC completion time as an ISO-8601 string. `links` is a list;
each record has an HTTP(S) `url`, numeric `source_channel_id`, source name, raw
message text, and an ISO-8601 `posted_time` or `null`. Contract changes require
updates to both `telegram_fetcher.py` and `assets/js/script.js`.

The full JSON is public, including raw message text and source metadata even
when the UI shows only a shortened preview. Configure only sources whose
content is intended for publication. `docs/archive/frontend-data.json` preserves
the old secondary snapshot; it is not a live input or rollback source.

## Frontend

`index.html` defines the hero, loading/empty states, links container,
`#link-card-template`, and footer. `assets/js/script.js` uses:

- `loadLinks()`: fetch JSON with `cache: "no-store"`; distinguish HTTP and JSON
  failures, show an error state, and update the displayed timestamp.
- `displayLinks()`: exclude invalid rows and disallowed URL destinations,
  sort by `posted_time` descending, and render cards or the empty state.
- `createLinkCard()`: clone the template, insert strings with `textContent`,
  show channel/time metadata and a 100-character message preview, and attach
  the Copy handler.
- Clipboard helpers: use the Clipboard API, fall back to a temporary textarea
  plus `execCommand("copy")`, and provide button/toast feedback.
- Timestamp helpers: display local human-readable dates with `en-GB` formatting.
- A five-minute interval after `DOMContentLoaded` to refresh the published data.

`assets/css/style.css` supplies the dark theme with one electric-blue accent.
Plus Jakarta Sans 800 is used for the hero, Space Grotesk for headings, and
Inter for body text. Google Fonts uses `display=swap`. The Unsplash hero is
limited to the header, with a dark overlay and solid-color fallback.

The CSS grid uses one column below 768px, two from 768px, and three from 1024px.
Hover effects are separated from touch states. CSS animation/transition rules
include reduced-motion overrides. The JavaScript loading skeleton reads
`prefers-reduced-motion` before starting its animations and keeps the static
loading bars when reduction is requested. Toast colors are inline in the script
and should stay aligned with the CSS accent.

## Public assets and metadata

Root `favicon.ico`, `robots.txt`, `sitemap.xml`, and `site.webmanifest` retain
their public paths; PNG icons live under `assets/icons/`. HTML/manifest asset
references are relative for the `/SwarnSportsHD/` project subpath. Canonical,
Open Graph URL, and sitemap URLs are intentionally absolute.

Keep `<title>`, description, Open Graph, and Twitter wording synchronized.
The manifest supplies names, colors, and icon references. There is no service
worker, offline cache, or custom frontend build. Fonts, the hero photograph, and
the Cloudflare Web Analytics beacon are intentional external runtime resources.
The beacon is a separate async module script after the application script; stream
loading does not depend on analytics. Its site token is public and does not
grant dashboard access. See [visitor analytics](OPERATIONS.md#visitor-analytics).

## Automation and maintenance

`.github/workflows/fetch-links.yml` is manual acquisition/publication automation
with Python 3.12, per-branch concurrency, secret-backed headless authentication,
and data-only commits. GitHub Pages deployment is a separate stage that must be
verified for the produced revision. `.github/workflows/checks.yml` separately
runs offline syntax, JSON/data-contract, and local HTML/manifest reference checks
on pull requests and source pushes to `main`. It has read-only permissions and
does not use Telegram credentials or install backend packages. It is static
validation, not a behavioral test suite. [OPERATIONS.md](OPERATIONS.md) describes
setup, source publication, failure recovery, and deployment checks.

The local wrappers and unused manual publishers live under `scripts/`; see
[their guide](../scripts/README.md). Keep generated refreshes separate from
source changes, preserve newer Actions commits, and keep secrets/session
artifacts out of staging. Runtime dependencies remain only `telethon` and
`python-dotenv`. [CONTRIBUTING.md](../CONTRIBUTING.md) covers scoped verification,
and [SECURITY.md](../SECURITY.md) covers public data and credential exposure.
