"""
Script para probar actualización de trabajadores directamente
"""
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / 'trabajadores.db'

def test_update():
    """Probar actualización de trabajador"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    print("="*70)
    print("TEST DE ACTUALIZACIÓN")
    print("="*70)
    
    # Listar trabajadores
    print("\n1. Trabajadores actuales:")
    c.execute("SELECT id, nombre, email, area FROM trabajadores")
    trabajadores = c.fetchall()
    
    for t_id, nombre, email, area in trabajadores:
        print(f"  ID {t_id}: {nombre} | {email} | Área: {area if area else 'NULL'}")
    
    if not trabajadores:
        print("  ❌ No hay trabajadores")
        conn.close()
        return
    
    # Seleccionar primer trabajador
    trabajador_id = trabajadores[0][0]
    trabajador_nombre = trabajadores[0][1]
    
    print(f"\n2. Actualizando trabajador ID {trabajador_id} ({trabajador_nombre})...")
    
    # Actualizar área
    nueva_area = "Test Área " + datetime.now().strftime("%H:%M:%S")
    
    c.execute(
        "UPDATE trabajadores SET area = ?, fecha_modificacion = ? WHERE id = ?",
        (nueva_area, datetime.now().isoformat(), trabajador_id)
    )
    
    affected = c.rowcount
    print(f"  Filas afectadas: {affected}")
    
    conn.commit()
    
    # Verificar actualización
    print("\n3. Verificando actualización...")
    c.execute("SELECT id, nombre, area FROM trabajadores WHERE id = ?", (trabajador_id,))
    resultado = c.fetchone()
    
    if resultado:
        print(f"  ID: {resultado[0]}")
        print(f"  Nombre: {resultado[1]}")
        print(f"  Área: {resultado[2]}")
        
        if resultado[2] == nueva_area:
            print(f"\n✅ ACTUALIZACIÓN EXITOSA")
        else:
            print(f"\n❌ ERROR: Área esperada '{nueva_area}' pero obtenida '{resultado[2]}'")
    else:
        print(f"\n❌ ERROR: No se encontró trabajador con ID {trabajador_id}")
    
    conn.close()
    
    print("\n" + "="*70)
    print("FIN DEL TEST")
    print("="*70)

def verificar_integridad():
    """Verificar integridad de la base de datos"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    print("\n🔍 VERIFICACIÓN DE INTEGRIDAD")
    print("-"*70)
    
    try:
        c.execute("PRAGMA integrity_check")
        result = c.fetchone()[0]
        if result == "ok":
            print("✅ Base de datos OK")
        else:
            print(f"❌ Problemas: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Verificar que la tabla existe
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trabajadores'")
    if c.fetchone():
        print("✅ Tabla 'trabajadores' existe")
        
        # Ver estructura
        c.execute("PRAGMA table_info(trabajadores)")
        columnas = c.fetchall()
        print("\nColumnas:")
        for col in columnas:
            print(f"  - {col[1]} ({col[2]})")
    else:
        print("❌ Tabla 'trabajadores' NO existe")
    
    conn.close()

if __name__ == '__main__':
    verificar_integridad()
    print()
    test_update()
