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
- Actualización automática de inventario al confirmar pedidos

### 4. Sistema de Reservas
- Reserva de mesas con verificación de disponibilidad
- Gestión de horarios y capacidad de mesas
- Confirmación automática por correo electrónico
- Historial de reservas

### 5. Control de Inventario
- Gestión de stock de ingredientes
- Movimientos de inventario (entradas, salidas, ajustes)
- Alertas de bajo stock
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
- Envío automático de correos de confirmación de pedidos
- Envío automático de correos de confirmación de reservas
- Configuración para desarrollo (consola) y producción (SMTP)

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
Proyecto-5/
├── restaurante/          # Configuración del proyecto
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── usuarios/             # App de usuarios y autenticación
│   ├── models.py         # Modelo Usuario con roles
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── menu/                 # App de menú
│   ├── models.py        # Plato, Categoria, Ingrediente, PlatoIngrediente
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── pedidos/             # App de pedidos
│   ├── models.py        # Pedido, ItemPedido
│   ├── views.py
│   ├── reportes.py      # Generación de reportes
│   └── urls.py
├── reservas/            # App de reservas
│   ├── models.py        # Mesa, Reserva
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── inventario/          # App de inventario
│   ├── models.py        # StockInventario, MovimientoInventario
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── templates/           # Templates HTML
│   ├── base.html
│   ├── usuarios/
│   ├── menu/
│   ├── pedidos/
│   ├── reservas/
│   └── inventario/
├── static/             # Archivos estáticos
├── media/              # Archivos subidos (imágenes)
├── manage.py
└── requirements.txt
```

## Modelos de Datos

### Usuario (Personalizado)
- Extiende AbstractUser de Django
- Campos: rol, teléfono, dirección, fecha_registro
- Roles: cliente, administrador, mesero

### Menu
- **Categoria**: Categorías de platos
- **Ingrediente**: Ingredientes disponibles
- **Plato**: Platos del menú con precio, imagen, tiempo de preparación
- **PlatoIngrediente**: Relación muchos a muchos entre platos e ingredientes con cantidad

### Pedidos
- **Pedido**: Pedidos con estados, método de pago, totales
- **ItemPedido**: Items individuales de un pedido

### Reservas
- **Mesa**: Mesas del restaurante con capacidad
- **Reserva**: Reservas con fecha, hora, número de personas

### Inventario
- **StockInventario**: Stock actual de cada ingrediente
- **MovimientoInventario**: Historial de movimientos (entrada/salida/ajuste)

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

6. **Recopilar archivos estáticos**:
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

1. **Dashboard**: Ver estadísticas y gráficos
2. **Gestión de Menú**: 
   - CRUD de platos: `/menu/admin/platos/`
   - CRUD de ingredientes: `/menu/admin/ingredientes/`
3. **Gestión de Inventario**: `/inventario/`
4. **Generar Reportes**: 
   - PDF: `/pedidos/reporte/pdf/?fecha_inicio=2025-01-01&fecha_fin=2025-01-31`
   - Excel: `/pedidos/reporte/excel/?fecha_inicio=2025-01-01&fecha_fin=2025-01-31`
5. **Panel Admin Django**: `/admin/`

## Configuración de Correo

Para desarrollo, los correos se muestran en la consola. Para producción, editar `restaurante/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu_email@gmail.com'
EMAIL_HOST_PASSWORD = 'tu_contraseña'
```

## Despliegue en Render

### Requisitos

- Cuenta en Render.com
- Base de datos PostgreSQL creada en Render
- Variables de entorno preparadas

### Variables de entorno

Define estas variables en Render → Environment:

- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS=<tu-dominio-de-render>`
- `CSRF_TRUSTED_ORIGINS=https://<tu-dominio-de-render>`
- `DATABASE_URL=<url de Postgres de Render>`
- `SENDGRID_API_KEY=<SG.XXXX...>`
- `DEFAULT_FROM_EMAIL=<remitente verificado Single Sender>`
- `MEDIA_ROOT=/var/data/media` (si usas Disk para persistir imágenes)

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
   - Render → Web Service → “Run Command”: `python manage.py createsuperuser --noinput` (requiere las variables `DJANGO_SUPERUSER_*`).

### Consideraciones

- Archivos estáticos: WhiteNoise está habilitado para servir `staticfiles` en producción.
- Media (imágenes): Se almacenan en disco persistente (`MEDIA_ROOT`), recomendado para Render.
- Correo: Usa SendGrid API con `.env`/variables de entorno; el remitente debe ser Single Sender verificado.
- Admin Django: disponible en `/admin/`; superusuarios son redirigidos ahí al iniciar sesión.

## Rutas Principales

- `/` - Menú principal
- `/usuarios/login/` - Inicio de sesión
- `/usuarios/registro/` - Registro de usuarios
- `/pedidos/carrito/` - Carrito de compras
- `/pedidos/historial/` - Historial de pedidos
- `/pedidos/dashboard/` - Panel de administración
- `/reservas/crear/` - Crear reserva
- `/reservas/mis-reservas/` - Mis reservas
- `/inventario/` - Control de inventario
- `/menu/admin/platos/` - Gestión de platos (admin)
- `/menu/admin/ingredientes/` - Gestión de ingredientes (admin)

## Características Técnicas

- **Arquitectura**: MVT (Modelo-Vista-Template)
- **Autenticación**: Sistema de usuarios personalizado con roles
- **Validaciones**: Formularios validados con Django Forms
- **Seguridad**: CSRF protection, autenticación requerida, control de acceso
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

## Autor

Desarrollado como proyecto académico para Electiva 1 - Quinto Semestre

## Licencia

Este proyecto es de uso educativo.

---

**Nota**: Este sistema está diseñado para fines educativos y de demostración. Para uso en producción, se recomienda implementar medidas de seguridad adicionales y realizar pruebas exhaustivas.

