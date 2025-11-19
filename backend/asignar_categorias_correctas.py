#!/usr/bin/env python3
"""Script para asignar categorías correctas según rating"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

def asignar_categorias():
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as conn:
            print("🔍 Asignando categorías según rating...")
            
            # Para usuarios masculinos
            queries = [
                ("Principiante M (0-499)", "UPDATE usuarios SET id_categoria = 7 WHERE sexo = 'M' AND rating >= 0 AND rating <= 499"),
                ("8va M (500-999)", "UPDATE usuarios SET id_categoria = 1 WHERE sexo = 'M' AND rating >= 500 AND rating <= 999"),
                ("7ma M (1000-1199)", "UPDATE usuarios SET id_categoria = 2 WHERE sexo = 'M' AND rating >= 1000 AND rating <= 1199"),
                ("6ta M (1200-1399)", "UPDATE usuarios SET id_categoria = 3 WHERE sexo = 'M' AND rating >= 1200 AND rating <= 1399"),
                ("5ta M (1400-1599)", "UPDATE usuarios SET id_categoria = 4 WHERE sexo = 'M' AND rating >= 1400 AND rating <= 1599"),
                ("4ta M (1600-1799)", "UPDATE usuarios SET id_categoria = 5 WHERE sexo = 'M' AND rating >= 1600 AND rating <= 1799"),
                ("Libre M (1800+)", "UPDATE usuarios SET id_categoria = 6 WHERE sexo = 'M' AND rating >= 1800"),
                
                # Para usuarios femeninos
                ("Principiante F (0-499)", "UPDATE usuarios SET id_categoria = 9 WHERE sexo = 'F' AND rating >= 0 AND rating <= 499"),
                ("8va F (500-999)", "UPDATE usuarios SET id_categoria = 10 WHERE sexo = 'F' AND rating >= 500 AND rating <= 999"),
                ("7ma F (1000-1199)", "UPDATE usuarios SET id_categoria = 11 WHERE sexo = 'F' AND rating >= 1000 AND rating <= 1199"),
                ("6ta F (1200-1399)", "UPDATE usuarios SET id_categoria = 12 WHERE sexo = 'F' AND rating >= 1200 AND rating <= 1399"),
                ("5ta F (1400-1599)", "UPDATE usuarios SET id_categoria = 13 WHERE sexo = 'F' AND rating >= 1400 AND rating <= 1599"),
                ("Libre F (1600+)", "UPDATE usuarios SET id_categoria = 14 WHERE sexo = 'F' AND rating >= 1600"),
            ]
            
            for nombre, query in queries:
                result = conn.execute(text(query))
                if result.rowcount > 0:
                    print(f"  ✓ {nombre}: {result.rowcount} usuarios")
            
            conn.commit()
            
            # Verificar resultado
            print("\n📊 Verificación final:")
            result = conn.execute(text("""
                SELECT 
                    u.nombre_usuario,
                    u.rating,
                    u.sexo,
                    c.nombre as categoria,
                    c.rating_min,
                    c.rating_max
                FROM usuarios u
                LEFT JOIN categorias c ON u.id_categoria = c.id_categoria
                ORDER BY u.rating DESC
                LIMIT 20
            """))
            
            print("-" * 90)
            print(f"{'Usuario':<20} {'Rating':<10} {'Sexo':<8} {'Categoría':<15} {'Min':<8} {'Max':<8}")
            print("-" * 90)
            for row in result:
                rating_max = str(row[5]) if row[5] is not None else "NULL"
                print(f"{row[0]:<20} {row[1]:<10} {row[2]:<8} {row[3] or 'NULL':<15} {row[4] or 'NULL':<8} {rating_max:<8}")
            
            print("\n✅ Categorías asignadas correctamente")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        engine.dispose()

if __name__ == "__main__":
    asignar_categorias()
