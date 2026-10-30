# Operations and publication

This is the maintainer runbook for SwarnSportsHD. The live update path is GitHub
Actions; local scripts are retained for optional use. See
[architecture](CONTEXT.md), [contributing](../CONTRIBUTING.md), and
[security](../SECURITY.md) for the corresponding boundaries.

## Configuration

The workflow uses repository **Actions secrets**:

- `API_ID`: integer Telegram API ID.
- `API_HASH`: the API hash paired with that ID.
- `PHONE_NUMBER`: Telegram account phone number, including country code.
- `CHANNELS`: comma-separated numeric channel/chat IDs accessible to the account.
- `SESSION_STRING`: full-access Telethon login credential for headless execution.

`backend/config.py` validates the first four values. Existing process environment
variables take precedence over values loaded from `backend/.env`. The workflow
requires `SESSION_STRING` before starting the backend; it must not prompt for
interactive login on a runner. Never print a secret to diagnose configuration.

For optional local use, copy root `.env.example` to `backend/.env` and fill it in.
Root `.env` is not loaded by the backend. `backend/.env.example` is retained as a
compatible placeholder template; keep its required keys aligned with the root
template. Leave `SESSION_STRING` unset for normal local file-session use.

### One-time session setup

Only the account owner or an explicitly authorized operator should perform this
real Telegram login. After installing `backend/requirements.txt`, run locally:

```bash
cd backend
python generate_session.py
```

Enter Telegram's login code and any 2FA password. Copy the resulting session into
the repository's `SESSION_STRING` Actions secret, then close the terminal view
containing it. Do not capture it in screenshots, logs, issue reports, templates,
or commits. This helper deliberately prints a credential; never run it in CI.
Follow [SECURITY.md](../SECURITY.md) if any session has been exposed.

### Optional local helpers

From `backend/`, use `python get_channel_info.py` to discover dialogs and
`python telegram_fetcher.py` for an explicitly authorized fetch. File-session
paths are currently relative to the process working directory: running helpers
from `backend/` reuses `backend/swarnsports_session.session`. Running the fetcher
from root can instead create a different root session and prompt for login.

The wrappers in [scripts/](../scripts/README.md) change to `backend/` themselves.
They are not invoked by Actions. Legacy publishers commit and push; they reject
branches other than `main`, detached HEADs, and existing staged changes before
fetching. Use them only when deliberately publishing.

## Update the live links

1. Open **Actions → Fetch Links → Run workflow** and select `main`.
2. Watch checkout, dependency installation, fetch, and commit/push complete.
3. Confirm that a data commit exists when the output changed. An unchanged file
   legitimately produces no commit.
4. Check the separate **pages build and deployment** run for that revision.
5. Read the [published data](https://swarn6402.github.io/SwarnSportsHD/data.json)
   and confirm its timestamp/content match the intended update. Then inspect
   the [site](https://swarn6402.github.io/SwarnSportsHD/).

The Fetch Links badge reports the acquisition workflow's status. It does not
prove Pages deployed the resulting commit, the data is fresh, or a link plays.
Browser polling every five minutes reads already-published JSON; it does not
trigger Telegram or expire old rows locally.

### Workflow behavior

- Trigger: manual `workflow_dispatch`; no schedule or pull-request execution.
- Runner: `ubuntu-latest`, Python 3.12. Requirements currently resolve from the
  two unpinned entries in `backend/requirements.txt`; this is not a lockfile.
- Checkout: latest commit on the selected branch. Use `main` for the live site.
- Permissions: `contents: write` for the data commit; secrets are scoped to the
  fetch step. Only `data.json` is staged.
- Concurrency: one running fetch per branch, without cancelling that running
  fetch. GitHub may replace an older pending run when another is requested;
  this is not a FIFO queue of every button press.
- No repository test pipeline is configured. Offline checks described in
  [CONTRIBUTING.md](../CONTRIBUTING.md) are maintainer verification.

GitHub Pages publication is separate from the fetch job. Do not change the
existing source settings during a source cleanup. GitHub documents that commits
pushed with `GITHUB_TOKEN` do not themselves trigger a branch Pages build; do not
assume that a successful `git push` proves deployment in every setup. This
repository has observed successful Fetch Links and Pages runs, but a release
must still verify the deployment revision. If the stages stop lining up,
investigate the configured Pages integration before changing tokens or workflows.
See GitHub's [publishing-source documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
and [concurrency behavior](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency).

## Failure handling

- Missing/invalid configuration or session: the job fails before publication.
  Correct the named secret in GitHub; never paste its value into an issue.
- Individual unreadable channel: other readable channels can still contribute.
  A partial run may contain fewer links; it does not promise full channel coverage.
- Every channel fails to be read/resolved: the fetcher raises, leaving the
  previous `data.json` in place and preventing the commit step.
- Successful reads with no matching URLs: an empty list is valid and may clear
  expired streams. Do not treat every empty result as an authentication failure.
- JSON serialization, flush, or replacement failure: the previous file survives;
  same-directory temporary output is cleaned up and ignored by Git.
- Push conflict/rejection: review remote changes and rerun from the current
  branch revision when appropriate. Never force-push over a newer data update.
- Fetch succeeds but site is old: check Pages status and revision first, then
  compare the repository and published JSON. Do not overwrite current data with
  the historical archive or regenerate it by hand.

## Local preview

From repository root:

```bash
python -m http.server --bind 127.0.0.1 8000
```

Open `http://127.0.0.1:8000/`, use HTTP rather than `file://`, and stop the server
when finished. The server serves dotfiles too: loopback restricts network
exposure but does not make private files inaccessible to local processes.
Do not bind a credential-containing checkout to another interface or tunnel it.

For a shared/public preview, first copy **only** these public files into a
temporary directory: `index.html`, `assets/`, `data.json`, `favicon.ico`,
`site.webmanifest`, `robots.txt`, and `sitemap.xml`. Do not copy `backend/`,
`.git/`, `.env` files, sessions, or machine settings. Serve that subset. Also
check asset/data paths under a `/SwarnSportsHD/` URL prefix before publishing.

## Source publication checklist

1. Finish review and verification. Resolve or explicitly accept remaining
   findings; do not equate an audit with certification of remote streams.
2. Check `git status` and read the staged paths. Include only source, necessary
   documentation/configuration, public assets, and intended workflow changes.
   Temporary audit scripts/reports, caches, secrets, and generated data churn
   are not source-release content.
3. Account for Actions updates that may have advanced `main`. Preserve newer
   generated JSON; never restore an older local snapshot merely to simplify a
   source merge. Do not discard or stash unrelated local work without approval.
4. Form focused commits with descriptive messages. Asset moves and their path
   references must land together. Policy producer/consumer changes must remain
   in sync. Keep each intermediate revision usable.
5. Commit and push only when authorized, using exact staged paths. No force
   pushes, broad `git add`, or unreviewed history cleanup.
6. Verify the Pages deployment revision, public assets, JSON timestamp, and UI.
   Run a live Telegram acquisition only with the corresponding authorization.

For a source regression, prepare a reviewed revert of the relevant source commit
while retaining the current generated data. For an acquisition issue, correct
the configuration/parser and perform an authorized refresh. The archived JSON
is not a rollback source for live streams.
