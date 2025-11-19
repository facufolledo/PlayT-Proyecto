#!/usr/bin/env python3
"""Script para ver usuarios femeninos"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

def ver_usuarios_femeninos():
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT u.nombre_usuario, u.rating, u.sexo, u.id_categoria, c.nombre as categoria
                FROM usuarios u
                LEFT JOIN categorias c ON u.id_categoria = c.id_categoria
                WHERE u.sexo = 'F'
            """))
            
            print("Usuarios femeninos:")
            print("-" * 80)
            for row in result:
                print(f"Usuario: {row[0]}, Rating: {row[1]}, Sexo: {row[2]}, Categoria: {row[4]}")
            
            # Ver distribución por sexo
            result = conn.execute(text("""
                SELECT sexo, COUNT(*) as total
                FROM usuarios
                GROUP BY sexo
            """))
            
            print("\nDistribución por sexo:")
            print("-" * 80)
            for row in result:
                print(f"{row[0]}: {row[1]} usuarios")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        engine.dispose()

if __name__ == "__main__":
    ver_usuarios_femeninos()
