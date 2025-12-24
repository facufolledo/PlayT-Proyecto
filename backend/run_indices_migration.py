"""
Script para ejecutar la migración de índices en Neon
Ejecutar: python run_indices_migration.py
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL no configurada en .env")
    exit(1)

print(f"🔗 Conectando a la base de datos...")

engine = create_engine(DATABASE_URL)

# Leer el archivo SQL
with open("migrations_indices_performance.sql", "r", encoding="utf-8") as f:
    sql_content = f.read()

# Separar por statements (cada CREATE INDEX)
statements = [s.strip() for s in sql_content.split(";") if s.strip() and not s.strip().startswith("--")]

print(f"📊 Ejecutando {len(statements)} índices...")

with engine.connect() as conn:
    for i, stmt in enumerate(statements, 1):
        if stmt.strip():
            try:
                conn.execute(text(stmt))
                conn.commit()
                # Extraer nombre del índice para mostrar
                if "CREATE INDEX" in stmt.upper():
                    idx_name = stmt.split("IF NOT EXISTS")[-1].split("ON")[0].strip()
                    print(f"  ✅ [{i}/{len(statements)}] {idx_name}")
            except Exception as e:
                print(f"  ⚠️ [{i}/{len(statements)}] Error: {str(e)[:50]}")

print("\n✅ Migración de índices completada!")
print("\n📋 Para verificar los índices creados, ejecutá en Neon SQL Editor:")
print("   SELECT indexname, tablename FROM pg_indexes WHERE schemaname = 'public' ORDER BY tablename;")
