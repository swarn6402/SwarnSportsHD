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
    """Extract URLs from a Telegram message text."""
    text = getattr(message, "text", None)
    if not text:
        return []
    return re.findall(r"https?://[^\s]+", text)


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
    """Persist fetched link data to frontend/data.json."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_dir = os.path.join(project_root, "frontend")
    os.makedirs(frontend_dir, exist_ok=True)

    output_path = os.path.join(frontend_dir, "data.json")
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
