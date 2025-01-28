# Use Python as the base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy all project files to the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Define a build argument for the bot version
ARG DEFAULT_VERSION="unknown"

# Pass the build argument to an environment variable
ENV BOT_VERSION=$DEFAULT_VERSION

# Expose the port for the HTTP server
EXPOSE 8080

# Run the bot
CMD ["python", "bookbot.py"]
