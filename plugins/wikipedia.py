import warnings
from bs4 import GuessedAtParserWarning
import wikipedia
from typing import Dict, Any

warnings.simplefilter('ignore', category=GuessedAtParserWarning)

def register(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Register the 'wiki' and 'wikipedia' commands to search on Wikipedia
    """
    speak = context["tts"]

    def wiki_handler(args: Dict[str, Any]) -> str:
        params = args.get("params", [])
        if not params:
            return "Please provide a search term for Wikipedia."
        query = " ".join(params)
        speak("Searching Wikipedia...")

        try:
            result = wikipedia.summary(query, sentences=2, auto_suggest=False)
        except wikipedia.exceptions.DisambiguationError as e:
            options = e.options[:5]
            return f"Multiple results found for '{query}'. Did you mean: {', '.join(options)}?"
        except wikipedia.exceptions.PageError:
            return f"I couldn't find a page for '{query}'."
        except Exception as e:
            return f"An error occurred while searching Wikipedia: {e}"

        return result

    return {
        "wiki": wiki_handler,
        "wikipedia": wiki_handler,
    }