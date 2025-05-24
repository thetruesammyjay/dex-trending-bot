import requests
import logging
from typing import List, Dict
from config.config import Config
from datetime import datetime

logger = logging.getLogger(__name__)

def get_top_trending_tokens() -> List[Dict[str, str]]:
    """Fetch trending tokens from DexScreener API"""
    try:
        response = requests.get(
            Config.DEXSCREENER_URL,
            headers=Config.REQUEST_HEADERS,
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        return [
            {
                'name': token['baseToken']['name'],
                'symbol': token['baseToken']['symbol']
            }
            for token in data.get('pairs', [])[:Config.TRENDING_TOKENS_LIMIT]
        ]
    except Exception as e:
        logger.error(f"DexScreener API error: {str(e)}")
        return []
