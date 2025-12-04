"""
Script para actualizar el área de un trabajador
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / 'trabajadores.db'

def actualizar_area_trabajador(nombre_trabajador, nueva_area):
    """Actualizar área de un trabajador por nombre"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    # Buscar trabajador
    c.execute("SELECT id, nombre, area FROM trabajadores WHERE nombre = ?", (nombre_trabajador,))
    trabajador = c.fetchone()
    
    if not trabajador:
        print(f"❌ No se encontró trabajador: {nombre_trabajador}")
        conn.close()
        return False
    
    trabajador_id, nombre, area_actual = trabajador
    print(f"Trabajador encontrado:")
    print(f"  ID: {trabajador_id}")
    print(f"  Nombre: {nombre}")
    print(f"  Área actual: {area_actual if area_actual else 'NULL'}")
    print(f"  Nueva área: {nueva_area}")
    
    # Actualizar
    c.execute("UPDATE trabajadores SET area = ? WHERE id = ?", (nueva_area, trabajador_id))
    conn.commit()
    
    # Verificar
    c.execute("SELECT area FROM trabajadores WHERE id = ?", (trabajador_id,))
    area_verificada = c.fetchone()[0]
    
    conn.close()
    
    if area_verificada == nueva_area:
        print(f"✅ Área actualizada correctamente a: {nueva_area}")
        return True
    else:
        print(f"❌ Error: área es {area_verificada}")
        return False

def listar_trabajadores():
    """Listar todos los trabajadores y sus áreas"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    c.execute("SELECT id, nombre, area, email FROM trabajadores ORDER BY nombre")
    trabajadores = c.fetchall()
    
    conn.close()
    
    print("\n" + "="*70)
    print("TRABAJADORES Y SUS ÁREAS")
    print("="*70)
    print(f"{'ID':<5} {'Nombre':<20} {'Área':<20} {'Email':<25}")
    print("-"*70)
    
    for t_id, nombre, area, email in trabajadores:
        area_str = area if area else "SIN ÁREA"
        print(f"{t_id:<5} {nombre:<20} {area_str:<20} {email:<25}")
    
    return trabajadores

if __name__ == '__main__':
    print("🔍 Listado actual de trabajadores:")
    trabajadores = listar_trabajadores()
    
    print("\n" + "="*70)
    print("ACTUALIZAR ÁREA")
    print("="*70)
    
    # Ejemplo: Actualizar patricio a "desarrollo web"
    actualizar_area_trabajador("patricio", "desarrollo web")
    
    print("\n🔍 Listado después de actualizar:")
    listar_trabajadores()
