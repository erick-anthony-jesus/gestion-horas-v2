"""
Script para migrar de SQLite a JSON
"""
import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / 'trabajadores.db'
JSON_DIR = Path(__file__).parent

def migrar_sqlite_a_json():
    """Migrar datos de SQLite a archivos JSON"""
    
    if not DB_PATH.exists():
        print("❌ No existe trabajadores.db")
        return
    
    conn = sqlite3.connect(str(DB_PATH))
    
    print("="*70)
    print("MIGRACIÓN: SQLite → JSON")
    print("="*70)
    
    # ========== TRABAJADORES ==========
    print("\n1. Migrando trabajadores...")
    c = conn.cursor()
    c.execute("SELECT id, nombre, email, telefono, area, foto, estatus FROM trabajadores")
    rows = c.fetchall()
    
    trabajadores_data = {
        "trabajadores": [],
        "next_id": 1
    }
    
    for row in rows:
        trabajador = {
            "id": row[0],
            "nombre": row[1],
            "email": row[2],
            "telefono": row[3] if row[3] else "",
            "area": row[4] if row[4] else "",
            "foto": row[5],
            "estatus": row[6] if row[6] else "activo"
        }
        trabajadores_data["trabajadores"].append(trabajador)
        
        if row[0] >= trabajadores_data["next_id"]:
            trabajadores_data["next_id"] = row[0] + 1
    
    # Guardar
    trabajadores_file = JSON_DIR / 'trabajadores.json'
    trabajadores_file.write_text(
        json.dumps(trabajadores_data, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )
    print(f"   ✅ {len(trabajadores_data['trabajadores'])} trabajadores → {trabajadores_file}")
    
    # ========== RUBROS ==========
    print("\n2. Migrando rubros...")
    c.execute("SELECT id, nombre, descripcion, activo FROM rubros")
    rows = c.fetchall()
    
    rubros_data = {
        "rubros": [],
        "next_id": 1
    }
    
    for row in rows:
        rubro = {
            "id": row[0],
            "nombre": row[1],
            "descripcion": row[2] if row[2] else "",
            "activo": bool(row[3]) if row[3] is not None else True
        }
        rubros_data["rubros"].append(rubro)
        
        if row[0] >= rubros_data["next_id"]:
            rubros_data["next_id"] = row[0] + 1
    
    # Guardar
    rubros_file = JSON_DIR / 'rubros.json'
    rubros_file.write_text(
        json.dumps(rubros_data, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )
    print(f"   ✅ {len(rubros_data['rubros'])} rubros → {rubros_file}")
    
    # ========== HORAS ==========
    print("\n3. Migrando horas asignadas...")
    c.execute("SELECT id, trabajador_id, rubro_id, horas, año FROM horas_asignadas")
    rows = c.fetchall()
    
    horas_data = {
        "horas_asignadas": [],
        "next_id": 1
    }
    
    for row in rows:
        hora = {
            "id": row[0],
            "trabajador_id": row[1],
            "rubro_id": row[2],
            "horas": float(row[3]),
            "año": row[4]
        }
        horas_data["horas_asignadas"].append(hora)
        
        if row[0] >= horas_data["next_id"]:
            horas_data["next_id"] = row[0] + 1
    
    # Guardar
    horas_file = JSON_DIR / 'horas_asignadas.json'
    horas_file.write_text(
        json.dumps(horas_data, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )
    print(f"   ✅ {len(horas_data['horas_asignadas'])} horas → {horas_file}")
    
    conn.close()
    
    print("\n" + "="*70)
    print("✅ MIGRACIÓN COMPLETADA")
    print("="*70)
    print("\nArchivos creados:")
    print(f"  - {trabajadores_file}")
    print(f"  - {rubros_file}")
    print(f"  - {horas_file}")
    print("\n💡 Puedes abrir estos archivos con cualquier editor de texto")
    print("   para ver y editar los datos directamente.")

if __name__ == '__main__':
    migrar_sqlite_a_json()
