"""
Módulo de autenticación para el sistema de gestión de horas
"""
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from pathlib import Path

def load_config():
    """Cargar configuración de usuarios"""
    config_path = Path(__file__).parent.parent / 'config.yaml'
    with open(config_path) as file:
        config = yaml.load(file, Loader=SafeLoader)
    return config

def save_config(config):
    """Guardar configuración de usuarios"""
    config_path = Path(__file__).parent.parent / 'config.yaml'
    with open(config_path, 'w') as file:
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

def login_page():
    """Página de login"""
    # Header personalizado
    st.markdown("""
        <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 2rem;'>
            <h1 style='color: white; margin: 0;'>🎯 Sistema de Gestión de Horas</h1>
            <p style='color: white; margin-top: 0.5rem;'>Inicia sesión para continuar</p>
        </div>
    """, unsafe_allow_html=True)
    
    authenticator, config = setup_authentication()
    
    # Crear tabs para login y recuperación de contraseña
    tab1, tab2 = st.tabs(["🔑 Iniciar Sesión", "🔄 Recuperar Contraseña"])
    
    with tab1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Nueva API de streamlit-authenticator
            authenticator.login(fields={'Form name': 'Login'}, location='main')
            
            name = st.session_state.get('name')
            authentication_status = st.session_state.get('authentication_status')
            username = st.session_state.get('username')
            
            if authentication_status:
                st.session_state['authenticated'] = True
                st.session_state['username'] = username
                st.session_state['name'] = name
                st.session_state['role'] = config['credentials']['usernames'][username]['role']
                st.session_state['email'] = config['credentials']['usernames'][username]['email']
                
                # Guardar área si es supervisor
                if st.session_state['role'] == 'supervisor':
                    st.session_state['area'] = config['credentials']['usernames'][username]['area']
                
                # Guardar ID si es trabajador
                if st.session_state['role'] == 'trabajador':
                    st.session_state['trabajador_id'] = config['credentials']['usernames'][username]['trabajador_id']
                
                st.success(f'✅ Bienvenido {name}!')
                st.rerun()
                
            elif authentication_status == False:
                st.error('❌ Usuario o contraseña incorrectos')
            
            if authentication_status is None:
                st.info('👋 Por favor ingresa tus credenciales')
                
                # Mostrar usuarios de demo
                with st.expander("👤 Usuarios de Demo"):
                    st.markdown("""
                    **Administrador:**
                    - Usuario: `admin`
                    - Contraseña: `admin123`
                    
                    **Supervisor:**
                    - Usuario: `supervisor1`
                    - Contraseña: `super123`
                    
                    **Trabajador:**
                    - Usuario: `trabajador1`
                    - Contraseña: `trabajo123`
                    """)
    
    with tab2:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            try:
                # Nueva API de streamlit-authenticator
                authenticator.forgot_password(fields={'Form name': 'Recuperar contraseña'}, location='main')
                
                # Verificar si se generó nueva contraseña
                if st.session_state.get('forgot_password_username'):
                    username_of_forgotten_password = st.session_state['forgot_password_username']
                    st.success('✅ Nueva contraseña temporal generada')
                    
                    # Obtener email del usuario
                    email = config['credentials']['usernames'][username_of_forgotten_password]['email']
                    st.info(f'📧 Se enviará un email a: {email}')
                    st.warning(f'⚠️ Revisa tu email para obtener la nueva contraseña')
                    st.info('💡 Recuerda cambiarla después de iniciar sesión')
                    
                    # Guardar nueva configuración
                    save_config(config)
                    
            except Exception as e:
                st.error(f'❌ Error: {e}')

def check_authentication():
    """Verificar si el usuario está autenticado"""
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    
    return st.session_state['authenticated']

def logout():
    """Cerrar sesión - Limpiar todo el estado"""
    # Limpiar TODAS las claves de session_state
    keys_to_delete = list(st.session_state.keys())
    for key in keys_to_delete:
        del st.session_state[key]
    
    # Asegurar que authenticated está en False
    st.session_state['authenticated'] = False
    st.session_state.clear()  # Extra seguridad
