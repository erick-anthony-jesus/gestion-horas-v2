"""
Gestión de trabajadores y horas en SQLite
"""
import sqlite3
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / 'trabajadores.db'

def init_workers_db():
    """Inicializar base de datos de trabajadores"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    # Tabla de trabajadores
    c.execute('''
        CREATE TABLE IF NOT EXISTS trabajadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT UNIQUE,
            telefono TEXT,
            area TEXT,
            foto TEXT,
            estatus TEXT DEFAULT 'activo',
            fecha_creacion TEXT,
            fecha_modificacion TEXT
        )
    ''')
    
    # Tabla de rubros
    c.execute('''
        CREATE TABLE IF NOT EXISTS rubros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            descripcion TEXT,
            activo INTEGER DEFAULT 1
        )
    ''')
    
    # Tabla de asignación de horas
    c.execute('''
        CREATE TABLE IF NOT EXISTS horas_asignadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trabajador_id INTEGER NOT NULL,
            rubro_id INTEGER NOT NULL,
            horas REAL NOT NULL,
            año INTEGER NOT NULL,
            fecha_asignacion TEXT,
            FOREIGN KEY (trabajador_id) REFERENCES trabajadores(id),
            FOREIGN KEY (rubro_id) REFERENCES rubros(id),
            UNIQUE(trabajador_id, rubro_id, año)
        )
    ''')
    
    conn.commit()
    conn.close()

def agregar_trabajador(nombre, email, telefono="", area="", foto=None):
    """Agregar nuevo trabajador"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    try:
        c.execute('''
            INSERT INTO trabajadores (nombre, email, telefono, area, foto, fecha_creacion, fecha_modificacion)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nombre, email, telefono, area, foto, datetime.now().isoformat(), datetime.now().isoformat()))
        
        trabajador_id = c.lastrowid
        conn.commit()
        conn.close()
        return trabajador_id, None
    except sqlite3.IntegrityError:
        conn.close()
        return None, "El email ya existe"
    except Exception as e:
        conn.close()
        return None, str(e)

def obtener_trabajadores(area=None, estatus='activo'):
    """Obtener lista de trabajadores"""
    conn = sqlite3.connect(str(DB_PATH))
    
    query = "SELECT * FROM trabajadores WHERE estatus = ?"
    params = [estatus]
    
    if area:
        query += " AND area = ?"
        params.append(area)
    
    query += " ORDER BY nombre"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    return df

def actualizar_trabajador(trabajador_id, **kwargs):
    """Actualizar datos de trabajador"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    # Construir query dinámicamente
    campos = []
    valores = []
    
    print(f"🔍 Actualizando trabajador {trabajador_id}:")
    for key, value in kwargs.items():
        if key in ['nombre', 'email', 'telefono', 'area', 'foto', 'estatus']:
            campos.append(f"{key} = ?")
            valores.append(value)
            print(f"  - {key}: {value if key != 'foto' else '[foto base64]'}")
    
    if not campos:
        print("❌ No hay campos para actualizar")
        conn.close()
        return False
    
    campos.append("fecha_modificacion = ?")
    valores.append(datetime.now().isoformat())
    valores.append(trabajador_id)
    
    query = f"UPDATE trabajadores SET {', '.join(campos)} WHERE id = ?"
    
    try:
        # Obtener valores anteriores
        c.execute("SELECT nombre, email, telefono, area FROM trabajadores WHERE id = ?", (trabajador_id,))
        anterior = c.fetchone()
        print(f"  Valores anteriores: {anterior}")
        
        # Actualizar
        c.execute(query, valores)
        affected = c.rowcount
        conn.commit()
        
        # Verificar actualización
        c.execute("SELECT nombre, email, telefono, area FROM trabajadores WHERE id = ?", (trabajador_id,))
        nuevo = c.fetchone()
        print(f"  Valores nuevos: {nuevo}")
        print(f"  Filas afectadas: {affected}")
        
        conn.close()
        
        if affected > 0:
            print(f"✅ Trabajador {trabajador_id} actualizado correctamente")
            return True
        else:
            print(f"⚠️ No se actualizó ninguna fila (id {trabajador_id} no existe?)")
            return False
            
    except Exception as e:
        print(f"❌ Error actualizando trabajador: {e}")
        conn.close()
        return False
        return False

def eliminar_trabajador(trabajador_id, hard_delete=False):
    """Eliminar trabajador
    
    Args:
        trabajador_id: ID del trabajador
        hard_delete: Si True, elimina completamente. Si False, solo marca como inactivo (default)
    """
    if hard_delete:
        # Eliminación completa (hard delete)
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        
        try:
            # Eliminar primero las horas asignadas
            c.execute("DELETE FROM horas_asignadas WHERE trabajador_id = ?", (trabajador_id,))
            horas_eliminadas = c.rowcount
            
            # Eliminar trabajador
            c.execute("DELETE FROM trabajadores WHERE id = ?", (trabajador_id,))
            trabajador_eliminado = c.rowcount
            
            conn.commit()
            conn.close()
            
            print(f"✅ Trabajador {trabajador_id} eliminado completamente")
            print(f"   - Horas eliminadas: {horas_eliminadas}")
            
            return trabajador_eliminado > 0
        except Exception as e:
            print(f"❌ Error eliminando trabajador: {e}")
            conn.close()
            return False
    else:
        # Soft delete (solo marca como inactivo)
        return actualizar_trabajador(trabajador_id, estatus='inactivo')

def agregar_rubro(nombre, descripcion=""):
    """Agregar nuevo rubro"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    try:
        c.execute('INSERT INTO rubros (nombre, descripcion) VALUES (?, ?)', (nombre, descripcion))
        rubro_id = c.lastrowid
        conn.commit()
        conn.close()
        return rubro_id, None
    except sqlite3.IntegrityError:
        conn.close()
        return None, "El rubro ya existe"
    except Exception as e:
        conn.close()
        return None, str(e)

def obtener_rubros(activos_solo=True):
    """Obtener lista de rubros"""
    conn = sqlite3.connect(str(DB_PATH))
    
    query = "SELECT * FROM rubros"
    if activos_solo:
        query += " WHERE activo = 1"
    query += " ORDER BY nombre"
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df

def asignar_horas(trabajador_id, rubro_id, horas, año=None):
    """Asignar horas a un trabajador para un rubro"""
    if año is None:
        año = datetime.now().year
    
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    try:
        # Primero verificar si existe una asignación previa
        c.execute('''
            SELECT id, horas FROM horas_asignadas 
            WHERE trabajador_id = ? AND rubro_id = ? AND año = ?
        ''', (trabajador_id, rubro_id, año))
        
        existing = c.fetchone()
        
        if existing:
            # Actualizar
            c.execute('''
                UPDATE horas_asignadas 
                SET horas = ?, fecha_asignacion = ?
                WHERE trabajador_id = ? AND rubro_id = ? AND año = ?
            ''', (horas, datetime.now().isoformat(), trabajador_id, rubro_id, año))
            print(f"✅ Actualizado: Trabajador {trabajador_id}, Rubro {rubro_id}: {existing[1]}h → {horas}h")
        else:
            # Insertar nuevo
            c.execute('''
                INSERT INTO horas_asignadas 
                (trabajador_id, rubro_id, horas, año, fecha_asignacion)
                VALUES (?, ?, ?, ?, ?)
            ''', (trabajador_id, rubro_id, horas, año, datetime.now().isoformat()))
            print(f"✅ Insertado: Trabajador {trabajador_id}, Rubro {rubro_id}: {horas}h")
        
        conn.commit()
        
        # Verificar que se guardó
        c.execute('''
            SELECT horas FROM horas_asignadas 
            WHERE trabajador_id = ? AND rubro_id = ? AND año = ?
        ''', (trabajador_id, rubro_id, año))
        
        result = c.fetchone()
        conn.close()
        
        if result and result[0] == horas:
            print(f"✅ Verificado en DB: {horas}h")
            return True
        else:
            print(f"❌ ERROR: No se verificó el guardado")
            return False
            
    except Exception as e:
        print(f"❌ ERROR en asignar_horas: {e}")
        conn.close()
        return False

def obtener_horas_trabajador(trabajador_id, año=None):
    """Obtener horas asignadas de un trabajador"""
    if año is None:
        año = datetime.now().year
    
    conn = sqlite3.connect(str(DB_PATH))
    
    query = '''
        SELECT h.id, r.nombre as rubro, h.horas, h.año
        FROM horas_asignadas h
        JOIN rubros r ON h.rubro_id = r.id
        WHERE h.trabajador_id = ? AND h.año = ?
        ORDER BY r.nombre
    '''
    
    df = pd.read_sql_query(query, conn, params=[trabajador_id, año])
    conn.close()
    
    return df

def obtener_total_horas(trabajador_id, año=None):
    """Obtener total de horas de un trabajador"""
    if año is None:
        año = datetime.now().year
    
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    c.execute('''
        SELECT SUM(horas) FROM horas_asignadas
        WHERE trabajador_id = ? AND año = ?
    ''', (trabajador_id, año))
    
    result = c.fetchone()
    conn.close()
    
    return result[0] if result[0] else 0

def obtener_resumen_area(area, año=None):
    """Obtener resumen de horas por área"""
    if año is None:
        año = datetime.now().year
    
    conn = sqlite3.connect(str(DB_PATH))
    
    query = '''
        SELECT 
            t.nombre as trabajador,
            COALESCE(SUM(h.horas), 0) as total_horas,
            COUNT(DISTINCT h.rubro_id) as num_rubros,
            t.area as area_actual
        FROM trabajadores t
        LEFT JOIN horas_asignadas h ON t.id = h.trabajador_id AND h.año = ?
        WHERE (t.area = ? OR (t.area IS NULL AND ? = '')) 
          AND t.estatus = 'activo'
        GROUP BY t.id, t.nombre, t.area
        ORDER BY total_horas DESC
    '''
    
    df = pd.read_sql_query(query, conn, params=[año, area, area])
    conn.close()
    
    print(f"DEBUG obtener_resumen_area: área='{area}', año={año}, resultados={len(df)}")
    if len(df) > 0:
        print(df[['trabajador', 'total_horas', 'area_actual']])
    
    return df
    
    return df

def inicializar_datos_demo():
    """Inicializar con datos de demostración"""
    # Agregar rubros
    rubros_demo = [
        ("Desarrollo", "Horas de desarrollo de software"),
        ("Diseño", "Horas de diseño gráfico"),
        ("Consultoría", "Horas de consultoría"),
        ("Capacitación", "Horas de capacitación")
    ]
    
    for nombre, desc in rubros_demo:
        agregar_rubro(nombre, desc)
    
    # Agregar trabajadores
    trabajadores_demo = [
        ("Juan Pérez", "juan@empresa.com", "+51999111111", "Ingeniería"),
        ("María García", "maria@empresa.com", "+51999222222", "Ingeniería"),
        ("Carlos López", "carlos@empresa.com", "+51999333333", "Diseño"),
        ("Ana Martínez", "ana@empresa.com", "+51999444444", "Consultoría")
    ]
    
    for nombre, email, tel, area in trabajadores_demo:
        trabajador_id, error = agregar_trabajador(nombre, email, tel, area)
        
        if trabajador_id:
            # Asignar horas aleatorias
            rubros_df = obtener_rubros()
            for _, rubro in rubros_df.iterrows():
                import random
                horas = random.choice([0, 4, 8, 12, 16, 20])
                asignar_horas(trabajador_id, rubro['id'], horas)
