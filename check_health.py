import requests

TOKEN = "xJlmeIxKPRMDZ715AJ3TkzDidrSvuIEw"
API_URL = "https://gate.whapi.cloud/health"

headers = {"Authorization": f"Bearer {TOKEN}"}

try:
    print("🏥 Prüfe Vitalwerte der API...")
    response = requests.get(API_URL, headers=headers, timeout=10) # 10 Sek Timeout
    
    if response.status_code == 200:
        data = response.json()
        status_text = data.get('status', {}).get('text')
        print(f"✅ Status: {status_text}")
        
        if status_text == "AUTH":
            print("🚀 Alles bereit! Du kannst jetzt nach Gruppen suchen.")
        else:
            print("⚠️ Noch nicht bereit. Bitte warten.")
    else:
        print(f"❌ Fehler: {response.status_code} - {response.text}")

except requests.exceptions.Timeout:
    print("⏳ Timeout: Die API antwortet immer noch zu langsam. Warte noch ein paar Minuten.")
except Exception as e:
    print(f"Fehler: {e}")
