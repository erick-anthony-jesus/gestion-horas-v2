"""Página de gestión de rubros"""
import streamlit as st
from database.workers_json import agregar_rubro, obtener_rubros
from database.audit import log_action
from auth.roles import require_role

@require_role(['admin'])
def show_rubros_page():
    st.title("📊 Gestión de Rubros")
    
    with st.form("nuevo_rubro"):
        st.subheader("Agregar Nuevo Rubro")
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre del Rubro*")
        with col2:
            descripcion = st.text_input("Descripción")
        
        if st.form_submit_button("Guardar Rubro"):
            if nombre:
                rubro_id, error = agregar_rubro(nombre, descripcion)
                if rubro_id:
                    log_action('CREATE', 'rubros', rubro_id, details=f"Creado {nombre}")
                    st.success(f"✅ Rubro '{nombre}' creado")
                    st.rerun()
                else:
                    st.error(f"❌ {error}")
            else:
                st.error("El nombre es obligatorio")
    
    rubros_df = obtener_rubros(activos_solo=False)
    if not rubros_df.empty:
        st.dataframe(rubros_df, use_container_width=True, hide_index=True)
