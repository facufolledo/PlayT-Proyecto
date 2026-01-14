"""
Script para eliminar parejas dadas de baja del torneo 9
"""
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    # Buscar parejas dadas de baja en el torneo 9
    result = conn.execute(text("""
        SELECT id, jugador1_id, jugador2_id, estado 
        FROM torneos_parejas 
        WHERE torneo_id = 9 AND estado = 'baja'
    """))
    
    parejas = result.fetchall()
    
    if not parejas:
        print("No hay parejas dadas de baja en el torneo 9")
    else:
        print(f"\nEncontradas {len(parejas)} parejas dadas de baja:")
        for p in parejas:
            print(f"  ID: {p[0]}, Jugador1: {p[1]}, Jugador2: {p[2]}, Estado: {p[3]}")
        
        # Eliminar las parejas
        conn.execute(text("""
            DELETE FROM torneos_parejas 
            WHERE torneo_id = 9 AND estado = 'baja'
        """))
        conn.commit()
        
        print(f"\n✅ {len(parejas)} pareja(s) eliminada(s) exitosamente")
        print("Ahora pueden volver a inscribirse")
