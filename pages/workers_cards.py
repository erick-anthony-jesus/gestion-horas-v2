"""
Página de trabajadores con diseño de cards (3 columnas) con fotos
"""
import streamlit as st
import pandas as pd
from database.workers_json import *
from database.audit import log_action
from auth.roles import require_role
import base64
from io import BytesIO
from PIL import Image
from notifications.email_service import EmailService
from notifications.templates import EmailTemplates
from notifications.whatsapp_service import WhatsAppService

def get_color_for_hours(total_horas, limite=40):
    """Obtener color según horas"""
    if total_horas <= limite * 0.9:
        return "#48bb78", "✅"
    elif total_horas <= limite:
        return "#ed8936", "⚠️"
    else:
        return "#f56565", "🚨"

@require_role(['admin', 'supervisor'])
def show_workers_cards_page():
    # Título con botón CSV
    col1, col2 = st.columns([6, 1])
    with col1:
        st.title("👥 Gestión de Trabajadores")
    with col2:
        # Botón CSV
        trabajadores_df = obtener_trabajadores()
        rubros_df = obtener_rubros()
        
        if not trabajadores_df.empty:
            export_data = []
            for _, trabajador in trabajadores_df.iterrows():
                row = {
                    'ID': trabajador['id'],
                    'Nombre': trabajador['nombre'],
                    'Email': trabajador['email'],
                    'Teléfono': trabajador.get('telefono', ''),
                    'Área': trabajador.get('area', '')
                }
                
                horas_df = obtener_horas_trabajador(trabajador['id'], 2025)
                total = 0
                for _, rubro in rubros_df.iterrows():
                    if not horas_df.empty and 'rubro' in horas_df.columns:
                        horas_rubro = horas_df[horas_df['rubro'] == rubro['nombre']]
                    else:
                        horas_rubro = pd.DataFrame()
                    horas = float(horas_rubro.iloc[0]['horas']) if not horas_rubro.empty else 0
                    row[rubro['nombre']] = horas
                    total += horas
                
                row['Total_Horas'] = total
                export_data.append(row)
            
            from datetime import datetime
            df_export = pd.DataFrame(export_data)
            
            # Usar Excel-compatible encoding con BOM
            csv = df_export.to_csv(index=False, sep=',', encoding='utf-8-sig', lineterminator='\n')
            
            st.download_button(
                label="📥 CSV",
                data=csv.encode('utf-8-sig'),
                file_name=f"trabajadores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
                help="Exportar todos los trabajadores a CSV"
            )
    
    # Botones de acción superiores
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col2:
        if st.button("➕ Agregar", type="primary", use_container_width=True):
            st.session_state.adding_worker = True
    with col3:
        if st.button("📧 Notificar Todos", use_container_width=True):
            st.session_state.notify_all = True
    with col4:
        if st.button("🗑️ Eliminar Todos", type="secondary", use_container_width=True):
            st.session_state.delete_all = True
    
    # Modal eliminar todos
    if st.session_state.get('delete_all'):
        with st.expander("⚠️ CONFIRMAR ELIMINACIÓN", expanded=True):
            st.error("**¿Estás seguro de eliminar TODOS los trabajadores?**")
            st.warning("Esta acción NO se puede deshacer")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Sí, eliminar todos", type="primary"):
                    trabajadores_df = obtener_trabajadores()
                    for _, t in trabajadores_df.iterrows():
                        eliminar_trabajador(t['id'])
                    log_action('DELETE_ALL', 'trabajadores', details='Eliminados todos los trabajadores')
                    st.success("Todos los trabajadores eliminados")
                    del st.session_state['delete_all']
                    st.rerun()
            with col2:
                if st.button("❌ Cancelar"):
                    del st.session_state['delete_all']
                    st.rerun()
    
    # Modal notificar todos
    if st.session_state.get('notify_all'):
        with st.expander("📧 NOTIFICAR A TODOS", expanded=True):
            mensaje = st.text_area("Mensaje personalizado", "Revisa tus horas asignadas en el sistema")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                enviar_email = st.checkbox("📧 Email", value=True)
            with col2:
                enviar_whatsapp = st.checkbox("💬 WhatsApp", value=False)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📤 Enviar", type="primary"):
                    trabajadores_df = obtener_trabajadores()
                    enviados = 0
                    
                    for _, t in trabajadores_df.iterrows():
                        if enviar_email and t.get('email'):
                            email_service = EmailService()
                            html = f"<h2>Hola {t['nombre']}</h2><p>{mensaje}</p>"
                            if email_service.send_email(t['email'], "Notificación del Sistema", html):
                                enviados += 1
                        
                        if enviar_whatsapp and t.get('telefono'):
                            whatsapp = WhatsAppService()
                            whatsapp.send_message(t['telefono'], mensaje)
                    
                    st.success(f"✅ Notificaciones enviadas a {enviados} trabajadores")
                    del st.session_state['notify_all']
                    st.rerun()
            with col2:
                if st.button("❌ Cancelar"):
                    del st.session_state['notify_all']
                    st.rerun()
    
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
    
    # Formulario agregar
    if st.session_state.get('adding_worker', False):
        with st.form("form_nuevo_trabajador"):
            st.subheader("➕ Nuevo Trabajador")
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre*")
                email = st.text_input("Email*")
                telefono = st.text_input("Teléfono (con código país, ej: +51999999999)")
            with col2:
                # Obtener áreas existentes
                trabajadores_existentes = obtener_trabajadores()
                areas_existentes = sorted(trabajadores_existentes['area'].dropna().unique().tolist()) if not trabajadores_existentes.empty else []
                
                # Opciones de área
                areas_opciones = ["-- Seleccionar área --", "-- Nueva área --"] + areas_existentes
                area_select = st.selectbox("Área*", areas_opciones)
                
                # Si selecciona nueva área, mostrar input
                if area_select == "-- Nueva área --":
                    area = st.text_input("Nueva área*", key="nueva_area_crear")
                elif area_select == "-- Seleccionar área --":
                    area = ""
                else:
                    area = area_select
                
                foto_upload = st.file_uploader("Foto de Perfil", type=['png', 'jpg', 'jpeg'])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Guardar", type="primary"):
                    if nombre and email and area:
                        foto_base64 = None
                        if foto_upload:
                            foto_base64 = procesar_foto(foto_upload)
                        
                        trabajador_id, error = agregar_trabajador(nombre, email, telefono, area, foto_base64)
                        if trabajador_id:
                            log_action('CREATE', 'trabajadores', trabajador_id, details=f"Creado {nombre}")
                            st.success(f"✅ Trabajador {nombre} creado con área {area}")
                            st.info(f"🆔 ID asignado: {trabajador_id}")
                            st.session_state.adding_worker = False
                            st.cache_data.clear()  # Limpiar cache
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {error}")
                    else:
                        st.error("❌ Nombre, email y área son obligatorios")
            with col2:
                if st.form_submit_button("❌ Cancelar"):
                    st.session_state.adding_worker = False
                    st.rerun()
    
    st.markdown("---")
    
    # Mostrar trabajadores en cards (3 columnas)
    if not trabajadores_df.empty:
        # Crear filas de 3 cards
        for i in range(0, len(trabajadores_df), 3):
            cols = st.columns(3)
            
            for idx, col in enumerate(cols):
                if i + idx < len(trabajadores_df):
                    trabajador = trabajadores_df.iloc[i + idx]
                    
                    with col:
                        # Calcular horas y color
                        total_horas = obtener_total_horas(trabajador['id'], 2025)
                        color, icono = get_color_for_hours(total_horas)
                        
                        # Card con foto
                        foto_html = ""
                        if trabajador.get('foto'):
                            foto_html = f'<img src="{trabajador["foto"]}" style="width: 80px; height: 80px;  margin-left:auto; margin-right:auto;border-radius: 50%; object-fit: cover; border: 3px solid {color};">'
                        else:
                            foto_html = f'<div style="width: 80px; height: 80px;  margin-left:auto; margin-right:auto; border-radius: 50%; background: {color}; display: flex; align-items: center; justify-content: center; font-size: 2rem; color: white;">👤</div>'
                        
                        st.markdown(f"""
                        <div style='background: white; padding: 1.5rem; border-radius: 15px; 
                                    box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center;
                                    border-top: 4px solid {color};'>
                            {foto_html}
                            <h3 style='margin: 1rem 0 0.5rem 0; color: #333;'>{trabajador['nombre']}</h3>
                            <p style='color: #666; margin: 0; font-size: 0.9rem;'>{trabajador.get('area', 'Sin área')}</p>
                            <div style='background: {color}; color: white; padding: 0.5rem; 
                                        border-radius: 8px; margin: 1rem 0; font-weight: bold;'>
                                {icono} {total_horas}h / 40h
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Botón toggle para mostrar/ocultar
                        key_toggle = f"toggle_{trabajador['id']}"
                        is_viewing = st.session_state.get(key_toggle, False)
                        
                        if st.button(
                            "❌ Cerrar" if is_viewing else "👁️ Ver/Editar",
                            key=f"btn_{trabajador['id']}",
                            use_container_width=True,
                            type="secondary" if is_viewing else "primary"
                        ):
                            st.session_state[key_toggle] = not is_viewing
                            st.rerun()
                        
                        # Mostrar modal si está activo
                        if is_viewing:
                            show_edit_modal(trabajador, rubros_df)
    else:
        st.info("No hay trabajadores registrados")

def show_edit_modal(trabajador, rubros_df):
    """Modal de edición de trabajador"""
    st.markdown("---")
    st.subheader(f"Editando: {trabajador['nombre']}")
    
    tabs = st.tabs(["📋 Info", "⏰ Horas", "📷 Foto", "📧 Notificar"])
    
    with tabs[0]:  # Info
        with st.form(f"edit_info_{trabajador['id']}"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre", value=trabajador['nombre'])
                email = st.text_input("Email", value=trabajador['email'])
            with col2:
                telefono = st.text_input("Teléfono", value=trabajador.get('telefono', ''))
                
                # Obtener áreas únicas de trabajadores existentes
                from database.workers_json import obtener_trabajadores
                trabajadores_df = obtener_trabajadores()
                areas_existentes = sorted(trabajadores_df['area'].dropna().unique().tolist())
                
                # Agregar área actual si no está en la lista
                area_actual = trabajador.get('area', '')
                if area_actual and area_actual not in areas_existentes:
                    areas_existentes.append(area_actual)
                    areas_existentes = sorted(areas_existentes)
                
                # Agregar opción para nueva área
                areas_opciones = ["-- Nueva área --"] + areas_existentes
                
                # Determinar índice por defecto
                default_index = 0
                if area_actual in areas_existentes:
                    default_index = areas_existentes.index(area_actual) + 1
                
                area_select = st.selectbox("Área", areas_opciones, index=default_index)
                
                # Si selecciona nueva área, mostrar input
                if area_select == "-- Nueva área --":
                    area = st.text_input("Nueva área", value=area_actual if area_actual not in areas_existentes else "")
                else:
                    area = area_select
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.form_submit_button("💾 Guardar", type="primary"):
                    # Mostrar valores que se van a guardar
                    st.info(f"🔍 Guardando información de {trabajador['nombre']}...")
                    st.write(f"- Nombre: {nombre}")
                    st.write(f"- Email: {email}")
                    st.write(f"- Teléfono: {telefono}")
                    st.write(f"- Área: {area}")
                    
                    resultado = actualizar_trabajador(
                        trabajador['id'], 
                        nombre=nombre, 
                        email=email, 
                        telefono=telefono, 
                        area=area
                    )
                    
                    if resultado:
                        log_action('UPDATE', 'trabajadores', trabajador['id'], 
                                 details=f"Actualizado {nombre}, área: {area}")
                        st.success(f"✅ Información de {nombre} actualizada correctamente")
                        st.info(f"📊 Área asignada: {area}")
                        
                        # Limpiar cache para forzar recarga
                        st.cache_data.clear()
                        
                        # Esperar un momento
                        import time
                        time.sleep(0.5)
                        
                        st.rerun()
                    else:
                        st.error("❌ Error al actualizar información")
            with col2:
                if st.form_submit_button("🗑️ Eliminar"):
                    if eliminar_trabajador(trabajador['id']):
                        log_action('DELETE', 'trabajadores', trabajador['id'], 
                                 details=f"Eliminado {trabajador['nombre']}")
                        st.success("Trabajador eliminado")
                        st.session_state[f"toggle_{trabajador['id']}"] = False
                        st.rerun()
            with col3:
                if st.form_submit_button("❌ Cerrar"):
                    st.session_state[f"toggle_{trabajador['id']}"] = False
                    st.rerun()
    
    with tabs[1]:  # Horas
        total_horas = obtener_total_horas(trabajador['id'], 2025)
        horas_df = obtener_horas_trabajador(trabajador['id'], 2025)
        color, estado = get_color_for_hours(total_horas)
        
        st.markdown(f"""
        <div style='background: {color}; color: white; padding: 1rem; border-radius: 10px; text-align: center;'>
            <h3>{estado} {total_horas}h / 40h</h3>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form(f"horas_{trabajador['id']}"):
            cambios = {}
            for _, rubro in rubros_df.iterrows():
                horas_actuales = 0
                if not horas_df.empty:
                    hr = horas_df[horas_df['rubro'] == rubro['nombre']]
                    if not hr.empty:
                        horas_actuales = float(hr.iloc[0]['horas'])
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{rubro['nombre']}**")
                with col2:
                    nuevas = st.number_input("h", 0.0, 100.0, float(horas_actuales), 0.5,
                                           key=f"h_{trabajador['id']}_{rubro['id']}",
                                           label_visibility="collapsed")
                    if nuevas != horas_actuales:
                        cambios[rubro['id']] = nuevas
            
            if st.form_submit_button("💾 Guardar Horas", type="primary"):
                if cambios:
                    st.info(f"🔍 DEBUG: Guardando {len(cambios)} cambios...")
                    
                    # Guardar cambios con feedback
                    for rubro_id, horas in cambios.items():
                        resultado = asignar_horas(trabajador['id'], rubro_id, horas, 2025)
                        st.write(f"- Rubro {rubro_id}: {horas}h → {'✅' if resultado else '❌'}")
                    
                    # Esperar un momento para que la DB se actualice
                    import time
                    time.sleep(0.1)
                    
                    # Obtener horas actualizadas DIRECTAMENTE de la DB
                    nuevo_total = obtener_total_horas(trabajador['id'], 2025)
                    nueva_horas_df = obtener_horas_trabajador(trabajador['id'], 2025)
                    
                    # Mostrar resumen detallado
                    st.success(f"✅ {len(cambios)} cambio(s) guardado(s) para {trabajador['nombre']}")
                    st.metric("Nuevo Total", f"{nuevo_total}h")
                    
                    # Mostrar tabla de horas actuales
                    st.write("📊 Horas en base de datos:")
                    st.dataframe(nueva_horas_df[['rubro', 'horas']], hide_index=True)
                    
                    # Preparar datos para email
                    rubros_tabla = []
                    for _, hora in nueva_horas_df.iterrows():
                        rubros_tabla.append({
                            'rubro': hora['rubro'],
                            'horas': hora['horas']
                        })
                    
                    # Enviar notificación con plantilla
                    try:
                        email_service = EmailService()
                        templates = EmailTemplates()
                        html = templates.horas_asignadas(
                            trabajador['nombre'],
                            rubros_tabla,
                            nuevo_total,
                            2025
                        )
                        
                        if email_service.send_email(
                            trabajador['email'],
                            f"Actualización de Horas - {trabajador['nombre']}",
                            html
                        ):
                            st.success(f"✅ Email enviado a {trabajador['email']}")
                        else:
                            st.warning("⚠️ No se pudo enviar el email")
                    except Exception as e:
                        st.warning(f"⚠️ Error enviando email: {e}")
                    
                    # Forzar recarga completa
                    st.cache_data.clear()
                    
                    # Guardar flag para recargar fuera del form
                    st.session_state['needs_reload'] = True
                else:
                    st.info("ℹ️ No hay cambios para guardar")
        
        # Botón de recarga FUERA del formulario
        if st.session_state.get('needs_reload', False):
            if st.button("🔄 Actualizar Vista", type="primary", key=f"reload_{trabajador['id']}"):
                st.session_state['needs_reload'] = False
                st.rerun()
    
    with tabs[2]:  # Foto
        if trabajador.get('foto'):
            st.image(trabajador['foto'], width=200)
        else:
            st.info("Sin foto")
        
        nueva_foto = st.file_uploader("Nueva foto", type=['png', 'jpg', 'jpeg'],
                                      key=f"foto_{trabajador['id']}")
        if nueva_foto:
            if st.button("💾 Guardar", key=f"save_foto_{trabajador['id']}"):
                foto_b64 = procesar_foto(nueva_foto)
                if actualizar_trabajador(trabajador['id'], foto=foto_b64):
                    st.success("Foto actualizada")
                    st.rerun()
    
    with tabs[3]:  # Notificar
        st.subheader("Enviar Notificación")
        mensaje = st.text_area("Mensaje", f"Hola {trabajador['nombre']}, revisa tus horas",
                              key=f"msg_{trabajador['id']}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📧 Enviar Email", type="primary", key=f"email_{trabajador['id']}"):
                # Obtener horas del trabajador
                horas_df = obtener_horas_trabajador(trabajador['id'], 2025)
                total_horas = obtener_total_horas(trabajador['id'], 2025)
                
                # Crear tabla de rubros
                rubros_tabla = []
                for _, hora in horas_df.iterrows():
                    rubros_tabla.append({
                        'rubro': hora['rubro'],
                        'horas': hora['horas']
                    })
                
                # Enviar con plantilla
                email_service = EmailService()
                templates = EmailTemplates()
                html = templates.horas_asignadas(
                    trabajador['nombre'],
                    rubros_tabla,
                    total_horas,
                    2025
                )
                
                if email_service.send_email(trabajador['email'], 
                                          f"Horas Asignadas - {trabajador['nombre']}", 
                                          html):
                    st.success("✅ Email enviado")
                else:
                    st.error("❌ Error enviando email")
        
        with col2:
            if trabajador.get('telefono'):
                if st.button("💬 Enviar WhatsApp", key=f"whats_{trabajador['id']}"):
                    # Obtener horas del trabajador
                    horas_df = obtener_horas_trabajador(trabajador['id'], 2025)
                    total_horas = obtener_total_horas(trabajador['id'], 2025)
                    
                    # Crear lista de rubros
                    rubros_lista = []
                    for _, hora in horas_df.iterrows():
                        rubros_lista.append({
                            'rubro': hora['rubro'],
                            'horas': hora['horas']
                        })
                    
                    # Enviar con plantilla
                    whatsapp = WhatsAppService()
                    template_data = {
                        'type': 'horas_asignadas',
                        'nombre': trabajador['nombre'],
                        'rubros': rubros_lista,
                        'total_horas': total_horas,
                        'año': 2025
                    }
                    
                    if whatsapp.send_template_message(trabajador['telefono'], template_data):
                        st.success("✅ WhatsApp enviado")
                    else:
                        st.error("❌ Error enviando WhatsApp")
            else:
                st.warning("Sin teléfono configurado")

def procesar_foto(uploaded_file):
    """Procesar y redimensionar foto"""
    try:
        img = Image.open(uploaded_file)
        img.thumbnail((200, 200), Image.Resampling.LANCZOS)
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        st.error(f"Error: {e}")
        return None
