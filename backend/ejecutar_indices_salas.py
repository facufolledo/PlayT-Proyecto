#!/usr/bin/env python3
"""
Ejecutar migración de índices para optimizar performance de salas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.config import get_db
from sqlalchemy import text

def ejecutar_indices():
    """Ejecutar la migración de índices"""
    
    # Leer archivo de migración
    with open('migrations_indices_salas_performance.sql', 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Obtener conexión
    db = next(get_db())
    
    try:
        print("🔄 Ejecutando migración de índices para salas...")
        
        # Dividir en statements individuales
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for i, statement in enumerate(statements):
            if statement:
                print(f"   Ejecutando statement {i+1}/{len(statements)}")
                db.execute(text(statement))
        
        db.commit()
        print("✅ Índices de performance para salas creados exitosamente")
        
        # Verificar índices creados
        result = db.execute(text("""
            SELECT 
                schemaname,
                tablename,
                indexname
            FROM pg_indexes 
            WHERE tablename IN ('sala', 'sala_jugador', 'usuario', 'perfil_usuario')
            AND indexname LIKE 'idx_%'
            ORDER BY tablename, indexname
        """))
        
        print("\n📊 Índices creados:")
        for row in result:
            print(f"   {row.tablename}.{row.indexname}")
            
    except Exception as e:
        print(f"❌ Error al crear índices: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    ejecutar_indices()