from src.database.config import engine
from sqlalchemy import text

conn = engine.connect()
result = conn.execute(text("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'usuarios' 
    ORDER BY ordinal_position
"""))

print("\n" + "="*60)
print("ESTRUCTURA DE LA TABLA USUARIOS")
print("="*60)
for r in result.fetchall():
    print(f"{r[0]:30s} {r[1]}")

conn.close()
