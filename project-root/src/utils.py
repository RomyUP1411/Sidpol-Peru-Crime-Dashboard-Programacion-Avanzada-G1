import logging
import time
from functools import wraps

# Configurar logger básico
logger = logging.getLogger("sidpol")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def log_time(func):
    """Decorador para registrar tiempo de ejecución de funciones."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            elapsed = time.time() - start
            logger.info(f"{func.__name__} ejecutado en {elapsed:.3f}s")
    return wrapper
