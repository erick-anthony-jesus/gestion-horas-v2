"""
Sistema de Autenticación
Gestión de login, roles y permisos
"""

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from functools import wraps
import os

def load_config():
    """Cargar configuración de usuarios desde config.yaml"""
    config_path = 'config.yaml'
    
    if not os.path.exists(config_path):
        st.error("❌ Archivo config.yaml no encontrado")
        st.stop()
    
    with open(config_path) as file:
        config = yaml.load(file, Loader=SafeLoader)
    
    return config

def save_config(config):
    """Guardar configuración actualizada"""
    with open('config.yaml', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)

def setup_authentication():
    """Configurar sistema de autenticación"""
    config = load_config()
    
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    
    return authenticator, config

def init_session_state():
    """Inicializar variables de sesión"""
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if 'username' not in st.session_state:
        st.session_state['username'] = None
    if 'name' not in st.session_state:
        st.session_state['name'] = None
    if 'role' not in st.session_state:
        st.session_state['role'] = None

def login_page():
    """Renderizar página de login"""
    st.set_page_config(
        page_title="Login - Gestión de Horas",
        page_icon="🔐",
        layout="centered"
    )
    
    # Estilos personalizados
    st.markdown("""
        <style>
        .main {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Logo y título
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style='text-align: center; padding: 2rem; background: white; border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.1);'>
                <h1 style='color: #667eea; margin-bottom: 0;'>🎯</h1>
                <h2 style='color: #333; margin-top: 0;'>Sistema de Gestión de Horas</h2>
                <p style='color: #666;'>Inicia sesión para continuar</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("")
    
    authenticator, config = setup_authentication()
    
    # Tabs de login y recuperación
    tab1, tab2 = st.tabs(["🔑 Iniciar Sesión", "🔄 Recuperar Contraseña"])
    
    with tab1:
        name, authentication_status, username = authenticator.login('Login', 'main')
        
        if authentication_status:
            # Login exitoso
            st.session_state['authenticated'] = True
            st.session_state['username'] = username
            st.session_state['name'] = name
            st.session_state['role'] = config['credentials']['usernames'][username]['role']
            st.session_state['email'] = config['credentials']['usernames'][username]['email']
            st.session_state['area'] = config['credentials']['usernames'][username].get('area')
            st.session_state['trabajador_id'] = config['credentials']['usernames'][username].get('trabajador_id')
            
            st.success(f"✅ Bienvenido {name}!")
            st.rerun()
            
        elif authentication_status == False:
            st.error('❌ Usuario o contraseña incorrectos')
            
            # Mostrar usuarios de ejemplo
            with st.expander("ℹ️ Usuarios de prueba"):
                st.info("""
                **Admin:**
                - Usuario: `admin`
                - Contraseña: `admin123`
                
                **Supervisor:**
                - Usuario: `supervisor1`
                - Contraseña: `super123`
                
                **Trabajador:**
                - Usuario: `trabajador1`
                - Contraseña: `trab123`
                """)
                
        elif authentication_status == None:
            st.info('ℹ️ Por favor ingresa tus credenciales')
    
    with tab2:
        forgot_password_section(authenticator, config)

def forgot_password_section(authenticator, config):
    """Sección de recuperación de contraseña"""
    st.markdown("### 🔄 Recuperar Contraseña")
    
    try:
        username_forgot_pw, email_forgot_password, random_password = \
            authenticator.forgot_password('Recuperar contraseña')
        
        if username_forgot_pw:
            st.success(f'✅ Nueva contraseña temporal generada')
            st.info(f'📧 Se enviará un email a: {email_forgot_password}')
            st.warning(f'⚠️ Contraseña temporal: `{random_password}`')
            
            # Guardar configuración actualizada
            save_config(config)
            
            st.info("💡 En producción, esto enviaría un email automático")
            
        elif username_forgot_pw == False:
            st.error('❌ Usuario no encontrado')
            
    except Exception as e:
        st.error(f'Error: {e}')

def require_role(allowed_roles):
    """
    Decorador para requerir roles específicos
    
    Uso:
    @require_role(['admin', 'supervisor'])
    def mi_funcion():
        pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not st.session_state.get('authenticated'):
                st.error("⛔ Debes iniciar sesión primero")
                st.stop()
            
            if st.session_state.get('role') not in allowed_roles:
                st.error(f"⛔ Acceso denegado. Se requiere rol: {', '.join(allowed_roles)}")
                st.warning(f"Tu rol actual: {st.session_state.get('role')}")
                st.stop()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def can_edit_worker(trabajador_id):
    """Verificar si el usuario puede editar un trabajador"""
    if st.session_state.get('role') == 'admin':
        return True
    
    if st.session_state.get('role') == 'supervisor':
        # Implementar lógica para verificar si el trabajador pertenece al área del supervisor
        # Por ahora retorna True, implementar según tu modelo de datos
        return True
    
    if st.session_state.get('role') == 'trabajador':
        return st.session_state.get('trabajador_id') == trabajador_id
    
    return False

def get_accessible_areas():
    """Obtener áreas accesibles según el rol del usuario"""
    role = st.session_state.get('role')
    
    if role == 'admin':
        # Admin ve todas las áreas
        return ['Ingeniería', 'Operaciones', 'Comercial', 'Administración']
    
    elif role == 'supervisor':
        # Supervisor ve solo su área
        return [st.session_state.get('area')]
    
    else:
        # Trabajador no tiene acceso a selector de áreas
        return []

def show_user_info():
    """Mostrar información del usuario en sidebar"""
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 👤 Usuario Actual")
        
        # Información del usuario
        st.markdown(f"**Nombre:** {st.session_state.get('name', 'N/A')}")
        st.markdown(f"**Rol:** {st.session_state.get('role', 'N/A').title()}")
        
        if st.session_state.get('area'):
            st.markdown(f"**Área:** {st.session_state.get('area')}")
        
        st.markdown("---")

def logout_button():
    """Botón de cerrar sesión"""
    authenticator, config = setup_authentication()
    
    if authenticator.logout('🚪 Cerrar Sesión', 'sidebar'):
        # Limpiar session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
