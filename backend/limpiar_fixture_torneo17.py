"""
Limpiar fixture del torneo 17 para regenerarlo correctamente
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.database.config import get_db
from sqlalchemy import text

def limpiar_fixture():
    db = next(get_db())
    
    print("🧹 LIMPIANDO FIXTURE DEL TORNEO 17...")
    
    # Eliminar partidos de fase de grupos del torneo 17
    result = db.execute(text("""
        DELETE FROM partidos 
        WHERE id_torneo = 17 
        AND fase = 'zona'
    """))
    
    partidos_eliminados = result.rowcount
    db.commit()
    
    print(f"✅ {partidos_eliminados} partidos eliminados")
    
    # Verificar que no queden partidos
    verificacion = db.execute(text("""
        SELECT COUNT(*) as total 
        FROM partidos 
        WHERE id_torneo = 17 AND fase = 'zona'
    """)).fetchone()
    
    print(f"📊 Partidos restantes: {verificacion.total}")
    
    if verificacion.total == 0:
        print("✅ Fixture limpiado correctamente")
    else:
        print("❌ Aún quedan partidos")
    
    db.close()

if __name__ == "__main__":
    limpiar_fixture()