# plugins/website.py

import os
from datetime import datetime
import pyautogui
from typing import Dict, Any

def register(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Register 'website' command, open a given website.
    """

    speak = context["tts"]

    def website_handler(args: Dict[str, Any]) -> str:
        params = args.get("params", [])
        site = {
            "google": "https://www.google.com",
            "youtube": "https://www.youtube.com",
            "github": "https://www.github.com",
            "duckduckgo": "https://www.duckduckgo.com",
            "wikipedia": "https://www.wikipedia.org",
            "facebook": "https://www.facebook.com",
            "reddit": "https://www.reddit.com", 
        }
        if not params:
            return "Please provide a URL to open."
        if params[0] in site:
            url = site[params[0].lower()]
        else :
            if params[0].startswith("http://") or params[0].startswith("https://"):
                url = " ".join(params)
            else:
                query = " ".join(params)
                url = f"https://www.google.com/search?q={query}"
                speak(f"Searching for {query} on Google and opening results.")
        try:
            os.startfile(url)
        except Exception as e:
            return f"Error opening website: {e}"
        return f"Opened website: {url}"
        
    return {
        "web": website_handler,
        "website": website_handler,
        "open": website_handler,
        "go": website_handler,
        "search": website_handler,
        "browse": website_handler,
        "visit": website_handler,
    }