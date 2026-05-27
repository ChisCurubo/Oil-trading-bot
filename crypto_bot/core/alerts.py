import os
import aiohttp
from dotenv import load_dotenv

load_dotenv("config/.env")

class AsyncAlertClient:
    def __init__(self):
        # Evolution API (WhatsApp)
        self.wp_url = os.getenv("EVOLUTION_API_URL")
        self.wp_key = os.getenv("EVOLUTION_API_KEY")
        self.wp_instance = os.getenv("EVOLUTION_INSTANCE_NAME")
        self.wp_number = os.getenv("EVOLUTION_DESTINATION_NUMBER")
        
        # Discord
        self.discord_url = os.getenv("DISCORD_WEBHOOK_URL")
        
        # Telegram
        self.tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.tg_chat_id = os.getenv("TELEGRAM_CHAT_ID")

    async def send_whatsapp(self, session, message):
        if not self.wp_url or not self.wp_key or not self.wp_instance:
            return
            
        endpoint = f"{self.wp_url}/message/sendText/{self.wp_instance}"
        headers = {"apikey": self.wp_key, "Content-Type": "application/json"}
        payload = {
            "number": self.wp_number,
            "text": message
        }
        
        try:
            async with session.post(endpoint, headers=headers, json=payload) as response:
                if response.status not in [200, 201]:
                    error_text = await response.text()
                    print(f"❌ Error WhatsApp: {response.status} - {error_text}")
        except Exception as e:
            print(f"❌ Exception WhatsApp: {e}")

    async def send_discord(self, session, message):
        if not self.discord_url or "tu_webhook" in self.discord_url:
            return
            
        payload = {"content": message}
        headers = {"Content-Type": "application/json"}
        try:
            async with session.post(self.discord_url, headers=headers, json=payload) as response:
                pass
        except Exception as e:
            print(f"❌ Exception Discord: {e}")

    async def send_telegram(self, session, message):
        if not self.tg_token or not self.tg_chat_id:
            return
            
        url = f"https://api.telegram.org/bot{self.tg_token}/sendMessage"
        payload = {"chat_id": self.tg_chat_id, "text": message, "parse_mode": "Markdown"}
        try:
            async with session.post(url, json=payload) as response:
                pass
        except Exception as e:
            print(f"❌ Exception Telegram: {e}")

    async def broadcast(self, message):
        """Envía el mensaje a todas las plataformas configuradas simultáneamente."""
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.send_whatsapp(session, message),
                self.send_discord(session, message),
                self.send_telegram(session, message)
            ]
            import asyncio
            await asyncio.gather(*tasks)
