import os
import requests
import json
from dotenv import load_dotenv

load_dotenv("config/.env")

class WhatsAppClient:
    def __init__(self):
        self.api_url = os.getenv("EVOLUTION_API_URL")
        self.api_key = os.getenv("EVOLUTION_API_KEY")
        self.instance_name = os.getenv("EVOLUTION_INSTANCE_NAME")
        self.destination_number = os.getenv("EVOLUTION_DESTINATION_NUMBER")

    def send_message(self, message):
        """
        Sends a WhatsApp message via Evolution API
        """
        if not self.api_url or not self.api_key or not self.instance_name:
            print("WhatsApp Client NO CONFIGURADO. Saltando alerta...")
            return False

        endpoint = f"{self.api_url}/message/sendText/{self.instance_name}"
        
        headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "number": self.destination_number,
            "options": {
                "delay": 1200,
                "presence": "composing"
            },
           "text": message
        }
        
        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=10)
            if response.status_code in [200, 201]:
                print(f"✅ Alerta enviada por WhatsApp al {self.destination_number}")
                return True
            else:
                print(f"❌ Error al enviar WhatsApp: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Excepción al enviar WhatsApp: {e}")
            return False
