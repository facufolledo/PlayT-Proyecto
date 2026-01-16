"""
Script para verificar los horarios del torneo 11
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.torneo_models import Torneo
import json

# Conectar a la base de datos
DATABASE_URL = "postgresql+pg8000://postgres:vZTwMxqfXXqPqPPqJqvXxqPPqPPPPPPP@autorack.proxy.rlwy.net:28517/railway"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

try:
    # Obtener torneo 11
    torneo = db.query(Torneo).filter(Torneo.id == 11).first()
    
    if not torneo:
        print("❌ Torneo 11 no encontrado")
    else:
        print(f"✅ Torneo encontrado: {torneo.nombre}")
        print(f"\nID: {torneo.id}")
        print(f"Nombre: {torneo.nombre}")
        print(f"Fecha inicio: {torneo.fecha_inicio}")
        print(f"Fecha fin: {torneo.fecha_fin}")
        print(f"\nHorarios disponibles (raw):")
        print(f"Tipo: {type(torneo.horarios_disponibles)}")
        print(f"Valor: {torneo.horarios_disponibles}")
        
        if torneo.horarios_disponibles:
            print(f"\nHorarios disponibles (JSON):")
            print(json.dumps(torneo.horarios_disponibles, indent=2, ensure_ascii=False))
        else:
            print("\n⚠️ horarios_disponibles es NULL o vacío")
            
finally:
    db.close()
