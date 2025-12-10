import asyncio
import logging
import os
import signal
import time
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
from typing import Optional

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.dispatcher.router import Router
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, Update
from dotenv import load_dotenv

from whitelist import WHITELIST  # Import authorized user list

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

SUPPORTED_BOT_MODES = {"polling", "webhook"}
ALLOWED_EXTENSIONS = {".epub", ".fb2", ".mobi", ".pdf", ".txt"}
MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB
MAX_FILES_PER_HOUR = 10
RETRY_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = 2


def _get_env(name: str, *, cast=int, required: bool = True, default: Optional[str] = None):
    value = os.getenv(name, default)
    if required and (value is None or value == ""):
        logging.error(f"Missing required environment variable: {name}")
        raise ValueError(f"Missing required environment variable: {name}")
    try:
        return cast(value) if cast and value is not None else value
    except Exception as exc:  # noqa: BLE001
        logging.error(f"Invalid value for environment variable {name}: {value}")
        raise ValueError(f"Invalid value for environment variable {name}") from exc


def validate_bot_mode(raw_mode: str) -> str:
    mode = raw_mode.lower()
    if mode not in SUPPORTED_BOT_MODES:
        logging.error("BOT_MODE must be either 'polling' or 'webhook'")
        raise ValueError("BOT_MODE must be either 'polling' or 'webhook'")
    return mode


API_TOKEN = _get_env("API_TOKEN", cast=str)
POCKETBOOK_EMAIL = _get_env("POCKETBOOK_EMAIL", cast=str)
SMTP_SERVER = _get_env("SMTP_SERVER", cast=str)
SMTP_PORT = _get_env("SMTP_PORT", cast=int, default="587")
EMAIL_ADDRESS = _get_env("EMAIL_ADDRESS", cast=str)
EMAIL_PASSWORD = _get_env("EMAIL_PASSWORD", cast=str)
BOT_MODE = validate_bot_mode(os.getenv("BOT_MODE", "polling"))
WEBHOOK_URL = _get_env("WEBHOOK_URL", cast=str, required=BOT_MODE == "webhook", default=None)
PORT = _get_env("PORT", cast=int, default="8080")

if not (1 <= PORT <= 65535):
    logging.error("PORT must be between 1 and 65535")
    raise ValueError("PORT must be between 1 and 65535")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Simple per-user rate limiting: timestamps (epoch seconds) of sent files
user_send_history: dict[int, list[float]] = {}


async def set_webhook():
    """Sets the webhook for Telegram updates."""
    try:
        await bot.set_webhook(WEBHOOK_URL)
        logging.info(f"Webhook successfully set to: {WEBHOOK_URL}")
    except Exception as exc:  # noqa: BLE001
        logging.error(f"Failed to set webhook: {exc}")
        raise


@router.message(Command(commands=["start"]))
async def send_welcome(message: Message):
    """Sends a detailed welcome message when the /start command is used."""
    help_text = (
        "Hi! Send me a book file, and I’ll forward it to your PocketBook.\n\n"
        "What to know:\n"
        f"• Allowed formats: {', '.join(sorted(ext.strip('.') for ext in ALLOWED_EXTENSIONS))}\n"
        f"• Max file size: {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB\n"
        f"• Rate limit: up to {MAX_FILES_PER_HOUR} files per hour per user\n"
        "• Make sure your PocketBook email is set in the bot configuration."
    )
    await message.reply(help_text)


def _is_allowed_extension(filename: str) -> bool:
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXTENSIONS


def _rate_limited(user_id: int) -> bool:
    now = time.time()
    window_start = now - 3600
    history = user_send_history.setdefault(user_id, [])
    user_send_history[user_id] = [ts for ts in history if ts >= window_start]
    if len(user_send_history[user_id]) >= MAX_FILES_PER_HOUR:
        return True
    user_send_history[user_id].append(now)
    return False


async def _download_file_with_retry(file_id: str, destination: str) -> None:
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            file_info = await bot.get_file(file_id)
            await bot.download_file(file_info.file_path, destination=destination)
            return
        except Exception as exc:  # noqa: BLE001
            logging.warning(
                "Download attempt %s/%s failed: %s", attempt, RETRY_ATTEMPTS, exc
            )
            if attempt == RETRY_ATTEMPTS:
                raise
            await asyncio.sleep(RETRY_BACKOFF_SECONDS * attempt)


def _send_email(file_path: str, file_name: str) -> None:
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = POCKETBOOK_EMAIL
    msg["Subject"] = "New Book"

    with open(file_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename={file_name}")
    msg.attach(part)

    with SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, POCKETBOOK_EMAIL, msg.as_string())


async def send_to_pocketbook(file_path: str, file_name: str) -> None:
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            await asyncio.to_thread(_send_email, file_path, file_name)
            return
        except Exception as exc:  # noqa: BLE001
            logging.warning(
                "Email send attempt %s/%s failed: %s", attempt, RETRY_ATTEMPTS, exc
            )
            if attempt == RETRY_ATTEMPTS:
                raise
            await asyncio.sleep(RETRY_BACKOFF_SECONDS * attempt)


@router.message(lambda message: message.document is not None)
async def handle_document(message: Message):
    """Handles document uploads, checks the whitelist, and sends books via email."""
    if message.from_user.id not in WHITELIST:
        await message.reply("You are not allowed to send files to this bot.")
        return

    document = message.document
    file_name = document.file_name

    if not _is_allowed_extension(file_name):
        await message.reply(
            f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )
        return

    if document.file_size and document.file_size > MAX_FILE_SIZE_BYTES:
        await message.reply(
            f"File is too large. Max size is {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB."
        )
        return

    if _rate_limited(message.from_user.id):
        await message.reply(
            "Rate limit exceeded. Please wait before sending more files (max "
            f"{MAX_FILES_PER_HOUR} per hour)."
        )
        return

    file_path = os.path.join(DOWNLOAD_FOLDER, file_name)

    try:
        await _download_file_with_retry(document.file_id, file_path)
        await message.reply(
            f"File {file_name} downloaded. Sending it to your PocketBook (this may take a moment)..."
        )
        await send_to_pocketbook(file_path, file_name)
        await message.reply("The book has been successfully sent to PocketBook!")
    except Exception as exc:  # noqa: BLE001
        logging.error(f"Error while processing the document: {exc}")
        await message.reply("An error occurred while sending the book. Please try again.")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


async def handle_webhook(request: web.Request):
    """Handles incoming updates from Telegram via webhook."""
    try:
        body = await request.json()
        logging.debug("Received webhook payload")

        update = Update.model_validate(body)  # Ensure correct structure
        await dp.feed_update(bot, update)
        return web.Response(status=200, text="OK")

    except Exception as exc:  # noqa: BLE001
        logging.error(f"Webhook error: {exc}")
        return web.Response(status=500, text="Internal Server Error")


async def healthcheck(_: web.Request) -> web.Response:
    return web.Response(status=200, text="OK")


async def start_server():
    """Starts an HTTP server for handling webhook updates."""
    app = web.Application()
    app.router.add_post("/", handle_webhook)
    app.router.add_get("/health", healthcheck)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logging.info(f"Webhook server running on port {PORT}...")

    shutdown_event = asyncio.Event()

    loop = asyncio.get_running_loop()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, shutdown_event.set)

    await shutdown_event.wait()
    logging.info("Shutting down webhook server...")
    await runner.cleanup()


async def main():
    """Starts the bot in either polling or webhook mode based on the BOT_MODE environment variable."""
    dp.include_router(router)

    if BOT_MODE == "webhook":
        logging.info("Starting in Webhook mode...")
        await set_webhook()
        await start_server()
    else:
        logging.info("Starting in Polling mode...")
        try:
            await dp.start_polling(bot)
        finally:
            await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:  # noqa: BLE001
        logging.critical(f"Script terminated with an unhandled exception: {exc}")
