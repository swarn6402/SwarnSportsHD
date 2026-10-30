"""Telegram fetcher for cricket streaming links."""

import asyncio
import datetime
import ipaddress
import json
import os
import re
import tempfile
from typing import Optional
from urllib.parse import urlsplit

from telethon import TelegramClient
from telethon.errors import ChannelPrivateError
from telethon.sessions import StringSession
from telethon.tl.types import MessageEntityTextUrl, MessageEntityUrl, PeerChannel

import config

# Keyword sets for per-message sport classification. Matched case-insensitively
# against message text. The classifier defaults to KEEPING a message: links are
# only dropped when a message looks like football (soccer) AND carries no cricket
# or F1 signal. This bias exists so no cricket stream is ever missed.
CRICKET_KEYWORDS = [
    "cricket", "t20i", "t20", "odi", " test", "test match", "ipl", "psl",
    "cpl", "bbl", "wtc", "ranji", "willow", "fancode", "innings", "wicket",
    "batting", "bowling", "day 1", "day 2", "day 3", "day 4", "day 5",
    "1st test", "2nd test", "3rd test", "4th test", "5th test",
]
F1_KEYWORDS = [
    "formula 1", "formula1", "f1 ", "grand prix", "qualifying", " gp ",
    "practice session", "sprint race",
]
FOOTBALL_KEYWORDS = [
    "football", "soccer", "fifa", "uefa", "epl", "premier league",
    "la liga", "laliga", "bundesliga", "serie a", "ligue 1",
    "champions league", "europa league", "ucl", "koora", "world cup qualifier",
]

# Match destination hosts, not substrings in a stream's path or query string.
# Unknown stream hosts remain allowed; this is not a stream-domain allowlist.
URL_BLACKLIST = [
    "t.me", "telegram.me", "telegram.org", "telegram.dog", "tg.me",
    "whatsapp.com", "whatsapp.net", "wa.me", "wa.link",
    "discord.gg", "discord.com", "discordapp.com",
    "bit.ly", "tinyurl.com", "shorturl.at", "shorturl.com",
]


async def authenticate() -> TelegramClient:
    """
    Create and authenticate a Telegram client session.

    Two modes, chosen automatically:
    - If ``SESSION_STRING`` is set (headless/CI, e.g. GitHub Actions), use an
      in-memory StringSession — no login prompt, no ``.session`` file.
    - Otherwise fall back to the on-disk ``swarnsports_session`` file used by the
      optional local scripts (interactive first-time login).
    """
    session_string = os.getenv("SESSION_STRING")
    if session_string:
        session = StringSession(session_string)
    else:
        session = "swarnsports_session"

    client = TelegramClient(session, config.API_ID, config.API_HASH)
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
        raise


def _message_text(message) -> str:
    """Read unformatted text, which Telegram's entity offsets refer to."""
    text = getattr(message, "raw_text", None)
    if text is None:
        text = getattr(message, "message", None)
    if text is None:
        text = getattr(message, "text", None)
    return text if isinstance(text, str) else ""


def _normalize_stream_url(url: str, assume_https: bool = False) -> Optional[str]:
    """Keep HTTP(S) destinations while excluding known join/contact hosts."""
    if not isinstance(url, str):
        return None
    cleaned = url.strip()
    if not cleaned or re.search(r"[\s\x00-\x1f\x7f\\]", cleaned):
        return None
    # Telegram URL entities also identify bare domains such as player.pages.dev/.
    has_scheme = re.match(r"^[a-z][a-z0-9+.-]*:", cleaned, re.I)
    bare_host_with_port = re.match(r"^[^/:?#]+\.[^/:?#]+:\d+(?:[/?#]|$)", cleaned)
    if assume_https and (not has_scheme or bare_host_with_port):
        cleaned = "https://" + cleaned
    try:
        parsed = urlsplit(cleaned)
        if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
            return None
        if parsed.username is not None or parsed.password is not None:
            return None
        # Accessing port also rejects invalid and out-of-range port strings.
        _ = parsed.port
        host = parsed.hostname.rstrip(".").encode("idna").decode("ascii").lower()
        try:
            ipaddress.ip_address(host)
        except ValueError:
            labels = host.split(".")
            if len(labels) < 2 or len(host) > 253 or labels[-1].isdigit():
                return None
            if any(
                not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", label)
                for label in labels
            ):
                return None
    except (ValueError, UnicodeError):
        return None
    if any(host == blocked or host.endswith("." + blocked) for blocked in URL_BLACKLIST):
        return None
    # Preserve the original path/query (including signed player parameters).
    return cleaned


def _clean_text_url(url: str) -> str:
    """Remove surrounding prose/Markdown punctuation, retaining balanced brackets."""
    cleaned = url.rstrip(">,.;:*'\"`")
    brackets = {")": "(", "]": "[", "}": "{"}
    while cleaned and cleaned[-1] in brackets:
        closing = cleaned[-1]
        if cleaned.count(closing) <= cleaned.count(brackets[closing]):
            break
        cleaned = cleaned[:-1].rstrip(">,.;:*'\"`")
    return cleaned


def extract_links_from_message(message) -> list[str]:
    """Extract URLs from Telegram entities and text, filtering out unwanted links."""
    collected_urls = []
    linked_spans = []
    text = _message_text(message)
    utf16_text = text.encode("utf-16-le", errors="surrogatepass")
    entities = getattr(message, "entities", None) or []
    for entity in entities:
        # Bold/italic/code entities are formatting, never URL boundaries.
        if not isinstance(entity, (MessageEntityUrl, MessageEntityTextUrl)):
            continue
        offset = getattr(entity, "offset", None)
        length = getattr(entity, "length", None)
        if (
            isinstance(offset, int)
            and isinstance(length, int)
            and offset >= 0
            and length > 0
            and offset + length <= len(utf16_text) // 2
        ):
            try:
                entity_url = utf16_text[offset * 2 : (offset + length) * 2].decode("utf-16-le")
            except UnicodeError:
                continue
            linked_spans.append((offset, offset + length))
            target = entity.url if isinstance(entity, MessageEntityTextUrl) else entity_url
            collected_urls.append((target, True))

    for match in re.finditer(r"https?://[^\s<>\"`]+", text, re.I):
        offset = len(text[:match.start()].encode("utf-16-le", errors="surrogatepass")) // 2
        # A hidden link's display text is not its destination. URL entities also
        # supply exact boundaries, so do not trim their signed queries again.
        if any(start <= offset < end for start, end in linked_spans):
            continue
        collected_urls.append((_clean_text_url(match.group()), False))

    cleaned_urls = []
    seen = set()
    for url, assume_https in collected_urls:
        cleaned = _normalize_stream_url(url, assume_https=assume_https)
        if cleaned is None:
            continue
        if cleaned in seen:
            continue
        seen.add(cleaned)
        cleaned_urls.append(cleaned)

    return cleaned_urls


def _is_football_message(text: str) -> bool:
    """
    Return True only for messages that clearly advertise football (soccer)
    streams and carry no cricket or F1 signal.

    The classifier is deliberately conservative: cricket and F1 keywords act as
    a protective allowlist, so an ambiguous or mixed message is always kept.
    Only unambiguous football posts get filtered out.
    """
    lowered = text.lower()
    if any(keyword in lowered for keyword in CRICKET_KEYWORDS):
        return False
    if any(keyword in lowered for keyword in F1_KEYWORDS):
        return False
    return any(keyword in lowered for keyword in FOOTBALL_KEYWORDS)


async def get_all_cricket_links() -> dict:
    """Collect links from all configured channels in the last 24 hours."""
    client = await authenticate()
    results = []
    seen_urls = set()
    successful_channels = 0

    try:
        for channel_id in config.CHANNELS:
            try:
                recent_messages = await fetch_recent_messages(client, channel_id)
                entity = await _resolve_channel_entity(client, channel_id)
                channel_name = getattr(entity, "title", str(channel_id))
                successful_channels += 1

                for message in recent_messages:
                    message_text = _message_text(message)
                    # Skip clear football posts; cricket/F1 messages fall through.
                    if _is_football_message(message_text):
                        continue

                    urls = extract_links_from_message(message)
                    urls = [u for u in urls if u not in seen_urls]
                    seen_urls.update(urls)
                    if not urls:
                        continue

                    for url in urls:
                        results.append(
                            {
                                "url": url,
                                "source_channel_id": channel_id,
                                "source_channel_name": channel_name,
                                "message_text": message_text,
                                "posted_time": message.date.isoformat() if getattr(message, "date", None) else None,
                            }
                        )
            except Exception as exc:
                print(f"Error processing channel {channel_id}: {exc}")
                continue

        if not successful_channels:
            raise RuntimeError("No channels could be read; keeping the existing data.json.")
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return {"timestamp": timestamp, "links": results}
    finally:
        await client.disconnect()


def save_to_json(data: dict) -> None:
    """Persist fetched link data to data.json in project root."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Root data.json is the only live output; docs/archive/ is historical.
    output_path = os.path.join(project_root, "data.json")
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=project_root,
            prefix=".data-", suffix=".json.tmp", delete=False,
        ) as f:
            temporary_path = f.name
            json.dump(data, f, indent=2, allow_nan=False)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(temporary_path, output_path)
    finally:
        if temporary_path and os.path.exists(temporary_path):
            os.unlink(temporary_path)

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
