#!/usr/bin/env python3
"""Script para corregir definitivamente el campo sexo"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

def corregir_sexo_definitivo():
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as conn:
            print("🔧 Corrigiendo campo sexo...")
            
            # Actualizar todos los que empiecen con F
            result = conn.execute(text("""
                UPDATE usuarios
                SET sexo = 'F'
                WHERE sexo LIKE 'F%'
                RETURNING id_usuario, nombre_usuario
            """))
            
            usuarios_f = list(result)
            
            # Actualizar todos los que empiecen con M
            result = conn.execute(text("""
                UPDATE usuarios
                SET sexo = 'M'
                WHERE sexo LIKE 'M%'
                RETURNING id_usuario, nombre_usuario
            """))
            
            usuarios_m = list(result)
            
            conn.commit()
            
            print(f"\n✅ Corregidos:")
            print(f"  - {len(usuarios_f)} usuarios a 'F'")
            print(f"  - {len(usuarios_m)} usuarios a 'M'")
            
            # Verificar resultado
            result = conn.execute(text("""
                SELECT sexo, COUNT(*) as total
                FROM usuarios
                GROUP BY sexo
                ORDER BY sexo
            """))
            
            print("\n📊 Distribución final:")
            for row in result:
                print(f"  - '{row[0]}': {row[1]} usuarios")
            
            # Ver usuarios femeninos
            result = conn.execute(text("""
                SELECT nombre_usuario, rating, id_categoria
                FROM usuarios
                WHERE sexo = 'F'
            """))
            
            print("\n👩 Usuarios femeninos:")
            for row in result:
                print(f"  - {row[0]}: Rating {row[1]}, Categoria ID {row[2]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        engine.dispose()

if __name__ == "__main__":
    corregir_sexo_definitivo()
