import tweepy
from typing import List, Dict
from config.config import Config
from config.secrets import Config as Secrets
from .database import DeduplicationDB
import logging

logger = logging.getLogger(__name__)
db = DeduplicationDB()

def setup_twitter_client() -> tweepy.Client:
    """Initialize and return Twitter API client"""
    return tweepy.Client(
        bearer_token=Secrets.TWITTER_BEARER_TOKEN,
        wait_on_rate_limit=True
    )

def find_relevant_twitter_accounts(token: Dict[str, str]) -> List[Dict]:
    """Find accounts tweeting about specific token"""
    client = setup_twitter_client()
    query = build_search_query(token)
    
    try:
        response = client.search_recent_tweets(
            query=query,
            max_results=Config.TWITTER_MAX_RESULTS,
            tweet_fields=Config.TWITTER_TWEET_FIELDS,
            user_fields=Config.TWITTER_USER_FIELDS,
            expansions=Config.TWITTER_EXPANSIONS
        )
        return process_twitter_response(response, token)
    except tweepy.TweepyException as e:
        logger.error(f"Twitter search failed for {token['name']}: {str(e)}")
        return []

def build_search_query(token: Dict[str, str]) -> str:
    """Construct Twitter search query for a token"""
    return f"{token['name']} OR {token['symbol']} -is:retweet has:verified"

def process_twitter_response(response, token: Dict[str, str]) -> List[Dict]:
    """Process Twitter API response and filter accounts"""
    if not response.includes or 'users' not in response.includes:
        return []
    
    valid_accounts = []
    for user in response.includes['users']:
        if is_eligible_account(user):
            account_id = f"{user.username}_{token['symbol']}"
            
            if not db.is_duplicate(account_id, token['symbol']):
                account_data = create_account_data(user, token)
                valid_accounts.append(account_data)
                db.record_account(account_id, token['symbol'])
    
    db.cleanup_old_records()
    return valid_accounts

def is_eligible_account(user) -> bool:
    """Check if account meets criteria"""
    return (user.verified and 
            user.public_metrics['followers_count'] >= Config.MIN_FOLLOWERS)

def create_account_data(user, token: Dict[str, str]) -> Dict:
    """Create account data dictionary"""
    return {
        'username': user.username,
        'followers': user.public_metrics['followers_count'],
        'url': f"https://twitter.com/{user.username}",
        'token_name': token['name'],
        'token_symbol': token['symbol'],
        'timestamp': datetime.now().isoformat()
    }