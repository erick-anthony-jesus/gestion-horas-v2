# 🎯 Sistema de Gestión de Horas
## Implementación Completa - Fase 2 y Fase 3

Sistema completo con autenticación, auditoría y notificaciones.

## 📦 Instalación

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno
Copia `.env.example` a `.env` y configura:
```bash
cp .env.example .env
```

Edita `.env` con tus credenciales:
```
GMAIL_USER=tu-email@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
```

#### Cómo obtener contraseña de aplicación de Gmail:
1. Ve a https://myaccount.google.com/security
2. Activa verificación en 2 pasos
3. Ve a "Contraseñas de aplicaciones"
4. Genera una para "Mail"
5. Copia el código de 16 caracteres

### 3. Ejecutar la aplicación
```bash
streamlit run app.py
```

## 👥 Usuarios de Demo

### Administrador
- Usuario: `admin`
- Contraseña: `admin123`
- Acceso completo al sistema

### Supervisor
- Usuario: `supervisor1`
- Contraseña: `super123`
- Acceso a su área (Ingeniería)

### Trabajador
- Usuario: `trabajador1`
- Contraseña: `trabajo123`
- Solo ve sus propias horas

## ✨ Características Implementadas

### Fase 2: Autenticación y Seguridad ✅
- ✅ Sistema de login con streamlit-authenticator
- ✅ 3 roles: Admin, Supervisor, Trabajador
- ✅ Control de acceso por roles
- ✅ Registro de auditoría en SQLite
- ✅ Recuperación de contraseña

### Fase 3: Notificaciones ✅
- ✅ Servicio de email con Gmail
- ✅ Plantillas HTML profesionales
- ✅ Notificaciones in-app
- ✅ WhatsApp con Twilio (opcional)
- ✅ Sistema de notificaciones por usuario

## 📁 Estructura del Proyecto

```
gestion_horas/
├── app.py                      # Aplicación principal
├── config.yaml                 # Configuración de usuarios
├── requirements.txt            # Dependencias
├── .env.example               # Variables de entorno
│
├── auth/
│   ├── login.py               # Sistema de login
│   └── roles.py               # Control de roles
│
├── database/
│   ├── audit.py               # Sistema de auditoría
│   └── workers.py             # Gestión de trabajadores
│
├── notifications/
│   ├── email_service.py       # Servicio de email
│   ├── templates.py           # Plantillas HTML
│   ├── whatsapp_service.py    # Servicio WhatsApp
│   └── inapp.py               # Notificaciones in-app
│
└── pages/
    ├── dashboard.py           # Dashboard principal
    ├── workers.py             # Gestión de trabajadores
    ├── rubros.py              # Gestión de rubros
    ├── notifications_page.py  # Panel de notificaciones
    ├── audit_page.py          # Panel de auditoría
    └── ... otros

```

## 🔧 Configuración Avanzada

### Agregar nuevo usuario
Edita `config.yaml`:

```yaml
credentials:
  usernames:
    nuevo_usuario:
      email: nuevo@empresa.com
      name: Nombre Completo
      password: $2b$12$... # Usar bcrypt para generar hash
      role: trabajador  # admin, supervisor o trabajador
      area: "Nombre Área"  # Solo para supervisores
      trabajador_id: 5  # Solo para trabajadores
```

### Generar hash de contraseña
```python
import bcrypt
password = "mi_contraseña"
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
print(hashed.decode())
```

### Configurar WhatsApp (Opcional)
1. Crear cuenta en Twilio (https://www.twilio.com)
2. Obtener número de WhatsApp de Twilio
3. Agregar a `.env`:
```
TWILIO_ACCOUNT_SID=ACxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

## 📊 Uso del Sistema

### Como Administrador
1. Ver dashboard global
2. Gestionar todos los trabajadores
3. Crear y editar rubros
4. Ver logs de auditoría
5. Configurar el sistema

### Como Supervisor
1. Ver equipo de su área
2. Asignar horas a trabajadores
3. Ver reportes del área
4. Recibir alertas de sobrecarga

### Como Trabajador
1. Ver sus horas asignadas
2. Ver distribución por rubros
3. Recibir notificaciones de cambios
4. Actualizar perfil

## 📧 Sistema de Notificaciones

### Tipos de notificaciones
- **Asignación de horas**: Cuando se asignan horas nuevas
- **Cambio de horas**: Cuando se modifican horas existentes
- **Sobrecarga**: Alerta cuando se superan 40h semanales
- **Recordatorios**: Recordatorios semanales automáticos
- **Bienvenida**: Email de bienvenida a nuevos usuarios

### Configurar recordatorios automáticos
(Próximamente con APScheduler)

## 🔍 Auditoría

Todas las acciones quedan registradas:
- Creación de trabajadores/rubros
- Modificación de horas
- Eliminaciones
- Login/logout
- Cambios de configuración

Ver logs en: **Menú → Auditoría** (solo admin)

## 🐛 Solución de Problemas

### Error: "Credenciales de Gmail no configuradas"
Verifica que `.env` tenga:
- GMAIL_USER correctamente configurado
- GMAIL_APP_PASSWORD (NO la contraseña normal)

### Error: "No module named 'streamlit_authenticator'"
```bash
pip install streamlit-authenticator
```

### Error: "Database is locked"
Cierra otras instancias de la app y reinicia

### Datos de demo no aparecen
Elimina `trabajadores.db` y reinicia la app

## 📝 Próximas Funcionalidades

- [ ] Scheduler para recordatorios automáticos
- [ ] Reportes avanzados con gráficos
- [ ] Exportación a PDF
- [ ] Integración con Google Sheets
- [ ] Panel de estadísticas avanzadas
- [ ] Sistema de aprobaciones
- [ ] Gestión de permisos granulares

## 📞 Soporte

Para dudas o problemas:
1. Revisa esta documentación
2. Verifica los logs de auditoría
3. Consulta el plan detallado en `FASE_2_Y_3_PLAN_DETALLADO.md`

## 🎉 ¡Listo!

Tu sistema de gestión de horas está completamente funcional con:
- ✅ Autenticación segura
- ✅ Control de roles
- ✅ Auditoría completa
- ✅ Notificaciones por email
- ✅ Notificaciones in-app
- ✅ Dashboard interactivo
- ✅ Base de datos SQLite

**¡Disfruta tu nuevo sistema!** 🚀
