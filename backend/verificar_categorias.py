#!/usr/bin/env python3
"""Script para verificar categorías en la base de datos"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

def verificar_categorias():
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id_categoria, nombre, rating_min, rating_max, sexo
                FROM categorias
                ORDER BY sexo, rating_min NULLS FIRST
            """))
            
            print("Categorias en la base de datos:")
            print("-" * 80)
            print(f"{'ID':<5} {'Nombre':<15} {'Rating Min':<12} {'Rating Max':<12} {'Sexo':<10}")
            print("-" * 80)
            
            for row in result:
                rating_min = str(row[2]) if row[2] is not None else "NULL"
                rating_max = str(row[3]) if row[3] is not None else "NULL"
                print(f"{row[0]:<5} {row[1]:<15} {rating_min:<12} {rating_max:<12} {row[4]:<10}")
            
            print("\nVerificando usuarios en categoria Libre:")
            print("-" * 80)
            
            result = conn.execute(text("""
                SELECT u.id_usuario, u.nombre_usuario, u.rating, u.sexo, c.nombre as categoria
                FROM usuarios u
                LEFT JOIN categorias c ON u.id_categoria = c.id_categoria
                WHERE u.rating >= 1500
                ORDER BY u.rating DESC
            """))
            
            for row in result:
                print(f"Usuario: {row[1]}, Rating: {row[2]}, Sexo: {row[3]}, Categoria: {row[4]}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        engine.dispose()

if __name__ == "__main__":
    verificar_categorias()
