# Sistema de Gestión de Restaurante

Sistema web completo desarrollado con Django para la gestión de pedidos, reservas, menú e inventario de un restaurante.

## Características Principales

### 1. Autenticación y Roles
- Sistema de inicio de sesión y registro de usuarios
- Tres roles: **Cliente**, **Administrador** y **Mesero**
- Control de acceso basado en roles

### 2. Gestión de Menú
- CRUD completo de platos, categorías e ingredientes
- Asociación de ingredientes a platos con cantidades
- Gestión de precios y disponibilidad
- Búsqueda y filtrado por categorías

### 3. Sistema de Pedidos
- Carrito de compras funcional
- Proceso de checkout con cálculo de IVA (19%)
- Pago simulado (efectivo, tarjeta, transferencia)
- Historial de pedidos para clientes
- Gestión de estados de pedidos (pendiente, confirmado, en preparación, listo, entregado)
- Actualización automática de inventario al confirmar pedidos (descuenta ingredientes según receta)

### 4. Sistema de Reservas
- Reserva de mesas con verificación de disponibilidad
- Gestión de horarios y capacidad de mesas
- Confirmación por correo electrónico (consola en desarrollo, SMTP/SendGrid en producción)
- Historial de reservas

### 5. Control de Inventario
- Gestión de stock de ingredientes
- Movimientos de inventario (entradas, salidas, ajustes)
- Alertas de bajo stock (comparación `cantidad_actual` vs `cantidad_minima`)
- Historial de movimientos

### 6. Panel de Administración (Dashboard)
- Estadísticas en tiempo real:
  - Total de pedidos
  - Pedidos del día
  - Ventas diarias y mensuales
- Gráficos interactivos con Chart.js:
  - Platos más vendidos (gráfico de barras)
  - Ingresos mensuales (gráfico de línea)
  - Pedidos por estado (gráfico de dona)
- Top 10 platos más vendidos

### 7. Reportes
- Generación de reportes en PDF (usando ReportLab)
- Generación de reportes en Excel (usando pandas y openpyxl)
- Filtros por rango de fechas
- Resumen de ventas y estadísticas

### 8. Confirmación por Correo
- Envío de correos de confirmación de pedidos y reservas
- Fallback automático a consola si no hay configuración SMTP
- Soporte de SendGrid mediante `SENDGRID_API_KEY`

### 9. Interfaz de Usuario
- Diseño responsivo con Bootstrap 5
- Modo oscuro/claro con persistencia en localStorage
- Iconos con Bootstrap Icons
- Navegación intuitiva según el rol del usuario

## Tecnologías Utilizadas

- **Backend**: Django 5.2.8
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Frontend**: Bootstrap 5, Chart.js
- **Reportes**: ReportLab (PDF), pandas + openpyxl (Excel)
- **Imágenes**: Pillow

## Estructura del Proyecto

```
Sistema-para-restaurante/
├── restaurante/          # Configuración del proyecto y contexto
│   ├── settings.py       # Configuración, WhiteNoise, AUTH_USER_MODEL, email
│   ├── urls.py           # Enrutamiento principal y media/static en DEBUG
│   ├── context_processors.py  # `carrito_context`
│   └── wsgi.py
├── usuarios/             # Usuarios y autenticación
│   ├── models.py         # `Usuario` con roles y `RegistroPendiente`
│   ├── views.py          # Login, registro, verificación correo, reset password
│   ├── forms.py
│   └── urls.py
├── menu/                 # Menú del restaurante
│   ├── models.py         # Plato, Categoria, Ingrediente, PlatoIngrediente
│   ├── views.py          # Index, detalle, CRUD con permisos
│   ├── decorators.py     # Permisos por rol (admin/mesero)
│   ├── forms.py
│   └── urls.py
├── pedidos/              # Pedidos y dashboard
│   ├── models.py         # Pedido, ItemPedido (IVA 19%)
│   ├── views.py          # Carrito, checkout, historial, dashboard
│   ├── reportes.py       # PDF y Excel
│   └── urls.py
├── reservas/             # Reservas de mesas
│   ├── models.py         # Mesa, Reserva
│   ├── views.py          # Crear, detalle, cancelar, disponibilidad (AJAX)
│   ├── forms.py
│   └── urls.py
├── inventario/           # Inventario de ingredientes
│   ├── models.py         # StockInventario, MovimientoInventario
│   ├── views.py          # Lista, detalle, movimientos, editar stock
│   ├── forms.py
│   └── urls.py
├── templates/            # Templates HTML
│   ├── base.html
│   ├── usuarios/
│   ├── menu/
│   ├── pedidos/
│   ├── reservas/
│   └── inventario/
├── manage.py
├── requirements.txt
└── db.sqlite3 (en desarrollo)
```

## Modelos de Datos

### Usuario (Personalizado)
- Extiende AbstractUser de Django
- Campos: rol, teléfono, dirección, fecha_registro
- Roles: cliente, administrador, mesero
  - Asignación automática de rol administrador para superusuarios

### Menu
- **Categoria**: Categorías de platos
- **Ingrediente**: Ingredientes disponibles
- **Plato**: Platos del menú con precio, imagen, tiempo de preparación
- **PlatoIngrediente**: Relación muchos a muchos entre platos e ingredientes con cantidad

### Pedidos
- **Pedido**: Pedidos con estados, método de pago, totales
- **ItemPedido**: Items individuales de un pedido
  - Cálculo automático de `subtotal` y recálculo de totales del pedido

### Reservas
- **Mesa**: Mesas del restaurante con capacidad
- **Reserva**: Reservas con fecha, hora, número de personas

### Inventario
- **StockInventario**: Stock actual de cada ingrediente
- **MovimientoInventario**: Historial de movimientos (entrada/salida/ajuste)
  - Se generan salidas automáticamente al confirmar pedidos

## Instalación

### Requisitos Previos
- Python 3.8 o superior
- pip
- Entorno virtual (recomendado)

### Pasos de Instalación

1. **Clonar o descargar el proyecto**

2. **Crear y activar entorno virtual** (si no existe):
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

4. **Aplicar migraciones**:
```bash
python manage.py migrate
```

5. **Crear superusuario** (opcional):
```bash
python manage.py createsuperuser
```

6. **Recopilar archivos estáticos** (necesario en producción):
```bash
python manage.py collectstatic
```

7. **Ejecutar servidor de desarrollo**:
```bash
python manage.py runserver
```

8. **Acceder a la aplicación**:
- URL principal: http://127.0.0.1:8000/
- Panel de administración: http://127.0.0.1:8000/admin/

## Uso del Sistema

### Para Clientes

1. **Registro/Inicio de Sesión**: Crear cuenta o iniciar sesión
2. **Ver Menú**: Navegar por platos disponibles
3. **Agregar al Carrito**: Seleccionar platos y cantidades
4. **Checkout**: Confirmar pedido y seleccionar método de pago
5. **Ver Historial**: Consultar pedidos anteriores
6. **Reservar Mesa**: Crear reservas de mesas

### Para Meseros

1. **Ver Pedidos**: Lista de pedidos pendientes y en curso
2. **Actualizar Estados**: Cambiar estado de pedidos (confirmado → en preparación → listo → entregado)

### Para Administradores

1. **Dashboard**: `/pedidos/dashboard/` (acceso rápido: `/gestion/`)
2. **Gestión de Menú**:
   - CRUD de platos: `/menu/gestion/platos/`
   - CRUD de ingredientes: `/menu/gestion/ingredientes/`
3. **Gestión de Inventario**: `/inventario/`
4. **Generar Reportes**:
   - PDF: `/pedidos/reporte/pdf/?fecha_inicio=YYYY-MM-DD&fecha_fin=YYYY-MM-DD`
   - Excel: `/pedidos/reporte/excel/?fecha_inicio=YYYY-MM-DD&fecha_fin=YYYY-MM-DD`
5. **Panel Admin Django**: `/admin/`

## Configuración de Correo

En desarrollo, si no se configuran variables de correo, se usa la consola.
En producción, configurar SMTP o SendGrid mediante variables de entorno.

Variables relevantes en `restaurante/settings.py`:

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend   # opcional; si no hay EMAIL_HOST, se usa consola
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<tu_email>
EMAIL_HOST_PASSWORD=<tu_contraseña>
DEFAULT_FROM_EMAIL=<remitente@dominio>
SENDGRID_API_KEY=<SG.xxxxx>  # si se usa SendGrid
```

## Despliegue en Render

### Requisitos

- Cuenta en Render.com
- Base de datos PostgreSQL creada en Render
- Variables de entorno preparadas

### Variables de entorno

Define estas variables en Render → Environment:

Obligatorias/útiles:

- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS=<tu-dominio-de-render>`
- `CSRF_TRUSTED_ORIGINS=https://<tu-dominio-de-render>`
- `DATABASE_URL=<url de Postgres de Render>`
- `DEFAULT_FROM_EMAIL=<remitente verificado>`
- `SENDGRID_API_KEY=<SG.XXXX...>` (opcional si usas SendGrid)
- `MEDIA_ROOT=/var/data/media` (si usas Disk para imágenes)

Opcionales para crear el superusuario automáticamente:

- `DJANGO_SUPERUSER_USERNAME`
- `DJANGO_SUPERUSER_EMAIL`
- `DJANGO_SUPERUSER_PASSWORD`

### Comandos de Build y Start

- Build Command:

```bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
```

- Start Command:

```bash
gunicorn restaurante.wsgi:application
```

### Pasos en Render

1. Crea la base de datos PostgreSQL y copia `DATABASE_URL` (Internal o External).
2. Crea un Web Service apuntando al repositorio.
3. En “Disks”, añade un Disk para persistir media:
   - Mount Path: `/var/data`
   - Define `MEDIA_ROOT=/var/data/media`
4. Configura las variables de entorno anteriores.
5. Guarda y despliega.
6. Crear superusuario (una vez):
   - Render → Web Service → “Run Command”: `python manage.py createsuperuser --noinput` (requiere `DJANGO_SUPERUSER_*`).

### Consideraciones

- Archivos estáticos: WhiteNoise sirve `staticfiles` en producción.
- Media (imágenes): Usar Disk persistente (`MEDIA_ROOT`) para Render.
- Correo: SendGrid o SMTP con variables de entorno. El remitente debe existir.
- Admin Django: `/admin/`; superusuarios redirigen automáticamente.

## Rutas Principales

- `/` - Menú principal
- `/gestion/` - Redirección a dashboard
- `/usuarios/login/` - Inicio de sesión
- `/usuarios/registro/` - Registro de usuarios
- `/pedidos/carrito/` - Carrito de compras
- `/pedidos/historial/` - Historial de pedidos
- `/pedidos/dashboard/` - Panel de administración
- `/pedidos/reporte/<pdf|excel>/` - Reportes
- `/reservas/crear/` - Crear reserva
- `/reservas/mis-reservas/` - Mis reservas
- `/inventario/` - Control de inventario
- `/menu/gestion/platos/` - Gestión de platos (admin/mesero)
- `/menu/gestion/ingredientes/` - Gestión de ingredientes (admin/mesero)

## Características Técnicas

- **Arquitectura**: MVT (Modelo-Vista-Template)
- **Autenticación**: Sistema de usuarios personalizado con roles (`AUTH_USER_MODEL`)
- **Validaciones**: Formularios validados con Django Forms
- **Seguridad**: CSRF, autenticación requerida, control de acceso por decoradores
- **Base de Datos**: Relaciones con ForeignKey, OneToOneField
- **Gráficos**: Chart.js para visualización de datos
- **Reportes**: PDF (ReportLab) y Excel (pandas/openpyxl)

## Desarrollo Futuro

- Integración con pasarelas de pago reales
- Notificaciones push
- App móvil
- Sistema de valoraciones y comentarios
- Programación de entregas
- Integración con servicios de delivery

## Desarrollo Local

### Variables de entorno (.env)

El proyecto puede cargar variables desde `.env` automáticamente.

Ejemplo de `.env` para desarrollo:

```
SECRET_KEY=dev-secret
DEBUG=True
DEFAULT_FROM_EMAIL=noreply@localhost
# Configuración SMTP opcional para probar correo
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=tu_email
# EMAIL_HOST_PASSWORD=tu_contraseña
```

### Comandos útiles

```
python manage.py check           # Verifica configuración
python manage.py makemigrations  # Crea migraciones
python manage.py migrate         # Aplica migraciones
python manage.py createsuperuser # Crea superusuario
python manage.py runserver       # Levanta servidor
python manage.py test            # Ejecuta pruebas (si existen)
```

### Flujo de operación

- Carrito: un `Pedido` en estado `pendiente` por cliente; items se agregan desde el menú.
- Checkout: cambia a `confirmado`, calcula totales con IVA 19% (`pedidos/models.py`).
- Inventario: por cada item confirmado se genera `MovimientoInventario` de salida y se descuenta `StockInventario` (`inventario/models.py`).
- Reservas: verifica disponibilidad y evita solapamientos de 2 horas por mesa.
- Dashboard: agrega métricas y series para gráficos.

### Acceso y permisos

- Decoradores en `menu/decorators.py` controlan acceso:
  - `staff_or_mesero_required`: administradores y meseros
  - `admin_role_required`: solo administradores/superusuarios

## Autor

Desarrollado como proyecto académico para Electiva 1 - Quinto Semestre

## Licencia

Este proyecto es de uso educativo.

---

**Nota**: Este sistema está diseñado para fines educativos y de demostración. Para uso en producción, se recomienda implementar medidas de seguridad adicionales y realizar pruebas exhaustivas.

