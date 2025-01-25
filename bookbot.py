import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.dispatcher.router import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from email.mime.base import MIMEBase
from email import encoders
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
from config import API_TOKEN, POCKETBOOK_EMAIL, SMTP_SERVER, SMTP_PORT, EMAIL_ADDRESS, EMAIL_PASSWORD
from whitelist import WHITELIST  # Импортируем whitelist

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

# Directory to store downloaded files
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Handle the "/start" command
@router.message(Command(commands=["start"]))
async def send_welcome(message: Message):
    await message.reply("Hi! Send me a book file, and I’ll upload it to your PocketBook.")

# Handle document uploads
@router.message(lambda message: message.document is not None)
async def handle_document(message: Message):
    # Проверяем, входит ли пользователь в whitelist
    if message.from_user.id not in WHITELIST:
        await message.reply("You are not allowed to send files to this bot.")
        return

    document = message.document
    file_name = document.file_name

    # Скачиваем файл
    file_path = os.path.join(DOWNLOAD_FOLDER, file_name)
    try:
        # Получаем информацию о файле
        file_info = await bot.get_file(document.file_id)
        # Загружаем файл
        await bot.download_file(file_info.file_path, destination=file_path)
        await message.reply(f"File {file_name} has been successfully downloaded. Sending it to your PocketBook...")

        # Отправляем файл на PocketBook
        send_to_pocketbook(file_path, file_name)
        await message.reply("The book has been successfully sent to PocketBook!")
    except Exception as e:
        logging.error(f"Error while processing the document: {e}")
        await message.reply("An error occurred while sending the book.")
    finally:
        # Удаляем файл после отправки
        if os.path.exists(file_path):
            os.remove(file_path)

# Function to send a file via email
def send_to_pocketbook(file_path, file_name):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = POCKETBOOK_EMAIL
    msg["Subject"] = "New Book"

    # Attach the file
    with open(file_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename={file_name}",
    )
    msg.attach(part)

    # Send email
    with SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, POCKETBOOK_EMAIL, msg.as_string())

# Start the bot
async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
