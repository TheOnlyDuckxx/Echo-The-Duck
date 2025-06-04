# plugins/screenshot.py

import os
from datetime import datetime
import pyautogui
from typing import Dict, Any

def register(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Register 'screenshot' command, takes a screenshot and saves it to the configured folder.
    """
    screenshot_folder = context["config"].get("screenshots", {}).get("folder", "")

    speak = context["tts"]

    def screenshot_handler(args: Dict[str, Any]) -> str:
        if not screenshot_folder:
            return "No screenshot folder configured."
        os.makedirs(screenshot_folder, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        img_path = os.path.join(screenshot_folder, filename)

        img = pyautogui.screenshot()
        try:
            img.save(img_path)
        except Exception as e:
            return f"Error saving screenshot: {e}"

        speak(f"Screenshot saved as {filename}")
        return f"Screenshot saved to {img_path}"

    return {
        "screenshot": screenshot_handler,
        "capture": screenshot_handler,
        "screen": screenshot_handler,
    }