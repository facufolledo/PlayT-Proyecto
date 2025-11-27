"""
Manejador de autenticación con Firebase
Valida tokens de Firebase y obtiene información del usuario
"""
from typing import Optional, Dict
import os
from dotenv import load_dotenv

load_dotenv()

# Intentar importar firebase_admin (solo si está instalado)
try:
    import firebase_admin
    from firebase_admin import credentials, auth
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("⚠️  firebase-admin no está instalado. Ejecuta: pip install firebase-admin")

class FirebaseHandler:
    """Manejador para validar tokens de Firebase"""
    
    _initialized = False
    
    @classmethod
    def initialize(cls):
        """Inicializar Firebase Admin SDK"""
        if not FIREBASE_AVAILABLE:
            return False
        
        if cls._initialized:
            return True
        
        try:
            # Opción 1: Usar FIREBASE_SERVICE_ACCOUNT (Railway)
            service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")
            if service_account_json:
                import json
                creds_dict = json.loads(service_account_json)
                cred = credentials.Certificate(creds_dict)
                firebase_admin.initialize_app(cred)
                cls._initialized = True
                print("🔥 Firebase Admin inicializado correctamente")
                return True
            
            # Opción 2: Usar archivo de credenciales JSON
            cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                cls._initialized = True
                print("✅ Firebase Admin inicializado con archivo de credenciales")
                return True
            
            # Opción 3: Usar FIREBASE_CREDENTIALS_JSON (legacy)
            cred_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
            if cred_json:
                import json
                cred_dict = json.loads(cred_json)
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                cls._initialized = True
                print("✅ Firebase Admin inicializado con JSON de variable de entorno")
                return True
            
            print("⚠️  Firebase Admin no inicializado. Configura FIREBASE_SERVICE_ACCOUNT, FIREBASE_CREDENTIALS_PATH o FIREBASE_CREDENTIALS_JSON")
            return False
            
        except Exception as e:
            print(f"⚠️  Error al inicializar Firebase Admin: {e}")
            return False
    
    @classmethod
    def verify_token(cls, token: str) -> Optional[Dict]:
        """
        Verificar y decodificar token de Firebase
        
        Args:
            token: Token de Firebase ID
            
        Returns:
            Dict con información del usuario o None si es inválido
        """
        if not FIREBASE_AVAILABLE:
            return None
        
        if not cls._initialized:
            cls.initialize()
        
        if not cls._initialized:
            return None
        
        try:
            # Verificar el token con Firebase Admin
            # check_revoked=False para evitar llamadas adicionales a Firebase
            # clock_skew_seconds=60 para tolerar diferencias de reloj de hasta 60 segundos
            decoded_token = auth.verify_id_token(token, check_revoked=False, clock_skew_seconds=60)
            
            # Retornar información útil del usuario
            return {
                "sub": decoded_token.get("uid"),  # Firebase UID
                "email": decoded_token.get("email"),
                "name": decoded_token.get("name"),
                "firebase_uid": decoded_token.get("uid"),
                "firebase_email": decoded_token.get("email"),
                "email_verified": decoded_token.get("email_verified", False),
                "firebase": True,  # Marca para identificar que es token de Firebase
            }
        except Exception as e:
            print(f"⚠️  Error al verificar token de Firebase: {e}")
            return None
    
    @classmethod
    def is_firebase_token(cls, token: str) -> bool:
        """
        Detectar si un token es de Firebase o JWT tradicional
        
        Los tokens de Firebase suelen ser más largos y tienen un formato diferente
        Por ahora, si el token no empieza con el formato típico de JWT, asumimos que es Firebase
        """
        # Los tokens JWT tradicionales suelen empezar con "eyJ" (Base64 de {"})
        # Los tokens de Firebase también son JWT pero se validan de forma diferente
        # Por ahora, intentamos validar con Firebase si falla con JWT tradicional
        return True  # Siempre intentar validar con Firebase si falla JWT
    
    @classmethod
    def get_user_by_email(cls, email: str) -> Optional[Dict]:
        """
        Obtener información de usuario de Firebase por email
        
        Args:
            email: Email del usuario
            
        Returns:
            Dict con información del usuario o None
        """
        if not FIREBASE_AVAILABLE or not cls._initialized:
            return None
        
        try:
            user = auth.get_user_by_email(email)
            return {
                "uid": user.uid,
                "email": user.email,
                "name": user.display_name,
                "email_verified": user.email_verified,
            }
        except Exception:
            return None

