import requests
import json
import os
from enum import Enum
from typing import Optional
from config import (
    WHAPI_TOKEN, WHATSAPP_GROUP_ID, WHAPI_API_URL,
    FLATASTIC_EMAIL, FLATASTIC_PASSWORD, FLATASTIC_BASE_URL, FLATASTIC_HEADERS,
    STATE_FILE
)


class TaskState(Enum):
    """Task status constants."""
    OK = "ok"
    DUE = "due"
    OVERDUE = "overdue"


class WhatsAppService:
    """Sends messages via GreenAPI."""
    
    def __init__(self, token: str = WHAPI_TOKEN, 
                 group_id: str = WHATSAPP_GROUP_ID,
                 api_url: str = WHAPI_API_URL):
        self.token = token
        self.group_id = group_id
        self.api_url = api_url

    def send_group_message(self, message: str) -> bool:
        if not self.group_id:
            print(f"⚠️ Simulation (keine Group ID): {message}")
            return False

        # Whapi nutzt Bearer Token Authentication
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # Whapi Payload Syntax: 'to' statt 'chatId', 'body' statt 'message'
        payload = {
            "to": self.group_id, 
            "body": message,
            "typing_time": 0 # Optional: Verhindert "Schreibt..." Anzeige
        }

        try:
            res = requests.post(self.api_url, headers=headers, json=payload)
            
            # Whapi gibt manchmal 200 oder 201 zurück
            res.raise_for_status()
            print(f"✅ WhatsApp (Whapi) gesendet: {message[:30]}...")
            return True
        except requests.RequestException as e:
            # Detaillierte Fehleranalyse bei API Fehlern
            error_msg = str(e)
            if e.response is not None:
                error_msg += f" | Server Response: {e.response.text}"
            
            print(f"❌ Fehler bei WhatsApp (Whapi): {error_msg}")
            return False

class FlatasticService:
    """Fetches tasks from Flatastic API."""
    
    SECONDS_PER_DAY = 60 * 60 * 24
    
    def __init__(self, email: str = FLATASTIC_EMAIL, 
                 password: str = FLATASTIC_PASSWORD,
                 base_url: str = FLATASTIC_BASE_URL):
        self.email = email
        self.password = password
        self.base_url = base_url
        self.token: Optional[str] = None
        self.user_map: dict[str, str] = {}

    def _get_headers(self, api_key: str = "publicKey") -> dict:
        """Returns headers with the specified API key."""
        headers = FLATASTIC_HEADERS.copy()
        headers["X-Api-Key"] = api_key
        return headers

    def _login(self) -> bool:
        """Authenticates and stores token + user map."""
        print("🔑 Logge ein bei Flatastic...")
        try:
            res = requests.post(
                f"{self.base_url}/auth/login",
                headers=self._get_headers("publicKey"),
                json={"email": self.email, "password": self.password}
            )
            res.raise_for_status()
            data = res.json()
            
            self.token = data.get('X-API-KEY')
            self.user_map = {
                str(u.get('id')): u.get('firstName', 'Unknown')
                for u in data.get('wg', {}).get('flatmates', [])
            }
            print("✅ Login erfolgreich.")
            return True
        except requests.RequestException as e:
            print(f"❌ Login fehlgeschlagen: {e}")
            return False

    def _ensure_authenticated(self) -> bool:
        """Ensures we have a valid token."""
        if not self.token:
            return self._login()
        return True

    def _determine_state(self, days_left: int) -> TaskState:
        """Determines task state based on days remaining."""
        if days_left < 0:
            return TaskState.OVERDUE
        elif days_left == 0:
            return TaskState.DUE
        return TaskState.OK

    def _transform_task(self, raw_task: dict) -> dict:
        """Transforms raw API task into clean format."""
        uid = str(raw_task.get('currentUser'))
        seconds_left = raw_task.get('timeLeftNext', 0)
        days_left = int(seconds_left / self.SECONDS_PER_DAY)
        
        return {
            "id": raw_task.get('id'),
            "title": raw_task.get('title'),
            "user": self.user_map.get(uid, "Jemand"),
            "days_left": days_left,
            "state": self._determine_state(days_left)
        }

    def _fetch_tasks_with_retry(self) -> list[dict]:
        """Fetches tasks, retrying once on auth failure."""
        headers = self._get_headers(str(self.token))
        res = requests.get(f"{self.base_url}/chores", headers=headers)
        
        if res.status_code == 401:
            print("🔄 Token abgelaufen, erneuter Login...")
            if not self._login():
                return []
            headers = self._get_headers(str(self.token))
            res = requests.get(f"{self.base_url}/chores", headers=headers)
        
        res.raise_for_status()
        return res.json()

    def get_current_tasks(self) -> list[dict]:
        """Fetches and transforms current tasks."""
        if not self._ensure_authenticated():
            return []
        
        try:
            raw_tasks = self._fetch_tasks_with_retry()
            return [self._transform_task(t) for t in raw_tasks]
        except requests.RequestException as e:
            print(f"❌ Fehler beim Abrufen der Aufgaben: {e}")
            return []

class StateService:
    """Manages task state persistence for tracking completions."""
    
    def __init__(self, state_file: str = STATE_FILE):
        self.state_file = state_file

    def load_state(self) -> dict[str, str]:
        """Loads previous task assignments."""
        if not os.path.exists(self.state_file):
            return {}
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def save_state(self, tasks: list[dict]) -> None:
        """Saves current task assignments."""
        state = {t['title']: t['user'] for t in tasks}
        with open(self.state_file, 'w') as f:
            json.dump(state, f)
