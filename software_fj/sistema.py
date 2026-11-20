"""Fachada: listas en memoria y reglas de registro y reserva."""
from .excepciones import (ClienteDuplicado, EntidadNoEncontrada, ErrorValidacion,
                          ServicioNoDisponible)
from .modelos import Cliente, Servicio, Reserva
from .registro import logger


class SistemaFJ:
    def __init__(self):
        self.__clientes = []
        self.__servicios = []
        self.__reservas = []

    @property
    def clientes(self):
        return tuple(self.__clientes)  # vista inmutable de la lista interna

    @property
    def servicios(self):
        return tuple(self.__servicios)

    @property
    def reservas(self):
        return tuple(self.__reservas)

    def registrar_cliente(self, documento, nombre, correo, telefono):
        cliente = Cliente(documento, nombre, correo, telefono)
        if any(c.documento == cliente.documento for c in self.__clientes):
            raise ClienteDuplicado(f'El documento {cliente.documento} ya está registrado.')
        self.__clientes.append(cliente)
        logger.info('Cliente registrado: %s', cliente.documento)
        return cliente

    def registrar_servicio(self, servicio):
        if not isinstance(servicio, Servicio):
            raise ErrorValidacion('Solo se pueden registrar objetos Servicio.')
        if any(s.identificador == servicio.identificador for s in self.__servicios):
            raise ErrorValidacion('Este servicio ya fue registrado.')
        self.__servicios.append(servicio)
        logger.info('Servicio registrado: %s (%s)', servicio.identificador, servicio.nombre)
        return servicio

    def buscar_cliente(self, documento):
        return next((c for c in self.__clientes if c.documento == str(documento)),
                    None) or self._no_encontrado('Cliente', documento)

    def buscar_servicio(self, identificador):
        return next((s for s in self.__servicios if s.identificador == str(identificador).upper()),
                    None) or self._no_encontrado('Servicio', identificador)

    def buscar_reserva(self, identificador):
        return next((r for r in self.__reservas if r.identificador == str(identificador).upper()),
                    None) or self._no_encontrado('Reserva', identificador)

    @staticmethod
    def _no_encontrado(tipo, identificador):
        raise EntidadNoEncontrada(f'{tipo} {identificador} no encontrado.')

    def _validar_cupo(self, servicio):
        ocupadas = sum(1 for r in self.__reservas
                       if r.servicio is servicio and r.estado in (Reserva.PENDIENTE, Reserva.CONFIRMADA))
        if ocupadas >= servicio.capacidad:
            raise ServicioNoDisponible(f'{servicio.nombre}: no hay cupos libres ({ocupadas}/{servicio.capacidad}).')

    def crear_reserva(self, documento, id_servicio, duracion, *, impuesto=0, descuento=0):
        cliente = self.buscar_cliente(documento)
        servicio = self.buscar_servicio(id_servicio)
        servicio.validar_disponibilidad()
        self._validar_cupo(servicio)
        reserva = Reserva(cliente, servicio, duracion, impuesto=impuesto, descuento=descuento)
        self.__reservas.append(reserva)
        logger.info('Reserva creada: %s, cliente=%s, servicio=%s, total=%s',
                    reserva.identificador, documento, id_servicio, reserva.costo)
        return reserva

    def confirmar_reserva(self, id_reserva):
        reserva = self.buscar_reserva(id_reserva)
        reserva.confirmar()
        return reserva

    def cancelar_reserva(self, id_reserva):
        reserva = self.buscar_reserva(id_reserva)
        reserva.cancelar()
        return reserva

    def procesar_reserva(self, id_reserva):
        reserva = self.buscar_reserva(id_reserva)
        reserva.procesar()
        return reserva
