"""
Base de datos JSON simple - Reemplazo de SQLite
"""
import json
from pathlib import Path
from datetime import datetime

# Rutas de archivos JSON
BASE_DIR = Path(__file__).parent
TRABAJADORES_FILE = BASE_DIR / 'trabajadores.json'
RUBROS_FILE = BASE_DIR / 'rubros.json'
HORAS_FILE = BASE_DIR / 'horas_asignadas.json'

def init_json_db():
    """Inicializar archivos JSON si no existen"""
    
    # Trabajadores
    if not TRABAJADORES_FILE.exists():
        data = {
            "trabajadores": [
                {
                    "id": 1,
                    "nombre": "Juan Pérez",
                    "email": "juan@empresa.com",
                    "telefono": "+51999111222",
                    "area": "Ingeniería",
                    "foto": None,
                    "estatus": "activo"
                },
                {
                    "id": 2,
                    "nombre": "María García",
                    "email": "maria@empresa.com",
                    "telefono": "+51999333444",
                    "area": "Diseño",
                    "foto": None,
                    "estatus": "activo"
                }
            ],
            "next_id": 3
        }
        TRABAJADORES_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        print(f"✅ Creado: {TRABAJADORES_FILE}")
    
    # Rubros
    if not RUBROS_FILE.exists():
        data = {
            "rubros": [
                {"id": 1, "nombre": "Desarrollo", "descripcion": "Desarrollo de software", "activo": True},
                {"id": 2, "nombre": "Diseño", "descripcion": "Diseño gráfico", "activo": True},
                {"id": 3, "nombre": "Consultoría", "descripcion": "Consultoría técnica", "activo": True},
                {"id": 4, "nombre": "Capacitación", "descripcion": "Capacitaciones", "activo": True}
            ],
            "next_id": 5
        }
        RUBROS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        print(f"✅ Creado: {RUBROS_FILE}")
    
    # Horas
    if not HORAS_FILE.exists():
        data = {
            "horas_asignadas": [
                {"id": 1, "trabajador_id": 1, "rubro_id": 1, "horas": 20.0, "año": 2025},
                {"id": 2, "trabajador_id": 1, "rubro_id": 2, "horas": 10.0, "año": 2025},
                {"id": 3, "trabajador_id": 2, "rubro_id": 1, "horas": 15.0, "año": 2025},
                {"id": 4, "trabajador_id": 2, "rubro_id": 3, "horas": 5.0, "año": 2025}
            ],
            "next_id": 5
        }
        HORAS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        print(f"✅ Creado: {HORAS_FILE}")

# ==================== TRABAJADORES ====================

def leer_trabajadores():
    """Leer todos los trabajadores del JSON"""
    if not TRABAJADORES_FILE.exists():
        init_json_db()
    
    try:
        # Intentar UTF-8
        data = json.loads(TRABAJADORES_FILE.read_text(encoding='utf-8'))
    except UnicodeDecodeError:
        # Si falla, intentar con latin-1 (Windows)
        data = json.loads(TRABAJADORES_FILE.read_text(encoding='latin-1'))
    
    return data

def guardar_trabajadores(data):
    """Guardar trabajadores al JSON"""
    TRABAJADORES_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"✅ Guardado en: {TRABAJADORES_FILE}")

def obtener_trabajadores(area=None, estatus='activo'):
    """Obtener trabajadores (con filtros opcionales)"""
    data = leer_trabajadores()
    trabajadores = data['trabajadores']
    
    # Filtrar por estatus
    trabajadores = [t for t in trabajadores if t['estatus'] == estatus]
    
    # Filtrar por área
    if area:
        trabajadores = [t for t in trabajadores if t.get('area') == area]
    
    # Convertir a DataFrame para compatibilidad
    import pandas as pd
    return pd.DataFrame(trabajadores)

def agregar_trabajador(nombre, email, telefono="", area="", foto=None):
    """Agregar nuevo trabajador"""
    data = leer_trabajadores()
    
    # Verificar email único
    if any(t['email'] == email for t in data['trabajadores']):
        return None, "El email ya existe"
    
    nuevo_trabajador = {
        "id": data['next_id'],
        "nombre": nombre,
        "email": email,
        "telefono": telefono,
        "area": area,
        "foto": foto,
        "estatus": "activo"
    }
    
    data['trabajadores'].append(nuevo_trabajador)
    data['next_id'] += 1
    
    guardar_trabajadores(data)
    
    print(f"✅ Trabajador creado: ID {nuevo_trabajador['id']}, {nombre}, {area}")
    return nuevo_trabajador['id'], None

def actualizar_trabajador(trabajador_id, **kwargs):
    """Actualizar datos de trabajador"""
    data = leer_trabajadores()
    
    # Buscar trabajador
    trabajador = None
    trabajador_index = -1
    for i, t in enumerate(data['trabajadores']):
        if t['id'] == trabajador_id:
            trabajador = t
            trabajador_index = i
            break
    
    if not trabajador:
        print(f"❌ Trabajador {trabajador_id} no encontrado")
        print(f"   IDs disponibles: {[t['id'] for t in data['trabajadores']]}")
        return False
    
    # Actualizar campos
    print(f"🔍 Actualizando trabajador {trabajador_id} (índice {trabajador_index}):")
    for key, value in kwargs.items():
        if key in ['nombre', 'email', 'telefono', 'area', 'foto', 'estatus']:
            old_value = trabajador.get(key, 'None')
            trabajador[key] = value
            print(f"  - {key}: {old_value if key != 'foto' else '[foto]'} → {value if key != 'foto' else '[foto base64]'}")
    
    # Guardar
    data['trabajadores'][trabajador_index] = trabajador
    guardar_trabajadores(data)
    print(f"✅ Trabajador {trabajador_id} actualizado")
    return True

def eliminar_trabajador(trabajador_id, hard_delete=False):
    """Eliminar trabajador"""
    if hard_delete:
        # Eliminar completamente
        data = leer_trabajadores()
        data['trabajadores'] = [t for t in data['trabajadores'] if t['id'] != trabajador_id]
        guardar_trabajadores(data)
        
        # También eliminar sus horas
        horas_data = leer_horas()
        horas_data['horas_asignadas'] = [h for h in horas_data['horas_asignadas'] if h['trabajador_id'] != trabajador_id]
        guardar_horas(horas_data)
        
        print(f"✅ Trabajador {trabajador_id} eliminado completamente")
        return True
    else:
        # Soft delete
        return actualizar_trabajador(trabajador_id, estatus='inactivo')

# ==================== RUBROS ====================

def leer_rubros():
    if not RUBROS_FILE.exists():
        init_json_db()
    
    try:
        data = json.loads(RUBROS_FILE.read_text(encoding='utf-8'))
    except UnicodeDecodeError:
        data = json.loads(RUBROS_FILE.read_text(encoding='latin-1'))
    
    return data

def guardar_rubros(data):
    """Guardar rubros al JSON"""
    RUBROS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

def obtener_rubros(activos_solo=True):
    """Obtener rubros"""
    data = leer_rubros()
    rubros = data['rubros']
    
    if activos_solo:
        rubros = [r for r in rubros if r['activo']]
    
    # Convertir a DataFrame para compatibilidad
    import pandas as pd
    return pd.DataFrame(rubros)

def agregar_rubro(nombre, descripcion=""):
    """Agregar nuevo rubro"""
    data = leer_rubros()
    
    # Verificar nombre único
    if any(r['nombre'] == nombre for r in data['rubros']):
        return None, "El rubro ya existe"
    
    nuevo_rubro = {
        "id": data['next_id'],
        "nombre": nombre,
        "descripcion": descripcion,
        "activo": True
    }
    
    data['rubros'].append(nuevo_rubro)
    data['next_id'] += 1
    
    guardar_rubros(data)
    
    print(f"✅ Rubro creado: ID {nuevo_rubro['id']}, {nombre}")
    return nuevo_rubro['id'], None

def actualizar_rubro(rubro_id, **kwargs):
    """Actualizar datos de rubro"""
    data = leer_rubros()
    
    # Buscar rubro
    rubro = None
    for r in data['rubros']:
        if r['id'] == rubro_id:
            rubro = r
            break
    
    if not rubro:
        print(f"❌ Rubro {rubro_id} no encontrado")
        return False
    
    # Actualizar campos
    print(f"🔍 Actualizando rubro {rubro_id}:")
    for key, value in kwargs.items():
        if key in rubro:
            print(f"  - {key}: {rubro[key]} → {value}")
            rubro[key] = value
    
    guardar_rubros(data)
    print(f"✅ Rubro {rubro_id} actualizado")
    return True

def eliminar_rubro(rubro_id):
    """Eliminar rubro (marca como inactivo)"""
    return actualizar_rubro(rubro_id, activo=False)

# ==================== HORAS ====================

def leer_horas():
    """Leer todas las horas del JSON"""
    if not HORAS_FILE.exists():
        init_json_db()
    
    try:
        data = json.loads(HORAS_FILE.read_text(encoding='utf-8'))
    except UnicodeDecodeError:
        data = json.loads(HORAS_FILE.read_text(encoding='latin-1'))
    
    return data

def guardar_horas(data):
    """Guardar horas al JSON"""
    HORAS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"✅ Horas guardadas en: {HORAS_FILE}")

def asignar_horas(trabajador_id, rubro_id, horas, año=None):
    """Asignar horas a un trabajador"""
    if año is None:
        año = datetime.now().year
    
    # Convertir a tipos nativos de Python
    trabajador_id = int(trabajador_id)
    rubro_id = int(rubro_id)
    horas = float(horas)
    año = int(año)
    
    data = leer_horas()
    
    # Buscar si ya existe
    hora_existente = None
    for h in data['horas_asignadas']:
        if h['trabajador_id'] == trabajador_id and h['rubro_id'] == rubro_id and h['año'] == año:
            hora_existente = h
            break
    
    if hora_existente:
        # Actualizar
        print(f"🔍 Actualizando: Trabajador {trabajador_id}, Rubro {rubro_id}: {hora_existente['horas']}h → {horas}h")
        hora_existente['horas'] = horas
    else:
        # Crear nuevo
        nueva_hora = {
            "id": data['next_id'],
            "trabajador_id": trabajador_id,
            "rubro_id": rubro_id,
            "horas": horas,
            "año": año
        }
        data['horas_asignadas'].append(nueva_hora)
        data['next_id'] += 1
        print(f"🔍 Insertando: Trabajador {trabajador_id}, Rubro {rubro_id}: {horas}h")
    
    guardar_horas(data)
    print(f"✅ Horas guardadas: {horas}h")
    return True

def obtener_horas_trabajador(trabajador_id, año=None):
    """Obtener horas de un trabajador"""
    if año is None:
        año = datetime.now().year
    
    data_horas = leer_horas()
    data_rubros = leer_rubros()
    
    # Filtrar horas del trabajador
    horas = [h for h in data_horas['horas_asignadas'] 
             if h['trabajador_id'] == trabajador_id and h['año'] == año]
    
    # Enriquecer con nombre del rubro
    resultado = []
    for h in horas:
        rubro = next((r for r in data_rubros['rubros'] if r['id'] == h['rubro_id']), None)
        if rubro:
            resultado.append({
                'id': h['id'],
                'rubro': rubro['nombre'],
                'horas': h['horas'],
                'año': h['año']
            })
    
    # Convertir a DataFrame para compatibilidad
    import pandas as pd
    return pd.DataFrame(resultado)

def obtener_total_horas(trabajador_id, año=None):
    """Obtener total de horas de un trabajador"""
    horas_df = obtener_horas_trabajador(trabajador_id, año)
    if len(horas_df) == 0:
        return 0
    return horas_df['horas'].sum()

def obtener_resumen_area(area, año=None):
    """Obtener resumen de horas por área"""
    if año is None:
        año = datetime.now().year
    
    trabajadores_df = obtener_trabajadores(area=area)
    
    resultado = []
    for _, t in trabajadores_df.iterrows():
        total = obtener_total_horas(t['id'], año)
        horas_df = obtener_horas_trabajador(t['id'], año)
        
        resultado.append({
            'trabajador': t['nombre'],
            'total_horas': total,
            'num_rubros': len(horas_df),
            'area_actual': t['area']
        })
    
    # Convertir a DataFrame para compatibilidad
    import pandas as pd
    return pd.DataFrame(resultado)

# Inicializar al importar
if __name__ != '__main__':
    init_json_db()
