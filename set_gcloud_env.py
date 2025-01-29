import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch required variables for Google Cloud Run
SERVICE_NAME = os.getenv("SERVICE_NAME")
REGION = os.getenv("REGION")

if not SERVICE_NAME or not REGION:
    print("Error: Missing SERVICE_NAME or REGION in .env file.")
    exit(1)

# Load only the environment variables from .env
env_vars = {}
with open(".env") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):  # Ignore comments
            key, value = line.split("=", 1)
            env_vars[key] = value

# Exclude variables that should not be set manually in Cloud Run
excluded_vars = {"PORT", "SERVICE_NAME", "REGION"}
env_vars = {key: value for key, value in env_vars.items() if key not in excluded_vars}

# Convert to --set-env-vars format
env_vars_str = ",".join([f"{key}={value}" for key, value in env_vars.items()])

# Construct the gcloud command
command = f"gcloud run services update {SERVICE_NAME} --region {REGION} --set-env-vars {env_vars_str}"

print(f"Running command: {command}")

# Execute the command
os.system(command)