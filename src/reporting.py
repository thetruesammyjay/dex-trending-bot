import csv
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from config.config import Config
from config.secrets import Config as Secrets
import requests
import logging

logger = logging.getLogger(__name__)

def generate_report(accounts: List[Dict]) -> str:
    """Generate CSV report and return file path"""
    report_path = get_report_path()
    fieldnames = [
        'timestamp', 
        'username', 
        'followers', 
        'url', 
        'token_name',
        'token_symbol'
    ]
    
    try:
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(accounts)
        
        logger.info(f"Generated report at {report_path}")
        return report_path
    except Exception as e:
        logger.error(f"Failed to generate report: {str(e)}")
        raise

def send_to_telegram(file_path: str) -> bool:
    """Send CSV file to Telegram"""
    try:
        with open(file_path, 'rb') as file:
            response = requests.post(
                Config.TELEGRAM_API_URL.format(token=Secrets.TELEGRAM_BOT_TOKEN),
                files={'document': file},
                data={'chat_id': Secrets.TELEGRAM_CHAT_ID}
            )
            response.raise_for_status()
        
        logger.info("Report successfully sent to Telegram")
        return True
    except Exception as e:
        logger.error(f"Failed to send to Telegram: {str(e)}")
        return False

def get_report_path() -> str:
    """Generate report file path with timestamp"""
    reports_dir = Path("data") / "historical"
    reports_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(reports_dir / f"trending_report_{timestamp}.csv")