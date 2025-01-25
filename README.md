README.md

# Telegram Bot: Send-to-PocketBook

This is a Telegram bot designed to simplify the process of uploading e-books to your PocketBook device. The bot allows users to send book files directly to a predefined PocketBook email address through Telegram. 

---

## **Features**
- Accepts files in popular e-book formats such as `.epub`, `.fb2`, `.mobi`, etc.
- Sends the received files to your PocketBook email for synchronization with your device.
- Supports a whitelist of authorized Telegram users.
- Easy to configure and extend.

---

## **Project Structure**
Here is a breakdown of the files in this repository:

- **`bookbot.py`**:  
  The main script for the bot. Handles file uploads, user authentication, and sending files to the PocketBook email.

- **`config.py`**:  
  Configuration file that contains essential variables such as the bot token, PocketBook email, and email server settings.

- **`whitelist.py`**:  
  Contains a list of authorized Telegram user IDs. Only these users are allowed to send files to the bot.

- **`.gitignore`**:  
  Specifies files and folders to exclude from version control (e.g., virtual environment files, logs, etc.).

- **`README.md`**:  
  This file. Explains the bot's purpose, features, setup, and usage.

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

4. Configure the Bot

Edit the config.py file to include your credentials and settings:

# config.py

# Telegram Bot API Token
API_TOKEN = "your-telegram-bot-token"

# PocketBook email address
POCKETBOOK_EMAIL = "your-pocketbook-email@pbsync.com"

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "your-email@gmail.com"  # Email used to send books
EMAIL_PASSWORD = "your-app-password"   # App-specific password for your email

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

Running the Bot as a Service

To ensure the bot runs continuously, you can set it up as a systemd service. Refer to the instructions in the conversation for detailed steps.

Example Usage
	1.	Start the bot in Telegram by sending the /start command.
	2.	Send an e-book file (e.g., .epub) to the bot.
	3.	The bot will upload the file to the configured PocketBook email and notify you when it’s successfully sent.

Future Enhancements
	•	Add multi-language support.
	•	Integrate with other e-reader platforms (e.g., Kindle, Bookmate).
	•	Enable real-time status tracking for uploaded books.

Contributing

Feel free to fork this repository and submit pull requests for improvements or new features.

License

This project is licensed under the MIT License. See the LICENSE file for details.

---

### **What’s Included**
1. **File descriptions**: Explained the purpose of each file in the project.
2. **Setup instructions**: Detailed steps for setting up and running the bot.
3. **Configuration template**: Included a template for `config.py`.
4. **Whitelist instructions**: Explained how to manage authorized users in `whitelist.py`.
5. **Future Enhancements**: Suggestions for expanding the bot.

Let me know if you need further adjustments!
