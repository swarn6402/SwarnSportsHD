# SwarnSportsHD

Telegram-based cricket stream link scraper with a static GitHub Pages frontend.

## Overview

SwarnSportsHD fetches recent messages from configured Telegram channels, extracts valid `http/https` links, and writes structured output to `data.json`.
The frontend reads that JSON and displays links with source and timestamp metadata.

## Key Features

- Scrapes links from multiple Telegram channels/supergroups
- Filters messages to the last 24 hours
- Extracts URLs from Telegram entities and message text
- Validates and deduplicates links, with blacklist filtering
- Writes normalized output to `data.json` at repository root
- Simple static frontend (`index.html`, `script.js`, `style.css`)
- Windows helper script (`update.bat`) for fetch + commit + push

## Requirements

- Python 3.8+
- Telegram account
- Telegram API credentials (`API_ID`, `API_HASH`, `PHONE_NUMBER`)
- Git (for deployment workflow)
- Python packages:
  - `telethon`
  - `python-dotenv`

## Setup

1. Clone the repository:

```bash
git clone https://github.com/swarn6402/SwarnSportsHD.git
cd SwarnSportsHD
```

2. Install dependencies:

```bash
pip install -r backend/requirements.txt
```

3. Configure environment variables:

```bash
copy .env.example backend\.env
```

Edit `backend/.env`:

```env
API_ID=12345678
API_HASH=your_api_hash
PHONE_NUMBER=+1234567890
CHANNELS=-1001111111111,-1002222222222
```

## Usage

Run scraper manually:

```bash
python backend/telegram_fetcher.py
```

Windows update workflow (fetch + git add/commit/push):

```bat
update.bat
```

Optional Linux/macOS deploy script:

```bash
./deploy.sh
```

## Adding New Channels

1. Get channel/chat IDs (optional helper):

```bash
python backend/get_channel_info.py
```

2. Add IDs to `CHANNELS` in `backend/.env` as comma-separated integers:

```env
CHANNELS=-1001111111111,-1002222222222,-1003333333333
```

3. Re-run scraper:

```bash
python backend/telegram_fetcher.py
```

## GitHub Pages Deployment

This project can be served as a static site on GitHub Pages.

### Option A: Serve from repository root

- Ensure `index.html`, `style.css`, `script.js`, and `data.json` are in root.
- GitHub: `Settings -> Pages -> Deploy from a branch -> main / (root)`.

### Option B: Serve from `/docs` (via `deploy.sh`)

- `deploy.sh` copies `frontend/*` to `docs/`.
- GitHub: `Settings -> Pages -> Deploy from a branch -> main /docs`.

## Troubleshooting

- `Missing required environment variable(s)`
  - Check `backend/.env` includes `API_ID`, `API_HASH`, `PHONE_NUMBER`, `CHANNELS`.

- `API_ID must be a valid integer`
  - Use numeric value only (no quotes).

- `CHANNELS must be a comma-separated list of integers`
  - Ensure each ID is an integer and comma-separated.

- `Malformed JSON in data.json`
  - Re-run scraper to regenerate:
  ```bash
  python backend/telegram_fetcher.py
  ```

- Channel fetch errors
  - Confirm your Telegram account has access to those channels and IDs are correct.

## Security and Privacy Note

- Keep `backend/.env` private and never commit real credentials.
- Do not expose `API_HASH` or phone number in public repositories.
- Session files (for Telethon login) are local authentication artifacts and should not be shared.

## License

This project is licensed under the MIT License — see the LICENSE file for details.
