import logging
import time
from functools import wraps
from pathlib import Path

# Configurar logger básico con archivo de log
logger = logging.getLogger("sidpol")
if not logger.handlers:
    # Handler a consola
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    
    # Handler a archivo
    log_dir = Path(__file__).resolve().parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(log_dir / "sidpol.log", encoding="utf-8")
    file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)


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


def debug(func):
    """Decorador para debugging: registra parámetros y resultado."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"→ {func.__name__} llamada con args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"← {func.__name__} retorna {type(result).__name__}")
            return result
        except Exception as e:
            logger.debug(f"✗ {func.__name__} lanzó {type(e).__name__}: {e}")
            raise
    return wrapper


def cache_result(func):
    """Decorador para cachear resultados de funciones dentro de una sesión."""
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Crear clave basada en función, args y kwargs
        key = (func.__name__, args, tuple(sorted(kwargs.items())))
        if key in cache:
            logger.debug(f"{func.__name__} retorna resultado cacheado")
            return cache[key]
        
        result = func(*args, **kwargs)
        cache[key] = result
        logger.debug(f"{func.__name__} resultado cacheado")
        return result
    
    wrapper.clear_cache = lambda: cache.clear()
    return wrapper


def handle_errors(default_return=None):
    """Decorador para capturar y loguear excepciones sin propagar."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(f"Error en {func.__name__}: {e}")
                return default_return
        return wrapper
    return decorator
