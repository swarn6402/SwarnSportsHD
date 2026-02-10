import os

from dotenv import load_dotenv

# Load environment variables from a local .env file (if present).
load_dotenv()

# API_ID: Telegram API ID from https://my.telegram.org (must be an integer).
_api_id_raw = os.getenv("API_ID")
# API_HASH: Telegram API hash paired with API_ID.
API_HASH = os.getenv("API_HASH")
# PHONE_NUMBER: Phone number for Telegram authentication (E.164 format recommended).
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
# CHANNELS: Comma-separated Telegram channel/chat IDs to scrape for links.
_channels_raw = os.getenv("CHANNELS")

missing_vars = []
if not _api_id_raw:
    missing_vars.append("API_ID")
if not API_HASH:
    missing_vars.append("API_HASH")
if not PHONE_NUMBER:
    missing_vars.append("PHONE_NUMBER")
if _channels_raw is None:
    missing_vars.append("CHANNELS")

if missing_vars:
    raise ValueError(f"Missing required environment variable(s): {', '.join(missing_vars)}")

try:
    API_ID = int(_api_id_raw)
except (TypeError, ValueError) as exc:
    raise ValueError("API_ID must be a valid integer.") from exc

try:
    CHANNELS = [int(channel.strip()) for channel in _channels_raw.split(",") if channel.strip()]
except ValueError as exc:
    raise ValueError("CHANNELS must be a comma-separated list of integers.") from exc

if not CHANNELS:
    raise ValueError("CHANNELS is empty. Provide at least one channel ID.")

print("Configuration loaded successfully.")
