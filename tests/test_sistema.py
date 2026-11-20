import unittest
from decimal import Decimal
from software_fj.modelos import Cliente, Sala, Equipo, Asesoria, Reserva
from software_fj.sistema import SistemaFJ
from software_fj.excepciones import (ErrorValidacion, ClienteDuplicado,
                                     ServicioNoDisponible, ReservaInvalida,
                                     OperacionNoPermitida, ErrorCalculo)


class TestSoftwareFJ(unittest.TestCase):
    def setUp(self):
        self.s = SistemaFJ()
        self.s.registrar_cliente('12345678', 'Ana Ruiz', 'ana@correo.com', '3001234567')
        self.s.registrar_servicio(Sala('Sala A', '100000', 10))

    def test_validacion_cliente(self):
        with self.assertRaises(ErrorValidacion):
            Cliente('12', 'Ana', 'ana@correo.com', '3001234567')

    def test_duplicado(self):
        with self.assertRaises(ClienteDuplicado):
            self.s.registrar_cliente('12345678', 'Ana Ruiz', 'ana@correo.com', '3001234567')

    def test_costo_sobrecarga_opcional(self):
        sala = self.s.servicios[0]
        self.assertEqual(sala.calcular_costo(2), Decimal('200000.00'))
        self.assertEqual(sala.calcular_costo(2, impuesto=19), Decimal('238000.00'))
        self.assertEqual(sala.calcular_costo(2, impuesto=19, descuento=10), Decimal('214200.00'))

    def test_polimorfismo(self):
        servicios = [Sala('Sala', 100, 4), Equipo('Equipo', 50, 2), Asesoria('Asesoría', 90, 'TI')]
        self.assertEqual([s.calcular_costo(2) for s in servicios],
                         [Decimal('200.00'), Decimal('100.00'), Decimal('180.00')])

    def test_cupo_y_cancelacion(self):
        uno = self.s.crear_reserva('12345678', self.s.servicios[0].identificador, 2)
        with self.assertRaises(ServicioNoDisponible):
            self.s.crear_reserva('12345678', self.s.servicios[0].identificador, 3)
        self.s.cancelar_reserva(uno.identificador)
        self.assertEqual(self.s.crear_reserva('12345678', self.s.servicios[0].identificador, 1).estado, Reserva.PENDIENTE)

    def test_estado(self):
        reserva = self.s.crear_reserva('12345678', self.s.servicios[0].identificador, 2)
        with self.assertRaises(OperacionNoPermitida):
            reserva.procesar()
        reserva.confirmar()
        reserva.procesar()
        with self.assertRaises(OperacionNoPermitida):
            reserva.cancelar()

    def test_duracion_equipo(self):
        e = Equipo('Proyector', 1000, 2)
        with self.assertRaises(ReservaInvalida):
            e.calcular_costo('1.5')

    def test_duracion_sala(self):
        with self.assertRaises(ReservaInvalida):
            self.s.servicios[0].calcular_costo(13)

    def test_porcentaje_invalido(self):
        with self.assertRaises(ErrorCalculo):
            self.s.servicios[0].calcular_costo(1, descuento=120)

    def test_encadenamiento(self):
        with self.assertRaises(ErrorValidacion) as contexto:
            self.s.servicios[0].calcular_costo('nan?')
        self.assertIsNotNone(contexto.exception.__cause__)

    def test_encapsulamiento(self):
        with self.assertRaises(OperacionNoPermitida):
            self.s.clientes[0].documento = '87654321'
        with self.assertRaises(AttributeError):
            self.s.clientes.append('fraude')

    def test_disponibilidad(self):
        self.s.servicios[0].cambiar_disponibilidad(False)
        with self.assertRaises(ServicioNoDisponible):
            self.s.crear_reserva('12345678', self.s.servicios[0].identificador, 1)


if __name__ == '__main__':
    unittest.main()
