import os
import requests
from dotenv import load_dotenv

# Carica le credenziali dal file .env
load_dotenv()
API_KEY = os.getenv("eyJjaSI6IjYwY2FiYjBiLTU1OTctNDQ4NS04ZjYzLTdlOWUwNTZlMGJiOCIsImVhbiI6IlVucmVnaXN0ZXJlZEFwcGxpY2F0aW9uIiwiZWsiOiJyNEU1OEc0QmJXV2xvYmtQTFZUd3ZFN0UxamE1aVJvNC1uRjVsNUVKdWhGdTZCeFNObGdSbERsLlpsN01ic0tPcWJZdUR4emk1dEFNdDhNUHFGRWU5TVVJR3E3LmpGTkVKNnVjdXZra2U0NF8ifQ__")
ACCOUNT_ID = os.getenv("ETORO_ACCOUNT_ID")

# URL base dell'API eToro (assicurati di usare l'endpoint corretto fornito nella loro doc)
BASE_URL = "https://api.etoro.com/v1" 

def get_etoro_balance():
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    # Endpoint d'esempio per il saldo
    url = f"{BASE_URL}/accounts/{ACCOUNT_ID}/balance"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return f"Errore: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Connessione fallita: {str(e)}"

if __name__ == "__main__":
    print("Verifica connessione eToro...")
    print(get_etoro_balance())
