import os
import requests
from dotenv import load_dotenv

load_dotenv("config/.env")

class DiscordClient:
    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    def send_message(self, message):
        """
        Envía un mensaje a un canal de Discord a través de Webhooks
        """
        if not self.webhook_url or self.webhook_url == "tu_webhook_url_aqui":
            print("Discord Webhook NO CONFIGURADO. Saltando alerta...")
            return False

        payload = {
            "content": message
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(self.webhook_url, headers=headers, json=payload, timeout=10)
            if response.status_code in [200, 204]:
                print("✅ Alerta enviada a Discord")
                return True
            else:
                print(f"❌ Error al enviar a Discord: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Excepción al enviar a Discord: {e}")
            return False
