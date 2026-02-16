"""Telegram fetcher for cricket streaming links."""

import asyncio
import datetime
import json
import os
import re

from telethon import TelegramClient
from telethon.errors import ChannelPrivateError
from telethon.tl.types import PeerChannel

import config

# Blacklist patterns for unwanted links
URL_BLACKLIST = [
    "t.me/+",           # Telegram invite links
    "t.me/joinchat",    # Old style Telegram invites
]


async def authenticate() -> TelegramClient:
    """Create and authenticate a Telegram client session."""
    client = TelegramClient("swarnsports_session", config.API_ID, config.API_HASH)
    await client.start(phone=config.PHONE_NUMBER)
    await client.connect()
    return client


def _normalize_channel_id_for_peer(channel_id: int) -> int:
    """
    Convert negative channel ID to proper format for PeerChannel.
    Telegram uses -100<channel_id> format for channels/supergroups.
    We need to extract the actual channel_id part.
    """
    if channel_id < 0:
        # Remove the -100 prefix that Telegram adds
        # Example: -1002292758419 -> 2292758419
        id_str = str(abs(channel_id))
        if id_str.startswith("100"):
            return int(id_str[3:])
    return abs(channel_id)


async def _resolve_channel_entity(client: TelegramClient, channel_id: int):
    """Resolve channel entity using PeerChannel for negative IDs."""
    if channel_id < 0:
        normalized_id = _normalize_channel_id_for_peer(channel_id)
        return await client.get_entity(PeerChannel(normalized_id))
    else:
        return await client.get_entity(channel_id)


async def fetch_recent_messages(client: TelegramClient, channel_id: int):
    """Fetch the last 100 messages from a channel, filtered to the last 24 hours."""
    try:
        entity = await _resolve_channel_entity(client, channel_id)
        messages = await client.get_messages(entity, limit=100)

        cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=24)
        recent_messages = [m for m in messages if m and m.date and m.date >= cutoff]
        return recent_messages
    except (ChannelPrivateError, ValueError) as exc:
        print(f"Failed to fetch messages for channel {channel_id}: {exc}")
        return []


def extract_links_from_message(message) -> list[str]:
    """Extract URLs from Telegram entities and text, filtering out unwanted links."""
    from urllib.parse import urlparse

    collected_urls = []

    text = getattr(message, "text", None) or ""
    entities = getattr(message, "entities", None) or []
    for entity in entities:
        entity_url = getattr(entity, "url", None)
        if entity_url:
            collected_urls.append(entity_url)
            continue

        offset = getattr(entity, "offset", None)
        length = getattr(entity, "length", None)
        if (
            isinstance(offset, int)
            and isinstance(length, int)
            and offset >= 0
            and length > 0
            and text
        ):
            slice_url = text[offset : offset + length]
            # Only accept slices that resemble actual URLs.
            if slice_url.startswith("http"):
                collected_urls.append(slice_url)

    collected_urls.extend(re.findall(r"https?://[^\s<>\"]+", text))

    cleaned_urls = []
    seen = set()
    trailing_punctuation = ")]}>,.;:*'"

    for url in collected_urls:
        cleaned = url.rstrip(trailing_punctuation)
        parsed = urlparse(cleaned)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            continue
        if any(pattern in cleaned for pattern in URL_BLACKLIST):
            continue
        if cleaned in seen:
            continue
        seen.add(cleaned)
        cleaned_urls.append(cleaned)

    return cleaned_urls


async def get_all_cricket_links() -> dict:
    """Collect links from all configured channels in the last 24 hours."""
    client = await authenticate()
    results = []

    try:
        for channel_id in config.CHANNELS:
            try:
                recent_messages = await fetch_recent_messages(client, channel_id)
                entity = await _resolve_channel_entity(client, channel_id)
                channel_name = getattr(entity, "title", str(channel_id))

                for message in recent_messages:
                    urls = extract_links_from_message(message)
                    if not urls:
                        continue

                    for url in urls:
                        results.append(
                            {
                                "url": url,
                                "source_channel_id": channel_id,
                                "source_channel_name": channel_name,
                                "message_text": getattr(message, "text", "") or "",
                                "posted_time": message.date.isoformat() if getattr(message, "date", None) else None,
                            }
                        )
            except Exception as exc:
                print(f"Error processing channel {channel_id}: {exc}")
                continue

        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return {"timestamp": timestamp, "links": results}
    finally:
        await client.disconnect()


def save_to_json(data: dict) -> None:
    """Persist fetched link data to data.json in project root."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Save at repo root (../data.json from backend/) instead of frontend/data.json.
    # This avoids creating or depending on a frontend directory for output storage.
    output_path = os.path.join(project_root, "data.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Saved {len(data.get('links', []))} links to {output_path}")


async def main() -> None:
    data = await get_all_cricket_links()
    save_to_json(data)
    print(
        f"Fetched {len(data.get('links', []))} links from {len(config.CHANNELS)} channels "
        f"at {data.get('timestamp')}"
    )


if __name__ == "__main__":
    asyncio.run(main())
