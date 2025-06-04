# plugins/music.py

import os
import glob
import random
from typing import Dict, Any

def register(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Register the 'play' command (and aliases) to play an audio file
    using the OS default player on Windows.
    Expects in config.json:
      "music": { "folder": "C:\\Users\\Admin\\Music" }
    """
    music_folder = context["config"].get("music", {}).get("folder", "")
    speak = context["tts"]

    def play_handler(args: Dict[str, Any]) -> str:
        params = args.get("params", [])

        if params:
            query = " ".join(params).lower()
            pattern = os.path.join(music_folder, f"*{query}*.mp3")
            files = glob.glob(pattern)
            if not files:
                return f"No track found matching '{query}'."
            track = files[0]
        else:
            files = glob.glob(os.path.join(music_folder, "*.mp3"))
            if not files:
                return "No music files found in folder."
            track = random.choice(files)

        track_name = os.path.basename(track)

        try:
            os.startfile(track)
        except Exception as e:
            return f"Error launching '{track_name}': {e}"

        return f"Started playing {track_name}"

    return {
        "play": play_handler,
        "music": play_handler,
        "playmusic": play_handler,
    }
