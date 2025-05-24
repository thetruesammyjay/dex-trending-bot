from datetime import datetime, timedelta
import json
from typing import Any, Dict

def format_timedelta(delta: timedelta) -> str:
    """Convert timedelta to human-readable format"""
    total_seconds = int(delta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"

def safe_json_serialize(data: Dict[str, Any]) -> str:
    """Safely serialize dictionary to JSON"""
    def default(o):
        if isinstance(o, (datetime, timedelta)):
            return o.isoformat()
        raise TypeError(f"Type {type(o)} not serializable")
    return json.dumps(data, default=default, indent=2)
