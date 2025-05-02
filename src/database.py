import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "processed_accounts.db"

class DeduplicationDB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self._create_table()
    
    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_accounts (
            account_id TEXT PRIMARY KEY,
            token_symbol TEXT,
            first_seen TIMESTAMP,
            last_seen TIMESTAMP,
            times_seen INTEGER DEFAULT 1
        )
        """)
        self.conn.commit()
    
    def is_duplicate(self, account_id, token_symbol, cooldown_hours=24):
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT last_seen, times_seen FROM processed_accounts 
        WHERE account_id = ? AND token_symbol = ?
        """, (account_id, token_symbol))
        
        result = cursor.fetchone()
        
        if not result:
            return False
        
        last_seen, times_seen = result
        last_seen = datetime.fromisoformat(last_seen)
        cooldown = timedelta(hours=cooldown_hours)
        
        return datetime.now() - last_seen < cooldown
    
    def record_account(self, account_id, token_symbol):
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        
        # Try to update existing record
        cursor.execute("""
        UPDATE processed_accounts 
        SET last_seen = ?, times_seen = times_seen + 1
        WHERE account_id = ? AND token_symbol = ?
        """, (now, account_id, token_symbol))
        
        # If no rows were updated, insert new record
        if cursor.rowcount == 0:
            cursor.execute("""
            INSERT INTO processed_accounts 
            (account_id, token_symbol, first_seen, last_seen)
            VALUES (?, ?, ?, ?)
            """, (account_id, token_symbol, now, now))
        
        self.conn.commit()
    
    def cleanup_old_records(self, days_to_keep=30):
        cutoff = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
        cursor = self.conn.cursor()
        cursor.execute("""
        DELETE FROM processed_accounts 
        WHERE last_seen < ?
        """, (cutoff,))
        self.conn.commit()
        return cursor.rowcount