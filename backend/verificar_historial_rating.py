"""
Script para verificar historial de rating de partidos 19 y 20
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# Crear engine
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

print("=" * 100)
print("HISTORIAL DE RATING PARA PARTIDOS 19 Y 20")
print("=" * 100)

query = text("""
    SELECT 
        hr.id_historial,
        hr.id_partido,
        hr.id_usuario,
        u.nombre_usuario,
        hr.rating_antes,
        hr.delta,
        hr.rating_despues
    FROM historial_rating hr
    LEFT JOIN usuarios u ON hr.id_usuario = u.id_usuario
    WHERE hr.id_partido IN (19, 20)
    ORDER BY hr.id_partido, hr.id_usuario
""")

result = db.execute(query)
historiales = result.fetchall()

if len(historiales) == 0:
    print("\n❌ No hay historial de rating para estos partidos")
else:
    print(f"\n✅ Historiales encontrados: {len(historiales)}\n")
    
    partido_actual = None
    for historial in historiales:
        if partido_actual != historial.id_partido:
            partido_actual = historial.id_partido
            print(f"\n--- Partido {historial.id_partido} ---")
        
        print(f"{historial.nombre_usuario} (ID: {historial.id_usuario})")
        print(f"  Rating antes: {historial.rating_antes}")
        print(f"  Delta: {historial.delta:+d}")
        print(f"  Rating después: {historial.rating_despues}")

db.close()
