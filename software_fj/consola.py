"""Menú interactivo resiliente; captura y registra excepciones por operación."""
from .demo import ejecutar_demo
from .excepciones import ErrorSoftwareFJ
from .modelos import Sala, Equipo, Asesoria
from .registro import logger
from .sistema import SistemaFJ


def solicitar(mensaje):
    return input(mensaje).strip()


def menu():
    sistema = SistemaFJ()
    opciones = '''\n=== SOFTWARE FJ - MENÚ ===
1. Registrar cliente
2. Crear servicio
3. Crear reserva
4. Confirmar reserva
5. Cancelar reserva
6. Procesar reserva
7. Ver clientes
8. Ver servicios
9. Ver reservas
10. Cambiar disponibilidad de servicio
11. Ejecutar simulación (20 operaciones en sistema independiente)
0. Salir
'''
    while True:
        print(opciones)
        try:
            opcion = solicitar('Elige una opción: ')
            if opcion == '0':
                logger.info('Aplicación finalizada por el usuario')
                print('Hasta pronto.')
                break
            elif opcion == '1':
                cliente = sistema.registrar_cliente(
                    solicitar('Documento: '), solicitar('Nombre: '),
                    solicitar('Correo: '), solicitar('Teléfono: '))
                print('Registrado:', cliente.describir())
            elif opcion == '2':
                tipo = solicitar('Tipo (1=Sala, 2=Equipo, 3=Asesoría): ')
                nombre = solicitar('Nombre del servicio: ')
                tarifa = solicitar('Tarifa por hora/día (COP): ')
                if tipo == '1':
                    servicio = Sala(nombre, tarifa, int(solicitar('Capacidad de personas: ')))
                elif tipo == '2':
                    servicio = Equipo(nombre, tarifa, int(solicitar('Unidades disponibles: ')))
                elif tipo == '3':
                    servicio = Asesoria(nombre, tarifa, solicitar('Especialidad: '))
                else:
                    raise ValueError('Tipo de servicio desconocido.')
                sistema.registrar_servicio(servicio)
                print('Creado:', servicio.describir())
            elif opcion == '3':
                reserva = sistema.crear_reserva(
                    solicitar('Documento del cliente: '),
                    solicitar('ID servicio (ej. S001): '),
                    solicitar('Duración (horas para sala/asesoría; días para equipo): '),
                    impuesto=solicitar('Impuesto % (0 si no aplica): ') or '0',
                    descuento=solicitar('Descuento % (0 si no aplica): ') or '0')
                print('Creada:', reserva.describir())
            elif opcion in ('4', '5', '6'):
                identificador = solicitar('ID reserva (ej. R001): ')
                accion = {'4': sistema.confirmar_reserva, '5': sistema.cancelar_reserva,
                          '6': sistema.procesar_reserva}[opcion]
                print('Actualizada:', accion(identificador).describir())
            elif opcion in ('7', '8', '9'):
                elementos = {'7': sistema.clientes, '8': sistema.servicios,
                             '9': sistema.reservas}[opcion]
                if not elementos:
                    print('No hay registros.')
                for elemento in elementos:
                    print('-', elemento.describir())
            elif opcion == '10':
                servicio = sistema.buscar_servicio(solicitar('ID servicio: '))
                valor = solicitar('¿Activar? (s/n): ').lower()
                if valor not in ('s', 'n'):
                    raise ValueError('Respuesta inválida; utiliza s o n.')
                servicio.cambiar_disponibilidad(valor == 's')
                print('Disponibilidad actualizada.')
            elif opcion == '11':
                ejecutar_demo()
            else:
                raise ValueError('Opción inválida; elige una de las opciones del menú.')
        except (ErrorSoftwareFJ, ValueError, TypeError, KeyError) as exc:
            logger.exception('Error controlado en opción %s', locals().get('opcion', '?'))
            print(f'Error controlado: {exc}')
        except (KeyboardInterrupt, EOFError):
            logger.info('Salida por interrupción de entrada')
            print('\nPrograma finalizado.')
            break
        except Exception as exc:
            logger.exception('Error inesperado de ejecución')
            print(f'Ocurrió un error inesperado: {exc}. Puedes seguir utilizando el programa.')
        finally:
            logger.info('Ciclo de menú completado')
