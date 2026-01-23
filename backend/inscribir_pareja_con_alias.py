"""
Script para inscribir pareja usando email con alias
Ejemplo: tuemail+jugador1@gmail.com, tuemail+jugador2@gmail.com
Todos los emails llegarán a tu cuenta principal
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def inscribir_pareja_con_alias():
    """Inscribir pareja usando email con alias"""
    session = Session()
    
    try:
        print(f"\n{'='*80}")
        print(f"INSCRIPCIÓN DE PAREJA CON EMAIL ALIAS")
        print(f"{'='*80}\n")
        
        # Email base
        email_base = input("Tu email (ej: tuemail@gmail.com): ").strip()
        if not email_base or '@' not in email_base:
            print("❌ Email inválido")
            return
        
        # Extraer partes del email
        email_user, email_domain = email_base.split('@')
        
        # Datos del torneo
        torneo_id = int(input("\nID del torneo: "))
        
        # Verificar que el torneo existe
        query_torneo = text("SELECT nombre FROM torneos WHERE id_torneo = :id")
        torneo = session.execute(query_torneo, {"id": torneo_id}).fetchone()
        if not torneo:
            print(f"❌ Torneo {torneo_id} no encontrado")
            return
        
        print(f"✅ Torneo: {torneo[0]}")
        
        # --- JUGADOR 1 ---
        print(f"\n{'─'*80}")
        print("JUGADOR 1")
        print(f"{'─'*80}")
        
        nombre1 = input("Nombre: ").strip()
        apellido1 = input("Apellido: ").strip()
        sexo1 = input("Sexo (M/F): ").upper().strip()
        categoria1 = input("Categoría (8va, 7ma, 6ta, 5ta, 4ta, Libre): ").strip()
        
        # Email con alias
        alias1 = input(f"Alias para email (ej: jugador1): ").strip().lower()
        email1 = f"{email_user}+{alias1}@{email_domain}"
        username1 = f"{nombre1.lower()}{apellido1.lower()}"
        
        print(f"📧 Email: {email1}")
        print(f"👤 Username: {username1}")
        
        # Buscar categoría
        query_cat = text("""
            SELECT id_categoria, rating_min, rating_max 
            FROM categorias 
            WHERE nombre = :nombre AND sexo = :sexo
            LIMIT 1
        """)
        cat1 = session.execute(query_cat, {
            "nombre": categoria1,
            "sexo": "masculino" if sexo1 == "M" else "femenino"
        }).fetchone()
        
        if not cat1:
            print(f"❌ Categoría '{categoria1}' no encontrada para sexo {sexo1}")
            return
        
        # Calcular rating inicial
        rating1 = (cat1[1] + cat1[2]) // 2 if cat1[1] and cat1[2] else 1200
        
        # Crear usuario 1
        query_user = text("""
            INSERT INTO usuarios (
                nombre_usuario, email, password_hash, sexo, 
                rating, id_categoria, partidos_jugados, creado_en
            )
            VALUES (
                :username, :email, '', :sexo, 
                :rating, :cat_id, 0, NOW()
            )
            RETURNING id_usuario
        """)
        
        user1_id = session.execute(query_user, {
            "username": username1,
            "email": email1,
            "sexo": sexo1,
            "rating": rating1,
            "cat_id": cat1[0]
        }).fetchone()[0]
        
        # Crear perfil 1
        query_perfil = text("""
            INSERT INTO perfil_usuario (
                id_usuario, nombre, apellido, pais, id_categoria_inicial
            )
            VALUES (:user_id, :nombre, :apellido, 'Argentina', :cat_id)
        """)
        
        session.execute(query_perfil, {
            "user_id": user1_id,
            "nombre": nombre1,
            "apellido": apellido1,
            "cat_id": cat1[0]
        })
        
        print(f"✅ Usuario 1 creado: {nombre1} {apellido1} (ID: {user1_id}, Rating: {rating1})")
        
        # --- JUGADOR 2 ---
        print(f"\n{'─'*80}")
        print("JUGADOR 2")
        print(f"{'─'*80}")
        
        nombre2 = input("Nombre: ").strip()
        apellido2 = input("Apellido: ").strip()
        sexo2 = input("Sexo (M/F): ").upper().strip()
        categoria2 = input("Categoría (8va, 7ma, 6ta, 5ta, 4ta, Libre): ").strip()
        
        # Email con alias
        alias2 = input(f"Alias para email (ej: jugador2): ").strip().lower()
        email2 = f"{email_user}+{alias2}@{email_domain}"
        username2 = f"{nombre2.lower()}{apellido2.lower()}"
        
        print(f"📧 Email: {email2}")
        print(f"👤 Username: {username2}")
        
        # Buscar categoría
        cat2 = session.execute(query_cat, {
            "nombre": categoria2,
            "sexo": "masculino" if sexo2 == "M" else "femenino"
        }).fetchone()
        
        if not cat2:
            print(f"❌ Categoría '{categoria2}' no encontrada para sexo {sexo2}")
            return
        
        # Calcular rating inicial
        rating2 = (cat2[1] + cat2[2]) // 2 if cat2[1] and cat2[2] else 1200
        
        # Crear usuario 2
        user2_id = session.execute(query_user, {
            "username": username2,
            "email": email2,
            "sexo": sexo2,
            "rating": rating2,
            "cat_id": cat2[0]
        }).fetchone()[0]
        
        # Crear perfil 2
        session.execute(query_perfil, {
            "user_id": user2_id,
            "nombre": nombre2,
            "apellido": apellido2,
            "cat_id": cat2[0]
        })
        
        print(f"✅ Usuario 2 creado: {nombre2} {apellido2} (ID: {user2_id}, Rating: {rating2})")
        
        # --- CREAR PAREJA ---
        print(f"\n{'─'*80}")
        print("CREAR PAREJA")
        print(f"{'─'*80}")
        
        nombre_pareja = input(f"Nombre de la pareja (default: {nombre1}/{nombre2}): ").strip()
        if not nombre_pareja:
            nombre_pareja = f"{nombre1}/{nombre2}"
        
        # Inscribir pareja
        query_pareja = text("""
            INSERT INTO parejas_torneo (
                id_torneo, 
                jugador1_id, 
                jugador2_id, 
                nombre_pareja,
                confirmado_jugador1,
                confirmado_jugador2,
                estado,
                created_at
            )
            VALUES (
                :torneo_id, :j1_id, :j2_id, :nombre, 
                TRUE, TRUE, 'confirmada', NOW()
            )
            RETURNING id_pareja
        """)
        
        pareja_id = session.execute(query_pareja, {
            "torneo_id": torneo_id,
            "j1_id": user1_id,
            "j2_id": user2_id,
            "nombre": nombre_pareja
        }).fetchone()[0]
        
        session.commit()
        
        # Resumen
        print(f"\n{'='*80}")
        print(f"✅ PAREJA INSCRITA EXITOSAMENTE")
        print(f"{'='*80}\n")
        
        print(f"📋 RESUMEN:")
        print(f"{'─'*80}")
        print(f"Torneo: {torneo[0]} (ID: {torneo_id})")
        print(f"Pareja: {nombre_pareja} (ID: {pareja_id})")
        print(f"\nJugador 1:")
        print(f"  • Nombre: {nombre1} {apellido1}")
        print(f"  • Email: {email1}")
        print(f"  • Username: {username1}")
        print(f"  • ID: {user1_id}")
        print(f"  • Rating: {rating1}")
        print(f"  • Categoría: {categoria1}")
        print(f"\nJugador 2:")
        print(f"  • Nombre: {nombre2} {apellido2}")
        print(f"  • Email: {email2}")
        print(f"  • Username: {username2}")
        print(f"  • ID: {user2_id}")
        print(f"  • Rating: {rating2}")
        print(f"  • Categoría: {categoria2}")
        print(f"\nEstado: CONFIRMADA ✅")
        print(f"{'─'*80}")
        
        print(f"\n📧 IMPORTANTE:")
        print(f"   Todos los emails llegarán a: {email_base}")
        print(f"   Puedes gestionar ambas cuentas desde tu email principal")
        print()
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    inscribir_pareja_con_alias()
