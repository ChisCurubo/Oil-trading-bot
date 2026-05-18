from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    """
    Clase base abstracta para todas las estrategias de trading.
    """
    def __init__(self, df):
        self.df = df

    @abstractmethod
    def check_signal(self):
        """
        Método obligatorio para evaluar señales de entrada/salida.
        Debe retornar una tupla (Señal, Nivel_SL).
        """
        pass
