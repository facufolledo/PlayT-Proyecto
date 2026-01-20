"""
Script para verificar usuarios sin nombre_usuario en la base de datos
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def verificar_usuarios_sin_username():
    """Verificar usuarios sin nombre_usuario"""
    session = Session()
    
    try:
        # Buscar usuarios sin nombre_usuario o con nombre_usuario vacío
        query = text("""
            SELECT 
                u.id_usuario,
                u.nombre_usuario,
                u.email,
                p.nombre,
                p.apellido
            FROM usuarios u
            LEFT JOIN perfil_usuario p ON u.id_usuario = p.id_usuario
            WHERE u.nombre_usuario IS NULL 
               OR u.nombre_usuario = ''
               OR TRIM(u.nombre_usuario) = ''
            LIMIT 20
        """)
        
        result = session.execute(query)
        usuarios = result.fetchall()
        
        print(f"\n{'='*80}")
        print(f"USUARIOS SIN NOMBRE_USUARIO VÁLIDO")
        print(f"{'='*80}\n")
        
        if not usuarios:
            print("✅ Todos los usuarios tienen nombre_usuario válido")
        else:
            print(f"⚠️  Encontrados {len(usuarios)} usuarios sin nombre_usuario válido:\n")
            
            for u in usuarios:
                print(f"ID: {u.id_usuario}")
                print(f"  Username: '{u.nombre_usuario}'")
                print(f"  Email: {u.email}")
                print(f"  Nombre: {u.nombre} {u.apellido}")
                print()
        
        # Contar total
        count_query = text("""
            SELECT COUNT(*) as total
            FROM usuarios
            WHERE nombre_usuario IS NULL 
               OR nombre_usuario = ''
               OR TRIM(nombre_usuario) = ''
        """)
        
        count_result = session.execute(count_query)
        total = count_result.fetchone()[0]
        
        print(f"\n{'='*80}")
        print(f"TOTAL: {total} usuarios sin nombre_usuario válido")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    verificar_usuarios_sin_username()
