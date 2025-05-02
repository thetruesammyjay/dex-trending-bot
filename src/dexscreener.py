import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict
from config.config import Config
import logging

logger = logging.getLogger(__name__)

def get_top_trending_tokens() -> List[Dict[str, str]]:
    """
    Fetches top trending tokens from DexScreener
    Returns list of dicts with 'name' and 'symbol' keys
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
        response = requests.get(Config.DEXSCREENER_URL, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        tokens = []
        
        # This selector needs to be verified on live site
        trending_items = soup.select('.trending-item')[:Config.TRENDING_TOKENS_LIMIT]
        
        for item in trending_items:
            name = item.select('.token-name')[0].text.strip()
            symbol = item.select('.token-symbol')[0].text.strip()
            tokens.append({'name': name, 'symbol': symbol})
            
        logger.debug(f"Fetched {len(tokens)} trending tokens")
        return tokens
        
    except Exception as e:
        logger.error(f"Failed to fetch trending tokens: {str(e)}")
        return []