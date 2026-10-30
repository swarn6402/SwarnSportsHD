# Contributing

Thank you for contributing to SwarnSportsHD. Start with [README.md](README.md),
the [architecture](docs/CONTEXT.md), and the [security policy](SECURITY.md).

## Scope changes carefully

- Use a focused branch and pull request for one behavior or a small related set
  of changes. Explain the concrete problem and resulting behavior.
- Preserve vanilla HTML/CSS/JavaScript and the Python/Telethon backend. There is
  no frontend build step or checked-in test suite; a dependency, framework, or
  new test infrastructure should be discussed separately.
- Keep source changes and generated `data.json` updates separate. Normal link
  updates use **Actions → Fetch Links → Run workflow** on `main`.
- Do not commit credentials, session artifacts, environments, caches, local
  settings, temporary audit files, or unrelated generated output.

## Develop without live credentials

Use Python 3.12 to match Actions. A frontend preview needs no backend packages:

```bash
python -m http.server --bind 127.0.0.1 8000
```

Open `http://127.0.0.1:8000/` and stop the server when finished. This server can
serve local dotfiles; keep it on loopback and do not expose a tunnel. For a
public preview, use only the public-file subset listed in
[operations](docs/OPERATIONS.md#local-preview).

Real Telegram calls are opt-in. Do not run login/fetch helpers, publishing
scripts, or the live workflow as a side effect of reviewing a change. Use
isolated fake clients/configuration for offline parser and failure checks.

## Verify the affected behavior

Useful source-only checks from root:

```bash
git diff --check
node --check assets/js/script.js
```

Node is optional developer tooling for the syntax check, not a frontend runtime
dependency or package manager. Python syntax can be checked without importing
the backend or loading `.env`:

```bash
python -c "import ast,pathlib; [ast.parse(p.read_text(encoding='utf-8-sig'), filename=str(p)) for p in pathlib.Path('backend').glob('*.py')]"
```

For shell changes, use `bash -n` on each affected `.sh` file. For frontend changes,
check rendering, copying, empty/error states, responsive layout, reduced motion,
and relative asset paths. Parser changes should cover raw/emoji offsets, hidden
targets, mixed player/join posts, exact signed queries, malformed neighbors,
deduplication, and new player hosts. Do not validate coverage using only blocked
examples: retain representative accepted links too.

Check both sides of URL policy or data-contract changes. Failed acquisition must
not erase previous data; successful empty reads remain valid. No offline check
proves a stream will play or that remote redirects are safe.

## Prepare the pull request

Describe the problem, the change, and verification. Separate completed checks
from skipped browser, Telegram, and deployment checks. For UI changes, include
screenshots only if you actually captured them. State changes to generated data,
workflow permissions, configuration, or deployment paths explicitly.

Review the exact staged paths and diff before an authorized commit. Use focused
commit messages such as `fix(parser): preserve complete Telegram URL targets`
or `docs: clarify the Actions publishing workflow`. Do not use `git add .` or
`git add -A` for a generated-data refresh. Account for newer Actions commits on
`main` before publication; do not solve drift with force pushes or stale JSON.

Report vulnerabilities using [SECURITY.md](SECURITY.md), not by posting account
credentials, private channel content, or exploit details in public issues.
