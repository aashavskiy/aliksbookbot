import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Update, Message
from aiogram.dispatcher.router import Router
from aiogram.filters import Command
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
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Webhook URL for Telegram updates

# Validate that all required environment variables are provided
if not all([API_TOKEN, POCKETBOOK_EMAIL, SMTP_SERVER, EMAIL_ADDRESS, EMAIL_PASSWORD, WEBHOOK_URL]):
    raise ValueError("One or more required environment variables are missing.")

# Configure logging for debugging purposes
logging.basicConfig(level=logging.INFO)

# Initialize the bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

# Directory for temporarily storing downloaded files
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


# Function to set the webhook for Telegram
async def set_webhook():
    """
    Sets the webhook for the bot using the provided WEBHOOK_URL.
    """
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook set to: {WEBHOOK_URL}")


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


# Handle incoming webhook requests
async def handle_webhook(request):
    """
    Handles incoming updates from Telegram via webhook.
    """
    try:
        body = await request.json()
        update = Update.to_object(body)
        await dp.feed_update(bot, update)
        return web.Response(status=200, text="OK")
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return web.Response(status=500, text="Internal Server Error")


# Start a lightweight HTTP server to receive webhook updates
async def start_server():
    """
    Starts an HTTP server to handle Telegram webhook updates.
    """
    app = web.Application()
    app.router.add_post("/", handle_webhook)

    port = int(os.getenv("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"Webhook server running on port {port}...")


# Main entry point of the bot
async def main():
    """
    Main function to set the webhook and start the HTTP server.
    """
    dp.include_router(router)

    # Set the webhook
    await set_webhook()

    # Start the HTTP server
    await start_server()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
