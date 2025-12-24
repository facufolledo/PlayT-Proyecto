"""
Script para limpiar partidos e historiales de la base de datos
Útil para testing y resetear el límite de partidos
"""
import pg8000
from datetime import datetime

# Conexión a la base de datos
conn = pg8000.connect(
    host="ep-dawn-frost-ac67h4ke-pooler.sa-east-1.aws.neon.tech",
    database="neondb",
    user="neondb_owner",
    password="npg_i2uqcNEZbk4M",
    ssl_context=True
)

cursor = conn.cursor()

print("=" * 60)
print("LIMPIEZA DE PARTIDOS E HISTORIALES")
print("=" * 60)

# Ver cuántos registros hay antes
cursor.execute("SELECT COUNT(*) FROM historial_rating")
historial_count = cursor.fetchone()[0]
print(f"\nHistorial de rating: {historial_count} registros")

cursor.execute("SELECT COUNT(*) FROM historial_enfrentamientos")
enfrentamientos_count = cursor.fetchone()[0]
print(f"Historial enfrentamientos: {enfrentamientos_count} registros")

cursor.execute("SELECT COUNT(*) FROM confirmaciones")
confirmaciones_count = cursor.fetchone()[0]
print(f"Confirmaciones: {confirmaciones_count} registros")

cursor.execute("SELECT COUNT(*) FROM resultados_partidos")
resultados_count = cursor.fetchone()[0]
print(f"Resultados partidos: {resultados_count} registros")

cursor.execute("SELECT COUNT(*) FROM partido_jugadores")
jugadores_count = cursor.fetchone()[0]
print(f"Partido jugadores: {jugadores_count} registros")

cursor.execute("SELECT COUNT(*) FROM partidos WHERE tipo IS NULL OR tipo = 'amistoso'")
partidos_count = cursor.fetchone()[0]
print(f"Partidos amistosos: {partidos_count} registros")

cursor.execute("SELECT COUNT(*) FROM salas")
salas_count = cursor.fetchone()[0]
print(f"Salas: {salas_count} registros")

print("\n" + "=" * 60)
print("ELIMINANDO REGISTROS...")
print("=" * 60)

# Eliminar en orden correcto (por foreign keys)
cursor.execute("DELETE FROM historial_rating")
print(f"✓ Historial rating eliminado")

cursor.execute("DELETE FROM historial_enfrentamientos")
print(f"✓ Historial enfrentamientos eliminado")

cursor.execute("DELETE FROM confirmaciones")
print(f"✓ Confirmaciones eliminadas")

cursor.execute("DELETE FROM resultados_partidos")
print(f"✓ Resultados partidos eliminados")

cursor.execute("DELETE FROM partido_jugadores")
print(f"✓ Partido jugadores eliminados")

# Primero eliminar salas (tienen FK a partidos)
cursor.execute("DELETE FROM salas")
print(f"✓ Salas eliminadas")

# Luego eliminar partidos amistosos (no de torneo)
cursor.execute("DELETE FROM partidos WHERE tipo IS NULL OR tipo = 'amistoso'")
print(f"✓ Partidos amistosos eliminados")

# Resetear partidos_jugados de usuarios a 0
cursor.execute("UPDATE usuarios SET partidos_jugados = 0")
print(f"✓ Contador de partidos de usuarios reseteado")

conn.commit()

print("\n" + "=" * 60)
print("✅ LIMPIEZA COMPLETADA")
print("=" * 60)

cursor.close()
conn.close()
