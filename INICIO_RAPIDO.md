# 🚀 GUÍA DE INICIO RÁPIDO

## ⚡ En 5 Minutos

### 1. Instalar Dependencias
```bash
cd gestion_horas
pip install -r requirements.txt
```

### 2. Configurar Email (Mínimo)
Edita `.env.example` y renómbralo a `.env`:

```env
GMAIL_USER=tu-email@gmail.com
GMAIL_APP_PASSWORD=tu-contraseña-de-app-gmail
```

**¿Cómo obtener contraseña de app?**
1. Ve a https://myaccount.google.com/security
2. Habilita "Verificación en 2 pasos"
3. Ve a https://myaccount.google.com/apppasswords
4. Genera una contraseña para "Correo"
5. Cópiala (16 caracteres sin espacios)

### 3. Ejecutar Setup
```bash
python setup.py
```

### 4. Iniciar Aplicación
```bash
streamlit run app.py
```

### 5. Login
Abre http://localhost:8501

**Usuarios de prueba:**
- Admin: `admin` / `admin123`
- Supervisor: `supervisor1` / `super123`
- Trabajador: `trabajador1` / `trab123`

---

## ✅ ¿Qué Está Implementado?

### Fase 2: Autenticación ✅
- ✅ Login con contraseñas encriptadas
- ✅ 3 roles (Admin, Supervisor, Trabajador)
- ✅ Control de acceso por rol
- ✅ Auditoría completa
- ✅ Recuperación de contraseña

### Fase 3: Notificaciones ✅
- ✅ Emails con Gmail
- ✅ WhatsApp con Twilio (opcional)
- ✅ Notificaciones in-app
- ✅ Tareas programadas
- ✅ Panel de configuración

---

## 📂 Estructura de Archivos

```
gestion_horas/
├── app.py                 ⭐ APLICACIÓN PRINCIPAL
├── setup.py              🔧 Script de setup inicial
├── config.yaml           👥 Usuarios del sistema
├── .env                  🔐 Variables de entorno
├── requirements.txt      📦 Dependencias
│
├── auth/                 🔐 Autenticación
│   └── __init__.py       - Login, roles, permisos
│
├── database/             💾 Bases de datos
│   ├── audit.py          - Sistema de auditoría
│   └── notifications.py  - Notificaciones in-app
│
├── notifications/        📧 Sistema de notificaciones
│   ├── email_service.py      - Servicio Gmail
│   ├── email_templates.py    - Plantillas HTML
│   ├── whatsapp_service.py   - Servicio Twilio
│   └── scheduler.py          - Tareas automáticas
│
└── pages/                📄 Páginas de la app
    ├── audit_page.py         - Visualización de logs
    └── notifications_config_page.py  - Configuración
```

---

## 🎯 Funcionalidades por Rol

### 👑 Administrador
- ✅ Acceso total al sistema
- ✅ Gestionar todos los trabajadores
- ✅ Ver registro de auditoría
- ✅ Exportar datos
- ✅ Configurar sistema

### 👥 Supervisor
- ✅ Gestionar su área
- ✅ Ver equipo
- ✅ Recibir reportes mensuales
- ✅ Aprobar cambios

### 👤 Trabajador
- ✅ Ver sus horas
- ✅ Configurar notificaciones
- ✅ Descargar reportes personales

---

## 📧 Tipos de Notificaciones

### Email
1. **Horas Asignadas** - Cuando se asignan horas
2. **Cambios** - Cuando se modifican horas
3. **Recordatorios Semanales** - Lunes 9 AM
4. **Reportes Mensuales** - Día 1 del mes
5. **Alertas de Sobrecarga** - >40h semanales

### WhatsApp (Opcional)
- 🚨 Alertas urgentes de sobrecarga
- ⚠️ Cambios críticos
- 📅 Recordatorios importantes

### In-App
- 🔔 Notificaciones en tiempo real
- 📊 Panel en sidebar
- ✅ Marcar como leídas
- 🗑️ Gestión de historial

---

## 🔧 Configuración Avanzada

### WhatsApp (Opcional)

1. **Crear cuenta Twilio:**
   https://www.twilio.com/try-twilio

2. **Obtener credenciales:**
   - Account SID
   - Auth Token
   - WhatsApp Number (sandbox: +14155238886)

3. **Agregar a `.env`:**
```env
TWILIO_ACCOUNT_SID=ACxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

4. **Unirte al sandbox:**
   - Envía WhatsApp a +1 415 523 8886
   - Mensaje: `join [código]`

---

## ⚙️ Tareas Programadas

El sistema ejecuta automáticamente:

| Tarea | Frecuencia | Descripción |
|-------|-----------|-------------|
| **Recordatorios** | Lunes 9 AM | Horas pendientes |
| **Reportes** | Día 1 a 8 AM | Reporte mensual |
| **Sobrecargas** | Cada 6 horas | Detectar excesos |
| **Limpieza** | Diario 2 AM | Eliminar antiguos |

---

## 🧪 Probar el Sistema

### 1. Login y Roles
```
✅ Login como admin (admin / admin123)
✅ Verificar menú completo
✅ Logout
✅ Login como supervisor (supervisor1 / super123)
✅ Verificar menú limitado
```

### 2. Auditoría
```
✅ Ir a "Auditoría"
✅ Ver logs de login
✅ Aplicar filtros
✅ Exportar a CSV
```

### 3. Notificaciones Email
```
✅ Ir a "Notificaciones"
✅ Configurar email
✅ Enviar email de prueba
✅ Verificar recepción en Gmail
```

### 4. Notificaciones In-App
```
✅ Verificar panel en sidebar
✅ Ver contador de no leídas
✅ Marcar como leída
✅ Eliminar notificación
```

---

## ❓ Problemas Comunes

### ❌ "Email no configurado"
**Solución:** Edita `.env` con tus credenciales de Gmail

### ❌ "Error enviando email"
**Solución:** Usa contraseña de aplicación, no tu contraseña normal

### ❌ "Module not found"
**Solución:** `pip install -r requirements.txt`

### ❌ "Database locked"
**Solución:** Cierra otras instancias de la app y reinicia

---

## 📚 Más Información

- **README.md** - Documentación completa
- **Comentarios en código** - Explicaciones detalladas
- **Plantillas** - Ejemplos de uso

---

## ✨ Características Destacadas

### Seguridad 🔐
- Contraseñas encriptadas con bcrypt
- Sesiones seguras con cookies
- Auditoría completa de acciones
- Control de acceso por roles

### Notificaciones 📧
- Plantillas HTML profesionales
- Emails automáticos
- WhatsApp para urgencias
- Notificaciones en tiempo real

### Automatización ⏰
- Recordatorios semanales
- Reportes mensuales
- Detección de sobrecargas
- Limpieza automática

---

## 🎉 ¡Listo!

Ya tienes un sistema completo de gestión de horas con:
- ✅ Autenticación segura
- ✅ 3 roles diferentes
- ✅ Auditoría completa
- ✅ Notificaciones por email
- ✅ WhatsApp (opcional)
- ✅ Notificaciones in-app
- ✅ Tareas automáticas

**¡Disfruta tu sistema!** 🚀

---

**Siguiente paso:** Lee el README.md para configuración avanzada
