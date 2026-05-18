import logging
import pandas as pd
from trading_ig import IGService

class IGClient:
    """
    Wrapper para la API de IG Markets.
    Maneja la autenticación y la descarga de datos históricos.
    """
    def __init__(self, username, password, api_key, acc_type):
        self.service = IGService(username, password, api_key, acc_type)
        self.session = None

    def connect(self):
        """Establece sesión con IG Markets."""
        try:
            self.session = self.service.create_session()
            return True
        except Exception as e:
            logging.error(f"Error de conexión IG: {e}")
            return False

    def fetch_accounts(self):
        """Obtiene la lista de cuentas vinculadas."""
        return self.service.fetch_accounts()

    def get_historical_data(self, epic, resolution='H', num_points=200):
        """
        Descarga históricos de velas y limpia el DataFrame resultante.
        Asegura que las columnas sean accesibles de forma sencilla.
        """
        try:
            response = self.service.fetch_historical_prices_by_epic_and_num_points(epic, resolution, num_points)
            df = response['prices']
            
            # Si el DataFrame viene con MultiIndex (bid/ask), nos quedamos con el nivel 1
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [col[1] for col in df.columns]
            
            # Mapeo de nombres para consistencia
            # IG usa 'bid' o 'ask' para los precios OHLC si no se especifica 'last'
            if 'bid' in df.columns:
                # Usamos los precios de venta (bid) para el análisis técnico conservador
                pass 
            
            # Renombramos columnas comunes si es necesario
            rename_map = {
                'LastTradedVolume': 'Volume',
                'bid': 'Close' # Simplificación si viene como bid
            }
            # No renombramos a ciegas para evitar errores si ya están bien
            if 'LastTradedVolume' in df.columns:
                df = df.rename(columns={'LastTradedVolume': 'Volume'})
            
            return df
        except Exception as e:
            logging.error(f"Error al obtener datos de IG: {e}")
            return None
