import os
import logging
import subprocess
from aiogram import Bot, Dispatcher
from aiogram.dispatcher.router import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from email.mime.base import MIMEBase
from email import encoders
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
from aiohttp import web
from dotenv import load_dotenv
from whitelist import WHITELIST  # Import authorized user list

# Load environment variables from .env file
load_dotenv()

# Fetch required secrets from environment variables
API_TOKEN = os.getenv("API_TOKEN")  # Telegram Bot API token
POCKETBOOK_EMAIL = os.getenv("POCKETBOOK_EMAIL")  # PocketBook email for file delivery
SMTP_SERVER = os.getenv("SMTP_SERVER")  # SMTP server (e.g., Gmail's SMTP)
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))  # SMTP port (default: 587 for TLS)
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")  # Email used to send books
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Password or app-specific password for the email

# Validate that all required environment variables are provided
if not all([API_TOKEN, POCKETBOOK_EMAIL, SMTP_SERVER, EMAIL_ADDRESS, EMAIL_PASSWORD]):
    raise ValueError("One or more required environment variables are missing.")

# Configure logging for debugging purposes
logging.basicConfig(level=logging.INFO)

# Initialize the bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

# Versioning
def get_git_version():
    """
    Retrieves the current version of the bot from the VERSION file.
    Falls back to 'unknown' if the file is missing.
    """
    try:
        with open("VERSION", "r") as version_file:
            return version_file.read().strip()
    except FileNotFoundError:
        return "unknown"

# Set the bot version
BOT_VERSION = get_git_version()

# Directory for temporarily storing downloaded files
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Handle the /start command
@router.message(Command(commands=["start"]))
async def send_welcome(message: Message):
    """
    Sends a welcome message to the user when they send the /start command.
    """
    await message.reply("Hi! Send me a book file, and I’ll upload it to your PocketBook.")

# Handle document uploads
@router.message(lambda message: message.document is not None)
async def handle_document(message: Message):
    """
    Handles document uploads from users.
    Downloads the file, validates the user against the whitelist,
    and sends the file to PocketBook via email.
    """
    # Check if the user is in the whitelist
    if message.from_user.id not in WHITELIST:
        await message.reply("You are not allowed to send files to this bot.")
        return

    document = message.document
    file_name = document.file_name

    # Path to save the downloaded file
    file_path = os.path.join(DOWNLOAD_FOLDER, file_name)

    try:
        # Fetch file information from Telegram
        file_info = await bot.get_file(document.file_id)
        # Download the file to the specified path
        await bot.download_file(file_info.file_path, destination=file_path)
        await message.reply(f"File {file_name} has been successfully downloaded. Sending it to your PocketBook...")

        # Send the file to the PocketBook email
        send_to_pocketbook(file_path, file_name)
        await message.reply("The book has been successfully sent to PocketBook!")
    except Exception as e:
        logging.error(f"Error while processing the document: {e}")
        await message.reply("An error occurred while sending the book.")
    finally:
        # Remove the file from the local storage after sending
        if os.path.exists(file_path):
            os.remove(file_path)

# Function to send a file to the PocketBook email
def send_to_pocketbook(file_path, file_name):
    """
    Sends the specified file to the PocketBook email address using SMTP.
    """
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = POCKETBOOK_EMAIL
    msg["Subject"] = "New Book"

    # Attach the file to the email
    with open(file_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename={file_name}",
    )
    msg.attach(part)

    # Connect to the SMTP server and send the email
    with SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()  # Start TLS encryption
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)  # Authenticate
        server.sendmail(EMAIL_ADDRESS, POCKETBOOK_EMAIL, msg.as_string())  # Send the email

# Start a lightweight HTTP server for Google Cloud Run
async def version_endpoint(request):
    """
    Returns the bot's version as a response.
    """
    return web.Response(text=f"Bot version: {BOT_VERSION}", status=200)

async def start_server():
    async def healthcheck(request):
        return web.Response(text="Bot is running!")

    app = web.Application()
    app.router.add_get("/", healthcheck)
    app.router.add_get("/version", version_endpoint)  # Add version endpoint

    port = int(os.getenv("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"HTTP server running on port {port}...")


# Main entry point of the bot
async def main():
    """
    Main function to start the bot's polling loop and HTTP server.
    """
    dp.include_router(router)

    # Start HTTP server in the background
    await start_server()

    # Start Telegram bot polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
