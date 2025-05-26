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
        
        # Debug logging to see what we actually received
        logger.debug(f"API Response structure: {type(data)}")
        if isinstance(data, dict):
            logger.debug(f"API Response keys: {list(data.keys())}")
        elif isinstance(data, list):
            logger.debug(f"API Response is list with {len(data)} items")
        
        # Check if data exists and has the expected structure
        if not data:
            logger.warning("Empty response from DexScreener API")
            return []
        
        # Handle different response formats
        tokens_data = None
        
        # Case 1: Response is a list of tokens directly
        if isinstance(data, list):
            tokens_data = data
            logger.debug("Response is direct list of tokens")
        
        # Case 2: Response has 'tokens' key
        elif isinstance(data, dict) and 'tokens' in data:
            tokens_data = data['tokens']
            logger.debug("Found tokens in 'tokens' key")
        
        # Case 3: Response has 'pairs' key (original format)
        elif isinstance(data, dict) and 'pairs' in data:
            pairs = data['pairs']
            if isinstance(pairs, list) and len(pairs) > 0:
                # Extract baseToken from pairs
                tokens_data = []
                for pair in pairs:
                    if pair.get('baseToken'):
                        tokens_data.append(pair['baseToken'])
                logger.debug("Extracted baseTokens from pairs")
        
        # Case 4: Check other possible keys
        elif isinstance(data, dict):
            possible_keys = ['data', 'results', 'trending']
            for key in possible_keys:
                if key in data and isinstance(data[key], list):
                    tokens_data = data[key]
                    logger.debug(f"Found tokens in '{key}' key")
                    break
        
        if not tokens_data:
            logger.warning("Could not find token data in API response")
            logger.debug(f"Response structure: {data}")
            return []
            
        if not isinstance(tokens_data, list):
            logger.warning(f"Token data is not a list, got: {type(tokens_data)}")
            return []
            
        if len(tokens_data) == 0:
            logger.warning("Empty tokens list from API")
            return []
        
        tokens = []
        for i, token_data in enumerate(tokens_data[:Config.TRENDING_TOKENS_LIMIT]):
            try:
                # Handle different token data structures
                name = None
                symbol = None
                
                # Direct token object
                if isinstance(token_data, dict):
                    name = token_data.get('name')
                    symbol = token_data.get('symbol')
                    
                    # If not found, try common alternatives
                    if not name:
                        name = token_data.get('tokenName') or token_data.get('token_name')
                    if not symbol:
                        symbol = token_data.get('tokenSymbol') or token_data.get('token_symbol')
                
                if not name or not symbol:
                    logger.warning(f"Token {i} missing name or symbol: name={name}, symbol={symbol}")
                    logger.debug(f"Token data keys: {list(token_data.keys()) if isinstance(token_data, dict) else 'Not a dict'}")
                    continue
                
                tokens.append({
                    'name': str(name),
                    'symbol': str(symbol)
                })
                
            except Exception as e:
                logger.warning(f"Error processing token {i}: {str(e)}")
                continue
        
        logger.info(f"Successfully parsed {len(tokens)} tokens from API")
        return tokens
        
    except requests.exceptions.RequestException as e:
        logger.error(f"DexScreener API request error: {str(e)}")
        return []
    except requests.exceptions.JSONDecodeError as e:
        logger.error(f"DexScreener API JSON decode error: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"DexScreener API unexpected error: {str(e)}")
        return []
