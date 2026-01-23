"""
Script para actualizar contraseña de usuario en Firebase
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

def actualizar_password():
    """Actualizar contraseña de usuario en Firebase"""
    
    if not inicializar_firebase():
        return
    
    print(f"\n{'='*80}")
    print(f"ACTUALIZAR CONTRASEÑA EN FIREBASE")
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
        print(f"   Email verificado: {user.email_verified}")
        
        # Pedir nueva contraseña
        nueva_password = input("\nNueva contraseña (mínimo 6 caracteres): ").strip()
        if len(nueva_password) < 6:
            print("❌ La contraseña debe tener al menos 6 caracteres")
            return
        
        confirmar = input(f"\n⚠️  ¿Actualizar contraseña de {email}? (s/n): ").lower().strip()
        if confirmar != 's':
            print("❌ Operación cancelada")
            return
        
        # Actualizar contraseña
        auth.update_user(
            user.uid,
            password=nueva_password
        )
        
        print(f"\n{'='*80}")
        print(f"✅ CONTRASEÑA ACTUALIZADA EXITOSAMENTE")
        print(f"{'='*80}\n")
        print(f"Email: {email}")
        print(f"Nueva contraseña: {nueva_password}")
        print(f"\n✅ El usuario puede iniciar sesión con la nueva contraseña\n")
        
    except auth.UserNotFoundError:
        print(f"\n❌ Usuario no encontrado en Firebase: {email}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    actualizar_password()
