"""
Script para debuggear el perfil de francoayet07
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def debug_usuario():
    """Debug del usuario francoayet07"""
    session = Session()
    
    try:
        username = "francoayet07"
        
        print(f"\n{'='*80}")
        print(f"DEBUG: Usuario '{username}'")
        print(f"{'='*80}\n")
        
        # Buscar usuario
        query = text("""
            SELECT 
                u.id_usuario,
                u.nombre_usuario,
                u.email,
                u.sexo,
                u.rating,
                u.partidos_jugados,
                u.id_categoria,
                u.fecha_registro
            FROM usuarios u
            WHERE LOWER(u.nombre_usuario) = LOWER(:username)
        """)
        
        result = session.execute(query, {"username": username})
        usuario = result.fetchone()
        
        if not usuario:
            print(f"❌ Usuario '{username}' NO ENCONTRADO en tabla usuarios")
            
            # Buscar similares
            query_similar = text("""
                SELECT nombre_usuario 
                FROM usuarios 
                WHERE nombre_usuario ILIKE :pattern
                LIMIT 10
            """)
            result_similar = session.execute(query_similar, {"pattern": f"%{username[:5]}%"})
            similares = result_similar.fetchall()
            
            if similares:
                print(f"\n🔍 Usuarios similares encontrados:")
                for s in similares:
                    print(f"  - {s[0]}")
            
            return
        
        print("✅ Usuario encontrado en tabla usuarios:")
        print(f"  ID: {usuario.id_usuario}")
        print(f"  Username: {usuario.nombre_usuario}")
        print(f"  Email: {usuario.email}")
        print(f"  Sexo: {usuario.sexo}")
        print(f"  Rating: {usuario.rating}")
        print(f"  Partidos: {usuario.partidos_jugados}")
        print(f"  Categoría ID: {usuario.id_categoria}")
        print(f"  Fecha registro: {usuario.fecha_registro}")
        
        # Buscar perfil
        query_perfil = text("""
            SELECT 
                p.id_usuario,
                p.nombre,
                p.apellido,
                p.ciudad,
                p.pais,
                p.posicion_preferida,
                p.mano_habil,
                p.url_avatar
            FROM perfil_usuario p
            WHERE p.id_usuario = :user_id
        """)
        
        result_perfil = session.execute(query_perfil, {"user_id": usuario.id_usuario})
        perfil = result_perfil.fetchone()
        
        print(f"\n{'='*80}")
        if not perfil:
            print("❌ PERFIL NO ENCONTRADO en tabla perfil_usuario")
            print("   Este es el problema - el usuario no tiene perfil asociado")
        else:
            print("✅ Perfil encontrado:")
            print(f"  Nombre: {perfil.nombre}")
            print(f"  Apellido: {perfil.apellido}")
            print(f"  Ciudad: {perfil.ciudad}")
            print(f"  País: {perfil.pais}")
            print(f"  Posición: {perfil.posicion_preferida}")
            print(f"  Mano: {perfil.mano_habil}")
            print(f"  Avatar: {perfil.url_avatar}")
        
        # Buscar categoría
        if usuario.id_categoria:
            query_cat = text("""
                SELECT nombre, sexo
                FROM categorias
                WHERE id_categoria = :cat_id
            """)
            result_cat = session.execute(query_cat, {"cat_id": usuario.id_categoria})
            categoria = result_cat.fetchone()
            
            print(f"\n{'='*80}")
            if categoria:
                print(f"✅ Categoría: {categoria.nombre} ({categoria.sexo})")
            else:
                print(f"⚠️  Categoría ID {usuario.id_categoria} no encontrada")
        
        print(f"\n{'='*80}")
        print("DIAGNÓSTICO:")
        print(f"{'='*80}")
        
        if not perfil:
            print("❌ PROBLEMA: Usuario sin perfil asociado")
            print("   El endpoint falla porque hace JOIN con perfil_usuario")
            print("   Solución: Crear perfil o cambiar JOIN a LEFT JOIN")
        else:
            print("✅ Usuario tiene todos los datos necesarios")
            print("   El error debe ser otra cosa (revisar logs del backend)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    debug_usuario()
