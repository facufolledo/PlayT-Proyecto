"""
Script para ejecutar la migración de pagos y horarios
"""
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

def ejecutar_migracion():
    engine = create_engine(os.getenv('DATABASE_URL'))
    
    with open('migrations_pagos_horarios.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
    
    # Dividir por statements (separados por ;)
    statements = [s.strip() for s in sql.split(';') if s.strip()]
    
    with engine.connect() as conn:
        for statement in statements:
            try:
                print(f"Ejecutando: {statement[:100]}...")
                conn.execute(text(statement))
                conn.commit()
                print("✅ OK")
            except Exception as e:
                print(f"⚠️ Error (puede ser normal si ya existe): {e}")
                conn.rollback()
    
    print("\n✅ Migración completada")

if __name__ == "__main__":
    ejecutar_migracion()
