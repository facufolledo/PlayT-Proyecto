from src.database.config import engine
from sqlalchemy import text

conn = engine.connect()
result = conn.execute(text("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema='public' 
    AND table_name IN ('resultados_padel', 'confirmaciones_usuarios')
""")).fetchall()

print('Tablas encontradas:', [r[0] for r in result])
conn.close()
