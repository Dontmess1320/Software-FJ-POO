# Software FJ | Sistema orientado a objetos sin bases de datos

Aplicación de consola en **Python 3.9 o superior**, sin dependencias externas. Gestiona clientes, salas por horas, equipos por días, asesorías por horas y reservas con estados. Todos los datos de negocio se guardan **exclusivamente en listas de objetos en memoria**; se pierden al cerrar. **Solo** se escribe el archivo `logs/software_fj.log`, para auditoría de eventos y errores.

## Ejecución

Desde la carpeta `Software_FJ`:

```bash
python main.py
```

Para la **simulación automática de 20 operaciones**:

```bash
python main.py --demo
```

Para ejecutar las pruebas automatizadas:

```bash
python -m unittest discover -s tests -v
```

En Windows, si `python` no está disponible, utiliza `py`.

## Estructura

- `main.py`: inicio de la aplicación / argumento `--demo`.
- `software_fj/modelos.py`: entidades `Entidad` y `Servicio` (abstractas), `Cliente`, `Sala`, `Equipo`, `Asesoria`, `Reserva`.
- `software_fj/sistema.py`: fachada de operaciones, listas encapsuladas y control de cupos.
- `software_fj/excepciones.py`: jerarquía de errores especializados.
- `software_fj/registro.py`: archivo de logs.
- `software_fj/consola.py`: menú interactivo y recuperación ante errores.
- `software_fj/demo.py`: 20 operaciones válidas e inválidas con ejecución independiente.
- `tests/test_sistema.py`: pruebas unitarias.

## Diseño orientado a objetos

- **Abstracción:** `Entidad` y `Servicio` usan `abc.ABC`, `@abstractmethod`.
- **Herencia:** `Cliente`, `Reserva` y `Servicio` derivan de `Entidad`; los tres servicios específicos derivan de `Servicio`.
- **Polimorfismo:** cada tipo de servicio sobrescribe `calcular_costo`, `validar_parametros`, `describir`.
- **Encapsulación:** campos con `__`, propiedades verificadas y vistas de listas como tuplas.
- **Sobrecarga:** en Python se implementan variantes del cálculo mediante **parámetros opcionales** (`calcular_costo(duracion)`, `calcular_costo(duracion, impuesto=19)`, `calcular_costo(duracion, impuesto=19, descuento=10)`). Python **no admite sobrecarga de firma tradicional**; esta es su alternativa idiomática.
- **Excepciones:** `try/except`, `try/except/else/finally`, excepciones personalizadas, `raise ... from ...` para encadenamiento, y trazas de error con `logger.exception`.

## Reglas de negocio

1. Documento: 5–15 dígitos, único. Nombre: mínimo 2 caracteres. Email y teléfono con formatos válidos.
2. Tarifa positiva y finita. Sala: 0+ a 12 horas, capacidad de asistentes informativa y **una reserva activa simultánea**. Equipo: 1–30 días completos, tantas reservas activas como unidades. Asesoría: 0.5–8 horas, una reserva activa simultánea.
3. Las reservas se crean **PENDIENTES** y ocupan cupo; pueden confirmarse y procesarse, o cancelarse desde PENDIENTE/CONFIRMADA. Cancelada/procesada libera cupo. No hay fechas ni calendarios: las reservas activas se consideran simultáneas. Este es un supuesto simplificado, explícito, no una agenda real.
4. Se aplican primero descuentos y luego impuestos, porcentajes entre 0 y 100 incluidos. Se calcula con `Decimal` para evitar errores monetarios típicos de `float`.
5. Cada operación de menú se gestiona con manejo de errores, registra el fallo y retorna al menú. No se usa SQLite, JSON, CSV, archivos de datos ni bases de datos.
6. Los IDs `S001`, `R001` se generan en memoria con contadores de clase. La demo consulta los IDs creados dinámicamente, incluso si se invoca desde el menú tras otras operaciones.

## Resultados esperados de la demo

20 operaciones: **11 correctas y 9 errores controlados**. Los errores incluyen correo inválido, cliente duplicado, tarifa negativa, cliente inexistente, capacidad agotada, doble confirmación, cancelación de reserva procesada, días fraccionarios e impuesto fuera de rango. El programa continúa hasta el final.

## Limitaciones explícitas

Este es un prototipo académico sin persistencia de negocio; cerrar el programa borra clientes, servicios y reservas. Las duraciones no incluyen horarios ni detección de solapamientos por fecha, ni roles, pagos o autenticación. No se debe interpretar como sistema comercial de producción.
