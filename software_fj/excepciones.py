"""Jerarquía de excepciones de dominio de Software FJ."""

class ErrorSoftwareFJ(Exception):
    """Error controlado en la operación de Software FJ."""

class ErrorValidacion(ErrorSoftwareFJ, ValueError):
    """Datos que incumplen reglas de negocio."""

class ClienteDuplicado(ErrorSoftwareFJ):
    """Ya existe un cliente con la identificación indicada."""

class EntidadNoEncontrada(ErrorSoftwareFJ, LookupError):
    """El objeto solicitado no está registrado."""

class ServicioNoDisponible(ErrorSoftwareFJ):
    """El servicio está inactivo o sin capacidad suficiente."""

class ReservaInvalida(ErrorSoftwareFJ):
    """La reserva incumple las condiciones de operación."""

class OperacionNoPermitida(ErrorSoftwareFJ):
    """Transición de estado u operación prohibida."""

class ErrorCalculo(ErrorSoftwareFJ, ArithmeticError):
    """Resultado numérico inválido."""
