"""
Script para verificar y corregir el uso de JSON vs SQLite
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

def verificar_imports():
    """Verificar qué sistema de base de datos se está usando"""
    print("="*70)
    print("VERIFICACIÓN DE IMPORTS")
    print("="*70)
    
    # Verificar app.py
    app_py = BASE_DIR / 'app.py'
    if app_py.exists():
        content = app_py.read_text(encoding='utf-8')
        
        print("\n📄 app.py:")
        if 'from database.workers_json import' in content:
            print("   ✅ Usa workers_json (JSON)")
        elif 'from database.workers import' in content:
            print("   ❌ Usa workers (SQLite) - NECESITA CORRECCIÓN")
        else:
            print("   ⚠️ No se encontró import de workers")
        
        if 'init_json_db' in content:
            print("   ✅ Llama a init_json_db()")
        elif 'init_workers_db' in content:
            print("   ❌ Llama a init_workers_db() - NECESITA CORRECCIÓN")
    else:
        print("\n❌ No se encontró app.py")
    
    # Verificar workers_cards.py
    workers_cards = BASE_DIR / 'pages' / 'workers_cards.py'
    if workers_cards.exists():
        content = workers_cards.read_text(encoding='utf-8')
        
        print("\n📄 pages/workers_cards.py:")
        if 'from database.workers_json import' in content:
            print("   ✅ Usa workers_json (JSON)")
        elif 'from database.workers import' in content:
            print("   ❌ Usa workers (SQLite) - NECESITA CORRECCIÓN")
        else:
            print("   ⚠️ No se encontró import de workers")
    else:
        print("\n❌ No se encontró pages/workers_cards.py")
    
    # Verificar dashboard.py
    dashboard = BASE_DIR / 'pages' / 'dashboard.py'
    if dashboard.exists():
        content = dashboard.read_text(encoding='utf-8')
        
        print("\n📄 pages/dashboard.py:")
        if 'from database.workers_json import' in content:
            print("   ✅ Usa workers_json (JSON)")
        elif 'from database.workers import' in content:
            print("   ❌ Usa workers (SQLite) - NECESITA CORRECCIÓN")
        else:
            print("   ⚠️ No se encontró import de workers")
    else:
        print("\n❌ No se encontró pages/dashboard.py")
    
    # Verificar archivos JSON
    print("\n📁 ARCHIVOS DE DATOS:")
    
    json_files = ['trabajadores.json', 'rubros.json', 'horas_asignadas.json']
    for file in json_files:
        file_path = BASE_DIR / file
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"   ✅ {file} ({size} bytes)")
        else:
            print(f"   ❌ {file} no existe")
    
    db_file = BASE_DIR / 'trabajadores.db'
    if db_file.exists():
        size = db_file.stat().st_size
        print(f"   ⚠️ trabajadores.db ({size} bytes) - SQLite detectado")
    else:
        print(f"   ✅ trabajadores.db no existe (correcto para JSON)")
    
    print("\n" + "="*70)

def corregir_app_py():
    """Corregir app.py para usar JSON"""
    app_py = BASE_DIR / 'app.py'
    
    if not app_py.exists():
        print("❌ No se encontró app.py")
        return False
    
    print("\n🔧 Corrigiendo app.py...")
    
    content = app_py.read_text(encoding='utf-8')
    
    # Reemplazar import
    content = content.replace(
        'from database.workers import',
        'from database.workers_json import'
    )
    
    # Reemplazar init_workers_db con init_json_db
    content = content.replace('init_workers_db', 'init_json_db')
    
    # Reemplazar inicializar_datos_demo
    content = content.replace('inicializar_datos_demo', 'init_json_db')
    
    # Remover verificación de trabajadores vacíos
    if 'if len(obtener_trabajadores()) == 0:' in content:
        lines = content.split('\n')
        new_lines = []
        skip_next = False
        
        for line in lines:
            if 'if len(obtener_trabajadores()) == 0:' in line:
                skip_next = True
                continue
            elif skip_next and 'init' in line:
                skip_next = False
                continue
            else:
                new_lines.append(line)
        
        content = '\n'.join(new_lines)
    
    # Guardar
    app_py.write_text(content, encoding='utf-8')
    print("   ✅ app.py corregido")
    return True

def corregir_workers_cards():
    """Corregir workers_cards.py para usar JSON"""
    workers_cards = BASE_DIR / 'pages' / 'workers_cards.py'
    
    if not workers_cards.exists():
        print("❌ No se encontró pages/workers_cards.py")
        return False
    
    print("\n🔧 Corrigiendo pages/workers_cards.py...")
    
    content = workers_cards.read_text(encoding='utf-8')
    
    # Reemplazar import
    content = content.replace(
        'from database.workers import *',
        'from database.workers_json import *'
    )
    
    # Guardar
    workers_cards.write_text(content, encoding='utf-8')
    print("   ✅ pages/workers_cards.py corregido")
    return True

def corregir_dashboard():
    """Corregir dashboard.py para usar JSON"""
    dashboard = BASE_DIR / 'pages' / 'dashboard.py'
    
    if not dashboard.exists():
        print("❌ No se encontró pages/dashboard.py")
        return False
    
    print("\n🔧 Corrigiendo pages/dashboard.py...")
    
    content = dashboard.read_text(encoding='utf-8')
    
    # Reemplazar import
    content = content.replace(
        'from database.workers import',
        'from database.workers_json import'
    )
    
    # Guardar
    dashboard.write_text(content, encoding='utf-8')
    print("   ✅ pages/dashboard.py corregido")
    return True

def limpiar_sqlite():
    """Eliminar archivos SQLite si existen"""
    print("\n🧹 Limpiando archivos SQLite...")
    
    db_files = ['trabajadores.db', 'auditoria.db', 'notifications.db']
    
    for db_file in db_files:
        file_path = BASE_DIR / db_file
        if file_path.exists():
            # No eliminar auditoria.db y notifications.db (aún los usamos)
            if db_file == 'trabajadores.db':
                # Hacer backup antes de eliminar
                backup = BASE_DIR / 'trabajadores.db.backup'
                import shutil
                shutil.copy(file_path, backup)
                print(f"   💾 Backup: trabajadores.db.backup")
                
                file_path.unlink()
                print(f"   ✅ Eliminado: {db_file}")
            else:
                print(f"   ℹ️ Mantenido: {db_file} (usado para logs)")

def limpiar_json_malos():
    """Eliminar archivos JSON con codificación incorrecta"""
    print("\n🧹 Limpiando archivos JSON con codificación mala...")
    
    json_files = ['trabajadores.json', 'rubros.json', 'horas_asignadas.json']
    
    for json_file in json_files:
        file_path = BASE_DIR / json_file
        if file_path.exists():
            try:
                # Intentar leer con UTF-8
                content = file_path.read_text(encoding='utf-8')
                print(f"   ✅ {json_file} tiene codificación correcta")
            except UnicodeDecodeError:
                print(f"   ❌ {json_file} tiene codificación incorrecta")
                
                # Hacer backup
                backup = BASE_DIR / f"{json_file}.backup"
                import shutil
                shutil.copy(file_path, backup)
                print(f"      💾 Backup: {json_file}.backup")
                
                # Eliminar
                file_path.unlink()
                print(f"      🗑️ Eliminado: {json_file}")

def main():
    """Ejecutar verificación y corrección"""
    print("\n🚀 INICIANDO VERIFICACIÓN Y CORRECCIÓN\n")
    
    # Paso 1: Verificar estado actual
    verificar_imports()
    
    # Preguntar si desea corregir
    print("\n" + "="*70)
    print("¿Deseas CORREGIR automáticamente? (s/n): ", end='')
    respuesta = input().lower()
    
    if respuesta != 's':
        print("\n❌ Corrección cancelada")
        return
    
    # Paso 2: Hacer correcciones
    print("\n" + "="*70)
    print("APLICANDO CORRECCIONES")
    print("="*70)
    
    corregir_app_py()
    corregir_workers_cards()
    corregir_dashboard()
    
    # Paso 3: Limpiar archivos viejos
    print("\n" + "="*70)
    print("LIMPIEZA DE ARCHIVOS")
    print("="*70)
    
    limpiar_json_malos()
    limpiar_sqlite()
    
    # Paso 4: Verificar de nuevo
    print("\n" + "="*70)
    print("VERIFICACIÓN FINAL")
    print("="*70)
    
    verificar_imports()
    
    # Paso 5: Instrucciones finales
    print("\n" + "="*70)
    print("✅ CORRECCIÓN COMPLETADA")
    print("="*70)
    print("\nPasos siguientes:")
    print("1. streamlit run app.py")
    print("2. Los archivos JSON se crearán automáticamente")
    print("3. Crear trabajadores de prueba")
    print("4. Verificar que los datos persisten")
    print("\n💡 Tip: Usa 'python verificar_db.py' para ver el estado de los datos")

if __name__ == '__main__':
    main()
