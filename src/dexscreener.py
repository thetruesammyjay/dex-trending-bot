import tweepy
import logging
from typing import List, Dict
from config.config import Config
from config.secrets import Config as Secrets
from .database import DeduplicationDB
from datetime import datetime

logger = logging.getLogger(__name__)
db = DeduplicationDB()

def setup_twitter_client() -> tweepy.Client:
    return tweepy.Client(
        bearer_token=Secrets.TWITTER_BEARER_TOKEN,
        wait_on_rate_limit=True,
        timeout=30
    )

def find_relevant_twitter_accounts(token: Dict[str, str]) -> List[Dict]:
    client = setup_twitter_client()
    query = f"{token['name']} OR {token['symbol']} -is:retweet has:verified"
    
    try:
        response = client.search_recent_tweets(
            query=query,
            max_results=Config.TWITTER_MAX_RESULTS,
            tweet_fields=['author_id', 'created_at'],
            user_fields=['username', 'verified', 'public_metrics'],
            expansions=['author_id']
        )
        return process_response(response, token)
    except tweepy.TweepyException as e:
        logger.error(f"Twitter search failed: {str(e)}")
        return []

def process_response(response, token: Dict[str, str]) -> List[Dict]:
    if not response.includes or 'users' not in response.includes:
        return []
    
    valid_accounts = []
    for user in response.includes['users']:
        if (user.verified and 
            user.public_metrics['followers_count'] >= Config.MIN_FOLLOWERS):
            account_id = f"{user.username}_{token['symbol']}"
            
            if not db.is_duplicate(account_id, token['symbol']):
                valid_accounts.append({
                    'username': user.username,
                    'followers': user.public_metrics['followers_count'],
                    'url': f"https://twitter.com/{user.username}",
                    'token_name': token['name'],
                    'token_symbol': token['symbol'],
                    'timestamp': datetime.now().isoformat()
                })
                db.record_account(account_id, token['symbol'])
    
    db.cleanup_old_records()
    return valid_accounts
