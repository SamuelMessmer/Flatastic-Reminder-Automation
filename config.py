import os
from dotenv import load_dotenv

load_dotenv()

FLATASTIC_EMAIL = os.getenv("FLATASTIC_EMAIL") or ""
FLATASTIC_PASSWORD = os.getenv("FLATASTIC_PASSWORD") or ""

# --- WHAPI CONFIG ---
WHAPI_TOKEN = os.getenv("WHAPI_TOKEN") or ""
WHATSAPP_GROUP_ID = os.getenv("WHATSAPP_GROUP_ID") or ""
# Standard Endpoint für Textnachrichten
WHAPI_API_URL = "https://gate.whapi.cloud/messages/text"

STATE_FILE = "task_state.json"

FLATASTIC_BASE_URL = "https://api.flatastic-app.com/index.php/api"
FLATASTIC_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "X-Client-Version": "2.3.35",
    "X-Api-Version": "2.0.0",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"
}
