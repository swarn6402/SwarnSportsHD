"""Utility for retrieving Telegram channel and supergroup metadata."""

import asyncio

from telethon import TelegramClient
from telethon.errors import ApiIdInvalidError, PhoneCodeInvalidError, SessionPasswordNeededError

import config


async def get_my_channels() -> None:
    """Authenticate and print all channel/supergroup dialogs for the account."""
    client = TelegramClient("swarnsports_session", config.API_ID, config.API_HASH)

    try:
        # Starts interactive auth when needed (code/password prompts in terminal).
        await client.start(phone=config.PHONE_NUMBER)

        dialogs = await client.get_dialogs()

        rows = []
        for dialog in dialogs:
            entity = dialog.entity
            if not getattr(entity, "broadcast", False) and not getattr(entity, "megagroup", False):
                continue

            chat_type = "Channel" if getattr(entity, "broadcast", False) else "Supergroup"
            rows.append((dialog.name or "(No title)", entity.id, chat_type))

        if not rows:
            print("No channels or supergroups found for this account.")
            return

        title_w = max(len("Channel Title"), max(len(str(r[0])) for r in rows))
        id_w = max(len("Chat ID"), max(len(str(r[1])) for r in rows))
        type_w = max(len("Type"), max(len(str(r[2])) for r in rows))

        separator = f"+-{'-' * title_w}-+-{'-' * id_w}-+-{'-' * type_w}-+"
        header = f"| {'Channel Title'.ljust(title_w)} | {'Chat ID'.ljust(id_w)} | {'Type'.ljust(type_w)} |"

        print(separator)
        print(header)
        print(separator)
        for title, chat_id, chat_type in rows:
            print(f"| {str(title).ljust(title_w)} | {str(chat_id).ljust(id_w)} | {str(chat_type).ljust(type_w)} |")
        print(separator)

    except (ApiIdInvalidError, PhoneCodeInvalidError, SessionPasswordNeededError) as exc:
        print(f"Authentication failed: {exc}")
    except Exception as exc:
        print(f"Failed to retrieve channel info: {exc}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(get_my_channels())
