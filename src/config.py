import importlib
import os
import sys
from dotenv import load_dotenv

# Ensure Python 3.12+ compatibility for cassandra/cassio (which requires asyncore)
if "asyncore" not in sys.modules:
    try:
        sys.modules["asyncore"] = importlib.import_module("pyasyncore")
    except Exception:
        pass

# Load local .env if available
load_dotenv()

# App Constants & Defaults
APP_PAGE_TITLE = "SportPulse AI | Next-Gen Sports Intelligence"
APP_PAGE_ICON = "⚡"

DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DEFAULT_KEYSPACE = "default_keyspace"
DEFAULT_TABLE_NAME = "sports_intelligence_vault"
DEFAULT_IN_MEMORY_TABLE = "sports_in_memory_vault"

SUPPORTED_GROQ_MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "allam-2-7b",
]


def get_available_groq_models(api_key: str = "") -> list:
    """Fetch active chat models from Groq API for this account, or return a curated fallback list."""
    fallback_models = [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "qwen/qwen3.8-27b",
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "allam-2-7b",
    ]
    if not api_key:
        return fallback_models

    try:
        import json
        import urllib.request

        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/models",
            headers={"Authorization": f"Bearer {api_key.strip()}", "User-Agent": "SportPulse/1.0"},
        )
        with urllib.request.urlopen(req, timeout=5) as res:
            data = json.loads(res.read())
            models = [
                m["id"]
                for m in data.get("data", [])
                if m.get("active", True)
                and not any(x in m["id"] for x in ["whisper", "prompt-guard", "orpheus", "safeguard"])
            ]
            if models:
                preferred_order = [
                    "openai/gpt-oss-120b",
                    "openai/gpt-oss-20b",
                    "qwen/qwen3.8-27b",
                    "llama-3.3-70b-versatile",
                    "llama-3.1-8b-instant",
                ]
                sorted_models = [m for m in preferred_order if m in models] + [
                    m for m in models if m not in preferred_order
                ]
                return sorted_models
    except Exception:
        pass
    return fallback_models


DEFAULT_SPORTS_URLS = [
    "https://en.wikipedia.org/wiki/Virat_Kohli",
    "https://en.wikipedia.org/wiki/Rohit_Sharma",
    "https://en.wikipedia.org/wiki/MS_Dhoni",
    "https://en.wikipedia.org/wiki/Sachin_Tendulkar",
    "https://en.wikipedia.org/wiki/ICC_Men%27s_Cricket_World_Cup",
    "https://en.wikipedia.org/wiki/Indian_Premier_League",
    "https://en.wikipedia.org/wiki/Lionel_Messi",
    "https://en.wikipedia.org/wiki/Cristiano_Ronaldo",
    "https://en.wikipedia.org/wiki/UEFA_Champions_League",
    "https://en.wikipedia.org/wiki/FIFA_World_Cup",
    "https://en.wikipedia.org/wiki/Premier_League",
    "https://en.wikipedia.org/wiki/Formula_One",
    "https://en.wikipedia.org/wiki/Lewis_Hamilton",
    "https://en.wikipedia.org/wiki/Max_Verstappen",
    "https://en.wikipedia.org/wiki/LeBron_James",
    "https://en.wikipedia.org/wiki/Michael_Jordan",
    "https://en.wikipedia.org/wiki/Roger_Federer",
    "https://en.wikipedia.org/wiki/Rafael_Nadal",
    "https://en.wikipedia.org/wiki/Novak_Djokovic",
    "https://en.wikipedia.org/wiki/Olympic_Games",
]

# Sport Category Preset Queries
SPORT_PRESETS = {
    "🏏 Cricket": [
        ("🔥 Virat Kohli Chase Masterclass Records", "What are Virat Kohli's major batting records in international cricket and run chases?"),
        ("🏆 MS Dhoni vs Rohit Sharma Captaincy Legacy", "What are MS Dhoni and Rohit Sharma's major captaincy achievements in ICC tournaments and IPL?"),
    ],
    "⚽ Football": [
        ("⭐ Lionel Messi World Cup & Ballon d'Or Records", "What are Lionel Messi's major achievements in the FIFA World Cup and career records?"),
        ("👑 Cristiano Ronaldo Champions League Legacy", "What are Cristiano Ronaldo's all-time records in the UEFA Champions League?"),
    ],
    "🏎️ Formula 1": [
        ("🏁 Lewis Hamilton vs Michael Schumacher 7 Titles", "What are Lewis Hamilton's career achievements and race win records in Formula One?"),
        ("🦁 Max Verstappen Record-Breaking Seasons", "What records did Max Verstappen set in recent Formula One World Championships?"),
    ],
    "🏀 Basketball": [
        ("🏀 LeBron James All-Time NBA Scoring Record", "What are LeBron James' major NBA career achievements and championships?"),
        ("🐐 Michael Jordan 6-0 Finals Legacy", "What is Michael Jordan's championship record with the Chicago Bulls?"),
    ],
    "🎾 Tennis": [
        ("🎾 Big Three (Federer, Nadal, Djokovic) Grand Slams", "What are the Grand Slam singles title records of Roger Federer, Rafael Nadal, and Novak Djokovic?"),
        ("👑 Rafael Nadal Roland Garros Clay Dominance", "How many French Open titles has Rafael Nadal won and what is his clay court record?"),
    ],
}
