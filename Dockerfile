# Use Python as the base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy all files, including .git, to the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Define a build argument for version fallback
ARG DEFAULT_VERSION="unknown"

# Generate the VERSION file from Git metadata or fallback to the default version
RUN if [ -d ".git" ]; then \
      VERSION=$(git describe --tags --always || echo $DEFAULT_VERSION); \
      echo "Version: $VERSION"; \
      echo $VERSION > VERSION; \
    else \
      echo $DEFAULT_VERSION > VERSION; \
    fi

# Expose the port for the HTTP server
EXPOSE 8080

# Run the bot
CMD ["python", "bookbot.py"]
