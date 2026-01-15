"""
Script para ejecutar la migración de horarios_disponibles
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from src.database.config import get_db

def ejecutar_migracion():
    """Ejecuta la migración para agregar horarios_disponibles"""
    db = next(get_db())
    
    try:
        print("Iniciando migración de horarios_disponibles...")
        
        # Leer el archivo SQL
        with open('migrations_horarios_disponibles.sql', 'r', encoding='utf-8') as f:
            sql = f.read()
        
        # Ejecutar cada statement
        statements = [s.strip() for s in sql.split(';') if s.strip() and not s.strip().startswith('--')]
        
        for statement in statements:
            if statement:
                print(f"\nEjecutando: {statement[:100]}...")
                db.execute(text(statement))
        
        db.commit()
        print("\n✅ Migración completada exitosamente!")
        
        # Verificar que la columna existe
        result = db.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'torneos' 
            AND column_name = 'horarios_disponibles'
        """))
        
        columna = result.fetchone()
        if columna:
            print(f"\n✅ Columna verificada: {columna[0]} ({columna[1]})")
        else:
            print("\n⚠️ Advertencia: No se pudo verificar la columna")
            
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    ejecutar_migracion()
