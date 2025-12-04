"""
Sistema de Gestión de Horas - Aplicación Principal
Versión JSON (sin SQLite)
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

# Agregar path del proyecto
sys.path.insert(0, str(Path(__file__).parent))

# Importar módulos - VERSIÓN JSON
from auth.login import login_page, check_authentication, setup_authentication, logout
from auth.roles import require_role, show_role_badge, can_edit_worker, get_accessible_workers
from database.audit import init_audit_db, log_action, get_recent_actions

# CAMBIO IMPORTANTE: Usar versión JSON
from database.workers_json import (
    init_json_db,
    obtener_trabajadores,
    obtener_rubros,
    obtener_horas_trabajador,
    obtener_total_horas
)

from notifications.inapp import init_notifications_db, get_user_notifications, get_unread_count, mark_notification_read, mark_all_read

# Configuración de la página
st.set_page_config(
    page_title="Gestión de Horas",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
    <style>
    .main {
        background: linear-gradient(to bottom, #f7fafc 0%, #edf2f7 100%);
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 500;
    }
    .notification-badge {
        background: #e74c3c;
        color: white;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 12px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

def inicializar_bases_datos():
    """Inicializar todas las bases de datos"""
    # Auditoría todavía usa SQLite (opcional)
    init_audit_db()
    
    # Notificaciones todavía usa SQLite (opcional)
    init_notifications_db()
    
    # Trabajadores ahora usa JSON
    init_json_db()
    
    print("✅ Bases de datos inicializadas (JSON + SQLite para logs)")

def main():
    # Inicializar bases de datos
    if 'db_initialized' not in st.session_state:
        inicializar_bases_datos()
        st.session_state.db_initialized = True
    
    # Verificar autenticación
    if not check_authentication():
        login_page()
        return
    
    # Usuario autenticado - mostrar app
    authenticator, config = setup_authentication()
    
    # Sidebar
    with st.sidebar:
        # Badge de rol
        show_role_badge()
        
        # Notificaciones
        username = st.session_state.get('username', '')
        unread_count = get_unread_count(username)
        
        if unread_count > 0:
            st.markdown(f"""
                <div style='background: #fff3cd; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 1rem;'>
                    <span class='notification-badge'>{unread_count}</span> 
                    <span style='color: #856404;'>notificaciones nuevas</span>
                </div>
            """, unsafe_allow_html=True)
        
        # Menú según rol
        st.markdown("---")
        st.subheader("📋 Menú")
        
        if st.session_state['role'] == 'admin':
            menu_options = [
                "🏠 Dashboard",
                "👥 Trabajadores",
                "📊 Rubros",
                "📈 Google Sheets",
                "🔔 Notificaciones",
                "📋 Auditoría",
                "⚙️ Configuración"
            ]
        elif st.session_state['role'] == 'supervisor':
            menu_options = [
                "🏠 Dashboard",
                "👥 Mi Equipo",
                "📊 Reportes",
                "🔔 Notificaciones"
            ]
        else:
            menu_options = [
                "🏠 Mis Horas",
                "👤 Mi Perfil",
                "🔔 Notificaciones"
            ]
        
        page = st.radio("Navegación", menu_options, label_visibility="collapsed")
        
        # Botón de cerrar sesión
        st.markdown("---")
        if st.button("🚪 Cerrar Sesión", type="secondary", key="logout_button"):
            log_action('LOGOUT', 'users', details=f"Usuario {st.session_state['username']} cerró sesión")
            
            # Limpiar COMPLETAMENTE el session_state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            
            # Forzar que authenticated sea False
            st.session_state['authenticated'] = False
            
            # Usar st.rerun() sin argumentos
            st.rerun()
        
        # Información del usuario
        st.markdown("---")
        st.caption(f"Usuario: {st.session_state['username']}")
        st.caption(f"Sesión activa desde {datetime.now().strftime('%H:%M')}")
    
    # Contenido principal según página seleccionada
    if "Dashboard" in page or "Mis Horas" in page:
        from pages.dashboard import show_dashboard
        show_dashboard()
    
    elif "Trabajadores" in page or "Mi Equipo" in page:
        from pages.workers_cards import show_workers_cards_page
        show_workers_cards_page()
    
    elif "Rubros" in page:
        from pages.rubros import show_rubros_page
        show_rubros_page()
    
    elif "Google Sheets" in page:
        from pages.google_sheets import show_google_sheets_page
        show_google_sheets_page()
    
    elif "Notificaciones" in page:
        from pages.notifications_page import show_notifications_page
        show_notifications_page()
    
    elif "Auditoría" in page:
        from pages.audit_page import show_audit_page
        show_audit_page()
    
    elif "Configuración" in page:
        from pages.settings import show_settings_page
        show_settings_page()
    
    elif "Reportes" in page:
        from pages.reports import show_reports_page
        show_reports_page()
    
    elif "Mi Perfil" in page:
        from pages.profile import show_profile_page
        show_profile_page()

if __name__ == '__main__':
    main()
