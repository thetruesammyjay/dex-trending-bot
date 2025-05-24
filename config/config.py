from datetime import timedelta
from typing import Final

class Config:
    # API Settings
    DEXSCREENER_URL: Final[str] = "https://api.dexscreener.com/latest/dex/tokens/trending"
    TWITTER_MAX_RESULTS: Final[int] = 50
    TELEGRAM_API_URL: Final[str] = "https://api.telegram.org/bot{token}/sendDocument"
    
    # Behavior Configs
    TRENDING_TOKENS_LIMIT: Final[int] = 10
    MIN_FOLLOWERS: Final[int] = 2000
    CHECK_INTERVAL_HOURS: Final[int] = 6
    DEDUPE_COOLDOWN_HOURS: Final[int] = 24
    DATA_RETENTION_DAYS: Final[int] = 30
    
    # Headers
    REQUEST_HEADERS: Final[dict] = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9'
    }
