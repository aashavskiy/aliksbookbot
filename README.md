# PocketBook Telegram Bot (Webhook Version)

This branch implements the **webhook version** of the PocketBook Telegram Bot, which allows users to send book files directly to their PocketBook email via Telegram. Instead of polling updates, this version uses a webhook to handle Telegram events more efficiently.

---

## **Features**
- Receive book files via Telegram.
- Validate users against a whitelist.
- Automatically send received files to the configured PocketBook email using SMTP.
- Webhook-based event handling for improved responsiveness.
- Minimal HTTP server to handle webhook updates.

---

## **Setup Instructions**

### **1. Prerequisites**
- Python 3.8 or higher.
- A valid Telegram Bot API token.
- A PocketBook email address.
- An SMTP server (e.g., Gmail) with valid credentials.
- A publicly accessible URL for setting up the Telegram webhook (e.g., via **ngrok** or Google Cloud Run).

---

### **2. Clone the Repository**
```bash
git clone https://github.com/aashavskiy/aliksbookbot.git
cd aliksbookbot
git checkout webhook-version

3. Install Dependencies

Create a virtual environment and install the required dependencies:

python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
pip install -r requirements.txt

4. Create and Configure .env

Create a .env file in the project root and populate it with the following variables:

SERVICE_NAME=pocketbook-bot
REGION=europe-central2

API_TOKEN=your_telegram_bot_api_token
POCKETBOOK_EMAIL=your_pocketbook_email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=your_email_address
EMAIL_PASSWORD=your_email_password
WEBHOOK_URL=https://your-public-webhook-url
PORT=8080

	•	Replace the placeholder values (your_...) with your actual credentials.
	•	The WEBHOOK_URL should point to your publicly accessible webhook endpoint (e.g., an ngrok URL or Google Cloud Run service URL).

5. Run the Bot Locally

If testing locally with ngrok:
	1.	Start the bot:

python bookbot.py


	2.	Start ngrok to expose your local server:

ngrok http 8080


	3.	Copy the ngrok URL and update the WEBHOOK_URL in your .env file.
	4.	Set the Telegram webhook:

curl -X POST "https://api.telegram.org/bot<API_TOKEN>/setWebhook" \
     -d "url=<YOUR_NGROK_URL>"



Replace <API_TOKEN> and <YOUR_NGROK_URL> with your bot token and ngrok URL.

6. Deploy to Google Cloud Run

To deploy the bot to Google Cloud Run:
	1.	Build and deploy the service:

gcloud run deploy pocketbook-bot \
    --source=. \
    --region=europe-central2 \
    --allow-unauthenticated \
    --set-env-vars API_TOKEN=your_telegram_bot_api_token,POCKETBOOK_EMAIL=your_pocketbook_email,SMTP_SERVER=smtp.gmail.com,SMTP_PORT=587,EMAIL_ADDRESS=your_email_address,EMAIL_PASSWORD=your_email_password,WEBHOOK_URL=https://your-cloud-run-url


	2.	Set the webhook to the Cloud Run URL:

curl -X POST "https://api.telegram.org/bot<API_TOKEN>/setWebhook" \
     -d "url=https://your-cloud-run-url"

Usage
	1.	Start a conversation with your bot on Telegram.
	2.	Send the /start command to receive a welcome message.
	3.	Upload a book file. If you’re whitelisted, the bot will forward the file to your PocketBook email.

Environment Variables

Variable	Description
SERVICE_NAME	Google Cloud Run service name.
REGION	Google Cloud Run deployment region.
API_TOKEN	Telegram Bot API token.
POCKETBOOK_EMAIL	PocketBook email address.
SMTP_SERVER	SMTP server address (e.g., smtp.gmail.com).
SMTP_PORT	SMTP server port (default: 587 for TLS).
EMAIL_ADDRESS	Email address used for sending files.
EMAIL_PASSWORD	Password or app-specific password for the email.
WEBHOOK_URL	Public webhook URL for receiving updates.
PORT	Local port for running the webhook server.

Troubleshooting

Common Issues
	•	Webhook Setup Fails: Ensure your WEBHOOK_URL is publicly accessible.
	•	SMTP Errors: Double-check your email credentials and ensure your SMTP server allows third-party access.
	•	File Not Sent: Verify that the sender’s Telegram ID is in the whitelist.

Check Logs

Run the bot with increased logging to debug:

python bookbot.py -vv

Contributing

Feel free to submit issues and pull requests for new features or bug fixes.

License

This project is licensed under the MIT License.

