# Repository scripts

`check.py` provides offline source and site validation using Python's standard
library and Git. Run `python scripts/check.py` from the repository root (or use
the script's full path from another directory). It checks
tracked Python/JSON files, the root data contract, and local HTML/manifest paths
without importing the backend, reading credentials, writing data, or making
network calls. Source Checks runs it in CI; see
[contributing](../CONTRIBUTING.md#verify-the-affected-behavior) for companion
JavaScript and shell syntax checks.

## Optional local scripts

The live site is updated through **GitHub Actions → Fetch Links → Run workflow**.
None of the local/legacy wrappers is called by that workflow. They are retained for manual
use only; do not run them as part of a frontend preview or repository cleanup.

- `local/run_fetcher.bat` and `local/run_fetcher.sh` run the scraper locally and
  write root `data.json`. They do not commit or push.
- `legacy/update.bat` and `legacy/deploy.sh` run the scraper, then commit and
  push only root `data.json`. They refuse to run outside `main` (including a
  detached HEAD) or with existing staged changes, and stop on failures.
  The Unix publisher now targets the root site, replacing
  its obsolete `/docs` copy step.

All four scripts resolve the repository and backend relative to their own
location. Use legacy publishers only on `main`; confirm the current branch
before running one. Optional local authentication continues to use `backend/.env` and
the session in `backend/`. The backend entry points and CI paths are unchanged.

From the repository root, Windows users can run `scripts\local\run_fetcher.bat`;
Unix users can run `bash scripts/local/run_fetcher.sh`. These commands perform
real Telegram network activity and may prompt for login. Use the legacy
publishers only when you explicitly intend to commit and push a link update.

See [the operations runbook](../docs/OPERATIONS.md) for setup, live updates,
verification, and publication checks. Do not use these scripts to test a change.
