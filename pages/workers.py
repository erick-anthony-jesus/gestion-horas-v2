"""
Página de gestión de trabajadores
"""
import streamlit as st
from database.workers_json import *
from database.audit import log_action
from auth.roles import require_role

@require_role(['admin', 'supervisor'])
def show_workers_page():
    st.title("👥 Gestión de Trabajadores")
    
    # Filtros
    area_filter = None
    if st.session_state['role'] == 'supervisor':
        area_filter = st.session_state['area']
        st.info(f"📍 Gestionando área: {area_filter}")
    else:
        areas = obtener_trabajadores()['area'].unique().tolist()
        area_filter = st.selectbox("Filtrar por área", ["Todas"] + areas)
        area_filter = None if area_filter == "Todas" else area_filter
    
    # Obtener trabajadores
    trabajadores_df = obtener_trabajadores(area=area_filter)
    
    # Botón agregar
    if st.button("➕ Agregar Trabajador", type="primary"):
        st.session_state.adding_worker = True
    
    # Formulario agregar
    if st.session_state.get('adding_worker', False):
        with st.form("form_nuevo_trabajador"):
            st.subheader("Nuevo Trabajador")
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre*")
                email = st.text_input("Email*")
            with col2:
                telefono = st.text_input("Teléfono")
                area = st.text_input("Área")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Guardar"):
                    if nombre and email:
                        trabajador_id, error = agregar_trabajador(nombre, email, telefono, area)
                        if trabajador_id:
                            log_action('CREATE', 'trabajadores', trabajador_id, details=f"Creado {nombre}")
                            st.success(f"✅ Trabajador {nombre} creado")
                            st.session_state.adding_worker = False
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {error}")
                    else:
                        st.error("Nombre y email son obligatorios")
            with col2:
                if st.form_submit_button("Cancelar"):
                    st.session_state.adding_worker = False
                    st.rerun()
    
    # Mostrar trabajadores
    if not trabajadores_df.empty:
        for _, trabajador in trabajadores_df.iterrows():
            with st.expander(f"👤 {trabajador['nombre']} - {trabajador['area'] or 'Sin área'}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Email:** {trabajador['email']}")
                    st.write(f"**Teléfono:** {trabajador['telefono'] or 'No especificado'}")
                    st.write(f"**Estatus:** {trabajador['estatus']}")
                
                with col2:
                    if st.button("Ver Horas", key=f"ver_{trabajador['id']}"):
                        st.session_state.viewing_worker = trabajador['id']
                    if st.button("✏️ Editar", key=f"edit_{trabajador['id']}"):
                        st.session_state.editing_worker = trabajador['id']
    else:
        st.info("No hay trabajadores registrados")
