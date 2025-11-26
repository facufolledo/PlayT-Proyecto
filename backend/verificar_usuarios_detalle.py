#!/usr/bin/env python3
"""Script para verificar usuarios en detalle"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

def verificar_usuarios():
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as conn:
            # Ver todos los usuarios con sus categorías
            result = conn.execute(text("""
                SELECT 
                    u.id_usuario,
                    u.nombre_usuario,
                    u.rating,
                    u.sexo,
                    u.id_categoria,
                    c.nombre as categoria_nombre,
                    c.rating_min,
                    c.rating_max
                FROM usuarios u
                LEFT JOIN categorias c ON u.id_categoria = c.id_categoria
                WHERE u.rating >= 1500
                ORDER BY u.rating DESC
            """))
            
            print("Usuarios con rating >= 1500:")
            print("-" * 100)
            print(f"{'Usuario':<20} {'Rating':<8} {'Sexo':<6} {'ID Cat':<8} {'Categoria':<15} {'Min':<8} {'Max':<8}")
            print("-" * 100)
            
            for row in result:
                rating_max = str(row[7]) if row[7] is not None else "NULL"
                print(f"{row[1]:<20} {row[2]:<8} {row[3]:<6} {row[4] or 'NULL':<8} {row[5] or 'NULL':<15} {row[6] or 'NULL':<8} {rating_max:<8}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        engine.dispose()

if __name__ == "__main__":
    verificar_usuarios()
