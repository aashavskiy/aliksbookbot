# Use Python as the base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy all project files, including the .git directory
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variable for version
ARG DEFAULT_VERSION="unknown"
ENV BOT_VERSION=$DEFAULT_VERSION

# Set the version at build time using Git metadata
RUN if [ -d ".git" ]; then \
      VERSION=$(git describe --tags || echo "unknown"); \
      echo "Version: $VERSION"; \
      echo $VERSION > VERSION; \
    else \
      echo "unknown" > VERSION; \
    fi

# Expose the port for the HTTP server
EXPOSE 8080

# Run the bot
CMD ["python", "bookbot.py"]
