"""Configuration settings for the delivery app."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# App Configuration
APP_NAME = "QuickDeliver"
APP_ICON = "🚚"
PAGE_TITLE = "QuickDeliver - Customer Service"

# Database Configuration
DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

# OpenRouter API Configuration
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "anthropic/claude-3.5-sonnet"
OPENROUTER_SITE_URL = "https://quickdeliver.app"
OPENROUTER_APP_NAME = "QuickDeliver"

# Use ONLY env var for API key (never fallback to hardcoded)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# UI Configuration
THEME = {
    "primary_color": "#667eea",
    "secondary_color": "#764ba2",
    "background_color": "#f8f9fa",
    "text_color": "#333333"
}

# Session Configuration
SESSION_TIMEOUT = 3600  # 1 hour in seconds

# Demo Credentials (for mock/demo login) - moved to env for safety
DEMO_USERNAME = os.getenv("DEMO_USERNAME")
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD")
