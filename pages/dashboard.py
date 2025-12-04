"""
Página de Dashboard principal
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from database.workers_json import obtener_trabajadores, obtener_rubros, obtener_total_horas, obtener_resumen_area
from database.audit import get_recent_actions
from auth.roles import get_accessible_workers

def show_dashboard():
    """Mostrar dashboard principal"""
    # Botón de recarga en la esquina
    col1, col2 = st.columns([6, 1])
    with col1:
        st.title("🏠 Dashboard")
    with col2:
        if st.button("🔄 Actualizar", help="Recargar datos"):
            # Limpiar TODA la cache
            st.cache_data.clear()
            st.cache_resource.clear()
            # Forzar recarga
            st.rerun()
    
    # Mensaje de bienvenida personalizado
    hora = datetime.now().hour
    saludo = "Buenos días" if hora < 12 else "Buenas tardes" if hora < 18 else "Buenas noches"
    
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgb(0 95 255) 0%, rgb(66 172 233) 100%); 
                    padding: 2rem; border-radius: 10px; color: white; margin-bottom: 2rem;'>
            <h2 style='margin: 0;'>{saludo}, {st.session_state['name']}! 👋</h2>
            <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>
                Aquí está el resumen de tu gestión de horas
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Contenido según rol
    if st.session_state['role'] == 'trabajador':
        show_trabajador_dashboard()
    elif st.session_state['role'] == 'supervisor':
        show_supervisor_dashboard()
    else:  # admin
        show_admin_dashboard()
    
    # Actividad reciente (común para todos)
    st.markdown("---")
    st.subheader("📋 Actividad Reciente")
    
    recent_df = get_recent_actions(limit=10)
    
    if not recent_df.empty:
        # Formatear para mostrar
        recent_df['timestamp'] = pd.to_datetime(recent_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
        
        st.dataframe(
            recent_df[['timestamp', 'username', 'action', 'details']],
            use_container_width=True,
            column_config={
                "timestamp": "Fecha/Hora",
                "username": "Usuario",
                "action": "Acción",
                "details": "Detalles"
            },
            hide_index=True
        )
    else:
        st.info("No hay actividad reciente registrada")

def show_trabajador_dashboard():
    """Dashboard para trabajadores"""
    trabajador_id = st.session_state.get('trabajador_id')
    
    if not trabajador_id:
        st.error("No se encontró ID de trabajador")
        return
    
    # Obtener datos
    año_actual = datetime.now().year
    horas_df = obtener_horas_trabajador(trabajador_id, año_actual)
    total_horas = obtener_total_horas(trabajador_id, año_actual)
    
    # Determinar color según horas
    limite = 40
    if total_horas <= limite * 0.9:
        color = "#48bb78"  # Verde
        estado = "✅ Normal"
        icono = "✅"
    elif total_horas <= limite:
        color = "#ed8936"  # Amarillo/Naranja
        estado = "⚠️ Cerca del límite"
        icono = "⚠️"
    else:
        color = "#f56565"  # Rojo
        estado = "🚨 Sobrecarga"
        icono = "🚨"
    
    # Banner con color
    st.markdown(f"""
        <div style='background: {color}; color: white; padding: 2rem; border-radius: 10px; text-align: center; margin-bottom: 2rem;'>
            <h1 style='margin: 0; font-size: 3rem;'>{icono}</h1>
            <h2 style='margin: 0.5rem 0;'>{estado}</h2>
            <h1 style='margin: 0; font-size: 3.5rem;'>{total_horas}h / {limite}h</h1>
            <p style='margin: 0.5rem 0; opacity: 0.9;'>
                {int((total_horas / limite) * 100)}% del límite usado
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Métricas adicionales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Horas", f"{total_horas}h")
    
    with col2:
        num_rubros = len(horas_df)
        st.metric("Rubros Asignados", num_rubros)
    
    with col3:
        promedio = total_horas / num_rubros if num_rubros > 0 else 0
        st.metric("Promedio por Rubro", f"{promedio:.1f}h")
    
    with col4:
        disponible = max(0, limite - total_horas)
        st.metric("Horas Disponibles", f"{disponible:.0f}h")
    
    # Gráfico de distribución
    if not horas_df.empty and len(horas_df) > 0:
        st.subheader("📊 Distribución de Horas")
        
        # Crear gráfico de barras
        try:
            st.bar_chart(horas_df.set_index('rubro')['horas'])
        except:
            st.info("No se pudo generar el gráfico")
        
        # Tabla detallada
        st.subheader("📋 Detalle de Asignaciones")
        st.dataframe(
            horas_df,
            use_container_width=True,
            column_config={
                "rubro": "Rubro",
                "horas": st.column_config.NumberColumn("Horas", format="%.0f h"),
                "año": "Año"
            },
            hide_index=True
        )
    else:
        st.info("No tienes horas asignadas aún")

def show_supervisor_dashboard():
    """Dashboard para supervisores"""
    area = st.session_state.get('area')
    
    if not area:
        st.error("No se encontró área asignada")
        return
    
    # Obtener datos del área
    año_actual = datetime.now().year
    resumen_df = obtener_resumen_area(area, año_actual)
    trabajadores_df = obtener_trabajadores(area=area)
    
    # Métricas del área
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        num_trabajadores = len(trabajadores_df)
        st.metric("Trabajadores", num_trabajadores)
    
    with col2:
        total_horas_area = resumen_df['total_horas'].sum() if not resumen_df.empty else 0
        st.metric("Total Horas Área", f"{total_horas_area:.0f}h")
    
    with col3:
        promedio_area = total_horas_area / num_trabajadores if num_trabajadores > 0 else 0
        st.metric("Promedio por Trabajador", f"{promedio_area:.0f}h")
    
    with col4:
        rubros_df = obtener_rubros()
        st.metric("Rubros Activos", len(rubros_df))
    
    # Resumen del equipo
    st.subheader(f"👥 Resumen del Área: {area}")
    
    if not resumen_df.empty:
        # Agregar columna de estado
        resumen_df['estado'] = resumen_df['total_horas'].apply(
            lambda x: "✅ Normal" if x <= 40 else "⚠️ Sobrecarga"
        )
        
        st.dataframe(
            resumen_df,
            use_container_width=True,
            column_config={
                "trabajador": "Trabajador",
                "total_horas": st.column_config.NumberColumn("Total Horas", format="%.0f h"),
                "num_rubros": st.column_config.NumberColumn("Rubros", format="%d"),
                "estado": "Estado"
            },
            hide_index=True
        )
        
        # Gráfico comparativo
        st.subheader("📊 Comparación de Carga")
        try:
            st.bar_chart(resumen_df.set_index('trabajador')['total_horas'])
        except:
            st.info("No se pudo generar el gráfico")
    else:
        st.info("No hay datos disponibles para tu área")

def show_admin_dashboard():
    """Dashboard para administradores"""
    # Obtener todos los datos
    trabajadores_df = obtener_trabajadores()
    rubros_df = obtener_rubros()
    año_actual = datetime.now().year
    
    # Métricas globales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Trabajadores", len(trabajadores_df))
    
    with col2:
        st.metric("Rubros Activos", len(rubros_df))
    
    with col3:
        # Calcular total de horas de todos
        total_global = sum(
            obtener_total_horas(t['id'], año_actual) 
            for _, t in trabajadores_df.iterrows()
        )
        st.metric("Total Horas Global", f"{total_global:.0f}h")
    
    with col4:
        # Áreas únicas
        areas = trabajadores_df['area'].nunique()
        st.metric("Áreas", areas)
    
    # Resumen por área
    st.subheader("📊 Resumen por Área")
    
    areas_list = trabajadores_df['area'].unique()
    
    tabs = st.tabs([f"📍 {area}" for area in areas_list])
    
    for i, area in enumerate(areas_list):
        with tabs[i]:
            resumen_area = obtener_resumen_area(area, año_actual)
            
            if not resumen_area.empty:
                # Métricas del área
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Trabajadores", len(resumen_area))
                
                with col2:
                    total_area = resumen_area['total_horas'].sum()
                    st.metric("Total Horas", f"{total_area:.0f}h")
                
                with col3:
                    promedio = total_area / len(resumen_area) if len(resumen_area) > 0 else 0
                    st.metric("Promedio", f"{promedio:.0f}h")
                
                # Tabla
                st.dataframe(
                    resumen_area,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Gráfico
                try:
                    st.bar_chart(resumen_area.set_index('trabajador')['total_horas'])
                except:
                    st.info("No se pudo generar el gráfico")
            else:
                st.info(f"No hay datos para el área {area}")
    
    # Alertas de sobrecarga
    st.subheader("⚠️ Alertas de Sobrecarga")
    
    sobrecargas = []
    for _, trabajador in trabajadores_df.iterrows():
        total = obtener_total_horas(trabajador['id'], año_actual)
        if total > 40:
            sobrecargas.append({
                'trabajador': trabajador['nombre'],
                'area': trabajador['area'],
                'horas': total,
                'exceso': total - 40
            })
    
    if sobrecargas:
        sobrecarga_df = pd.DataFrame(sobrecargas)
        st.dataframe(
            sobrecarga_df,
            use_container_width=True,
            column_config={
                "trabajador": "Trabajador",
                "area": "Área",
                "horas": st.column_config.NumberColumn("Total Horas", format="%.0f h"),
                "exceso": st.column_config.NumberColumn("Exceso", format="%.0f h")
            },
            hide_index=True
        )
    else:
        st.success("✅ No hay trabajadores con sobrecarga")
