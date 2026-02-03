# 🤖 WG-Bot (The Enforcer)

Ein Python-Bot, der unsere WG-Orga automatisiert. Er verbindet **Flatastic** mit **WhatsApp** (via Whapi), um sicherzustellen, dass Putzpläne eingehalten werden und wir uns das manuelle "Erinnern" sparen.

## 🚀 Features

* **Daily Reminder:** Überprüft täglich (09:00 & 18:00), ob Aufgaben fällig (`due`) oder überfällig (`overdue`) sind.
* **Public Shaming (aka Accountability):** Sendet Nachrichten in die WG-Gruppe, wenn Aufgaben überfällig sind.
* **Success Tracking:** Erkennt automatisch, wenn eine Aufgabe in Flatastic erledigt wurde (User-Wechsel), und postet, wer als nächstes dran ist.
* **State Persistence:** Speichert den letzten bekannten Status in `task_state.json`, um Erledigungen zu erkennen.
* **Graceful Handling:** Leere Aufgabenlisten, neue Aufgaben und verschwundene Aufgaben werden korrekt behandelt.
* **Zero-Maintenance:** Läuft als Daemon via Systemd oder manuell im Terminal.

## 🛠 Tech Stack

* **Language:** Python 3.9+
* **Services:**
    * [Flatastic](https://flatastic-app.com/) (Unofficial API)
    * [Whapi](https://whapi.cloud/) (WhatsApp Gateway)
* **Libs:** `schedule`, `requests`, `python-dotenv`

## ⚙️ Setup & Installation

### 1. Clone Repo
```bash
git clone <DEIN_REPO_URL>
cd wg-automation
```

### 2. Python Virtual Environment erstellen
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# oder: venv\Scripts\activate  # Windows
```

### 3. Dependencies installieren
```bash
pip install -r requirements.txt
```

### 4. Umgebungsvariablen konfigurieren
Erstelle eine `.env` Datei im Projektverzeichnis:
```bash
# Flatastic Credentials (dein Flatastic Login)
FLATASTIC_EMAIL=deine@email.de
FLATASTIC_PASSWORD=dein_passwort

# Whapi Credentials (von https://whapi.cloud/)
WHAPI_TOKEN=dein_whapi_token
WHATSAPP_GROUP_ID=1234567890@g.us
```

**Whapi Token bekommen:**
1. Registriere dich bei [whapi.cloud](https://whapi.cloud/)
2. Verbinde deine WhatsApp-Nummer (QR-Code scannen)
3. Kopiere den API Token aus dem Dashboard

**WhatsApp Group ID finden:**
- Die Group ID hat das Format `1234567890@g.us`
- Du kannst sie über die Whapi API abrufen oder in den Gruppen-Einstellungen finden

### 5. Bot starten
```bash
python main.py
```

Der Bot läuft nun und prüft automatisch um 09:00 und 18:00 Uhr.

## 🧪 Testen

Das Projekt enthält einen interaktiven Test-Modus, der verschiedene Szenarien simuliert:

```bash
python __test.py
```

**Test-Szenarien:**
1. Initialisierung (keine Aufgaben fällig)
2. Stress-Test (überfällig + heute fällig)
3. Erledigung (User-Wechsel erkannt)
4. Leere Aufgabenliste
5. Neue Aufgabe erscheint
6. Aufgabe verschwindet
7. Mehrere Erledigungen gleichzeitig

Die Tests senden echte WhatsApp-Nachrichten - check dein Handy!

## 🔧 Wartung & Maintenance

### Logs prüfen
Der Bot gibt Status-Meldungen in stdout aus:
- ✅ Erfolgreiche Aktionen
- ❌ Fehler (API-Probleme, Auth-Fehler)
- 🔄 Token-Refresh bei Flatastic

### State zurücksetzen
Falls der Bot falsche Erledigungen meldet:
```bash
rm task_state.json
```
Der Bot initialisiert beim nächsten Run neu.

### Als Systemd Service (Linux)
```bash
# /etc/systemd/system/wg-bot.service
[Unit]
Description=WG Bot
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/wg-automation
ExecStart=/home/pi/wg-automation/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable wg-bot
sudo systemctl start wg-bot
sudo systemctl status wg-bot
```

### Health Check
```bash
python check_health.py
```

## 📁 Projektstruktur

```
wg-automation/
├── main.py           # Hauptlogik + Scheduler
├── services.py       # API-Services (Flatastic, WhatsApp, State)
├── config.py         # Konfiguration aus .env
├── check_health.py   # Health-Check Script
├── __test.py         # Interaktive Test-Suite
├── task_state.json   # Persistierter Task-Status (generiert)
├── requirements.txt  # Python Dependencies
└── .env              # Secrets (nicht committen!)
```

## ⚠️ Bekannte Limitierungen

- Flatastic API ist inoffiziell und kann sich ändern
- Whapi erfordert eine aktive WhatsApp-Session (Handy muss online bleiben)
- Bot erkennt Erledigungen nur durch User-Wechsel, nicht durch explizites "Erledigt"-Klicken

---

*🤖 Dieses Projekt wurde vibcoded.*
