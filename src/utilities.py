from datetime import datetime, timedelta
from typing import Any, Dict
import json

def format_timedelta(delta: timedelta) -> str:
    """Format timedelta as human-readable string"""
    hours, remainder = divmod(delta.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

def safe_json_dumps(data: Dict[str, Any]) -> str:
    """Safely serialize dictionary to JSON"""
    def default_serializer(obj):
        if isinstance(obj, (datetime, timedelta)):
            return str(obj)
        raise TypeError(f"Type {type(obj)} not serializable")
    
    return json.dumps(data, default=default_serializer, indent=2)