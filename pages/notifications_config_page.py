"""
Página de Configuración de Notificaciones
Permite a los usuarios personalizar sus preferencias de notificaciones
"""

import streamlit as st
import json
import os
from database.notifications import get_user_notifications, mark_all_read, delete_all_notifications
from notifications.email_service import EmailService
from notifications.whatsapp_service import WhatsAppService
from notifications.email_templates import EmailTemplates

def load_user_notification_config(username):
    """Cargar configuración de notificaciones del usuario"""
    config_file = f'database/notification_config_{username}.json'
    
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    
    # Configuración por defecto
    return {
        'email_enabled': True,
        'email_horas_asignadas': True,
        'email_cambios': True,
        'email_weekly': True,
        'email_monthly': False,
        'whatsapp_enabled': False,
        'whatsapp_urgentes': True,
        'telefono': '',
        'inapp_enabled': True,
        'inapp_desktop': True
    }

def save_user_notification_config(username, config):
    """Guardar configuración de notificaciones"""
    os.makedirs('database', exist_ok=True)
    config_file = f'database/notification_config_{username}.json'
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

def show_notifications_config_page():
    """Página principal de configuración de notificaciones"""
    
    username = st.session_state.get('username')
    if not username:
        st.error("⛔ Debes iniciar sesión")
        return
    
    st.title("⚙️ Configuración de Notificaciones")
    st.markdown("Personaliza cómo y cuándo recibes notificaciones")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📧 Email", "💬 WhatsApp", "🔔 In-App"])
    
    # Cargar configuración actual
    config = load_user_notification_config(username)
    
    with tab1:
        config = show_email_config(config)
    
    with tab2:
        config = show_whatsapp_config(config)
    
    with tab3:
        config = show_inapp_config(config)
    
    # Botones de acción
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Guardar Configuración", type="primary", use_container_width=True):
            save_user_notification_config(username, config)
            st.success("✅ Configuración guardada correctamente")
            st.rerun()
    
    with col2:
        if st.button("🔄 Restablecer Valores", use_container_width=True):
            # Eliminar archivo de configuración
            config_file = f'database/notification_config_{username}.json'
            if os.path.exists(config_file):
                os.remove(config_file)
            st.success("✅ Valores restablecidos")
            st.rerun()
    
    with col3:
        if st.button("✉️ Enviar Email de Prueba", use_container_width=True):
            send_test_email()

def show_email_config(config):
    """Configuración de notificaciones por email"""
    
    st.subheader("📧 Notificaciones por Email")
    
    email_enabled = st.toggle(
        "Recibir notificaciones por email",
        value=config.get('email_enabled', True),
        key='email_enabled'
    )
    
    config['email_enabled'] = email_enabled
    
    if email_enabled:
        st.markdown("**Tipos de notificaciones:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            config['email_horas_asignadas'] = st.checkbox(
                "✅ Asignación de horas",
                value=config.get('email_horas_asignadas', True),
                help="Te notificaremos cuando se te asignen horas",
                disabled=True  # Siempre activo
            )
            
            config['email_cambios'] = st.checkbox(
                "🔄 Cambios en horas",
                value=config.get('email_cambios', True),
                help="Te notificaremos cuando se modifiquen tus horas"
            )
        
        with col2:
            config['email_weekly'] = st.checkbox(
                "📅 Recordatorios semanales",
                value=config.get('email_weekly', True),
                help="Recordatorio semanal de horas pendientes"
            )
            
            config['email_monthly'] = st.checkbox(
                "📊 Reportes mensuales",
                value=config.get('email_monthly', False),
                help="Reporte mensual de tu actividad"
            )
        
        # Mostrar email del usuario
        user_email = st.session_state.get('email', 'No configurado')
        st.info(f"📨 Los emails se enviarán a: **{user_email}**")
    
    else:
        st.warning("⚠️ No recibirás notificaciones por email")
    
    return config

def show_whatsapp_config(config):
    """Configuración de notificaciones por WhatsApp"""
    
    st.subheader("💬 Notificaciones por WhatsApp")
    
    st.info("""
    **Acerca de WhatsApp:**
    - Solo se envían alertas urgentes (sobrecargas, cambios críticos)
    - Requiere número de teléfono con código de país
    - Servicio opcional y sujeto a disponibilidad
    """)
    
    whatsapp_enabled = st.toggle(
        "Recibir alertas por WhatsApp",
        value=config.get('whatsapp_enabled', False),
        key='whatsapp_enabled'
    )
    
    config['whatsapp_enabled'] = whatsapp_enabled
    
    if whatsapp_enabled:
        telefono = st.text_input(
            "📱 Teléfono (con código de país)",
            value=config.get('telefono', ''),
            placeholder="+51999999999",
            help="Formato: +[código país][número]. Ejemplo: +51987654321"
        )
        
        config['telefono'] = telefono
        
        # Validar formato de teléfono
        if telefono:
            if not telefono.startswith('+'):
                st.warning("⚠️ El número debe empezar con + seguido del código de país")
            elif len(telefono) < 10:
                st.warning("⚠️ El número parece incompleto")
            else:
                st.success(f"✅ Número válido: {telefono}")
        
        st.markdown("**Tipos de alertas:**")
        
        config['whatsapp_urgentes'] = st.checkbox(
            "🚨 Alertas urgentes",
            value=config.get('whatsapp_urgentes', True),
            help="Sobrecargas de horas, cambios críticos"
        )
        
        # Botón de prueba
        if telefono and st.button("📤 Enviar WhatsApp de Prueba"):
            send_test_whatsapp(telefono)
    
    else:
        st.info("ℹ️ No recibirás alertas por WhatsApp")
    
    return config

def show_inapp_config(config):
    """Configuración de notificaciones in-app"""
    
    st.subheader("🔔 Notificaciones en la Aplicación")
    
    inapp_enabled = st.toggle(
        "Mostrar notificaciones en la aplicación",
        value=config.get('inapp_enabled', True),
        key='inapp_enabled'
    )
    
    config['inapp_enabled'] = inapp_enabled
    
    if inapp_enabled:
        st.markdown("**Preferencias:**")
        
        config['inapp_desktop'] = st.checkbox(
            "🖥️ Mostrar en escritorio/sidebar",
            value=config.get('inapp_desktop', True),
            help="Mostrar panel de notificaciones en el sidebar"
        )
        
        st.info("""
        **Acerca de las notificaciones in-app:**
        - Aparecen en tiempo real en el sidebar
        - Puedes marcarlas como leídas o eliminarlas
        - Se limpian automáticamente después de 30 días
        """)
        
        # Mostrar notificaciones actuales
        username = st.session_state.get('username')
        notif_df = get_user_notifications(username, limit=10)
        
        if not notif_df.empty:
            st.markdown("---")
            st.markdown("**Tus últimas notificaciones:**")
            
            for _, notif in notif_df.iterrows():
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    status = "🔴 Nueva" if notif['read'] == 0 else "✅ Leída"
                    st.markdown(f"{notif['icon']} **{notif['title']}** - {status}")
                    st.caption(notif['message'])
                
                with col2:
                    st.caption(notif['timestamp'][:10])
            
            # Botones de gestión
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✓ Marcar Todas Leídas", use_container_width=True):
                    mark_all_read(username)
                    st.success("✅ Notificaciones marcadas como leídas")
                    st.rerun()
            
            with col2:
                if st.button("🗑️ Eliminar Todas", use_container_width=True):
                    delete_all_notifications(username)
                    st.success("✅ Notificaciones eliminadas")
                    st.rerun()
        else:
            st.info("📭 No tienes notificaciones")
    
    else:
        st.warning("⚠️ No verás notificaciones en la aplicación")
    
    return config

def send_test_email():
    """Enviar email de prueba"""
    email_service = EmailService()
    user_email = st.session_state.get('email')
    user_name = st.session_state.get('name')
    
    if not user_email:
        st.error("❌ Email no configurado")
        return
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px; background: #f4f4f4;">
        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
            <h2 style="color: #667eea;">✅ Email de Prueba</h2>
            <p>Hola <strong>{user_name}</strong>,</p>
            <p>Este es un email de prueba del Sistema de Gestión de Horas.</p>
            <p>Tu configuración de email está funcionando correctamente.</p>
            <hr>
            <p style="color: #666; font-size: 12px;">
                Este es un correo automático, por favor no responder.
            </p>
        </div>
    </body>
    </html>
    """
    
    with st.spinner("Enviando email de prueba..."):
        if email_service.send_email(user_email, "Prueba de Notificaciones", html):
            st.success(f"✅ Email de prueba enviado a {user_email}")
        else:
            st.error("❌ Error enviando email. Verifica la configuración en .env")

def send_test_whatsapp(telefono):
    """Enviar WhatsApp de prueba"""
    whatsapp_service = WhatsAppService()
    user_name = st.session_state.get('name', 'Usuario')
    
    mensaje = f"""🎯 *Prueba de Notificaciones*

Hola {user_name.split()[0]},

Este es un mensaje de prueba del Sistema de Gestión de Horas.

✅ Tu configuración de WhatsApp está funcionando correctamente.
"""
    
    with st.spinner("Enviando WhatsApp de prueba..."):
        message_sid = whatsapp_service.send_message(telefono, mensaje)
        
        if message_sid:
            st.success(f"✅ WhatsApp de prueba enviado a {telefono}")
            st.info(f"ID del mensaje: {message_sid}")
        else:
            st.error("❌ Error enviando WhatsApp. Verifica la configuración en .env")
