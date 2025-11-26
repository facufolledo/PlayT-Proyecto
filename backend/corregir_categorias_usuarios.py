#!/usr/bin/env python3
"""Script para corregir categorías de usuarios según su rating"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

def corregir_categorias():
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as conn:
            print("🔍 Buscando usuarios con categoría incorrecta...")
            
            # Actualizar categorías según rating para usuarios masculinos
            result = conn.execute(text("""
                UPDATE usuarios u
                SET id_categoria = (
                    SELECT c.id_categoria
                    FROM categorias c
                    WHERE c.sexo = u.sexo
                    AND (c.rating_min IS NULL OR u.rating >= c.rating_min)
                    AND (c.rating_max IS NULL OR u.rating <= c.rating_max)
                    ORDER BY c.rating_min DESC NULLS LAST
                    LIMIT 1
                )
                WHERE u.id_categoria IS NOT NULL
                RETURNING u.id_usuario, u.nombre_usuario, u.rating, u.id_categoria
            """))
            
            usuarios_actualizados = list(result)
            conn.commit()
            
            if usuarios_actualizados:
                print(f"\n✅ Actualizados {len(usuarios_actualizados)} usuarios:")
                for row in usuarios_actualizados:
                    print(f"  - {row[1]}: Rating {row[2]} → Categoría ID {row[3]}")
            else:
                print("\n✅ Todas las categorías están correctas")
            
            # Verificar resultado
            print("\n📊 Verificando resultado:")
            result = conn.execute(text("""
                SELECT 
                    u.nombre_usuario,
                    u.rating,
                    u.sexo,
                    c.nombre as categoria
                FROM usuarios u
                LEFT JOIN categorias c ON u.id_categoria = c.id_categoria
                WHERE u.rating >= 1500
                ORDER BY u.rating DESC
            """))
            
            print("-" * 70)
            print(f"{'Usuario':<20} {'Rating':<10} {'Sexo':<8} {'Categoría':<15}")
            print("-" * 70)
            for row in result:
                print(f"{row[0]:<20} {row[1]:<10} {row[2]:<8} {row[3] or 'NULL':<15}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        engine.dispose()

if __name__ == "__main__":
    corregir_categorias()
