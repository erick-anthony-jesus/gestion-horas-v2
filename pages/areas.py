"""
Página de Gestión de Áreas
"""
import streamlit as st
import pandas as pd
from database.workers_json import obtener_trabajadores, actualizar_trabajador
from database.audit import log_action
from auth.roles import require_role

@require_role(['admin'])
def show_areas_page():
    st.title("🏢 Gestión de Áreas")
    
    # Obtener áreas existentes
    trabajadores_df = obtener_trabajadores()
    
    if trabajadores_df.empty or 'area' not in trabajadores_df.columns:
        st.warning("No hay trabajadores registrados para gestionar áreas")
        return
    
    # Obtener áreas únicas
    areas_existentes = trabajadores_df['area'].dropna().unique().tolist()
    
    # Contar trabajadores por área
    area_counts = trabajadores_df['area'].value_counts().to_dict()
    
    # Tabs
    tab1, tab2 = st.tabs(["📊 Áreas Actuales", "✏️ Renombrar/Fusionar"])
    
    # TAB 1: Áreas actuales
    with tab1:
        st.subheader("📊 Áreas Registradas")
        
        st.info("💡 **Para crear una nueva área:** Ve a 'Trabajadores' → Agregar/Editar → Selecciona '-- Nueva área --' y escribe el nombre")
        
        if areas_existentes:
            # Crear DataFrame para mostrar
            areas_data = []
            for area in sorted(areas_existentes):
                count = area_counts.get(area, 0)
                areas_data.append({
                    'Área': area,
                    'Trabajadores': count
                })
            
            areas_df = pd.DataFrame(areas_data)
            
            st.dataframe(
                areas_df,
                use_container_width=True,
                column_config={
                    "Área": st.column_config.TextColumn("Área", width="large"),
                    "Trabajadores": st.column_config.NumberColumn("Nº Trabajadores", format="%d")
                },
                hide_index=True
            )
            
            # Métricas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Áreas", len(areas_existentes))
            with col2:
                st.metric("Total Trabajadores", len(trabajadores_df))
            with col3:
                promedio = len(trabajadores_df) / len(areas_existentes) if areas_existentes else 0
                st.metric("Promedio por Área", f"{promedio:.1f}")
        else:
            st.info("No hay áreas registradas")
    
    # TAB 2: Renombrar/Fusionar
    with tab2:
        st.subheader("✏️ Renombrar o Fusionar Áreas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Renombrar Área")
            
            area_antigua = st.selectbox(
                "Área a renombrar",
                ["-- Seleccionar --"] + sorted(areas_existentes),
                key="rename_old"
            )
            
            area_nueva = st.text_input("Nuevo nombre", key="rename_new")
            
            if st.button("🔄 Renombrar", type="primary"):
                if area_antigua != "-- Seleccionar --" and area_nueva:
                    # Obtener trabajadores del área antigua
                    trabajadores_area = trabajadores_df[trabajadores_df['area'] == area_antigua]
                    
                    # Actualizar todos
                    for _, trabajador in trabajadores_area.iterrows():
                        actualizar_trabajador(trabajador['id'], area=area_nueva)
                    
                    log_action('UPDATE', 'areas', 
                             details=f"Renombrada área '{area_antigua}' → '{area_nueva}' ({len(trabajadores_area)} trabajadores)")
                    
                    st.success(f"✅ Área renombrada: '{area_antigua}' → '{area_nueva}'")
                    st.info(f"📊 {len(trabajadores_area)} trabajadores actualizados")
                    st.rerun()
                else:
                    st.error("❌ Completa ambos campos")
        
        with col2:
            st.markdown("### Fusionar Áreas")
            
            area_origen = st.selectbox(
                "Área origen (se eliminará)",
                ["-- Seleccionar --"] + sorted(areas_existentes),
                key="merge_from"
            )
            
            area_destino = st.selectbox(
                "Área destino (se mantendrá)",
                ["-- Seleccionar --"] + sorted([a for a in areas_existentes if a != area_origen]),
                key="merge_to"
            )
            
            if st.button("🔗 Fusionar", type="primary"):
                if area_origen != "-- Seleccionar --" and area_destino != "-- Seleccionar --":
                    # Obtener trabajadores del área origen
                    trabajadores_origen = trabajadores_df[trabajadores_df['area'] == area_origen]
                    
                    # Mover todos al destino
                    for _, trabajador in trabajadores_origen.iterrows():
                        actualizar_trabajador(trabajador['id'], area=area_destino)
                    
                    log_action('UPDATE', 'areas', 
                             details=f"Fusionada área '{area_origen}' → '{area_destino}' ({len(trabajadores_origen)} trabajadores)")
                    
                    st.success(f"✅ Áreas fusionadas: '{area_origen}' → '{area_destino}'")
                    st.info(f"📊 {len(trabajadores_origen)} trabajadores movidos")
                    st.rerun()
                else:
                    st.error("❌ Selecciona ambas áreas")
        
        st.markdown("---")
        st.warning("⚠️ **Importante:** Renombrar o fusionar áreas afectará todos los trabajadores asignados")