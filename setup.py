"""
Script de Setup Inicial
Configura el sistema por primera vez
"""

import os
import sys

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_step(number, text):
    print(f"\n[{number}] {text}")

def create_env_file():
    """Crear archivo .env si no existe"""
    if not os.path.exists('.env'):
        print("📝 Creando archivo .env...")
        with open('.env.example', 'r') as f:
            content = f.read()
        with open('.env', 'w') as f:
            f.write(content)
        print("✅ Archivo .env creado. Por favor configúralo con tus credenciales.")
        return False
    else:
        print("✅ Archivo .env ya existe")
        return True

def check_dependencies():
    """Verificar dependencias instaladas"""
    print("\n🔍 Verificando dependencias...")
    
    required = [
        'streamlit',
        'streamlit_authenticator',
        'pandas',
        'yaml',
        'apscheduler'
    ]
    
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - NO INSTALADO")
            missing.append(package)
    
    return missing

def initialize_databases():
    """Inicializar bases de datos"""
    print("\n💾 Inicializando bases de datos...")
    
    try:
        from database.audit import init_audit_db
        from database.notifications import init_notifications_db
        
        init_audit_db()
        print("  ✅ Base de datos de auditoría creada")
        
        init_notifications_db()
        print("  ✅ Base de datos de notificaciones creada")
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_email_config():
    """Probar configuración de email"""
    print("\n📧 Verificando configuración de email...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    gmail_user = os.getenv('GMAIL_USER')
    gmail_pass = os.getenv('GMAIL_APP_PASSWORD')
    
    if not gmail_user or not gmail_pass:
        print("  ⚠️  Email no configurado en .env")
        print("     Por favor configura GMAIL_USER y GMAIL_APP_PASSWORD")
        return False
    
    if gmail_pass == 'xxxx-xxxx-xxxx-xxxx':
        print("  ⚠️  Usando contraseña de ejemplo")
        print("     Por favor configura tu contraseña real de Gmail")
        return False
    
    print(f"  ✅ Email configurado: {gmail_user}")
    return True

def main():
    print_header("🚀 SETUP INICIAL - Sistema de Gestión de Horas")
    
    print("\nEste script te ayudará a configurar el sistema por primera vez.\n")
    
    # Paso 1: Crear .env
    print_step(1, "Configuración de variables de entorno")
    env_exists = create_env_file()
    
    if not env_exists:
        print("\n⚠️  IMPORTANTE: Edita el archivo .env con tus credenciales antes de continuar.")
        print("   Luego ejecuta este script nuevamente.\n")
        return
    
    # Paso 2: Verificar dependencias
    print_step(2, "Verificación de dependencias")
    missing = check_dependencies()
    
    if missing:
        print(f"\n❌ Faltan dependencias: {', '.join(missing)}")
        print("\n💡 Instálalas con:")
        print("   pip install -r requirements.txt\n")
        return
    
    # Paso 3: Inicializar bases de datos
    print_step(3, "Inicialización de bases de datos")
    if not initialize_databases():
        print("\n❌ Error inicializando bases de datos")
        return
    
    # Paso 4: Verificar email
    print_step(4, "Verificación de configuración de email")
    email_ok = test_email_config()
    
    # Resumen final
    print_header("✅ SETUP COMPLETADO")
    
    print("\n🎉 El sistema está listo para usar!\n")
    print("📋 Próximos pasos:")
    print("   1. Ejecuta: streamlit run app.py")
    print("   2. Abre: http://localhost:8501")
    print("   3. Login con:")
    print("      - Admin: admin / admin123")
    print("      - Supervisor: supervisor1 / super123")
    print("      - Trabajador: trabajador1 / trab123")
    
    if not email_ok:
        print("\n⚠️  Recuerda configurar tus credenciales de Gmail en .env")
        print("   para poder enviar emails.")
    
    print("\n📖 Lee el README.md para más información.\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelado por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error durante el setup: {e}")
        import traceback
        traceback.print_exc()
