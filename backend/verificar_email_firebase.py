"""
Script para marcar email como verificado en Firebase
"""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

# Importar Firebase Admin
try:
    import firebase_admin
    from firebase_admin import credentials, auth
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("❌ firebase-admin no está instalado")
    sys.exit(1)

def inicializar_firebase():
    """Inicializar Firebase Admin SDK"""
    try:
        firebase_admin.get_app()
        return True
    except ValueError:
        pass
    
    try:
        service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")
        if service_account_json:
            import json
            creds_dict = json.loads(service_account_json)
            cred = credentials.Certificate(creds_dict)
            firebase_admin.initialize_app(cred)
            return True
        
        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            return True
        
        cred_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
        if cred_json:
            import json
            cred_dict = json.loads(cred_json)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            return True
        
        print("❌ No se encontraron credenciales de Firebase")
        return False
        
    except Exception as e:
        print(f"❌ Error al inicializar Firebase: {e}")
        return False

def verificar_email():
    """Marcar email como verificado en Firebase"""
    
    if not inicializar_firebase():
        return
    
    print(f"\n{'='*80}")
    print(f"VERIFICAR EMAIL EN FIREBASE")
    print(f"{'='*80}\n")
    
    email = input("Email del usuario: ").strip().lower()
    if not email or '@' not in email:
        print("❌ Email inválido")
        return
    
    try:
        # Buscar usuario por email
        user = auth.get_user_by_email(email)
        print(f"\n✅ Usuario encontrado en Firebase:")
        print(f"   UID: {user.uid}")
        print(f"   Email: {user.email}")
        print(f"   Display Name: {user.display_name or 'N/A'}")
        print(f"   Email verificado: {'✅ SÍ' if user.email_verified else '❌ NO'}")
        
        if user.email_verified:
            print(f"\n✅ El email ya está verificado")
            return
        
        confirmar = input(f"\n⚠️  ¿Marcar email como verificado? (s/n): ").lower().strip()
        if confirmar != 's':
            print("❌ Operación cancelada")
            return
        
        # Marcar email como verificado
        auth.update_user(
            user.uid,
            email_verified=True
        )
        
        print(f"\n{'='*80}")
        print(f"✅ EMAIL VERIFICADO EXITOSAMENTE")
        print(f"{'='*80}\n")
        print(f"Email: {email}")
        print(f"Estado: ✅ Verificado")
        print(f"\n✅ El usuario puede iniciar sesión sin verificar el email\n")
        
    except auth.UserNotFoundError:
        print(f"\n❌ Usuario no encontrado en Firebase: {email}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_email()
