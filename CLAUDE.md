# CLAUDE.md

Claude Code entry point for SwarnSportsHD. Follow [AGENTS.md](AGENTS.md), the
canonical repository instructions; do not maintain a competing copy here.

## Start here

- [README.md](README.md): public project overview and automation.
- [docs/CONTEXT.md](docs/CONTEXT.md): implementation and data contract.
- [docs/OPERATIONS.md](docs/OPERATIONS.md): configuration, Actions, verification,
  and release/recovery procedures.
- [CONTRIBUTING.md](CONTRIBUTING.md): change scope and review expectations.
- [SECURITY.md](SECURITY.md): credentials, public data, and reporting.

## Essential constraints

- Normal live updates use the manual **Fetch Links** GitHub Actions workflow,
  not local batch files. Python 3.12 runs in Actions; there is no frontend build
  or checked-in automated test suite.
- Never print, stage, or commit real `.env` values, Telegram sessions or their
  sidecars, login codes, or `SESSION_STRING`.
- Do not run Telegram helpers, dispatch Actions, commit, or push without the
  corresponding user authorization. Reviews use source and offline checks.
- Root `data.json` is generated. Preserve the backend/frontend contract and
  keep generated refreshes out of unrelated source commits.
- Preserve conservative stream coverage, raw-text/UTF-16 URL parsing,
  destination-host filtering, atomic writes, and all-channel failure handling.
- Keep the current vanilla frontend and two backend dependencies. Avoid broad
  refactoring, new build tooling, and unrequested test infrastructure.
- For a local preview, serve root with
  `python -m http.server --bind 127.0.0.1 8000`; never expose a credential-bearing
  checkout to other interfaces or tunnels. Local Telegram helpers should run
  from `backend/` to reuse the existing file session.
- Report actual verification and remaining risks; do not label offline checks
  as real-browser tests or playback/deployment verification.
