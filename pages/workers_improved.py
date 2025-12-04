"""
Página mejorada de gestión de trabajadores con edición de horas estilo index4.py
"""
import streamlit as st
import pandas as pd
from database.workers_json import *
from database.audit import log_action
from auth.roles import require_role
import base64
from io import BytesIO
from PIL import Image

def get_color_for_hours(total_horas, limite=40):
    """Obtener color según horas (verde/amarillo/rojo)"""
    if total_horas <= limite * 0.9:  # ≤90% del límite
        return "#48bb78", "✅ Normal"  # Verde
    elif total_horas <= limite:  # 90-100% del límite
        return "#ed8936", "⚠️ Cerca del límite"  # Amarillo
    else:  # >100% del límite
        return "#f56565", "🚨 Sobrecarga"  # Rojo

@require_role(['admin', 'supervisor'])
def show_workers_improved_page():
    st.title("👥 Gestión de Trabajadores")
    
    # Filtros
    area_filter = None
    if st.session_state['role'] == 'supervisor':
        area_filter = st.session_state['area']
        st.info(f"📍 Gestionando área: {area_filter}")
    else:
        trabajadores_df = obtener_trabajadores()
        if not trabajadores_df.empty and 'area' in trabajadores_df.columns:
            areas = trabajadores_df['area'].unique().tolist()
            area_filter = st.selectbox("Filtrar por área", ["Todas"] + areas)
            area_filter = None if area_filter == "Todas" else area_filter
    
    # Obtener trabajadores
    trabajadores_df = obtener_trabajadores(area=area_filter)
    rubros_df = obtener_rubros()
    
    # Botón agregar
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➕ Agregar Trabajador", type="primary", use_container_width=True):
            st.session_state.adding_worker = True
    
    # Formulario agregar
    if st.session_state.get('adding_worker', False):
        with st.form("form_nuevo_trabajador"):
            st.subheader("Nuevo Trabajador")
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre*")
                email = st.text_input("Email*")
                telefono = st.text_input("Teléfono")
            with col2:
                area = st.text_input("Área")
                foto_upload = st.file_uploader("Foto de Perfil", type=['png', 'jpg', 'jpeg'])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Guardar", type="primary"):
                    if nombre and email:
                        # Procesar foto si existe
                        foto_base64 = None
                        if foto_upload:
                            foto_base64 = procesar_foto(foto_upload)
                        
                        trabajador_id, error = agregar_trabajador(nombre, email, telefono, area, foto_base64)
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
                if st.form_submit_button("❌ Cancelar"):
                    st.session_state.adding_worker = False
                    st.rerun()
    
    # Mostrar trabajadores con edición inline
    if not trabajadores_df.empty:
        for _, trabajador in trabajadores_df.iterrows():
            with st.expander(f"👤 {trabajador['nombre']} - {trabajador.get('area', 'Sin área')}", expanded=False):
                # Tabs para info, horas y foto
                tab1, tab2, tab3 = st.tabs(["📋 Información", "⏰ Horas Asignadas", "📷 Foto"])
                
                with tab1:
                    # Información básica
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Email:** {trabajador['email']}")
                        st.write(f"**Teléfono:** {trabajador.get('telefono', 'No especificado')}")
                    with col2:
                        st.write(f"**Área:** {trabajador.get('area', 'No especificada')}")
                        st.write(f"**Estatus:** {trabajador['estatus']}")
                    
                    # Botones de acción
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("✏️ Editar Info", key=f"edit_info_{trabajador['id']}"):
                            st.session_state[f'editing_{trabajador["id"]}'] = True
                    with col2:
                        if st.button("📊 Ver Dashboard", key=f"dash_{trabajador['id']}"):
                            st.info("Dashboard individual próximamente")
                    with col3:
                        if st.button("🗑️ Eliminar", key=f"del_{trabajador['id']}", type="secondary"):
                            if eliminar_trabajador(trabajador['id']):
                                log_action('DELETE', 'trabajadores', trabajador['id'], 
                                         details=f"Eliminado {trabajador['nombre']}")
                                st.success("Trabajador eliminado")
                                st.rerun()
                
                with tab2:
                    # Obtener horas actuales
                    año_actual = 2025
                    horas_df = obtener_horas_trabajador(trabajador['id'], año_actual)
                    total_horas = obtener_total_horas(trabajador['id'], año_actual)
                    
                    # Indicador de carga con color
                    color, estado = get_color_for_hours(total_horas)
                    
                    st.markdown(f"""
                    <div style='background: {color}; color: white; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px;'>
                        <h3 style='margin: 0;'>{estado}</h3>
                        <h1 style='margin: 10px 0;'>{total_horas}h / 40h</h1>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Tabla editable de horas
                    st.subheader("Editar Horas por Rubro")
                    
                    if not rubros_df.empty:
                        with st.form(f"form_horas_{trabajador['id']}"):
                            cambios = {}
                            
                            for _, rubro in rubros_df.iterrows():
                                # Obtener horas actuales para este rubro
                                horas_actuales = 0
                                if not horas_df.empty:
                                    horas_rubro = horas_df[horas_df['rubro'] == rubro['nombre']]
                                    if not horas_rubro.empty:
                                        horas_actuales = float(horas_rubro.iloc[0]['horas'])
                                
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.write(f"**{rubro['nombre']}**")
                                with col2:
                                    nuevas_horas = st.number_input(
                                        "Horas",
                                        min_value=0.0,
                                        max_value=100.0,
                                        value=float(horas_actuales),
                                        step=0.5,
                                        key=f"horas_{trabajador['id']}_{rubro['id']}",
                                        label_visibility="collapsed"
                                    )
                                    if nuevas_horas != horas_actuales:
                                        cambios[rubro['id']] = nuevas_horas
                            
                            if st.form_submit_button("💾 Guardar Cambios", type="primary", use_container_width=True):
                                if cambios:
                                    for rubro_id, horas in cambios.items():
                                        if asignar_horas(trabajador['id'], rubro_id, horas, año_actual):
                                            log_action('UPDATE', 'horas_asignadas', 
                                                     record_id=trabajador['id'],
                                                     details=f"Actualizado horas para rubro {rubro_id}: {horas}h")
                                    st.success(f"✅ Horas actualizadas para {trabajador['nombre']}")
                                    st.rerun()
                                else:
                                    st.info("No hay cambios para guardar")
                    else:
                        st.warning("No hay rubros creados. Ve a la sección de Rubros para crear algunos.")
                
                with tab3:
                    # Foto de perfil
                    if trabajador.get('foto'):
                        st.image(trabajador['foto'], width=200, caption=trabajador['nombre'])
                    else:
                        st.info("No hay foto de perfil")
                    
                    # Upload nueva foto
                    nueva_foto = st.file_uploader(
                        "Cambiar foto", 
                        type=['png', 'jpg', 'jpeg'],
                        key=f"foto_{trabajador['id']}"
                    )
                    
                    if nueva_foto:
                        if st.button("💾 Guardar Foto", key=f"save_foto_{trabajador['id']}"):
                            foto_base64 = procesar_foto(nueva_foto)
                            if actualizar_trabajador(trabajador['id'], foto=foto_base64):
                                st.success("Foto actualizada")
                                st.rerun()
    else:
        st.info("No hay trabajadores registrados en esta área")

def procesar_foto(uploaded_file):
    """Procesar imagen subida y convertir a base64"""
    try:
        # Leer imagen
        img = Image.open(uploaded_file)
        
        # Redimensionar a 200x200 manteniendo aspecto
        img.thumbnail((200, 200), Image.Resampling.LANCZOS)
        
        # Convertir a base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        st.error(f"Error procesando imagen: {e}")
        return None
