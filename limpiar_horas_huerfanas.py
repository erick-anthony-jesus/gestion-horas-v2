"""
Script para limpiar horas huérfanas (sin trabajador o rubro válido)
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / 'trabajadores.db'

def limpiar_horas_huerfanas():
    """Eliminar horas asignadas que no tienen trabajador o rubro válido"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    print("="*70)
    print("LIMPIEZA DE HORAS HUÉRFANAS")
    print("="*70)
    
    # Encontrar horas sin trabajador válido
    print("\n1. Buscando horas sin trabajador válido...")
    c.execute('''
        SELECT h.id, h.trabajador_id, h.rubro_id, h.horas
        FROM horas_asignadas h
        WHERE NOT EXISTS (SELECT 1 FROM trabajadores t WHERE t.id = h.trabajador_id)
    ''')
    
    sin_trabajador = c.fetchall()
    
    if sin_trabajador:
        print(f"   ⚠️ Encontradas {len(sin_trabajador)} horas sin trabajador:")
        for hora_id, trab_id, rubro_id, horas in sin_trabajador:
            print(f"      ID {hora_id}: trabajador_id={trab_id}, rubro_id={rubro_id}, horas={horas}")
    else:
        print("   ✅ No hay horas sin trabajador válido")
    
    # Encontrar horas sin rubro válido
    print("\n2. Buscando horas sin rubro válido...")
    c.execute('''
        SELECT h.id, h.trabajador_id, h.rubro_id, h.horas
        FROM horas_asignadas h
        WHERE NOT EXISTS (SELECT 1 FROM rubros r WHERE r.id = h.rubro_id)
    ''')
    
    sin_rubro = c.fetchall()
    
    if sin_rubro:
        print(f"   ⚠️ Encontradas {len(sin_rubro)} horas sin rubro:")
        for hora_id, trab_id, rubro_id, horas in sin_rubro:
            print(f"      ID {hora_id}: trabajador_id={trab_id}, rubro_id={rubro_id}, horas={horas}")
    else:
        print("   ✅ No hay horas sin rubro válido")
    
    total_huerfanas = len(sin_trabajador) + len(sin_rubro)
    
    if total_huerfanas > 0:
        print(f"\n⚠️ Total de horas huérfanas: {total_huerfanas}")
        print("\n¿Deseas eliminarlas? (s/n): ", end='')
        respuesta = input().lower()
        
        if respuesta == 's':
            # Eliminar horas sin trabajador
            if sin_trabajador:
                ids = [str(h[0]) for h in sin_trabajador]
                c.execute(f"DELETE FROM horas_asignadas WHERE id IN ({','.join(ids)})")
                print(f"   ✅ Eliminadas {len(sin_trabajador)} horas sin trabajador")
            
            # Eliminar horas sin rubro
            if sin_rubro:
                ids = [str(h[0]) for h in sin_rubro]
                c.execute(f"DELETE FROM horas_asignadas WHERE id IN ({','.join(ids)})")
                print(f"   ✅ Eliminadas {len(sin_rubro)} horas sin rubro")
            
            conn.commit()
            print(f"\n✅ Se eliminaron {total_huerfanas} horas huérfanas")
        else:
            print("\n❌ Cancelado. No se eliminó nada")
    else:
        print("\n✅ No hay horas huérfanas. Base de datos limpia!")
    
    conn.close()
    
    print("\n" + "="*70)
    print("FIN DE LA LIMPIEZA")
    print("="*70)

def verificar_integridad():
    """Verificar integridad después de limpiar"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    c.execute('''
        SELECT COUNT(*) FROM horas_asignadas h
        WHERE NOT EXISTS (SELECT 1 FROM trabajadores t WHERE t.id = h.trabajador_id)
           OR NOT EXISTS (SELECT 1 FROM rubros r WHERE r.id = h.rubro_id)
    ''')
    
    huerfanas = c.fetchone()[0]
    conn.close()
    
    if huerfanas == 0:
        print("\n✅ VERIFICACIÓN: Base de datos íntegra")
    else:
        print(f"\n⚠️ VERIFICACIÓN: Aún hay {huerfanas} horas huérfanas")

if __name__ == '__main__':
    limpiar_horas_huerfanas()
    verificar_integridad()
