"""
Script simple para actualizar la sala 18 a estado en_juego
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Cargar variables de entorno
load_dotenv()

# Configurar base de datos
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

print("Actualizando sala 18...")

with engine.connect() as conn:
    # Ver estado actual
    result = conn.execute(text("""
        SELECT id_sala, nombre, estado 
        FROM salas 
        WHERE id_sala = 18
    """))
    sala = result.fetchone()
    
    if sala:
        print(f"Estado actual: {sala.estado}")
        
        # Actualizar
        conn.execute(text("""
            UPDATE salas 
            SET estado = 'en_juego'
            WHERE id_sala = 18
        """))
        conn.commit()
        
        print("✅ Sala actualizada a 'en_juego'")
    else:
        print("❌ Sala no encontrada")
