"""
Script para verificar el estado de la base de datos
"""
import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).parent / 'trabajadores.db'

def verificar_db():
    """Verificar el estado de la base de datos"""
    if not DB_PATH.exists():
        print("❌ Base de datos NO existe")
        print(f"   Esperada en: {DB_PATH}")
        return
    
    print(f"✅ Base de datos existe: {DB_PATH}")
    print(f"   Tamaño: {DB_PATH.stat().st_size / 1024:.2f} KB\n")
    
    conn = sqlite3.connect(str(DB_PATH))
    
    # Verificar trabajadores
    print("=" * 60)
    print("TRABAJADORES")
    print("=" * 60)
    trabajadores_df = pd.read_sql_query("SELECT * FROM trabajadores", conn)
    print(f"Total: {len(trabajadores_df)}")
    print(trabajadores_df[['id', 'nombre', 'email', 'area']].to_string(index=False))
    print()
    
    # Verificar rubros
    print("=" * 60)
    print("RUBROS")
    print("=" * 60)
    rubros_df = pd.read_sql_query("SELECT * FROM rubros WHERE activo = 1", conn)
    print(f"Total: {len(rubros_df)}")
    print(rubros_df[['id', 'nombre']].to_string(index=False))
    print()
    
    # Verificar horas asignadas
    print("=" * 60)
    print("HORAS ASIGNADAS")
    print("=" * 60)
    horas_query = '''
        SELECT 
            h.id,
            t.nombre as trabajador,
            r.nombre as rubro,
            h.horas,
            h.año
        FROM horas_asignadas h
        JOIN trabajadores t ON h.trabajador_id = t.id
        JOIN rubros r ON h.rubro_id = r.id
        ORDER BY t.nombre, r.nombre
    '''
    horas_df = pd.read_sql_query(horas_query, conn)
    print(f"Total registros: {len(horas_df)}")
    
    if len(horas_df) > 0:
        print(horas_df.to_string(index=False))
        print()
        
        # Totales por trabajador
        print("TOTALES POR TRABAJADOR:")
        totales = horas_df.groupby('trabajador')['horas'].sum().reset_index()
        totales.columns = ['Trabajador', 'Total Horas']
        print(totales.to_string(index=False))
    else:
        print("⚠️ NO HAY HORAS ASIGNADAS")
    
    print()
    
    # Verificar integridad
    print("=" * 60)
    print("VERIFICACIÓN DE INTEGRIDAD")
    print("=" * 60)
    
    # Verificar que todos los trabajadores tengan email
    sin_email = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM trabajadores WHERE email IS NULL OR email = ''", 
        conn
    )
    if sin_email['count'][0] > 0:
        print(f"⚠️ {sin_email['count'][0]} trabajadores sin email")
    else:
        print("✅ Todos los trabajadores tienen email")
    
    # Verificar que todos los trabajadores tengan área
    sin_area = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM trabajadores WHERE area IS NULL OR area = ''", 
        conn
    )
    if sin_area['count'][0] > 0:
        print(f"⚠️ {sin_area['count'][0]} trabajadores sin área")
    else:
        print("✅ Todos los trabajadores tienen área")
    
    # Verificar horas órfanas (sin trabajador o rubro válido)
    orfanas = pd.read_sql_query('''
        SELECT COUNT(*) as count FROM horas_asignadas h
        WHERE NOT EXISTS (SELECT 1 FROM trabajadores t WHERE t.id = h.trabajador_id)
           OR NOT EXISTS (SELECT 1 FROM rubros r WHERE r.id = h.rubro_id)
    ''', conn)
    if orfanas['count'][0] > 0:
        print(f"⚠️ {orfanas['count'][0]} horas asignadas con referencias inválidas")
    else:
        print("✅ Todas las horas asignadas son válidas")
    
    conn.close()

if __name__ == '__main__':
    verificar_db()
