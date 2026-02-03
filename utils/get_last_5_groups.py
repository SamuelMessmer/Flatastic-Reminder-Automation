import requests

TOKEN = "xJlmeIxKPRMDZ715AJ3TkzDidrSvuIEw"
API_URL = "https://gate.whapi.cloud/groups"

headers = {"Authorization": f"Bearer {TOKEN}"}

params = {
    "count": 5  # Hol nur die neuesten 5 Gruppen, damit es kein Timeout gibt
}

print(f"Frage die letzten 5 Gruppen ab...")

try:
    response = requests.get(API_URL, headers=headers, params=params, timeout=20)

    if response.status_code == 200:
        data = response.json()
        groups = data.get('groups', [])
        
        # Fallback für andere API Struktur
        if not groups and 'chats' in data:
            groups = data['chats']

        print(f"\n--- Gefundene Gruppen: {len(groups)} ---")
        for group in groups:
            print(f"Name: {group.get('name')}")
            print(f"ID:   {group.get('id')}")
            print("-" * 20)
            
        if len(groups) == 0:
            print("⚠️ Liste leer. Schreib nochmal eine Nachricht in die Gruppe, damit sie nach oben rutscht!")
    else:
        print(f"Fehler: {response.status_code} - {response.text}")

except Exception as e:
    print(f"Fehler: {e}")
