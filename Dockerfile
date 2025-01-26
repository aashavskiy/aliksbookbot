FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose default port (optional)
EXPOSE 8080

# Start the bot
CMD ["python", "bookbot.py"]
