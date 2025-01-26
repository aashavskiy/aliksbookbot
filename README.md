Updated README.md

# Telegram Bot: Send-to-PocketBook

This is a Telegram bot designed to simplify the process of uploading e-books to your PocketBook device. The bot allows authorized users to send book files directly to a predefined PocketBook email address through Telegram. It securely manages secrets and configurations using environment variables.

---

## **Features**
- **File Uploads**: Accepts popular e-book formats (e.g., `.epub`, `.fb2`, `.mobi`) and sends them to PocketBook.
- **Whitelist Security**: Only authorized users can interact with the bot.
- **Environment Variables**: Secrets like API tokens and email credentials are securely managed using `.env` files or cloud-managed environment variables.
- **Automatic File Cleanup**: Deletes temporary files after successful upload.
- **SMTP Integration**: Sends files via email using the configured SMTP server.

---

## **Project Structure**

Here is a breakdown of the files in this repository:

- **`bookbot.py`**:  
  The main bot script that handles file uploads, user authentication, and sending books to PocketBook.

- **`requirements.txt`**:  
  Lists all the dependencies required for the bot to function.

- **`.env`**:  
  A file containing secrets such as the Telegram API token and email credentials (used locally, not included in the repository for security reasons).

- **`whitelist.py`**:  
  Contains a list of authorized Telegram user IDs (whitelist).

- **`.gitignore`**:  
  Specifies files and folders to exclude from version control (e.g., `.env`, virtual environment files, logs).

- **`README.md`**:  
  Explains the bot's purpose, features, setup, and usage instructions.

---

## **Setup Instructions**

### **1. Clone the Repository**
Clone this repository to your local machine:
```bash
git clone https://github.com/username/send-to-pocketbook.git
cd send-to-pocketbook

2. Create a Virtual Environment

Set up a virtual environment to manage dependencies:

python3 -m venv myenv
source myenv/bin/activate

3. Install Dependencies

Install the required Python libraries:

pip install -r requirements.txt

4. Create a .env File

Create a .env file in the project root and add your secrets:

API_TOKEN=your-telegram-bot-token
POCKETBOOK_EMAIL=your-pocketbook-email@pbsync.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

5. Add Authorized Users

Edit the whitelist.py file to include the Telegram user IDs of authorized users:

# whitelist.py

WHITELIST = [
    123456789,  # Replace with your Telegram ID
    987654321,  # Add more IDs as needed
]

6. Run the Bot

Start the bot using the following command:

python bookbot.py

Running the Bot in the Cloud

For deploying the bot in a cloud environment like Google Cloud Run or Heroku, ensure you set the environment variables directly in the cloud platform instead of using .env. Example for Google Cloud Run:

gcloud run services update pocketbook-bot \
    --update-env-vars API_TOKEN="your-telegram-bot-token",POCKETBOOK_EMAIL="your-pocketbook-email@pbsync.com",SMTP_SERVER="smtp.gmail.com",SMTP_PORT="587",EMAIL_ADDRESS="your-email@gmail.com",EMAIL_PASSWORD="your-app-password"

Example Usage
	1.	Start the bot in Telegram by sending the /start command.
	2.	Send an e-book file (e.g., .epub) to the bot.
	3.	The bot will upload the file to the configured PocketBook email and notify you when it’s successfully sent.

Future Enhancements
	•	Add multi-language support.
	•	Extend functionality to support other e-reader platforms (e.g., Kindle, Bookmate).
	•	Add support for larger files and chunked uploads.

Contributing

Feel free to fork this repository and submit pull requests for improvements or new features.

License

This project is licensed under the MIT License. See the LICENSE file for details.
