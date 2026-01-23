"""
Script para completar el perfil de Marcelo Rearte (ID: 92)
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def completar_perfil():
    session = Session()
    
    try:
        print("\n🔧 Completando perfil de Marcelo Rearte (ID: 92)...\n")
        
        # Verificar que el usuario existe
        user = session.execute(
            text("SELECT id_usuario, nombre_usuario, email, id_categoria FROM usuarios WHERE id_usuario = 92")
        ).fetchone()
        
        if not user:
            print("❌ Usuario ID 92 no encontrado")
            return
        
        print(f"✅ Usuario encontrado: {user[1]} ({user[2]})")
        
        # Crear perfil
        query_perfil = text("""
            INSERT INTO perfil_usuarios (
                id_usuario, nombre, apellido, pais, id_categoria_inicial
            )
            VALUES (92, 'Marcelo', 'Rearte', 'Argentina', :cat_id)
        """)
        
        session.execute(query_perfil, {"cat_id": user[3]})
        session.commit()
        
        print("✅ Perfil creado exitosamente")
        print("\n📋 Usuario completo:")
        print(f"   ID: 92")
        print(f"   Username: {user[1]}")
        print(f"   Email: {user[2]}")
        print(f"   Nombre: Marcelo Rearte")
        print(f"   Categoría ID: {user[3]}")
        print("\n✅ El usuario puede iniciar sesión normalmente\n")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    completar_perfil()
