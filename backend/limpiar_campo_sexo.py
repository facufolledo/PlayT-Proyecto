#!/usr/bin/env python3
"""Script para limpiar el campo sexo"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

def limpiar_sexo():
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as conn:
            # Limpiar espacios y tabs
            print("🧹 Limpiando campo sexo...")
            
            result = conn.execute(text("""
                UPDATE usuarios
                SET sexo = TRIM(sexo)
                WHERE sexo != TRIM(sexo)
                RETURNING id_usuario, nombre_usuario, sexo
            """))
            
            usuarios_limpiados = list(result)
            conn.commit()
            
            if usuarios_limpiados:
                print(f"\n✅ Limpiados {len(usuarios_limpiados)} usuarios:")
                for row in usuarios_limpiados:
                    print(f"  - {row[1]}: '{row[2]}'")
            else:
                print("\n✅ Todos los campos están limpios")
            
            # Verificar resultado
            result = conn.execute(text("""
                SELECT sexo, COUNT(*) as total
                FROM usuarios
                GROUP BY sexo
            """))
            
            print("\n📊 Distribución por sexo:")
            for row in result:
                print(f"  - '{row[0]}': {row[1]} usuarios")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        engine.dispose()

if __name__ == "__main__":
    limpiar_sexo()
