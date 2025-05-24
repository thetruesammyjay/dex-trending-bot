import sqlite3
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from config.config import Config

logger = logging.getLogger(__name__)

class DeduplicationDB:
    def __init__(self):
        self.db_path = Path(__file__).parent.parent / "data" / "processed_accounts.db"
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database with proper settings"""
        self.db_path.parent.mkdir(exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, timeout=20)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_accounts (
            account_id TEXT NOT NULL,
            token_symbol TEXT NOT NULL,
            first_seen TIMESTAMP NOT NULL,
            last_seen TIMESTAMP NOT NULL,
            times_seen INTEGER DEFAULT 1,
            PRIMARY KEY (account_id, token_symbol)
        )
        """)
        self.conn.commit()
    
    def is_duplicate(self, account_id: str, token_symbol: str) -> bool:
        """
        Check if account-token pair has been seen within cooldown period
        Returns True if duplicate, False if new/expired
        """
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT last_seen FROM processed_accounts
        WHERE account_id = ? AND token_symbol = ?
        """, (account_id, token_symbol))
        
        result = cursor.fetchone()
        if not result:
            return False
        
        last_seen = datetime.fromisoformat(result[0])
        cooldown = timedelta(hours=Config.DEDUPE_COOLDOWN_HOURS)
        return datetime.now() - last_seen < cooldown
    
    def record_account(self, account_id: str, token_symbol: str) -> None:
        """Record or update account-token interaction"""
        now = datetime.now().isoformat()
        cursor = self.conn.cursor()
        
        # Try to update existing record
        cursor.execute("""
        UPDATE processed_accounts 
        SET last_seen = ?, times_seen = times_seen + 1
        WHERE account_id = ? AND token_symbol = ?
        """, (now, account_id, token_symbol))
        
        # Insert new record if not exists
        if cursor.rowcount == 0:
            cursor.execute("""
            INSERT INTO processed_accounts 
            (account_id, token_symbol, first_seen, last_seen)
            VALUES (?, ?, ?, ?)
            """, (account_id, token_symbol, now, now))
        
        self.conn.commit()
    
    def cleanup_old_records(self) -> int:
        """Remove records older than retention period"""
        cutoff = (datetime.now() - timedelta(days=Config.DATA_RETENTION_DAYS)).isoformat()
        cursor = self.conn.cursor()
        cursor.execute("""
        DELETE FROM processed_accounts 
        WHERE last_seen < ?
        """, (cutoff,))
        deleted_count = cursor.rowcount
        self.conn.commit()
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old records")
        
        return deleted_count
    
    def __del__(self):
        """Clean up database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()
