"""
Script para verificar el perfil de un usuario específico
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Cargar variables de entorno
load_dotenv()

# Configurar conexión a la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def verificar_perfil():
    db = SessionLocal()
    
    try:
        # Buscar usuario por email
        result = db.execute(text("""
            SELECT 
                u.id_usuario,
                u.nombre_usuario,
                u.email,
                p.nombre,
                p.apellido,
                p.ciudad,
                p.pais,
                p.posicion_preferida,
                p.mano_habil,
                p.dni,
                p.telefono,
                p.fecha_nacimiento,
                p.url_avatar
            FROM usuarios u
            LEFT JOIN perfil_usuarios p ON u.id_usuario = p.id_usuario
            WHERE u.email LIKE '%facundo%' OR u.nombre_usuario LIKE '%facundo%'
            ORDER BY u.id_usuario
        """))
        
        usuarios = result.fetchall()
        
        if not usuarios:
            print("❌ No se encontró ningún usuario con 'facundo' en el email o nombre de usuario")
            return
        
        print("=" * 80)
        print("PERFILES DE USUARIOS ENCONTRADOS")
        print("=" * 80)
        
        for usuario in usuarios:
            print(f"\n📋 Usuario ID: {usuario[0]}")
            print(f"   Nombre de usuario: {usuario[1]}")
            print(f"   Email: {usuario[2]}")
            print(f"   Nombre completo: {usuario[3]} {usuario[4]}")
            print(f"   Ciudad: {usuario[5]}")
            print(f"   País: {usuario[6]}")
            print(f"   Posición preferida: {usuario[7]}")
            print(f"   Mano hábil: {usuario[8]}")
            print(f"   DNI: {usuario[9]}")
            print(f"   Teléfono: {usuario[10]}")
            print(f"   Fecha nacimiento: {usuario[11]}")
            print(f"   URL Avatar: {usuario[12]}")
            print("-" * 80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verificar_perfil()
