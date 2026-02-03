import requests

TOKEN = "xJlmeIxKPRMDZ715AJ3TkzDidrSvuIEw"
API_URL = "https://gate.whapi.cloud/groups"

headers = {"Authorization": f"Bearer {TOKEN}"}

# TRICK: Wir begrenzen die Anfrage auf 5 Gruppen, damit es kein Timeout gibt
params = {
    "count": 5  # Hol nur die neuesten 5 Gruppen
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

# import requests
#
# # Werte aus deinem Screenshot
# TOKEN = "xjImelxKPRMDZ715Aj3TkzDidrSvulEw" 
# API_URL = "https://gate.whapi.cloud/chats"
#
# headers = {"Authorization": f"Bearer {TOKEN}"}
#
# response = requests.get(API_URL, headers=headers)
# chats = response.json().get('chats', [])
#
# print("--- Deine Gruppen ---")
# for chat in chats:
#     if chat['id'].endswith('@g.us'):
#         print(f"Name: {chat.get('name')}")
#         print(f"ID:   {chat['id']}") # <--- DAS BRAUCHST DU
#


# import requests
#
# TOKEN = "xJlmeIxKPRMDZ715AJ3TkzDidrSvuIEw"
# # ÄNDERUNG: Nutze den speziellen Groups-Endpoint
# API_URL = "https://gate.whapi.cloud/groups" 
#
# headers = {"Authorization": f"Bearer {TOKEN}"}
#
# print(f"Frage Daten ab von: {API_URL} ...")
# response = requests.get(API_URL, headers=headers)
#
# if response.status_code == 200:
#     # Die Struktur bei /groups ist etwas anders (Liste von Gruppen direkt in 'groups')
#     data = response.json()
#     groups = data.get('groups', [])
#     
#     # Fallback, falls die API doch 'chats' zurückgibt
#     if not groups and 'chats' in data:
#         groups = data['chats']
#
#     print(f"\n--- Gefundene Gruppen: {len(groups)} ---")
#     
#     for group in groups:
#         # Bei Whapi enden Gruppen immer auf @g.us
#         print(f"Name: {group.get('name', 'Unbekannt')}")
#         print(f"ID:   {group.get('id')}") 
#         print("-" * 20)
#         
#     if len(groups) == 0:
#         print("⚠️ Immer noch leer? Schreibe eine Nachricht in die WG-Gruppe!")
# else:
#     print(f"Fehler: {response.status_code}")
#     print(response.text)         
#     print("-" * 20)
