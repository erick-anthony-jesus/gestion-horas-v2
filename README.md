# 🎯 Sistema de Gestión de Horas - FASE 2 y 3 ✅

Sistema completo de gestión de horas con **autenticación**, **auditoría** y **notificaciones**.

## ✨ Características Implementadas

### Fase 2: Autenticación y Seguridad 🔐
- ✅ Sistema de login con contraseñas encriptadas
- ✅ 3 roles: Admin, Supervisor, Trabajador
- ✅ Control de acceso basado en roles
- ✅ Registro completo de auditoría
- ✅ Recuperación de contraseña
- ✅ Sesiones seguras con cookies

### Fase 3: Notificaciones 📧
- ✅ Emails profesionales con Gmail
- ✅ WhatsApp con Twilio (opcional)
- ✅ Notificaciones in-app en tiempo real
- ✅ Tareas programadas automáticas
- ✅ Plantillas HTML personalizables
- ✅ Panel de configuración de notificaciones

---

## 🚀 Instalación Rápida

### 1. Requisitos Previos
```bash
Python 3.8 o superior
pip
```

### 2. Clonar/Descargar el Proyecto
```bash
cd gestion_horas
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Copiar `.env.example` a `.env` y configurar:

```bash
cp .env.example .env
```

Editar `.env` con tus credenciales:

```env
# Gmail (REQUERIDO para emails)
GMAIL_USER=tu-email@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx

# Twilio WhatsApp (OPCIONAL)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# App
SECRET_KEY=tu-clave-secreta-muy-segura
APP_URL=http://localhost:8501
```

### 5. Ejecutar la Aplicación
```bash
streamlit run app.py
```

La aplicación estará disponible en: **http://localhost:8501**

---

## 👤 Usuarios de Prueba

### Administrador
- **Usuario:** `admin`
- **Contraseña:** `admin123`
- **Permisos:** Acceso total al sistema

### Supervisor
- **Usuario:** `supervisor1`
- **Contraseña:** `super123`
- **Permisos:** Gestión de su área

### Trabajador
- **Usuario:** `trabajador1`
- **Contraseña:** `trab123`
- **Permisos:** Solo ver sus propias horas

---

## 📧 Configuración de Gmail

Para enviar emails necesitas una **Contraseña de Aplicación** de Gmail:

### Paso 1: Habilitar 2FA
1. Ve a https://myaccount.google.com/security
2. Habilita "Verificación en dos pasos"

### Paso 2: Generar Contraseña de Aplicación
1. Ve a https://myaccount.google.com/apppasswords
2. Selecciona "Correo" y "Windows Computer"
3. Copia la contraseña generada (16 caracteres)
4. Pégala en `.env` como `GMAIL_APP_PASSWORD`

⚠️ **Importante:** Usa la contraseña de aplicación, NO tu contraseña normal de Gmail.

---

## 💬 Configuración de WhatsApp (Opcional)

WhatsApp usa Twilio. Para configurarlo:

### 1. Crear Cuenta Twilio
- Registrarte en: https://www.twilio.com/try-twilio
- Obtener créditos gratuales de prueba

### 2. Obtener Credenciales
- **Account SID:** En el dashboard de Twilio
- **Auth Token:** En el dashboard de Twilio
- **WhatsApp Number:** `whatsapp:+14155238886` (Twilio Sandbox)

### 3. Configurar Sandbox
1. Envía un WhatsApp a +1 415 523 8886
2. Mensaje: `join [tu-código]` (te lo da Twilio)
3. Ahora puedes recibir mensajes

**Nota:** El sandbox es gratuito pero requiere que cada usuario se una primero.

---

## 📂 Estructura del Proyecto

```
gestion_horas/
│
├── app.py                      # Aplicación principal ⭐
├── config.yaml                 # Usuarios y configuración
├── requirements.txt            # Dependencias
├── .env                        # Variables de entorno (crear desde .env.example)
│
├── auth/
│   └── __init__.py            # Sistema de autenticación 🔐
│
├── database/
│   ├── audit.py               # Sistema de auditoría 📋
│   ├── notifications.py       # Notificaciones in-app 🔔
│   ├── auditoria.db           # Base de datos de logs (se crea automáticamente)
│   └── notifications.db       # Base de datos de notificaciones (se crea automáticamente)
│
├── notifications/
│   ├── email_service.py       # Servicio de Gmail 📧
│   ├── email_templates.py     # Plantillas HTML 📝
│   ├── whatsapp_service.py    # Servicio de WhatsApp 💬
│   └── scheduler.py           # Tareas programadas ⏰
│
└── pages/
    ├── audit_page.py          # Página de auditoría
    └── notifications_config_page.py  # Configuración de notificaciones
```

---

## 🔧 Funcionalidades Detalladas

### 1. Sistema de Autenticación

#### Roles y Permisos

| Rol | Permisos |
|-----|----------|
| **Admin** | Acceso total, gestión de usuarios, auditoría |
| **Supervisor** | Gestión de su área, reportes de equipo |
| **Trabajador** | Ver sus propias horas, configurar notificaciones |

#### Seguridad
- Contraseñas encriptadas con bcrypt
- Sesiones con cookies firmadas
- Recuperación de contraseña por email
- Auditoría de intentos de login fallidos

### 2. Sistema de Auditoría

#### Qué se Registra
- ✅ Inicios y cierres de sesión
- ✅ Creación/modificación/eliminación de trabajadores
- ✅ Cambios en horas asignadas
- ✅ Exportaciones e importaciones
- ✅ Navegación entre páginas
- ✅ Todos los cambios críticos

#### Visualización
- Filtros por usuario, acción, fecha
- Exportación a CSV/Excel
- Estadísticas y gráficos
- Búsqueda avanzada

#### Mantenimiento
- Limpieza automática de logs antiguos
- Retención configurable (30-365 días)

### 3. Notificaciones por Email

#### Tipos de Emails
1. **Horas Asignadas** - Cuando se asignan horas a un trabajador
2. **Cambios en Horas** - Cuando se modifican horas existentes
3. **Recordatorios Semanales** - Lunes a las 9 AM
4. **Reportes Mensuales** - Primer día del mes
5. **Alertas de Sobrecarga** - Cuando se excede el límite de horas
6. **Bienvenida** - Para nuevos usuarios
7. **Recuperación de Contraseña**

#### Plantillas
- HTML profesional y responsivo
- Diseño moderno con gradientes
- Compatible con todos los clientes de email
- Personalizables

### 4. Notificaciones por WhatsApp

#### Tipos de Alertas
- 🚨 **Sobrecargas urgentes** (>40h semanales)
- ⚠️ **Cambios críticos** en horas
- 📅 **Recordatorios** importantes
- ✅ **Aprobaciones** requeridas

#### Características
- Solo alertas urgentes (no spam)
- Mensajes cortos y concisos
- Formato optimizado para WhatsApp
- Opcional y configurable por usuario

### 5. Notificaciones In-App

#### Características
- 🔔 Panel en el sidebar
- 📊 Contador de no leídas
- 🎨 Iconos y colores por tipo
- ⏰ Timestamp de cada notificación
- ✅ Marcar como leída
- 🗑️ Eliminar individual o masiva

#### Tipos
- **Info** 🔵 - Información general
- **Warning** 🟡 - Advertencias
- **Success** 🟢 - Confirmaciones
- **Error** 🔴 - Errores críticos
- **Reminder** ⏰ - Recordatorios

### 6. Tareas Programadas

#### Jobs Automáticos

| Tarea | Frecuencia | Descripción |
|-------|-----------|-------------|
| Recordatorio Semanal | Lunes 9 AM | Envía recordatorios de horas pendientes |
| Reporte Mensual | Día 1 a las 8 AM | Reporte mensual a supervisores |
| Verificar Sobrecargas | Cada 6 horas | Detecta trabajadores sobrecargados |
| Limpiar Notificaciones | Diario 2 AM | Elimina notificaciones leídas antiguas |

---

## 📊 Uso del Sistema

### Como Administrador

1. **Gestionar Usuarios**
   - Ver todos los trabajadores
   - Asignar/modificar horas
   - Cambiar roles y permisos

2. **Monitorear Actividad**
   - Revisar logs de auditoría
   - Ver estadísticas del sistema
   - Exportar reportes

3. **Configurar Sistema**
   - Gestionar rubros
   - Configurar notificaciones globales
   - Limpiar datos antiguos

### Como Supervisor

1. **Gestionar Mi Equipo**
   - Ver trabajadores de mi área
   - Modificar horas de mi equipo
   - Aprobar cambios

2. **Recibir Reportes**
   - Reporte mensual automático
   - Alertas de sobrecargas en mi equipo
   - Estadísticas del área

### Como Trabajador

1. **Ver Mis Horas**
   - Consultar horas asignadas
   - Ver distribución por rubro
   - Confirmar asignaciones

2. **Configurar Notificaciones**
   - Elegir cómo recibir notificaciones
   - Configurar email/WhatsApp
   - Personalizar preferencias

---

## 🔔 Configurar Notificaciones

Cada usuario puede personalizar sus notificaciones:

### Email
- ✅ Activar/desactivar emails
- 📧 Elegir qué tipos recibir
- 📅 Frecuencia de recordatorios

### WhatsApp
- 💬 Activar solo para urgentes
- 📱 Configurar número de teléfono
- 🚨 Recibir alertas críticas

### In-App
- 🔔 Mostrar/ocultar en sidebar
- 🖥️ Notificaciones de escritorio
- 📊 Gestionar historial

---

## 🧪 Probar el Sistema

### 1. Probar Autenticación
```
1. Iniciar sesión como admin
2. Cerrar sesión
3. Iniciar como supervisor
4. Verificar permisos diferentes
```

### 2. Probar Auditoría
```
1. Login como admin
2. Ir a "Auditoría"
3. Ver logs de login
4. Aplicar filtros
5. Exportar a CSV
```

### 3. Probar Emails
```
1. Ir a "Notificaciones"
2. Configurar tu email
3. Click en "Enviar Email de Prueba"
4. Verificar recepción
```

### 4. Probar WhatsApp (opcional)
```
1. Configurar Twilio en .env
2. Unirte al sandbox
3. Configurar tu número
4. Enviar mensaje de prueba
```

### 5. Probar Notificaciones In-App
```
1. Las notificaciones aparecen automáticamente
2. Revisar en el sidebar
3. Marcar como leídas
4. Eliminar antiguas
```

---

## ⚠️ Solución de Problemas

### Emails no se envían

**Problema:** Error al enviar email

**Soluciones:**
1. Verificar que `GMAIL_USER` y `GMAIL_APP_PASSWORD` estén en `.env`
2. Usar contraseña de aplicación, no contraseña normal
3. Habilitar 2FA en Gmail
4. Verificar que no haya espacios extra en `.env`

### WhatsApp no funciona

**Problema:** Error enviando WhatsApp

**Soluciones:**
1. Verificar credenciales de Twilio en `.env`
2. Asegurarse de estar unido al sandbox
3. Verificar formato del número: `+51999999999`
4. Revisar créditos de Twilio

### Base de datos no se crea

**Problema:** Error "database locked"

**Soluciones:**
1. Cerrar otras instancias de la app
2. Eliminar archivos `.db` y reiniciar
3. Verificar permisos de la carpeta `database/`

### Scheduler no inicia

**Problema:** Tareas programadas no se ejecutan

**Soluciones:**
1. Verificar que APScheduler esté instalado
2. Revisar logs en consola
3. Reiniciar la aplicación
4. Verificar zona horaria del sistema

---

## 📝 Notas Importantes

### Seguridad
- ⚠️ **NUNCA** commitear `.env` o `config.yaml` con credenciales reales
- 🔒 Cambiar `SECRET_KEY` en producción
- 🔐 Usar contraseñas fuertes para usuarios
- 🛡️ Habilitar HTTPS en producción

### Producción
- 📧 Configurar un servidor SMTP profesional (no Gmail personal)
- 💬 Upgrade de Twilio de sandbox a número real
- 🗄️ Migrar de SQLite a PostgreSQL para mejor rendimiento
- ⚙️ Configurar backup automático de bases de datos
- 🚀 Usar servidor WSGI (Gunicorn) en vez de Streamlit directo

### Escalabilidad
- Si >1000 usuarios, considerar Redis para sesiones
- Para emails masivos, usar SendGrid o Amazon SES
- Implementar queue system (Celery + Redis) para tareas pesadas

---

## 🆘 Soporte

### Problemas Comunes
- Revisa la sección "Solución de Problemas"
- Verifica los logs en la consola
- Asegúrate de que todas las dependencias estén instaladas

### Obtener Ayuda
- Revisa la documentación de cada módulo
- Consulta los comentarios en el código
- Verifica los ejemplos en las plantillas

---

## 📦 Dependencias Principales

| Librería | Versión | Uso |
|----------|---------|-----|
| streamlit | 1.31.0 | Framework web |
| streamlit-authenticator | 0.3.2 | Autenticación |
| pandas | 2.2.0 | Manejo de datos |
| APScheduler | 3.10.4 | Tareas programadas |
| twilio | 8.13.0 | WhatsApp |
| PyYAML | 6.0.1 | Configuración |
| bcrypt | 4.1.2 | Encriptación |

---

## 🎯 Próximas Fases

### Fase 4: Estadísticas 📊
- Dashboard interactivo con Plotly
- Reportes PDF automatizados
- Métricas y KPIs
- Comparativas y tendencias

### Fase 5: Workflow ⚙️
- Sistema de aprobaciones
- Comentarios en cambios
- Histórico detallado
- Reversión de cambios

### Fase 6: Inteligencia 🤖
- Distribución automática con ML
- Detección de anomalías
- Predicción de necesidades
- Optimización de recursos

---

## ✅ Checklist de Implementación

### Fase 2 - Completada ✅
- [x] Login funcional
- [x] 3 roles implementados
- [x] Control de acceso
- [x] Auditoría completa
- [x] Recuperación de contraseña

### Fase 3 - Completada ✅
- [x] Servicio de email
- [x] Plantillas HTML
- [x] WhatsApp con Twilio
- [x] Notificaciones in-app
- [x] Scheduler automático
- [x] Panel de configuración

---

## 📄 Licencia

Este proyecto es propietario y confidencial.

---

## 🎉 ¡Listo para Usar!

El sistema está completamente funcional con:
- ✅ Autenticación segura
- ✅ Auditoría completa
- ✅ Notificaciones por email
- ✅ WhatsApp (opcional)
- ✅ Notificaciones in-app
- ✅ Tareas automatizadas

**¡Disfruta tu nuevo sistema de gestión de horas!** 🚀
