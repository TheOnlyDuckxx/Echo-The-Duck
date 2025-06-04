# plugins/time.py

from datetime import datetime
from typing import Dict, Any

def register(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Register 'time' command, gives the current time or date.
    """

    speak = context["tts"]

    def time_handler(args: Dict[str, Any]) -> str:
        date_time = datetime.now()
        time_str = date_time.strftime("%H:%M:%S")
        return f"The current time is {time_str}"
    
    def date_handler(args: Dict[str, Any]) -> str:
        date_time = datetime.now()
        date_str = date_time.strftime("%A, %B %d, %Y")
        return f"Today's date is {date_str}"

    return {
        "time": time_handler,
        "date": date_handler,
    }