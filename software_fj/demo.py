"""Demostración reproducible de operaciones válidas e inválidas."""
from .sistema import SistemaFJ
from .modelos import Sala, Equipo, Asesoria
from .registro import logger


def ejecutar_demo():
    sistema = SistemaFJ()
    resultados = []
    ids = {}

    def operar(nombre, accion):
        try:
            salida = accion()
        except Exception as exc:
            # La demo nunca se detiene por fallos individuales.
            logger.exception('DEMO FALLIDA | %s', nombre)
            resultados.append((nombre, 'ERROR CONTROLADO', str(exc)))
        else:
            detalle = salida.describir() if hasattr(salida, 'describir') else str(salida)
            logger.info('DEMO CORRECTA | %s', nombre)
            resultados.append((nombre, 'CORRECTO', detalle))
        finally:
            logger.info('DEMO FINALIZADA | %s', nombre)

    operar('01 Registrar cliente correcto', lambda: sistema.registrar_cliente('12345678', 'Ana Pérez', 'ana@correo.com', '3001234567'))
    operar('02 Registrar cliente con correo inválido', lambda: sistema.registrar_cliente('87654321', 'Luis Rojas', 'correo_invalido', '3001234567'))
    operar('03 Registrar cliente duplicado', lambda: sistema.registrar_cliente('12345678', 'Otra Ana', 'otra@correo.com', '3001234567'))
    operar('04 Registrar segundo cliente', lambda: sistema.registrar_cliente('12345999', 'Juan Castro', 'juan@correo.com', '3101234567'))
    operar('05 Crear sala válida', lambda: sistema.registrar_servicio(Sala('Sala Ejecutiva', '60000', 12)))
    ids['sala'] = sistema.servicios[-1].identificador
    operar('06 Crear equipo válido', lambda: sistema.registrar_servicio(Equipo('Proyector 4K', '45000', 2)))
    ids['equipo'] = sistema.servicios[-1].identificador
    operar('07 Crear asesoría válida', lambda: sistema.registrar_servicio(Asesoria('Transformación digital', '90000', 'Tecnología')))
    ids['asesoria'] = sistema.servicios[-1].identificador
    operar('08 Crear servicio con tarifa inválida', lambda: sistema.registrar_servicio(Sala('Sala Invalida', '-100', 10)))
    operar('09 Crear reserva de sala válida', lambda: sistema.crear_reserva('12345678', ids['sala'], '2', impuesto=19))
    ids['reserva_sala'] = sistema.reservas[-1].identificador
    operar('10 Rechazar reserva con cliente inexistente', lambda: sistema.crear_reserva('00000000', ids['sala'], '2'))
    operar('11 Rechazar reserva por falta de cupo', lambda: sistema.crear_reserva('12345999', ids['sala'], '1'))
    operar('12 Confirmar reserva', lambda: sistema.confirmar_reserva(ids['reserva_sala']))
    operar('13 Rechazar confirmación repetida', lambda: sistema.confirmar_reserva(ids['reserva_sala']))
    operar('14 Procesar reserva confirmada', lambda: sistema.procesar_reserva(ids['reserva_sala']))
    operar('15 Rechazar cancelación procesada', lambda: sistema.cancelar_reserva(ids['reserva_sala']))
    operar('16 Crear reserva de equipo con descuento', lambda: sistema.crear_reserva('12345999', ids['equipo'], '3', descuento=10))
    ids['reserva_equipo'] = sistema.reservas[-1].identificador
    operar('17 Cancelar reserva de equipo', lambda: sistema.cancelar_reserva(ids['reserva_equipo']))
    operar('18 Rechazar duración fraccionaria para equipo', lambda: sistema.crear_reserva('12345999', ids['equipo'], '1.5'))
    operar('19 Crear reserva de asesoría', lambda: sistema.crear_reserva('12345678', ids['asesoria'], '1.5'))
    operar('20 Rechazar impuesto excesivo', lambda: sistema.crear_reserva('12345999', ids['equipo'], '2', impuesto=101))

    print('\n' + '=' * 78)
    print('SOFTWARE FJ | DEMOSTRACIÓN DE 20 OPERACIONES')
    print('=' * 78)
    for nombre, estado, detalle in resultados:
        print(f'\n{nombre} | {estado}\n  {detalle}')
    print(f'\nResumen: {sum(e == "CORRECTO" for _, e, _ in resultados)} correctas, '
          f'{sum(e == "ERROR CONTROLADO" for _, e, _ in resultados)} errores controlados.')
    print('Registro de eventos: logs/software_fj.log')
    return resultados
