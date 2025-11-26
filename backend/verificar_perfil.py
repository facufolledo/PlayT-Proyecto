#!/usr/bin/env python3
"""Script para verificar campos de perfil_usuarios"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect

load_dotenv()

def verificar_campos():
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    
    try:
        inspector = inspect(engine)
        columns = inspector.get_columns('perfil_usuarios')
        
        print("Campos en perfil_usuarios:")
        print("-" * 50)
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
        
        print("\nVerificacion exitosa!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        engine.dispose()

if __name__ == "__main__":
    verificar_campos()
