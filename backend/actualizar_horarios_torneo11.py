"""
Script para actualizar los horarios del torneo 11
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import json

# Conectar a la base de datos
DATABASE_URL = "postgresql+pg8000://postgres:vZTwMxqfXXqPqPPqJqvXxqPPqPPPPPPP@autorack.proxy.rlwy.net:28517/railway"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

try:
    # Horarios correctos del torneo 11
    horarios = {
        "semana": [
            {"desde": "12:00", "hasta": "23:00"}  # Jueves y Viernes
        ],
        "finDeSemana": [
            {"desde": "09:00", "hasta": "23:00"}  # Sábado y Domingo
        ]
    }
    
    # Actualizar el torneo
    query = text("""
        UPDATE torneos 
        SET horarios_disponibles = :horarios
        WHERE id = 11
    """)
    
    db.execute(query, {"horarios": json.dumps(horarios)})
    db.commit()
    
    print("✅ Horarios del torneo 11 actualizados correctamente")
    print(f"\nHorarios configurados:")
    print(f"  Semana (Jue-Vie): 12:00 - 23:00")
    print(f"  Fin de semana (Sáb-Dom): 09:00 - 23:00")
    
    # Verificar
    result = db.execute(text("SELECT horarios_disponibles FROM torneos WHERE id = 11")).fetchone()
    print(f"\nVerificación:")
    print(f"  {result[0]}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
