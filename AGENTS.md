# AGENTS.md

Repository instructions for coding agents working on SwarnSportsHD. Use this file
as the operating guide, [docs/CONTEXT.md](docs/CONTEXT.md) for architecture, and
[docs/OPERATIONS.md](docs/OPERATIONS.md) for setup and publishing.

## Project and operational boundaries

- Python/Telethon in `backend/` writes root `data.json`. Root `index.html`,
  `assets/js/script.js`, and `assets/css/style.css` form the static frontend.
- The live update path is **GitHub Actions → Fetch Links → Run workflow** on
  `main`. The local scripts are optional, unused in normal production updates.
- GitHub Pages uses the repository-root layout. Keep `index.html`, `data.json`,
  backend entry points, and `.github/workflows/fetch-links.yml` at their paths.
  `docs/` contains documentation, not the Pages deployment root.
- No frontend build, framework, package manager, or checked-in test suite.
  Do not introduce one unless explicitly requested. Python 3.12 is the Actions
  runtime. Backend dependencies remain `telethon` and `python-dotenv`.

## Credentials and live operations

- Never print, stage, commit, or paste real `.env` contents, session files,
  session sidecars, login codes, 2FA passwords, or `SESSION_STRING` values.
  Only placeholder `.env.example` templates belong in Git.
- `SESSION_STRING` grants Telegram account access and belongs in GitHub Actions
  secrets. See [SECURITY.md](SECURITY.md), including historical exposure.
- Do not execute `telegram_fetcher.py`, `get_channel_info.py`,
  `generate_session.py`, or their wrappers without explicit authorization for
  live Telegram operations. A review or documentation task is not that approval.
- Do not dispatch Actions, modify repository settings, commit, or push without
  the user's authorization. Do not run publishing scripts for verification.
- Preserve ignored local credentials and sessions. Read source and use isolated
  offline checks with fake configuration/clients instead of importing live
  configuration during parser verification.

## Generated data and parsing

- `data.json` is generated output. Do not hand-author records, alter it for a
  UI feature, or replace it with `docs/archive/frontend-data.json`.
- Its contract is `{timestamp, links}`; records contain `url`,
  `source_channel_id`, `source_channel_name`, `message_text`, and `posted_time`.
  Keep producer and consumer synchronized for any contract change.
- Use raw message text and UTF-16 units for Telegram URL entities. Only URL and
  hidden-link entities identify targets; formatting entities are not links.
  Text covered by a real link entity must not be extracted again as a different
  target. Preserve exact player paths and signed queries.
- Match blocked join/contact destinations by hostname and subdomain, not by
  arbitrary words in a player's query. Keep backend `URL_BLACKLIST` and frontend
  `blockedLinkHosts` synchronized. Do not add a fixed stream-domain allowlist,
  media-extension rule, or positive cricket-keyword requirement.
- Preserve the conservative sport gate: drop a football-keyword post only when
  no cricket/F1 keyword is present. Do not classify by source-channel name.
- Isolate channel failures. All-channel read failure must preserve previous
  data; a successful empty read may publish an empty list. Preserve atomic
  JSON replacement and client cleanup.

## Implementation conventions

- Keep changes small, dependency-free where practical, and consistent with
  vanilla JavaScript and the existing Python style. Do not reformat unrelated
  code. New dependencies require a clear justification.
- Use timezone-aware UTC for backend cutoffs and timestamps. Render untrusted
  message strings with `textContent`, and validate URL schemes before linking.
- Preserve the dark theme, electric-blue accent, responsive layout, hero-image
  solid fallback, touch behavior, and accessibility. New animation must respect
  reduced-motion preferences, including JavaScript animations.
- Asset paths must be relative to support `/SwarnSportsHD/`. Keep title,
  description, Open Graph, and Twitter metadata synchronized.
- Respect `.gitattributes`: LF for source/docs/shell files, CRLF for batch files.

## Verification and release discipline

- Preview the frontend with
  `python -m http.server --bind 127.0.0.1 8000` from root. Do not use `file://`,
  bind a credential-containing checkout to other interfaces, or expose a tunnel.
- Exercise cards, copying, empty/error states, responsive layout, and asset/data
  paths. State explicitly when a browser or live backend check was unavailable.
- Use syntax checks and isolated offline cases appropriate to the change.
  Existing acquisition automation is not an automated test pipeline.
- Follow [CONTRIBUTING.md](CONTRIBUTING.md) and the publication checklist in
  [docs/OPERATIONS.md](docs/OPERATIONS.md). Stage exact reviewed paths only;
  never use broad staging for generated link updates. Keep source changes and
  generated data refreshes separate.
- Before an authorized publication, account for Actions commits that may have
  advanced `main`. Never force-push or overwrite newer generated data to resolve
  that drift. Report failures before attempting dependent publication steps.
- End with the changes, verification performed, remaining findings, and whether
  anything was committed or published. Do not claim playback, coverage, test
  automation, credential rotation, or deployment success without evidence.
