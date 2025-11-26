from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL'))
conn = engine.connect()

# Ver constraints de la tabla partidos
result = conn.execute(text("""
    SELECT conname, pg_get_constraintdef(oid) 
    FROM pg_constraint 
    WHERE conrelid = 'partidos'::regclass AND contype = 'c'
"""))

print("Constraints en tabla 'partidos':")
for row in result:
    print(f"  {row[0]}: {row[1]}")
