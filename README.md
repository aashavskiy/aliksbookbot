📚 PocketBook Telegram Bot (Webhook Version)

This Telegram bot allows users to send book files directly to their PocketBook e-reader via email. This version uses webhooks instead of polling, making it more efficient and scalable.

🚀 Features
	•	✅ Accepts book files from whitelisted Telegram users.
	•	✅ Sends uploaded books to a PocketBook email.
	•	✅ Uses webhooks for event-driven message processing.
	•	✅ Hosted on Google Cloud Run for seamless deployment.
	•	✅ Secure authentication via environment variables.

📂 Project Structure

/project-root
│── bookbot.py               # Main bot script (webhook-based)
│── requirements.txt         # Python dependencies
│── set_gcloud_env.py        # Script to set Google Cloud Run environment variables
│── cloudbuild.yaml          # Google Cloud Build configuration for automated deployment
│── whitelist.py             # Contains the Telegram user whitelist
│── .env                     # Environment variables (not included in Git)
│── .env.example             # Template for environment variables
│── README.md                # This documentation file

🔧 Setup Instructions

1️⃣ Install Dependencies

Make sure you have Python installed. Then, install dependencies:

pip install -r requirements.txt

2️⃣ Set Up Environment Variables

Create a .env file using .env.example as a reference. Fill in your values.

To load the environment variables, run:

source .env

3️⃣ Run Locally with Webhooks

You need ngrok to expose your local server to the internet.
	1.	Start ngrok:

ngrok http 8080

Copy the public URL (e.g., https://xxxx.ngrok-free.app).

	2.	Run the bot:

python bookbot.py

☁️ Deployment to Google Cloud Run

This bot is deployed using Google Cloud Run.

1️⃣ Set Environment Variables in Google Cloud Run

python set_gcloud_env.py

2️⃣ Deploy to Google Cloud Run

gcloud run deploy pocketbook-bot \
  --region europe-central2 \
  --source .

Current Deployment Info:
	•	Cloud Run URL: PocketBook Bot
	•	Google Cloud Project ID: aliks-book-bot
	•	Service Name: pocketbook-bot
	•	Region: europe-central2

📝 Notes
	•	Webhooks vs Polling: This branch uses webhooks. If you need polling, switch to the poll-version branch.
	•	Environment Variables: Secrets are stored in .env, which should never be committed to Git.
	•	Google Cloud Run Scaling: Auto-scales based on demand but may have cold starts.
	•	Debugging Webhooks: Run locally using ngrok and check logs for errors.

📢 Contributing

Feel free to submit issues or pull requests to improve this bot.

📜 License

MIT License. Use freely but with proper attribution.

