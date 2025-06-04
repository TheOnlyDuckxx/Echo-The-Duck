# Echo The Duck Voice Assistant

A modular, Python-based voice assistant that supports offline speech recognition (Vosk), text-to-speech (pyttsx3), fuzzy command matching, and a plugin architecture. Commands are triggered via a configurable wake word and a strict Vosk grammar for command keywords.

---

## Table of Contents

- [Requirements](#requirements)  
- [Installation](#installation)  
- [Configuration](#configuration)  
  - [config.json Structure](#configjson-structure)  
  - [Example `config.json`](#example-configjson)  
- [Usage](#usage)  
  - [Launching the Assistant](#launching-the-assistant)  
  - [Interaction Flow](#interaction-flow)  
- [Available Plugins & Commands](#available-plugins--commands)  
- [Developing New Plugins](#developing-new-plugins)  
- [Troubleshooting](#troubleshooting)

---

## Requirements

- Python 3.7 or higher  
- pip (to install dependencies)  
- A Vosk model directory (for offline STT)  
- A valid OpenWeatherMap API key (for the Weather plugin)  

---

## Installation

1. **Clone or copy the repository** to your local machine.  
2. **Create a virtual environment** (recommended):  
   ```bash
   python -m venv .venv
   ```
3. **Activate** the virtual environment:  
   - **Windows (PowerShell)**  
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - **Windows (CMD)**  
     ```batch
     .\.venv\Scripts\activate.bat
     ```
   - **macOS / Linux**  
     ```bash
     source .venv/bin/activate
     ```
4. **Install dependencies** via `requirements.txt`:  
   ```bash
   pip install -r requirements.txt
   ```
   This will install:
   - `pyttsx3` (offline TTS)  
   - `fuzzywuzzy` + `python-Levenshtein` (fuzzy matching)  
   - `vosk` + `pyaudio` (offline STT)  
   - `wikipedia`, `beautifulsoup4` (Wikipedia plugin)  
   - `word2number` (timer plugin)  
   - `pyautogui` (screenshot plugin)

5. **Download a Vosk model** (e.g., `vosk-model-small-en-us-0.15`) and place it under the `models/` folder. For example:

   ```
   Echo-The-Duck/
   ├─ core.py
   ├─ requirements.txt
   ├─ config.json
   └─ models/
       └─ vosk-model-small-en-us-0.15/
            ├─ am/
            ├─ conf/
            ├─ ivector/
            └─ ...
   ```

---

## Configuration

All runtime settings live in `config.json`. You must edit this file before launching the assistant.

### config.json Structure

```jsonc
{
  "assistant": {
    "name": "duck",
    "wake_words": ["duck", "hey duck", "ok duck"],
    "wake_threshold": 60
  },
  "stt": {
    "model_path": "models/vosk-model-small-en-us-0.15"
  },
  "tts": {
    "rate": 150
  },
  "music": {
    "folder": "C:\Users\Admin\Music"
  },
  "screenshots": {
    "folder": "C:\Users\Admin\Screenshots"
  },
  "weather": {
    "apikey": "YOUR_OPENWEATHERMAP_KEY",
    "units": "metric",
    "default_city": "Paris"
  }
}
```

- **assistant**  
  - `name` (string): default name (also used as wake word).  
  - `wake_words` (array of strings): list of acceptable wake-word phrases.  
  - `wake_threshold` (integer 0–100): minimum fuzzy score to accept a wake-phrase.

- **stt**  
  - `model_path` (string): path to your Vosk model directory.

- **tts** (optional)  
  - `rate` (integer): speaking rate (words per minute) for `pyttsx3`.  

- **music**  
  - `folder` (string): absolute path to your local MP3 folder.

- **screenshots**  
  - `folder` (string): absolute path to save screenshot PNGs.

- **weather**  
  - `apikey` (string): your OpenWeatherMap API key.  
  - `units` (string): `"metric"` or `"imperial"`.  
  - `default_city` (string): fallback city when no city is spoken.

### Example `config.json`

```json
{
  "assistant": {
    "name": "Echo",
    "wake_words": ["echo", "hey echo", "ok echo"],
    "wake_threshold": 60
  },
  "stt": {
    "model_path": "models/vosk-model-small-en-us-0.15"
  },
  "tts": {
    "rate": 150
  },
  "music": {
    "folder": "C:\Users\Admin\Music"
  },
  "screenshots": {
    "folder": "C:\Users\Admin\Screenshots"
  },
  "weather": {
    "apikey": "abcd1234efgh5678ijkl9012mnop3456",
    "units": "metric",
    "default_city": "Paris"
  }
}
```

---

## Usage

### Launching the Assistant

Activate your virtual environment (if not already) and run:
```bash
python core.py
```
You should see:
```
[Echo]: Echo is ready. Say one of ['echo', 'hey echo', 'ok echo'] to wake me.
```

### Interaction Flow

The assistant uses a **3-phase** voice recognition flow:

1. **Wake-word Phase**  
   - Listens continuously to a **small grammar** consisting of your `wake_words`.  
   - Only when fuzzy‐matched above `wake_threshold`, it proceeds.  
   - Example: you say **“Echo”** or **“Hey echo”** (even slightly mispronounced), and Vosk picks up a close match.

2. **Command Keyword Phase**  
   - Prompts “Yes?” and listens to a **strict grammar** of available command keywords (e.g., `weather`, `timer`, `play`, `wiki`, `screenshot`, `name`, `exit`, etc.).  
   - Always returns exactly one of your registered handlers or asks you to repeat if not recognized.

3. **Arguments Phase**  
   - Once a command keyword is recognized, the assistant asks a follow-up question (if needed) and then receives **free-form speech** for arguments (city names, durations, search terms, etc.).  
   - The raw recognized text is split into `params` and passed to the plugin’s handler function.

#### Example Session

```
You: echo
[Echo]: Yes?
You: weather
[Echo]: What would you like Echo to do for 'weather'?
You: Berlin
[Echo]: Weather in Berlin: clear sky, temp 18°C, feels like 17°C, humidity 60%, wind 3 m/s.
```

---

## Available Plugins & Commands

- **`name` / `setname`**  
  - Show or change the assistant’s name.  
  - Usage:  
    - `You: name` → “My current name is Echo.”  
    - `You: name Bob` → “My name has been changed to Bob.”

- **`timer` / `countdown`**  
  - Sets a countdown of X minutes.  
  - Supports numbers in digits (`timer 5`) or words (`timer five`, `timer one point five`).  
  - Example:  
    ```
    You: timer two
    [Echo]: Timer set for 2 minutes.
    (After 2 minutes) [Echo]: Timer for 2 minutes is up!
    ```

- **`weather` / `forecast`**  
  - Retrieves current weather from OpenWeatherMap.  
  - Prompts for a city if not provided as an argument.  
  - Uses `config.json` API key & default city.

- **`play` / `music` / `playmusic`**  
  - Plays an MP3 from your configured music folder.  
  - You can specify a keyword to match a filename (e.g., `play imagine`) or just say `play` for a random track.

- **`screenshot` / `capture` / `screen`**  
  - Takes a desktop screenshot and saves it as a timestamped PNG in your configured folder.

- **`wiki` / `wikipedia`**  
  - Fetches a 2-sentence summary from Wikipedia for a given topic.  
  - Example:  
    ```
    You: wiki Python
    [Echo]: Python is an interpreted, high-level programming language… (etc.)
    ```

- **`search`**  
  - Opens your default web browser to search Google for a given query.  
  - Example:  
    ```
    You: search panda
    [Echo]: Searching the web for panda
    ```

- **`time`**  
  - Reads out the current system time in HH:MM:SS format.

- **`exit` / `quit`**  
  - Gracefully shuts down the assistant.

---

## Developing New Plugins

All plugins live in the `plugins/` folder. Each plugin file must contain:

1. A `register(context: Dict[str, Any])` function.  
2. `register` returns a dictionary mapping command-keywords (strings) to handler functions.  
3. Each **handler** takes a single `args` dict with:  
   - `"raw"` (the full recognized text for parameters)  
   - `"params"` (a list of words/tokens for convenience)  
4. The handler returns a **string**; the core loop will call `speak(...)` on it.

### Example Template

```python
# plugins/example.py

from typing import Dict, Any

def register(context: Dict[str, Any]) -> Dict[str, Any]:
    speak = context["tts"]
    config = context["config"]

    def example_handler(args: Dict[str, Any]) -> str:
        # args["params"] is a list of words for your command
        # Perform your logic here
        return "This is an example response!"

    return {
        "example": example_handler,
        "ex": example_handler  # alias if desired
    }
```

After saving `example.py`, restart `core.py`. The new command `"example"` (and `"ex"`) become available in the “Command Keyword” grammar.

---

## Troubleshooting

- **“Folder '' does not contain model files”**  
  - Your `stt.model_path` is empty or incorrect. Check `config.json` → `stt.model_path` points to an existing Vosk model directory.

- **Wake-word never triggers** (`Ignoring word missing in vocabulary` warnings)  
  - Vosk’s small model might not include proper nouns (like “Echo”). Switch your wake word to a common word in the model’s vocabulary (e.g., “hello”), or use fuzzy matching instead of a strict grammar.  
  - To use fuzzy matching for wake detection, remove the Vosk grammar and revert to a loop that checks `partial_ratio("echo", raw_text)`.

- **No internet for Wikipedia / Weather**  
  - Wikipedia and weather plugins rely on Internet access. If offline, these commands will return an error.

---

With this README, you should have everything needed to install dependencies, configure your settings, and start using or extending Echo The Duck. Feel free to add more plugins or tweak thresholds to match your environment and accent. Enjoy!
