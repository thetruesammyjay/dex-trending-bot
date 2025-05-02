import time
from datetime import datetime
from .dexscreener import get_top_trending_tokens
from .twitter_search import find_relevant_twitter_accounts
from .reporting import generate_report, send_to_telegram
from config.secrets import load_secrets
from config.config import Config
import logging

# Initialize logging
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def run_analysis():
    logger.info("🚀 Starting analysis cycle")
    
    try:
        
        load_secrets()
        
        tokens = get_top_trending_tokens()
        logger.info(f"🔍 Found {len(tokens)} trending tokens")
        
        all_accounts = []
        for token in tokens:
            accounts = find_relevant_twitter_accounts(token)
            all_accounts.extend(accounts)
            logger.info(f"🐦 Found {len(accounts)} accounts for {token['name']}")
        
        if all_accounts:
            report_path = generate_report(all_accounts)
            send_to_telegram(report_path)
            logger.info(f"📊 Report generated with {len(all_accounts)} accounts")
        else:
            logger.info("⚠️ No valid accounts found")
            
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
    finally:
        logger.info(f"✅ Analysis completed at {datetime.now()}")

def start_scheduler():
    while True:
        run_analysis()
        sleep_seconds = Config.CHECK_INTERVAL_HOURS * 3600
        logger.info(f"⏳ Next run in {Config.CHECK_INTERVAL_HOURS} hours...")
        time.sleep(sleep_seconds)

if __name__ == "__main__":
    start_scheduler()