# Echo The Duck - A simple voice assistant in Python
# Author: TheOnlyDuckxx
# core.py
# ==============================================================================================

import os
import importlib
import json
from vosk import Model, KaldiRecognizer
import pyttsx3
import sys
import threading
import pyaudio
from typing import Any, Dict, Callable, Tuple
from fuzzywuzzy import fuzz


FUZZY_THRESHOLD = 70

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def load_config(path: str = "config.json") -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def init_tts(config, assistant_name):
    """
    Initialize the TTS system using pyttsx3.
    """
    engine = pyttsx3.init()
    lock = threading.Lock()
    rate = config.get("rate")
    if rate:
        engine.setProperty("rate", rate)

    voices = engine.getProperty("voices")
    selected_voice = None
    for v in voices:
        langs = getattr(v, "languages", None)
        if not langs:
            continue
        first = langs[0]
        if isinstance(first, (bytes, bytearray)):
            try:
                first = first.decode()
            except:
                pass
        if isinstance(first, str) and "en" in first.lower():
            selected_voice = v.id
            break

    if selected_voice:
        engine.setProperty("voice", selected_voice)
    else:
        default_voice = voices[0].id if voices else None
        if default_voice:
            engine.setProperty("voice", default_voice)

    def speak(text: str):
        print(f"[{assistant_name}]: {text}")
        with lock:
            engine.say(text)
            engine.runAndWait()

    return speak

def init_stt(
    config: Dict[str, Any],
    assistant_conf: Dict[str, Any],
    command_list: list
) -> Tuple[Callable[[], str], Callable[[], str], Callable[[], str]]:
    """
    Initialize the STT system using Vosk.
    """
    model_path = config.get("stt", {}).get("model_path", "")
    if not model_path:
        raise RuntimeError("STT model_path not set in config.json")

    sample_rate = 16000
    model = Model(model_path)

    wake_list    = assistant_conf.get("wake_words", [assistant_conf.get("name", "")])
    wake_grammar = json.dumps([w.lower() for w in wake_list])
    wake_rec     = KaldiRecognizer(model, sample_rate, wake_grammar)

    cmd_grammar = json.dumps([cmd.lower() for cmd in command_list])
    cmd_rec     = KaldiRecognizer(model, sample_rate, cmd_grammar)

    full_rec    = KaldiRecognizer(model, sample_rate)

    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16,
                     channels=1,
                     rate=sample_rate,
                     input=True,
                     frames_per_buffer=8000)
    stream.start_stream()

    def wait_for_wake() -> str:
        """Attendre une des wake-phrases."""
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            if wake_rec.AcceptWaveform(data):
                res = json.loads(wake_rec.Result())
                txt = res.get("text", "")
                if txt:
                    return txt

    def wait_for_command() -> str:
        """Attendre une des commandes connues (sans argument)."""
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            if cmd_rec.AcceptWaveform(data):
                res = json.loads(cmd_rec.Result())
                txt = res.get("text", "")
                if txt:
                    return txt

    def listen_full() -> str:
        """Reconnaissance libre pour récupérer les paramètres."""
        full_rec.Reset()
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            if full_rec.AcceptWaveform(data):
                res = json.loads(full_rec.Result())
                return res.get("text", "")

    return wait_for_wake, wait_for_command, listen_full

def load_plugins(context: Dict[str, Any]) -> Dict[str, Callable[[Dict[str, Any]], str]]:
    handlers: Dict[str, Callable[[Dict[str, Any]], str]] = {}
    plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
    for fname in os.listdir(plugins_dir):
        if not fname.endswith(".py") or fname == "__init__.py":
            continue
        mod = importlib.import_module(f"plugins.{fname[:-3]}")
        if hasattr(mod, "register"):
            handlers.update(mod.register(context))
    return handlers

def parse_command(raw_text: str) -> Tuple[str, Dict[str, Any]]:
    parts = raw_text.strip().split()
    if not parts:
        return "", {"raw": raw_text, "params": []}
    command = parts[0].lower()
    return command, {"raw": raw_text, "params": parts[1:]}

def find_best_match(cmd: str, candidates: Dict[str, Any]) -> Tuple[str, int]:
    """
    Retourne la meilleure commande et son score de similarité.
    """
    best_cmd, best_score = None, 0
    for key in candidates.keys():
        score = ratio(cmd, key)
        if score > best_score:
            best_cmd, best_score = key, score
    return best_cmd, best_score

def ratio(a: str, b: str) -> int:
    return fuzz.ratio(a, b)

def partial_ratio(a: str, b: str) -> int:
    return fuzz.partial_ratio(a, b)

def main():
    config_path = "config.json"
    config = load_config(config_path)

    assistant_conf = config.get("assistant", {})
    assistant_name = assistant_conf.get("name", "duck")
    wake_phrases = [wp.lower() for wp in assistant_conf.get(
        "wake_words", [assistant_name]
    )]
    wake_threshold = assistant_conf.get("wake_threshold", 60)

    tts = init_tts(config.get("tts", {}), assistant_name)
    context  = { "config": config, "config_path": config_path, "tts": tts }
    handlers = load_plugins(context)
    command_list = list(handlers.keys())


    wait_for_wake, wait_for_command, listen_full = init_stt(
        config, assistant_conf, command_list
    )

    tts(f"{assistant_name} is ready. Say one of your wake words to wake me.")

    while True:
        wake_txt = wait_for_wake()
        print(f"[WAKE]: {wake_txt}")
        tts("Yes?")

        cmd_txt = wait_for_command()
        print(f"[COMMAND KEYWORD]: {cmd_txt}")
        command = cmd_txt.strip().lower()

        if command in ("exit", "quit"):
            break

        if command not in handlers:
            tts(f"Command '{command}' not recognized.")
            continue

        tts(f"What would you like {assistant_name} to do for '{command}'?")
        args_txt = listen_full()
        print(f"[ARGS]: {args_txt}")

        args = { 
            "raw": args_txt, 
            "params": args_txt.strip().split() if args_txt else [] 
        }

        try:
            response = handlers[command](args)
        except Exception as e:
            response = f"Error executing '{command}': {e}"

        tts(response)






        
if __name__ == "__main__":
    main()