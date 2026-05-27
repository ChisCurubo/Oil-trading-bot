import os
import requests
import time
from dotenv import load_dotenv

load_dotenv("config/.env")

class MempoolClient:
    def __init__(self):
        self.base_url = os.getenv("MEMPOOL_API_URL", "https://mempool.space/api")

    def get_recommended_fees(self):
        """
        Devuelve las tarifas recomendadas actuales. 
        Alta congestión (fees altos) suele coincidir con pánico o euforia extrema.
        """
        try:
            res = requests.get(f"{self.base_url}/v1/fees/recommended", timeout=10)
            if res.status_code == 200:
                return res.json()
        except Exception as e:
            print(f"Error fetching mempool fees: {e}")
        return None

    def analyze_recent_blocks_for_whales(self, min_btc_size=500):
        """
        Busca transacciones gigantescas en los bloques recientes.
        Devuelve información sobre posibles movimientos de ballenas.
        """
        whale_txs = []
        try:
            # 1. Obtener el hash del bloque más reciente
            res_tip = requests.get(f"{self.base_url}/blocks/tip/hash", timeout=10)
            if res_tip.status_code != 200:
                return whale_txs
            
            tip_hash = res_tip.text.strip()
            
            # 2. Obtener las transacciones del bloque (limitado a 25 para no sobrecargar en REST)
            res_txs = requests.get(f"{self.base_url}/block/{tip_hash}/txs", timeout=15)
            if res_txs.status_code == 200:
                txs = res_txs.json()
                for tx in txs:
                    total_out = sum([vout.get('value', 0) for vout in tx.get('vout', [])])
                    # Sats a BTC
                    total_btc = total_out / 100000000.0
                    if total_btc >= min_btc_size:
                        whale_txs.append({
                            'txid': tx['txid'],
                            'btc_amount': total_btc,
                            'usd_estimated': total_btc * 60000, # placeholder, actualized by logic
                            'link': f"https://mempool.space/tx/{tx['txid']}"
                        })
        except Exception as e:
            print(f"Error fetching whale txs from mempool: {e}")
            
        return whale_txs

    def get_network_status(self):
        fees = self.get_recommended_fees()
        whales = self.analyze_recent_blocks_for_whales(min_btc_size=300) # 300 BTC es un movimiento muy notable
        
        estado = "NORMAL"
        if fees and fees.get('fastestFee', 0) > 100:
            estado = "CONGESTION_ALTA"
            
        return {
            'fees': fees,
            'estado': estado,
            'whales_detected': whales
        }
