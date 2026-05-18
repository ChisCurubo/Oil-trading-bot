import csv
import os

class ThoughtLogger:
    """
    Registra el estado mental del bot en cada ciclo de análisis.
    Permite auditar por qué el bot tomó (o no) una decisión.
    """
    def __init__(self, filename='bitacora_analisis.csv'):
        self.filename = filename
        self.headers = [
            'Fecha', 'Precio', 'ADX', 'RSI', 'SMA200_Trend', 
            'SMA50_Rel', 'Soporte', 'Resistencia', 'Sentimiento', 'Decision'
        ]
        self._inicializar_archivo()

    def _inicializar_archivo(self):
        if not os.path.exists(self.filename):
            with open(self.filename, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(self.headers)

    def registrar_analisis(self, datos):
        """Guarda una fila con el estado de los indicadores en ese minuto."""
        with open(self.filename, mode='a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.headers)
            writer.writerow(datos)
