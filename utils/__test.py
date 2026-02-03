import os
from services import FlatasticService, WhatsAppService, StateService, TaskState
from main import run_check

# --- 1. Der Mock (Der Schauspieler) ---
class MockFlatasticService(FlatasticService):
    """Ein Fake-Service, der Aufgaben simuliert, ohne die API zu fragen."""
    
    def __init__(self):
        self._fake_tasks: list[dict] = []

    def set_scenario(self, tasks: list[dict]) -> None:
        """Hier definieren wir, was der Bot 'sehen' soll."""
        self._fake_tasks = tasks

    def get_current_tasks(self) -> list[dict]:
        """Gibt einfach unsere simulierten Daten zurück."""
        return self._fake_tasks

# --- 2. Die Test-Simulation ---
def run_tests():
    print("🧪 STARTE SYSTEM-TEST (Simulation)")
    print("-----------------------------------")

    # Wir nutzen den ECHTEN WhatsApp Service (damit du Nachrichten bekommst)
    # Aber wir nutzen eine TEST-State-Datei, damit wir den echten Status nicht kaputt machen.
    test_state_file = "test_state.json"
    
    # Aufräumen: Alte Test-Dateien löschen
    if os.path.exists(test_state_file):
        os.remove(test_state_file)

    # Initialisierung
    real_whatsapp = WhatsAppService() # Nutzt ID aus .env
    fake_flatastic = MockFlatasticService()
    test_state = StateService(state_file=test_state_file)

    # ---------------------------------------------------------
    # SZENARIO 1: Alles ist ruhig (Initialisierung)
    # ---------------------------------------------------------
    print("\n[SZ 1] Initialisierung: Keine Aufgaben fällig.")
    fake_flatastic.set_scenario([
        {
            "id": 1, "title": "Küche", "user": "Samuel", 
            "days_left": 5, "state": TaskState.OK
        },
        {
            "id": 2, "title": "Bad", "user": "Hannes", 
            "days_left": 3, "state": TaskState.OK
        }
    ])
    
    run_check(messenger=real_whatsapp, task_service=fake_flatastic, state_service=test_state)
    print("👉 Check dein Handy: Es sollte KEINE Nachricht kommen.")
    input("Drücke ENTER für Szenario 2...")

    # ---------------------------------------------------------
    # SZENARIO 2: Alarm (Überfällig & Fällig)
    # ---------------------------------------------------------
    print("\n[SZ 2] Stress-Test: Samuel ist überfällig, Hannes ist heute dran.")
    fake_flatastic.set_scenario([
        {
            "id": 1, "title": "Küche", "user": "Samuel", 
            "days_left": -2, "state": TaskState.OVERDUE # <--- ALARM
        },
        {
            "id": 2, "title": "Bad", "user": "Hannes", 
            "days_left": 0, "state": TaskState.DUE      # <--- HEUTE
        }
    ])

    run_check(messenger=real_whatsapp, task_service=fake_flatastic, state_service=test_state)
    print("👉 Check dein Handy: Du solltest 2 Nachrichten bekommen (Alarm & Heute fällig).")
    input("Drücke ENTER für Szenario 3...")

    # ---------------------------------------------------------
    # SZENARIO 3: Erledigung (Der Wechsel)
    # ---------------------------------------------------------
    print("\n[SZ 3] Erledigung: Samuel hat geputzt -> Jetzt ist Peter dran.")
    # Wir ändern den User bei "Küche" von Samuel auf Peter. 
    # Der Bot vergleicht das mit dem Status aus Szenario 2 und merkt: "Aha, erledigt!"
    fake_flatastic.set_scenario([
        {
            "id": 1, "title": "Küche", "user": "Peter", # <--- WECHSEL
            "days_left": 7, "state": TaskState.OK
        },
        {
            "id": 2, "title": "Bad", "user": "Hannes", 
            "days_left": -1, "state": TaskState.OVERDUE # Hannes hat immer noch nicht geputzt
        }
    ])

    run_check(messenger=real_whatsapp, task_service=fake_flatastic, state_service=test_state)
    print("👉 Check dein Handy: Nachricht 'Sauber! Samuel hat erledigt...' + Alarm für Hannes.")
    input("Drücke ENTER für Szenario 4...")

    # ---------------------------------------------------------
    # SZENARIO 4: Leere Aufgabenliste
    # ---------------------------------------------------------
    print("\n[SZ 4] Edge Case: Keine Aufgaben von der API.")
    fake_flatastic.set_scenario([])
    
    run_check(messenger=real_whatsapp, task_service=fake_flatastic, state_service=test_state)
    print("👉 Check dein Handy: Es sollte KEINE Nachricht kommen (Bot gibt Fehlermeldung in Konsole).")
    input("Drücke ENTER für Szenario 5...")

    # ---------------------------------------------------------
    # SZENARIO 5: Neue Aufgabe erscheint
    # ---------------------------------------------------------
    print("\n[SZ 5] Neue Aufgabe: 'Flur' taucht zum ersten Mal auf.")
    fake_flatastic.set_scenario([
        {
            "id": 1, "title": "Küche", "user": "Peter", 
            "days_left": 6, "state": TaskState.OK
        },
        {
            "id": 2, "title": "Bad", "user": "Hannes", 
            "days_left": 5, "state": TaskState.OK
        },
        {
            "id": 3, "title": "Flur", "user": "Lisa",  # <--- NEU
            "days_left": 0, "state": TaskState.DUE
        }
    ])
    
    run_check(messenger=real_whatsapp, task_service=fake_flatastic, state_service=test_state)
    print("👉 Check dein Handy: Nur 'Heute fällig' für Lisa (keine Erledigung, da neu).")
    input("Drücke ENTER für Szenario 6...")

    # ---------------------------------------------------------
    # SZENARIO 6: Aufgabe verschwindet
    # ---------------------------------------------------------
    print("\n[SZ 6] Aufgabe entfernt: 'Flur' existiert nicht mehr.")
    fake_flatastic.set_scenario([
        {
            "id": 1, "title": "Küche", "user": "Peter", 
            "days_left": 5, "state": TaskState.OK
        },
        {
            "id": 2, "title": "Bad", "user": "Hannes", 
            "days_left": 4, "state": TaskState.OK
        }
        # Flur ist weg
    ])
    
    run_check(messenger=real_whatsapp, task_service=fake_flatastic, state_service=test_state)
    print("👉 Check dein Handy: Es sollte KEINE Nachricht kommen (Aufgabe einfach weg).")
    input("Drücke ENTER für Szenario 7...")

    # ---------------------------------------------------------
    # SZENARIO 7: Mehrere Erledigungen gleichzeitig
    # ---------------------------------------------------------
    print("\n[SZ 7] Doppel-Erledigung: Peter UND Hannes haben geputzt.")
    fake_flatastic.set_scenario([
        {
            "id": 1, "title": "Küche", "user": "Samuel",  # <--- Peter -> Samuel
            "days_left": 7, "state": TaskState.OK
        },
        {
            "id": 2, "title": "Bad", "user": "Lisa",      # <--- Hannes -> Lisa
            "days_left": 7, "state": TaskState.OK
        }
    ])
    
    run_check(messenger=real_whatsapp, task_service=fake_flatastic, state_service=test_state)
    print("👉 Check dein Handy: 2 Erledigungs-Nachrichten (Peter->Samuel, Hannes->Lisa).")
    
    # Aufräumen
    if os.path.exists(test_state_file):
        os.remove(test_state_file)
    print("\n✅ TEST ABGESCHLOSSEN.")

if __name__ == "__main__":
    run_tests()
