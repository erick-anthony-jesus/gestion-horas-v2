"""
Control de acceso basado en roles
"""
import streamlit as st
from functools import wraps

def require_role(allowed_roles):
    """
    Decorador para requerir roles específicos
    Uso: @require_role(['admin', 'supervisor'])
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'role' not in st.session_state:
                st.error("⛔ Debes iniciar sesión")
                st.stop()
            
            if st.session_state['role'] not in allowed_roles:
                st.error(f"⛔ Acceso denegado. Se requiere rol: {', '.join(allowed_roles)}")
                st.info(f"Tu rol actual: {st.session_state['role']}")
                st.stop()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def can_edit_worker(trabajador_id, trabajadores_data):
    """Verificar si el usuario puede editar un trabajador"""
    if st.session_state['role'] == 'admin':
        return True
    
    if st.session_state['role'] == 'supervisor':
        # Verificar si el trabajador está en el área del supervisor
        trabajador = next((t for t in trabajadores_data if t['id'] == trabajador_id), None)
        if trabajador:
            return trabajador.get('area') == st.session_state.get('area')
        return False
    
    if st.session_state['role'] == 'trabajador':
        # Solo puede ver/editar sus propios datos
        return st.session_state.get('trabajador_id') == trabajador_id
    
    return False

def get_accessible_workers(trabajadores_data):
    """Obtener trabajadores accesibles según rol"""
    if st.session_state['role'] == 'admin':
        return trabajadores_data
    
    elif st.session_state['role'] == 'supervisor':
        # Filtrar por área
        area_supervisor = st.session_state.get('area')
        return [t for t in trabajadores_data if t.get('area') == area_supervisor]
    
    elif st.session_state['role'] == 'trabajador':
        # Solo sus propios datos
        trabajador_id = st.session_state.get('trabajador_id')
        return [t for t in trabajadores_data if t['id'] == trabajador_id]
    
    return []

def show_role_badge():
    """Mostrar badge del rol actual"""
    role = st.session_state.get('role', 'guest')
    name = st.session_state.get('name', 'Usuario')
    
    role_colors = {
        'admin': "#3c94e7",
        'supervisor': '#3498db',
        'trabajador': '#2ecc71'
    }
    
    role_icons = {
        'admin': '👑',
        'supervisor': '📊',
        'trabajador': '👤'
    }
    
    role_names = {
        'admin': 'Administrador',
        'supervisor': 'Supervisor',
        'trabajador': 'Trabajador'
    }
    
    color = role_colors.get(role, '#95a5a6')
    icon = role_icons.get(role, '❓')
    role_name = role_names.get(role, role)
    
    st.sidebar.markdown(f"""
        <div style='background: {color}; padding: 1rem; border-radius: 10px; text-align: center; margin-bottom: 1rem;'>
            <h3 style='color: white; margin: 0;'>{icon} {name}</h3>
            <p style='color: white; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>{role_name}</p>
        </div>
    """, unsafe_allow_html=True)
