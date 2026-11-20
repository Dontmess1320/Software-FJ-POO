"""Configuración centralizada de logs de eventos y errores."""
import logging
from pathlib import Path


def obtener_logger():
    logger = logging.getLogger('software_fj')
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    logger.propagate = False
    carpeta = Path(__file__).resolve().parent.parent / 'logs'
    carpeta.mkdir(exist_ok=True)
    handler = logging.FileHandler(carpeta / 'software_fj.log', encoding='utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
    logger.addHandler(handler)
    return logger

logger = obtener_logger()
