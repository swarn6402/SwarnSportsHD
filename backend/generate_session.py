"""
One-time helper to generate a Telethon StringSession for headless runs.

Run this locally ONCE (it uses the same API_ID / API_HASH / PHONE_NUMBER from
backend/.env and performs a real interactive Telegram login). Copy the printed
string into a GitHub Actions secret named SESSION_STRING so the fetcher can
authenticate on GitHub's servers without the interactive phone-code step.

    cd backend
    python generate_session.py

SECURITY: the printed string grants full access to your Telegram account. Treat
it like a password — paste it only into GitHub's encrypted secrets, never commit
it, and never paste it into chat or logs.
"""

import asyncio

from telethon import TelegramClient
from telethon.sessions import StringSession

import config


async def main() -> None:
    """Interactively log in and print a reusable StringSession."""
    # StringSession() with no argument starts empty. We call start() explicitly
    # with the phone from .env so it isn't prompted for interactively.
    client = TelegramClient(StringSession(), config.API_ID, config.API_HASH)
    await client.start(phone=config.PHONE_NUMBER)
    try:
        session_string = client.session.save()
    finally:
        await client.disconnect()

    print("\n" + "=" * 60)
    print("SESSION_STRING (copy the line below into a GitHub secret):")
    print("=" * 60)
    print(session_string)
    print("=" * 60)
    print("Do NOT commit this or share it. It logs in as your account.")


if __name__ == "__main__":
    asyncio.run(main())
