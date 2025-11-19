"""
Excepciones personalizadas para la aplicación SIDPOL.
"""


class SIDPOLException(Exception):
    """Excepción base para la aplicación SIDPOL."""
    pass


class DataLoadError(SIDPOLException):
    """Error al cargar datos (CSV o BD)."""
    pass


class DatabaseError(SIDPOLException):
    """Error en operaciones de base de datos."""
    pass


class DownloadError(SIDPOLException):
    """Error al descargar datos desde API/web."""
    pass


class ProcessingError(SIDPOLException):
    """Error en procesamiento/transformación de datos."""
    pass


class ValidationError(SIDPOLException):
    """Error en validación de datos."""
    pass
