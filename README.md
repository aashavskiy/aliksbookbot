# PocketBook Telegram Bot

This bot allows users to send books via Telegram, and it automatically forwards them to their PocketBook email. The bot supports two modes of operation: **polling** (for local execution) and **webhook** (for deployment on cloud services like Google Cloud Run).

## Features
- Accepts document uploads via Telegram
- Sends books to a predefined PocketBook email
- Supports **polling** and **webhook** modes (configurable via environment variable `BOT_MODE`)
- Runs on Google Cloud Run or locally
- Uses environment variables for configuration security

## Project Structure
```
.
├── bookbot.py           # Main bot script
├── requirements.txt     # Dependencies
├── Dockerfile          # Docker configuration for Cloud Run
├── cloudbuild.yaml     # Google Cloud Build configuration
├── .env.example        # Example environment variable file
├── set_gcloud_env.py   # Script to upload environment variables to Google Cloud
├── whitelist.py        # List of allowed Telegram user IDs
```

## Installation
### **Local Setup**
1. Clone the repository:
   ```bash
   git clone https://github.com/aashavskiy/aliksbookbot.git
   cd aliksbookbot
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv myvenv
   source myvenv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file from `.env.example` and fill in your credentials.

### **Running Locally**
#### **Polling Mode**
To start the bot using **polling** (suitable for local development):
```bash
export BOT_MODE=polling
python bookbot.py
```

#### **Webhook Mode** (Requires `ngrok` or public server)
1. Install and start `ngrok`:
   ```bash
   ngrok http 8080
   ```
   Copy the `ngrok` URL (e.g., `https://xxxx.ngrok.io`).
2. Set the webhook URL in `.env`:
   ```bash
   export WEBHOOK_URL=https://xxxx.ngrok.io
   export BOT_MODE=webhook
   ```
3. Start the bot:
   ```bash
   python bookbot.py
   ```

## Deployment on Google Cloud Run
### **Prerequisites**
- Google Cloud SDK installed
- A Google Cloud project with billing enabled

### **Steps to Deploy**
1. Authenticate with Google Cloud:
   ```bash
   gcloud auth login
   gcloud config set project aliks-book-bot
   ```
2. Build and push the container:
   ```bash
   gcloud builds submit --tag gcr.io/aliks-book-bot/bookbot
   ```
3. Deploy the bot:
   ```bash
   gcloud run deploy pocketbook-bot \
      --image gcr.io/aliks-book-bot/bookbot \
      --region europe-central2 \
      --platform managed \
      --allow-unauthenticated \
      --set-env-vars BOT_MODE=webhook,WEBHOOK_URL=https://pocketbook-bot-xxxx.run.app
   ```

## Updating Google Cloud Run Environment Variables
If you update your `.env` file, use the following script:
```bash
python set_gcloud_env.py
```

## License
MIT License

testing CI build (29.01.2025)
