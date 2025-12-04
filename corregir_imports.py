"""
Script para corregir TODOS los imports de workers a workers_json
"""
import os
from pathlib import Path

def corregir_archivo(filepath):
    """Corregir imports en un archivo"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Buscar si tiene import de workers
        if 'from database.workers import' in contenido:
            print(f"📝 Corrigiendo: {filepath}")
            
            # Reemplazar
            contenido_nuevo = contenido.replace(
                'from database.workers import',
                'from database.workers_json import'
            )
            
            # Guardar
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(contenido_nuevo)
            
            print(f"   ✅ Corregido")
            return True
        
        return False
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Buscar y corregir todos los archivos .py"""
    print("🔍 Buscando archivos con imports incorrectos...\n")
    
    # Archivos a revisar
    archivos = [
        'app.py',
        'pages/workers_cards.py',
        'pages/dashboard.py',
        'pages/rubros.py',
        'pages/google_sheets.py',
        'pages/workers.py',
        'pages/workers_improved.py',
        'pages/profile.py',
        'pages/reports.py'
    ]
    
    corregidos = 0
    
    for archivo in archivos:
        if os.path.exists(archivo):
            if corregir_archivo(archivo):
                corregidos += 1
        else:
            print(f"⚠️  No existe: {archivo}")
    
    print(f"\n✅ Total corregidos: {corregidos} archivos")
    print("\n🚀 Ahora ejecuta: streamlit run app.py")

if __name__ == '__main__':
    main()
