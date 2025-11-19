#!/usr/bin/env python3
"""Script para ver todos los usuarios"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

def ver_todos_usuarios():
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    u.id_usuario,
                    u.nombre_usuario, 
                    u.rating, 
                    u.sexo,
                    LENGTH(u.sexo) as sexo_length,
                    ASCII(SUBSTRING(u.sexo, 1, 1)) as first_char_ascii,
                    u.id_categoria, 
                    c.nombre as categoria
                FROM usuarios u
                LEFT JOIN categorias c ON u.id_categoria = c.id_categoria
                ORDER BY u.id_usuario
            """))
            
            print("Todos los usuarios:")
            print("-" * 120)
            print(f"{'ID':<5} {'Usuario':<20} {'Rating':<8} {'Sexo':<10} {'Len':<5} {'ASCII':<8} {'Cat ID':<8} {'Categoria':<15}")
            print("-" * 120)
            
            for row in result:
                print(f"{row[0]:<5} {row[1]:<20} {row[2]:<8} {repr(row[3]):<10} {row[4]:<5} {row[5]:<8} {row[6] or 'NULL':<8} {row[7] or 'NULL':<15}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        engine.dispose()

if __name__ == "__main__":
    ver_todos_usuarios()
