import os
from dotenv import load_dotenv
from .config import Config

def load_secrets():
    load_dotenv()
    
    Config.TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
    Config.TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    Config.TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    # Validate required secrets
    required = {
        "TWITTER_BEARER_TOKEN": Config.TWITTER_BEARER_TOKEN,
        "TELEGRAM_BOT_TOKEN": Config.TELEGRAM_BOT_TOKEN,
        "TELEGRAM_CHAT_ID": Config.TELEGRAM_CHAT_ID
    }
    
    missing = [k for k, v in required.items() if not v]
    if missing:
        raise ValueError(f"Missing required environment variables: {missing}")