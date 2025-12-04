"""
Integración con Google Sheets (estilo index4.py)
"""
import streamlit as st
from auth.roles import require_role
from database.workers_json import obtener_trabajadores, obtener_rubros, obtener_horas_trabajador
from database.audit import log_action
import pandas as pd

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GOOGLE_SHEETS_AVAILABLE = True
except:
    GOOGLE_SHEETS_AVAILABLE = False

@require_role(['admin'])
def show_google_sheets_page():
    st.title("📊 Integración con Google Sheets")
    
    if not GOOGLE_SHEETS_AVAILABLE:
        st.error("⚠️ Librerías de Google Sheets no instaladas")
        st.code("pip install gspread google-auth")
        return
    
    # Configuración
    st.subheader("1️⃣ Configurar Conexión")
    
    with st.expander("📖 Cómo obtener credenciales", expanded=False):
        st.markdown("""
        **Pasos para configurar:**
        
        1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
        2. Crea un proyecto nuevo
        3. Habilita la API de Google Sheets
        4. Crea credenciales de cuenta de servicio
        5. Descarga el archivo JSON
        6. Sube el archivo aquí 👇
        """)
    
    # Upload de credentials
    creds_file = st.file_uploader("Subir credentials.json", type=['json'])
    sheet_url = st.text_input("URL de Google Sheet", placeholder="https://docs.google.com/spreadsheets/d/...")
    
    if st.button("🔗 Conectar", type="primary"):
        if creds_file and sheet_url:
            # Guardar credentials temporalmente
            with open('credentials.json', 'wb') as f:
                f.write(creds_file.getbuffer())
            
            try:
                # Conectar
                worksheet = conectar_google_sheets(sheet_url)
                if worksheet:
                    st.session_state['worksheet'] = worksheet
                    st.session_state['sheet_url'] = sheet_url
                    st.success("✅ Conectado a Google Sheets")
            except Exception as e:
                st.error(f"❌ Error: {e}")
        else:
            st.warning("Completa ambos campos")
    
    # Opciones si está conectado
    if st.session_state.get('worksheet'):
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("2️⃣ Importar desde Sheets")
            if st.button("⬇️ Importar Datos", type="primary", use_container_width=True):
                try:
                    importar_desde_sheets(st.session_state['worksheet'])
                    st.success("✅ Datos importados exitosamente")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        
        with col2:
            st.subheader("3️⃣ Exportar a Sheets")
            if st.button("⬆️ Exportar Datos", type="primary", use_container_width=True):
                try:
                    exportar_a_sheets(st.session_state['worksheet'])
                    st.success("✅ Datos exportados exitosamente")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        
        # Preview
        st.markdown("---")
        st.subheader("👀 Preview de Datos Actuales")
        
        trabajadores_df = obtener_trabajadores()
        rubros_df = obtener_rubros()
        
        if not trabajadores_df.empty:
            # Crear preview
            preview_data = []
            for _, trabajador in trabajadores_df.iterrows():
                row = {
                    'Trabajador': trabajador['nombre'],
                    'Email': trabajador['email'],
                    'Área': trabajador.get('area', '')
                }
                
                # Agregar horas por rubro
                horas_df = obtener_horas_trabajador(trabajador['id'], 2025)
                for _, rubro in rubros_df.iterrows():
                    if not horas_df.empty and 'rubro' in horas_df.columns:
                        horas_rubro = horas_df[horas_df['rubro'] == rubro['nombre']]
                        row[rubro['nombre']] = float(horas_rubro.iloc[0]['horas']) if not horas_rubro.empty else 0
                    else:
                        row[rubro['nombre']] = 0
                
                # Total
                row['Total_Horas'] = sum([v for k, v in row.items() if k not in ['Trabajador', 'Email', 'Área']])
                preview_data.append(row)
            
            preview_df = pd.DataFrame(preview_data)
            st.dataframe(preview_df, use_container_width=True)
            
            # Botón desconectar
            if st.button("🔌 Desconectar"):
                del st.session_state['worksheet']
                del st.session_state['sheet_url']
                st.rerun()

def conectar_google_sheets(sheet_url, creds_file='credentials.json'):
    """Conectar con Google Sheets"""
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    creds = Credentials.from_service_account_file(creds_file, scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(sheet_url)
    worksheet = sheet.get_worksheet(0)
    
    return worksheet

def importar_desde_sheets(worksheet):
    """Importar datos desde Google Sheets - ACTUALIZA trabajadores existentes"""
    from database.workers_json import (
        agregar_trabajador, 
        agregar_rubro, 
        asignar_horas,
        obtener_trabajadores,
        obtener_rubros
    )
    
    # Leer datos
    data = worksheet.get_all_records()
    
    if not data:
        raise Exception("La hoja está vacía")
    
    # Obtener rubros de las columnas
    rubros_en_sheet = [k for k in data[0].keys() if k not in ['Trabajador', 'Total_Horas', 'id', 'foto', 'Email', 'Área']]
    
    # Crear rubros si no existen
    rubros_actuales = obtener_rubros()
    for rubro_nombre in rubros_en_sheet:
        if rubro_nombre not in rubros_actuales['nombre'].values:
            print(f"🆕 Creando rubro: {rubro_nombre}")
            agregar_rubro(rubro_nombre)
    
    # Refrescar rubros
    rubros_df = obtener_rubros()
    
    # Obtener trabajadores existentes
    trabajadores_existentes = obtener_trabajadores(estatus='activo')
    
    # Importar trabajadores
    importados = 0
    actualizados = 0
    
    for row in data:
        trabajador_nombre = row.get('Trabajador', '').strip()
        email = row.get('Email', '').strip()
        area = row.get('Área', '').strip()
        
        if not trabajador_nombre or not email:
            continue  # Saltar filas vacías
        
        # Buscar si el trabajador ya existe (por email)
        trabajador_existente = trabajadores_existentes[trabajadores_existentes['email'] == email]
        
        if not trabajador_existente.empty:
            # Trabajador ya existe, usar su ID
            trabajador_id = trabajador_existente.iloc[0]['id']
            print(f"♻️ Actualizando: {trabajador_nombre} (ID: {trabajador_id})")
            actualizados += 1
        else:
            # Crear nuevo trabajador
            trabajador_id, error = agregar_trabajador(trabajador_nombre, email, '', area)
            if trabajador_id:
                print(f"🆕 Creado: {trabajador_nombre} (ID: {trabajador_id})")
                importados += 1
            else:
                print(f"❌ Error creando {trabajador_nombre}: {error}")
                continue
        
        # Asignar horas (SIEMPRE, para actualizar o crear)
        if trabajador_id:
            for rubro_nombre in rubros_en_sheet:
                horas = row.get(rubro_nombre, 0)
                try:
                    horas = float(horas) if horas else 0
                except:
                    horas = 0
                
                # Asignar horas (actualiza si existe, crea si no)
                rubro = rubros_df[rubros_df['nombre'] == rubro_nombre]
                if not rubro.empty:
                    rubro_id = rubro.iloc[0]['id']
                    asignar_horas(trabajador_id, rubro_id, horas, 2025)
                    print(f"   ✅ {rubro_nombre}: {horas}h")
            
            log_action('IMPORT', 'trabajadores', trabajador_id, 
                      details=f'Importado/Actualizado desde Google Sheets: {trabajador_nombre}')
    
    print(f"\n📊 Resumen:")
    print(f"   🆕 Nuevos: {importados}")
    print(f"   ♻️ Actualizados: {actualizados}")
    print(f"   ✅ Total procesados: {importados + actualizados}")

def exportar_a_sheets(worksheet):
    """Exportar datos a Google Sheets"""
    from database.workers_json import obtener_trabajadores, obtener_rubros, obtener_horas_trabajador
    from datetime import datetime
    
    # Forzar recarga de datos (sin cache)
    año_actual = datetime.now().year
    
    trabajadores_df = obtener_trabajadores()
    rubros_df = obtener_rubros()
    
    if trabajadores_df.empty:
        raise Exception("No hay trabajadores para exportar")
    
    # Preparar datos
    export_data = []
    
    # Header
    headers = ['Trabajador', 'Email', 'Área']
    headers.extend(rubros_df['nombre'].tolist())
    headers.append('Total_Horas')
    export_data.append(headers)
    
    # Datos - IMPORTANTE: Obtener horas actualizadas
    for _, trabajador in trabajadores_df.iterrows():
        row = [
            trabajador['nombre'],
            trabajador['email'],
            trabajador.get('area', '')
        ]
        
        total = 0
        # Usar año actual
        horas_df = obtener_horas_trabajador(trabajador['id'], año_actual)
        
        for _, rubro in rubros_df.iterrows():
            if not horas_df.empty and 'rubro' in horas_df.columns:
                horas_rubro = horas_df[horas_df['rubro'] == rubro['nombre']]
                horas = float(horas_rubro.iloc[0]['horas']) if not horas_rubro.empty else 0
            else:
                horas = 0
            row.append(horas)
            total += horas
        
        row.append(total)
        export_data.append(row)
    
    # Limpiar y escribir
    worksheet.clear()
    worksheet.update(values=export_data, range_name='A1')
    
    # Formatear
    worksheet.format('A1:Z1', {
        'backgroundColor': {'red': 0.4, 'green': 0.5, 'blue': 0.9},
        'textFormat': {'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}, 'bold': True}
    })
    
    log_action('EXPORT', 'trabajadores', details=f'Exportado a Google Sheets ({año_actual})')