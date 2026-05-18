from textblob import TextBlob
import logging

def analyze_market_sentiment(headlines):
    """
    Analizador de Sentimiento Cuantitativo Especializado en Crudo.
    Usa NLP + Ponderación de palabras clave industriales para mayor precisión.
    """
    if not headlines:
        return "NEUTRAL"
    
    # Palabras clave que suelen impulsar el precio al alza (Bullish)
    bullish_keywords = ['cut', 'shortage', 'tension', 'war', 'sanctions', 'conflict', 'decrease', 'unrest', 'strike', 'disruption']
    
    # Palabras clave que suelen presionar el precio a la baja (Bearish)
    bearish_keywords = ['increase', 'glut', 'surplus', 'recession', 'slowdown', 'inventory rise', 'stocks up', 'easing', 'production growth']

    try:
        total_score = 0
        for h in headlines:
            h = h.lower()
            # Polaridad base (-1 a 1)
            score = TextBlob(h).sentiment.polarity
            
            # Ponderación por contexto industrial
            for word in bullish_keywords:
                if word in h: score += 0.25 # Peso extra por factor de escasez/tensión
            for word in bearish_keywords:
                if word in h: score -= 0.25 # Peso extra por factor de sobreoferta
            
            total_score += score
        
        avg_score = total_score / len(headlines)
        
        # Umbrales más sensibles para reducir la neutralidad
        if avg_score > 0.05:
            return "ALCISTA"
        elif avg_score < -0.05:
            return "BAJISTA"
        else:
            return "NEUTRAL"
            
    except Exception as e:
        logging.error(f"Error en análisis de sentimiento cuantitativo: {e}")
        return "NEUTRAL"
