#!/usr/bin/env python3
"""Script para corregir el campo sexo de usuarios"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

def corregir_sexo():
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as conn:
            # Verificar usuarios con sexo incorrecto
            result = conn.execute(text("""
                SELECT id_usuario, nombre_usuario, sexo
                FROM usuarios
                WHERE sexo NOT IN ('M', 'F')
            """))
            
            usuarios_incorrectos = list(result)
            
            if not usuarios_incorrectos:
                print("✅ Todos los usuarios tienen el campo sexo correcto")
                return
            
            print(f"⚠️ Encontrados {len(usuarios_incorrectos)} usuarios con sexo incorrecto:")
            for row in usuarios_incorrectos:
                print(f"  - {row[1]}: '{row[2]}'")
            
            # Corregir
            print("\n🔧 Corrigiendo...")
            
            conn.execute(text("""
                UPDATE usuarios
                SET sexo = 'M'
                WHERE sexo = 'masculino'
            """))
            
            conn.execute(text("""
                UPDATE usuarios
                SET sexo = 'F'
                WHERE sexo = 'femenino'
            """))
            
            conn.commit()
            
            print("✅ Campo sexo corregido exitosamente")
            
            # Verificar resultado
            result = conn.execute(text("""
                SELECT sexo, COUNT(*) as total
                FROM usuarios
                GROUP BY sexo
            """))
            
            print("\n📊 Distribución actual:")
            for row in result:
                print(f"  - {row[0]}: {row[1]} usuarios")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        engine.dispose()

if __name__ == "__main__":
    corregir_sexo()
