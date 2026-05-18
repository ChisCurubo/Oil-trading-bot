import csv
import os

class TradeLogger:
    """
    Registra las operaciones cerradas con métricas financieras y balance.
    """
    def __init__(self, filename='operaciones_backtest.csv'):
        self.filename = filename
        # Headers actualizados para Gestión de Capital
        self.headers = [
            'Ticket_ID', 'Fecha_Entrada', 'Tipo', 'Precio_Entrada', 
            'Fecha_Salida', 'Precio_Salida', 'Resultado_USD', 
            'Balance_Final', 'Razon_Salida', 'Contexto_Noticias'
        ]
        self._inicializar_archivo()

    def _inicializar_archivo(self):
        """Si el archivo no existe o tiene headers viejos, lo reinicia."""
        # Si ya existe, comprobamos si necesita actualización de headers
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                first_line = f.readline().strip()
                if 'Resultado_USD' in first_line:
                    return # Ya está actualizado
        
        # Crear o sobrescribir con nuevos headers
        with open(self.filename, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(self.headers)

    def registrar_trade_cerrado(self, datos):
        """Inserta una operación cerrada en el CSV."""
        try:
            with open(self.filename, mode='a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.headers)
                writer.writerow(datos)
        except Exception as e:
            print(f"Error escribiendo en el ledger de trades: {e}")
