#!/usr/bin/env python3
"""
Script para ejecutar la migración de perfil_usuarios
Agrega campos adicionales para completar perfil
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Cargar variables de entorno
load_dotenv()

def ejecutar_migracion():
    """Ejecuta la migración SQL"""
    
    # Obtener URL de la base de datos
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ Error: DATABASE_URL no está configurada")
        return False
    
    # Crear engine
    engine = create_engine(db_url)
    
    try:
        # Leer archivo SQL
        with open("migrations_perfil_completo.sql", "r", encoding="utf-8") as f:
            sql_content = f.read()
        
        # Ejecutar migración
        print("🚀 Ejecutando migración de perfil_usuarios...")
        with engine.connect() as conn:
            # Ejecutar cada statement por separado
            statements = [s.strip() for s in sql_content.split(';') if s.strip()]
            
            for i, statement in enumerate(statements, 1):
                if statement:
                    print(f"  📝 Ejecutando statement {i}/{len(statements)}...")
                    conn.execute(text(statement))
            
            conn.commit()
        
        print("✅ Migración ejecutada exitosamente")
        print("\n📋 Campos agregados a perfil_usuarios:")
        print("  • dni (VARCHAR(20))")
        print("  • fecha_nacimiento (DATE)")
        print("  • telefono (VARCHAR(20))")
        print("  • mano_habil (VARCHAR(10))")
        print("  • posicion_preferida (VARCHAR(15))")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al ejecutar migración: {e}")
        return False
    finally:
        engine.dispose()

if __name__ == "__main__":
    ejecutar_migracion()
