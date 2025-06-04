# plugins/timer.py

import threading
from typing import Dict, Any
from word2number import w2n   # ← nouveau

def register(context: Dict[str, Any]) -> Dict[str, Any]:
    speak = context["tts"]

    def timer_handler(args: Dict[str, Any]) -> str:
        params = args.get("params", [])
        if not params:
            return "Please specify a duration in minutes, e.g. 'timer five'."

        param_str = " ".join(params)
        try:
            minutes = float(w2n.word_to_num(param_str))
            if minutes <= 0:
                return "Please provide a positive number of minutes."
        except Exception:
            return f"Invalid duration '{param_str}'. Please give a number of minutes."

        seconds = minutes * 60

        def on_timeout():
            disp = int(minutes) if minutes.is_integer() else minutes
            speak(f"⏰ Timer for {disp} minute{'s' if disp!=1 else ''} is up!")

        t = threading.Timer(seconds, on_timeout)
        t.daemon = True
        t.start()

        disp = int(minutes) if minutes.is_integer() else minutes
        return f"Timer set for {disp} minute{'s' if disp!=1 else ''}."

    return {
        "timer": timer_handler,
        "countdown": timer_handler,
    }