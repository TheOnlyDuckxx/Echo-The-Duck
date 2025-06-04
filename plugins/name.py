# plugins/name.py

import os
import json
from typing import Dict, Any

def register(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Register the 'name' command to return or set the assistant's name.
    """
    speak = context["tts"]
    config = context["config"]
    config_path = context["config_path"]

    def name_handler(args: Dict[str, Any]) -> str:
        params = args.get("params", [])
        if not params:
            current = config.get("assistant", {}).get("name", "duck")
            return f"My current name is {current}."
        new_name = " ".join(params)
        
        if "assistant" not in config:
            config["assistant"] = {}
        config["assistant"]["name"] = new_name

        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            return f"Error saving new name: {e}"
        
        speak(f"My name has been changed to {new_name}.")
        return f"Name updated to {new_name}."

    return {
        "name": name_handler,
        "setname": name_handler,
    }