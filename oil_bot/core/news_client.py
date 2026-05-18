import requests
import logging

class NewsClient:
    """
    Cliente para NewsData.io (Sustituye a NewsAPI).
    """
    def __init__(self, api_key):
        self.api_key = api_key
        # Nueva URL base para NewsData.io
        self.url = "https://newsdata.io/api/1/latest"

    def get_headlines(self, limit=10):
        """
        Obtiene titulares usando NewsData.io con filtros geopolíticos.
        """
        params = {
            'apikey': self.api_key,
            'q': 'oil OR petroleum OR petrol OR gas OR OPEC OR geopolitics',
            'language': 'en'
            # Se elimina el filtro de país para capturar noticias geopolíticas globales
        }
        try:
            response = requests.get(self.url, params=params)
            data = response.json()
            
            if data.get('status') == 'success':
                # NewsData usa el campo 'results' en lugar de 'articles'
                results = data.get('results', [])
                return [item['title'] for item in results if 'title' in item]
            else:
                # NewsData puede poner el mensaje de error en 'results' o en 'message'
                results_field = data.get('results', {})
                error_msg = results_field.get('message') if isinstance(results_field, dict) else data.get('message')
                logging.warning(f"Error en NewsData.io: {error_msg or 'Sin mensaje'}")
                return []
        except Exception as e:
            logging.error(f"Error conectando con NewsData.io: {e}")
            return []
