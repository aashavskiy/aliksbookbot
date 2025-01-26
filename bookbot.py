import os
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.dispatcher.router import Router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from dotenv import load_dotenv
from aiohttp import web
import logging

# Load environment variables
load_dotenv()

# Telegram Bot API Token from environment variables
API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    raise ValueError("API_TOKEN is not set!")

# Webhook URL from environment variables
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL is not set!")

# Initialize Bot and Dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Register a simple /start command handler
@router.message(Command("start"))
async def start_handler(message):
    """
    Handles the /start command and sends a greeting message.
    """
    await message.reply("Hi! Send me a book, and I'll process it!")

# Handle document uploads
@router.message(lambda message: message.document is not None)
async def document_handler(message):
    """
    Handles document uploads and acknowledges receipt.
    """
    await message.reply("Thanks for the book! Processing...")

# Add the router to the dispatcher
dp.include_router(router)

# Aiohttp webhook setup
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
        logging.error(f"Webhook processing error: {e}")
        return web.Response(status=500, text="Internal Server Error")

# Main entry point
async def main():
    """
    Main function to set up the webhook and run the aiohttp web server.
    """
    # Set the webhook for Telegram
    await bot.set_webhook(WEBHOOK_URL)

    # Create aiohttp web server
    app = web.Application()
    app.router.add_post("/", handle_webhook)

    # Start the web server
    port = int(os.getenv("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"Webhook listening on port {port}...")

if __name__ == "__main__":
    import asyncio
<<<<<<< HEAD
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"Unhandled exception: {e}")
=======
    asyncio.run(main()) 
>>>>>>> 8125c3a (Rolling back to lockal working version)
