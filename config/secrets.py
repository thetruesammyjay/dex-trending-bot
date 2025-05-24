import os
from dotenv import load_dotenv
from .config import Config

def load_secrets():
    """Load environment variables with validation"""
    load_dotenv()
    
    required_vars = {
        'TWITTER_BEARER_TOKEN': os.getenv('TWITTER_BEARER_TOKEN'),
        'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
        'TELEGRAM_CHAT_ID': os.getenv('TELEGRAM_CHAT_ID')
    }
    
    if not all(required_vars.values()):
        missing = [k for k, v in required_vars.items() if not v]
        raise ValueError(f"Missing required env vars: {missing}")
    
    # Assign to Config class
    Config.TWITTER_BEARER_TOKEN = required_vars['TWITTER_BEARER_TOKEN']
    Config.TELEGRAM_BOT_TOKEN = required_vars['TELEGRAM_BOT_TOKEN']
    Config.TELEGRAM_CHAT_ID = required_vars['TELEGRAM_CHAT_ID']
