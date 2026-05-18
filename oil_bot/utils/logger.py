import logging
import os
from datetime import datetime

def setup_logger(name="OilBot"):
    """
    Configura un sistema de registro robusto que guarda en archivo y muestra en consola.
    """
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Evitar duplicados si el logger ya existe
    if not logger.handlers:
        # Formato de los mensajes
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Handler para archivo
        log_file = os.path.join(log_dir, f"bot_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
