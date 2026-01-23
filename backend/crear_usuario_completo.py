"""
Script para crear usuario completo con perfil
Crea usuario en BD + Firebase Authentication
Sin validación de email - Usuario listo para usar inmediatamente
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Agregar el directorio raíz al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.auth.jwt_handler import JWTHandler

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Importar Firebase Admin
try:
    import firebase_admin
    from firebase_admin import credentials, auth
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("⚠️  firebase-admin no está instalado")

def inicializar_firebase():
    """Inicializar Firebase Admin SDK"""
    if not FIREBASE_AVAILABLE:
        return False
    
    try:
        # Verificar si ya está inicializado
        try:
            firebase_admin.get_app()
            print("✅ Firebase ya inicializado")
            return True
        except ValueError:
            pass
        
        # Intentar inicializar
        service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")
        if service_account_json:
            import json
            creds_dict = json.loads(service_account_json)
            cred = credentials.Certificate(creds_dict)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase inicializado con FIREBASE_SERVICE_ACCOUNT")
            return True
        
        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase inicializado con archivo de credenciales")
            return True
        
        cred_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
        if cred_json:
            import json
            cred_dict = json.loads(cred_json)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase inicializado con FIREBASE_CREDENTIALS_JSON")
            return True
        
        print("⚠️  No se encontraron credenciales de Firebase")
        return False
        
    except Exception as e:
        print(f"⚠️  Error al inicializar Firebase: {e}")
        return False

def crear_usuario_completo():
    """Crear usuario completo con perfil en BD + Firebase"""
    session = Session()
    firebase_inicializado = inicializar_firebase()
    
    try:
        print(f"\n{'='*80}")
        print(f"CREAR USUARIO COMPLETO - Drive+ (BD + Firebase)")
        print(f"{'='*80}\n")
        
        if not firebase_inicializado:
            print("⚠️  Firebase no disponible. El usuario solo se creará en la BD.")
            print("   Deberás crear el usuario manualmente en Firebase Console.\n")
        
        # --- DATOS DEL USUARIO ---
        print("📋 DATOS DEL USUARIO")
        print(f"{'─'*80}")
        
        nombre = input("Nombre: ").strip()
        if not nombre:
            print("❌ El nombre es requerido")
            return
        
        apellido = input("Apellido: ").strip()
        if not apellido:
            print("❌ El apellido es requerido")
            return
        
        nombre_usuario = input("Nombre de usuario (username): ").strip().lower()
        if not nombre_usuario:
            print("❌ El nombre de usuario es requerido")
            return
        
        # Verificar que el username no exista
        check_username = session.execute(
            text("SELECT id_usuario FROM usuarios WHERE nombre_usuario = :username"),
            {"username": nombre_usuario}
        ).fetchone()
        
        if check_username:
            print(f"❌ El nombre de usuario '{nombre_usuario}' ya existe")
            return
        
        email = input("Email: ").strip().lower()
        if not email or '@' not in email:
            print("❌ Email inválido")
            return
        
        # Verificar que el email no exista en BD
        check_email = session.execute(
            text("SELECT id_usuario FROM usuarios WHERE email = :email"),
            {"email": email}
        ).fetchone()
        
        if check_email:
            print(f"❌ El email '{email}' ya está registrado en la BD")
            return
        
        # Verificar que el email no exista en Firebase
        if firebase_inicializado:
            try:
                firebase_user = auth.get_user_by_email(email)
                print(f"⚠️  El email '{email}' ya existe en Firebase (UID: {firebase_user.uid})")
                usar_existente = input("¿Usar este usuario de Firebase? (s/n): ").lower().strip()
                if usar_existente != 's':
                    return
                firebase_uid = firebase_user.uid
                print(f"✅ Usando usuario existente de Firebase")
            except auth.UserNotFoundError:
                firebase_uid = None
            except Exception as e:
                print(f"⚠️  Error verificando email en Firebase: {e}")
                firebase_uid = None
        else:
            firebase_uid = None
        
        password = input("Contraseña: ").strip()
        if not password or len(password) < 6:
            print("❌ La contraseña debe tener al menos 6 caracteres")
            return
        
        # Hashear la contraseña
        print("\n🔐 Hasheando contraseña...")
        password_hash = JWTHandler.get_password_hash(password)
        
        sexo = input("Sexo (M/F): ").upper().strip()
        if sexo not in ['M', 'F']:
            print("❌ Sexo debe ser M o F")
            return
        
        categoria = input("Categoría (8va, 7ma, 6ta, 5ta, 4ta, Libre): ").strip()
        
        # Buscar categoría
        query_cat = text("""
            SELECT id_categoria, rating_min, rating_max 
            FROM categorias 
            WHERE nombre = :nombre AND sexo = :sexo
            LIMIT 1
        """)
        cat = session.execute(query_cat, {
            "nombre": categoria,
            "sexo": "masculino" if sexo == "M" else "femenino"
        }).fetchone()
        
        if not cat:
            print(f"❌ Categoría '{categoria}' no encontrada para sexo {sexo}")
            print("\n💡 Categorías disponibles:")
            cats_disponibles = session.execute(
                text("SELECT nombre, sexo FROM categorias ORDER BY sexo, nombre")
            ).fetchall()
            for c in cats_disponibles:
                print(f"   • {c[0]} ({c[1]})")
            return
        
        # Calcular rating inicial
        rating = (cat[1] + cat[2]) // 2 if cat[1] and cat[2] else 1200
        
        print(f"\n✅ Rating inicial: {rating}")
        
        # --- CREAR USUARIO EN FIREBASE ---
        if firebase_inicializado and not firebase_uid:
            print(f"\n{'─'*80}")
            print("� Creando usuario en Firebase...")
            
            try:
                firebase_user = auth.create_user(
                    email=email,
                    password=password,
                    display_name=f"{nombre} {apellido}",
                    email_verified=True  # Marcar como verificado
                )
                firebase_uid = firebase_user.uid
                print(f"✅ Usuario creado en Firebase (UID: {firebase_uid})")
            except Exception as e:
                print(f"❌ Error creando usuario en Firebase: {e}")
                continuar = input("¿Continuar creando solo en BD? (s/n): ").lower().strip()
                if continuar != 's':
                    return
        
        # --- CREAR USUARIO EN BD ---
        print(f"\n{'─'*80}")
        print("💾 Creando usuario en BD...")
        
        query_user = text("""
            INSERT INTO usuarios (
                nombre_usuario, email, password_hash, sexo, 
                rating, id_categoria, partidos_jugados, creado_en
            )
            VALUES (
                :username, :email, :password_hash, :sexo, 
                :rating, :cat_id, 0, NOW()
            )
            RETURNING id_usuario
        """)
        
        user_id = session.execute(query_user, {
            "username": nombre_usuario,
            "email": email,
            "password_hash": password_hash,
            "sexo": sexo,
            "rating": rating,
            "cat_id": cat[0]
        }).fetchone()[0]
        
        print(f"✅ Usuario creado en BD (ID: {user_id})")
        
        # --- CREAR PERFIL ---
        print("💾 Creando perfil...")
        
        query_perfil = text("""
            INSERT INTO perfil_usuarios (
                id_usuario, nombre, apellido, pais, id_categoria_inicial
            )
            VALUES (:user_id, :nombre, :apellido, 'Argentina', :cat_id)
        """)
        
        session.execute(query_perfil, {
            "user_id": user_id,
            "nombre": nombre,
            "apellido": apellido,
            "cat_id": cat[0]
        })
        
        print(f"✅ Perfil creado")
        
        session.commit()
        
        # --- RESUMEN ---
        print(f"\n{'='*80}")
        print(f"✅ USUARIO CREADO EXITOSAMENTE")
        print(f"{'='*80}\n")
        
        print(f"📋 RESUMEN:")
        print(f"{'─'*80}")
        print(f"ID Usuario (BD): {user_id}")
        if firebase_uid:
            print(f"UID Firebase: {firebase_uid}")
        print(f"Nombre: {nombre} {apellido}")
        print(f"Username: {nombre_usuario}")
        print(f"Email: {email}")
        print(f"Sexo: {sexo}")
        print(f"Categoría: {categoria}")
        print(f"Rating: {rating}")
        print(f"{'─'*80}")
        
        print(f"\n✅ El usuario puede iniciar sesión:")
        if firebase_uid:
            print(f"   • Desde el frontend (Firebase Auth)")
        print(f"   • Desde Swagger/API (username/password)")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print()
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    crear_usuario_completo()
