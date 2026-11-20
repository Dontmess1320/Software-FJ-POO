"""Clases abstractas y entidades de dominio; almacenamiento solo en memoria."""
from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal, InvalidOperation
from itertools import count
import re

from .excepciones import (ErrorValidacion, ErrorCalculo, OperacionNoPermitida,
                          ReservaInvalida, ServicioNoDisponible)
from .registro import logger


def numero_positivo(valor, campo, *, admite_cero=False):
    """Convierte de forma segura a Decimal y valida finitud/signo."""
    if isinstance(valor, bool):
        raise ErrorValidacion(f'{campo}: no se permite un booleano.')
    try:
        numero = Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ErrorValidacion(f'{campo}: debe ser un número válido.') from exc
    if not numero.is_finite() or (numero < 0 if admite_cero else numero <= 0):
        raise ErrorValidacion(f'{campo}: valor fuera del rango permitido.')
    return numero


def texto_requerido(valor, campo, longitud=2):
    if not isinstance(valor, str) or len(valor.strip()) < longitud:
        raise ErrorValidacion(f'{campo}: debe contener al menos {longitud} caracteres.')
    return valor.strip()


class Entidad(ABC):
    """Abstracción de las entidades que tienen identidad y presentación."""
    @property
    @abstractmethod
    def identificador(self):
        pass

    @abstractmethod
    def describir(self):
        pass


class Cliente(Entidad):
    """Información de cliente encapsulada y validada mediante propiedades."""
    def __init__(self, documento, nombre, correo, telefono):
        self.__documento = None
        self.__nombre = None
        self.__correo = None
        self.__telefono = None
        self.documento = documento
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def documento(self):
        return self.__documento

    @documento.setter
    def documento(self, valor):
        cadena = str(valor).strip() if not isinstance(valor, bool) else ''
        if not re.fullmatch(r'\d{5,15}', cadena):
            raise ErrorValidacion('Documento: ingresa entre 5 y 15 dígitos.')
        if self.__documento is not None:
            raise OperacionNoPermitida('No se permite modificar el documento de un cliente.')
        self.__documento = cadena

    @property
    def identificador(self):
        return self.documento

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        self.__nombre = texto_requerido(valor, 'Nombre')

    @property
    def correo(self):
        return self.__correo

    @correo.setter
    def correo(self, valor):
        if not isinstance(valor, str) or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', valor.strip()):
            raise ErrorValidacion('Correo: dirección de email inválida.')
        self.__correo = valor.strip().lower()

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        cadena = str(valor).strip() if not isinstance(valor, bool) else ''
        if not re.fullmatch(r'\+?\d{7,15}', cadena):
            raise ErrorValidacion('Teléfono: ingresa entre 7 y 15 dígitos y + opcional.')
        self.__telefono = cadena

    def describir(self):
        return f'Cliente {self.documento} | {self.nombre} | {self.correo}'

    def __repr__(self):
        return f'Cliente(documento={self.documento!r}, nombre={self.nombre!r})'


class Servicio(Entidad, ABC):
    """Contrato polimórfico de servicios disponibles por unidad de tiempo."""
    _ids = count(1)

    def __init__(self, nombre, tarifa, capacidad=1):
        self.__identificador = f'S{next(self._ids):03d}'
        self.__nombre = texto_requerido(nombre, 'Nombre de servicio')
        self.__tarifa = numero_positivo(tarifa, 'Tarifa')
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad < 1:
            raise ErrorValidacion('Capacidad: debe ser un entero positivo.')
        self.__capacidad = capacidad
        self.__activo = True

    @property
    def identificador(self):
        return self.__identificador

    @property
    def nombre(self):
        return self.__nombre

    @property
    def tarifa(self):
        return self.__tarifa

    @property
    def capacidad(self):
        return self.__capacidad

    @property
    def activo(self):
        return self.__activo

    def cambiar_disponibilidad(self, activo):
        if not isinstance(activo, bool):
            raise ErrorValidacion('La disponibilidad debe ser verdadera o falsa.')
        self.__activo = activo
        logger.info('Disponibilidad de %s cambiada a %s', self.identificador, activo)

    def validar_disponibilidad(self):
        if not self.activo:
            raise ServicioNoDisponible(f'{self.nombre} se encuentra inactivo.')

    def validar_parametros(self, duracion):
        return numero_positivo(duracion, 'Duración')

    @abstractmethod
    def calcular_costo(self, duracion, *, impuesto=0, descuento=0):
        """Costo con parámetros opcionales: 0, impuesto o descuento."""

    @abstractmethod
    def describir(self):
        pass

    def _ajustar_costo(self, subtotal, *, impuesto=0, descuento=0):
        """Sobrecarga funcional con variantes de argumentos opcionales."""
        tasa = numero_positivo(impuesto, 'Impuesto (%)', admite_cero=True)
        rebaja = numero_positivo(descuento, 'Descuento (%)', admite_cero=True)
        if tasa > 100 or rebaja > 100:
            raise ErrorCalculo('Impuesto y descuento deben estar entre 0 y 100 %.')
        subtotal = numero_positivo(subtotal, 'Subtotal')
        try:
            # Se descuenta primero y luego se agrega impuesto.
            total = subtotal * (Decimal('1') - rebaja / 100) * (Decimal('1') + tasa / 100)
            if not total.is_finite() or total < 0:
                raise ErrorCalculo('El total calculado es inconsistente.')
            return total.quantize(Decimal('0.01'))
        except (InvalidOperation, ArithmeticError) as exc:
            raise ErrorCalculo('No se pudo calcular el costo.') from exc


class Sala(Servicio):
    def __init__(self, nombre, tarifa_hora, capacidad_personas):
        super().__init__(nombre, tarifa_hora, capacidad=1)
        if isinstance(capacidad_personas, bool) or not isinstance(capacidad_personas, int) or capacidad_personas < 1:
            raise ErrorValidacion('Personas: la capacidad de la sala debe ser un entero positivo.')
        self.__capacidad_personas = capacidad_personas

    @property
    def capacidad_personas(self):
        return self.__capacidad_personas

    def validar_parametros(self, duracion):
        horas = super().validar_parametros(duracion)
        if horas > 12:
            raise ReservaInvalida('La reserva de sala no puede exceder 12 horas.')
        return horas

    def calcular_costo(self, duracion, *, impuesto=0, descuento=0):
        horas = self.validar_parametros(duracion)
        return self._ajustar_costo(self.tarifa * horas, impuesto=impuesto, descuento=descuento)

    def describir(self):
        return f'{self.identificador} | Sala: {self.nombre} | {self.capacidad_personas} personas | ${self.tarifa}/hora'


class Equipo(Servicio):
    def __init__(self, nombre, tarifa_dia, unidades):
        super().__init__(nombre, tarifa_dia, capacidad=unidades)

    def validar_parametros(self, duracion):
        dias = super().validar_parametros(duracion)
        if dias != dias.to_integral_value() or dias > 30:
            raise ReservaInvalida('Los equipos se alquilan entre 1 y 30 días enteros.')
        return dias

    def calcular_costo(self, duracion, *, impuesto=0, descuento=0):
        dias = self.validar_parametros(duracion)
        return self._ajustar_costo(self.tarifa * dias, impuesto=impuesto, descuento=descuento)

    def describir(self):
        return f'{self.identificador} | Equipo: {self.nombre} | {self.capacidad} unidades | ${self.tarifa}/día'


class Asesoria(Servicio):
    def __init__(self, nombre, tarifa_hora, especialidad):
        super().__init__(nombre, tarifa_hora, capacidad=1)
        self.__especialidad = texto_requerido(especialidad, 'Especialidad')

    @property
    def especialidad(self):
        return self.__especialidad

    def validar_parametros(self, duracion):
        horas = super().validar_parametros(duracion)
        if horas < Decimal('0.5') or horas > 8:
            raise ReservaInvalida('Una asesoría dura entre 0.5 y 8 horas.')
        return horas

    def calcular_costo(self, duracion, *, impuesto=0, descuento=0):
        horas = self.validar_parametros(duracion)
        return self._ajustar_costo(self.tarifa * horas, impuesto=impuesto, descuento=descuento)

    def describir(self):
        return f'{self.identificador} | Asesoría: {self.nombre} ({self.especialidad}) | ${self.tarifa}/hora'


class Reserva(Entidad):
    """Reserva con estados y transiciones controladas."""
    _ids = count(1)
    PENDIENTE = 'PENDIENTE'
    CONFIRMADA = 'CONFIRMADA'
    CANCELADA = 'CANCELADA'
    PROCESADA = 'PROCESADA'

    def __init__(self, cliente, servicio, duracion, *, impuesto=0, descuento=0):
        if not isinstance(cliente, Cliente) or not isinstance(servicio, Servicio):
            raise ErrorValidacion('La reserva requiere un cliente y un servicio válidos.')
        servicio.validar_disponibilidad()
        self.__duracion = servicio.validar_parametros(duracion)
        self.__costo = servicio.calcular_costo(self.__duracion, impuesto=impuesto, descuento=descuento)
        self.__identificador = f'R{next(self._ids):03d}'
        self.__cliente = cliente
        self.__servicio = servicio
        self.__estado = self.PENDIENTE
        self.__creada = datetime.now()

    @property
    def identificador(self):
        return self.__identificador

    @property
    def cliente(self):
        return self.__cliente

    @property
    def servicio(self):
        return self.__servicio

    @property
    def duracion(self):
        return self.__duracion

    @property
    def costo(self):
        return self.__costo

    @property
    def estado(self):
        return self.__estado

    def confirmar(self):
        if self.__estado != self.PENDIENTE:
            raise OperacionNoPermitida(f'No se puede confirmar una reserva {self.estado}.')
        self.servicio.validar_disponibilidad()
        self.__estado = self.CONFIRMADA
        logger.info('Reserva %s confirmada', self.identificador)

    def cancelar(self):
        if self.__estado in (self.CANCELADA, self.PROCESADA):
            raise OperacionNoPermitida(f'No se puede cancelar una reserva {self.estado}.')
        self.__estado = self.CANCELADA
        logger.info('Reserva %s cancelada', self.identificador)

    def procesar(self):
        if self.__estado != self.CONFIRMADA:
            raise OperacionNoPermitida('Solo se puede procesar una reserva confirmada.')
        self.__estado = self.PROCESADA
        logger.info('Reserva %s procesada', self.identificador)

    def describir(self):
        return (f'{self.identificador} | {self.cliente.nombre} | {self.servicio.nombre} | '
                f'{self.duracion} | ${self.costo} | {self.estado}')
