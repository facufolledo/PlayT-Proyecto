#!/usr/bin/env python3
"""
Script para crear la tabla categoria_checkpoints
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.config import engine, Base
from src.models.driveplus_models import CategoriaCheckpoint

def create_checkpoints_table():
    """Crear la tabla categoria_checkpoints"""
    
    print("🏆 Creando tabla categoria_checkpoints...")
    print("=" * 50)
    
    try:
        # Crear solo la tabla categoria_checkpoints
        CategoriaCheckpoint.__table__.create(engine, checkfirst=True)
        print("✅ Tabla 'categoria_checkpoints' creada exitosamente")
        
        print("\n🎾 ¡Tabla de checkpoints creada correctamente!")
        print("Esta tabla se usa para:")
        print("- Tracking de ascensos de categoría")
        print("- Sistema de inmunidad post-ascenso")
        print("- Historial de cambios de categoría")
        
    except Exception as e:
        print(f"❌ Error creando la tabla: {e}")
        return False
    
    return True

if __name__ == "__main__":
    create_checkpoints_table()
