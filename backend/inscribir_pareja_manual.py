"""
Script para inscribir manualmente una pareja sin email
Para gente mayor que no tiene cuenta
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def inscribir_pareja_manual():
    """Inscribir pareja manualmente"""
    session = Session()
    
    try:
        print(f"\n{'='*80}")
        print(f"INSCRIPCIÓN MANUAL DE PAREJA")
        print(f"{'='*80}\n")
        
        # Solicitar datos
        torneo_id = int(input("ID del torneo: "))
        
        print("\n--- JUGADOR 1 ---")
        nombre1 = input("Nombre: ")
        apellido1 = input("Apellido: ")
        sexo1 = input("Sexo (M/F): ").upper()
        categoria1 = input("Categoría (8va, 7ma, 6ta, 5ta, 4ta, Libre): ")
        
        print("\n--- JUGADOR 2 ---")
        nombre2 = input("Nombre: ")
        apellido2 = input("Apellido: ")
        sexo2 = input("Sexo (M/F): ").upper()
        categoria2 = input("Categoría (8va, 7ma, 6ta, 5ta, 4ta, Libre): ")
        
        nombre_pareja = input(f"\nNombre de la pareja (default: {nombre1}/{nombre2}): ").strip()
        if not nombre_pareja:
            nombre_pareja = f"{nombre1}/{nombre2}"
        
        # Crear usuarios temporales
        print("\n🔄 Creando usuarios...")
        
        # Usuario 1
        email1 = f"{nombre1.lower()}.{apellido1.lower()}@invitado.local"
        username1 = f"{nombre1.lower()}{apellido1.lower()}"
        
        # Buscar categoría
        query_cat1 = text("""
            SELECT id_categoria FROM categorias 
            WHERE nombre = :nombre AND sexo = :sexo
            LIMIT 1
        """)
        cat1 = session.execute(query_cat1, {
            "nombre": categoria1,
            "sexo": "masculino" if sexo1 == "M" else "femenino"
        }).fetchone()
        
        if not cat1:
            print(f"❌ Categoría '{categoria1}' no encontrada para sexo {sexo1}")
            return
        
        # Crear usuario 1
        query_user1 = text("""
            INSERT INTO usuarios (nombre_usuario, email, password_hash, sexo, rating, id_categoria, partidos_jugados)
            VALUES (:username, :email, '', :sexo, 1200, :cat_id, 0)
            RETURNING id_usuario
        """)
        user1_id = session.execute(query_user1, {
            "username": username1,
            "email": email1,
            "sexo": sexo1,
            "cat_id": cat1[0]
        }).fetchone()[0]
        
        # Crear perfil 1
        query_perfil1 = text("""
            INSERT INTO perfil_usuario (id_usuario, nombre, apellido, pais)
            VALUES (:user_id, :nombre, :apellido, 'Argentina')
        """)
        session.execute(query_perfil1, {
            "user_id": user1_id,
            "nombre": nombre1,
            "apellido": apellido1
        })
        
        print(f"✅ Usuario 1 creado: {nombre1} {apellido1} (ID: {user1_id})")
        
        # Usuario 2
        email2 = f"{nombre2.lower()}.{apellido2.lower()}@invitado.local"
        username2 = f"{nombre2.lower()}{apellido2.lower()}"
        
        query_cat2 = text("""
            SELECT id_categoria FROM categorias 
            WHERE nombre = :nombre AND sexo = :sexo
            LIMIT 1
        """)
        cat2 = session.execute(query_cat2, {
            "nombre": categoria2,
            "sexo": "masculino" if sexo2 == "M" else "femenino"
        }).fetchone()
        
        if not cat2:
            print(f"❌ Categoría '{categoria2}' no encontrada para sexo {sexo2}")
            return
        
        query_user2 = text("""
            INSERT INTO usuarios (nombre_usuario, email, password_hash, sexo, rating, id_categoria, partidos_jugados)
            VALUES (:username, :email, '', :sexo, 1200, :cat_id, 0)
            RETURNING id_usuario
        """)
        user2_id = session.execute(query_user2, {
            "username": username2,
            "email": email2,
            "sexo": sexo2,
            "cat_id": cat2[0]
        }).fetchone()[0]
        
        query_perfil2 = text("""
            INSERT INTO perfil_usuario (id_usuario, nombre, apellido, pais)
            VALUES (:user_id, :nombre, :apellido, 'Argentina')
        """)
        session.execute(query_perfil2, {
            "user_id": user2_id,
            "nombre": nombre2,
            "apellido": apellido2
        })
        
        print(f"✅ Usuario 2 creado: {nombre2} {apellido2} (ID: {user2_id})")
        
        # Crear pareja
        print("\n🔄 Inscribiendo pareja en el torneo...")
        
        query_pareja = text("""
            INSERT INTO parejas_torneo (
                id_torneo, 
                jugador1_id, 
                jugador2_id, 
                nombre_pareja,
                confirmado_jugador1,
                confirmado_jugador2,
                estado
            )
            VALUES (:torneo_id, :j1_id, :j2_id, :nombre, TRUE, TRUE, 'confirmada')
            RETURNING id_pareja
        """)
        
        pareja_id = session.execute(query_pareja, {
            "torneo_id": torneo_id,
            "j1_id": user1_id,
            "j2_id": user2_id,
            "nombre": nombre_pareja
        }).fetchone()[0]
        
        session.commit()
        
        print(f"\n{'='*80}")
        print(f"✅ PAREJA INSCRITA EXITOSAMENTE")
        print(f"{'='*80}")
        print(f"\nID Pareja: {pareja_id}")
        print(f"Nombre: {nombre_pareja}")
        print(f"Jugador 1: {nombre1} {apellido1} (ID: {user1_id})")
        print(f"Jugador 2: {nombre2} {apellido2} (ID: {user2_id})")
        print(f"Estado: CONFIRMADA")
        print(f"\n⚠️  IMPORTANTE: Estos usuarios tienen emails temporales (@invitado.local)")
        print(f"   No podrán iniciar sesión en la app, pero aparecerán en el torneo.")
        print()
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    inscribir_pareja_manual()
