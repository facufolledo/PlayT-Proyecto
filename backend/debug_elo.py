"""
Debug del cálculo de Elo - Verificar qué está pasando
"""
import pg8000

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
print("DEBUG: Verificar datos de partidos y Elo")
print("=" * 60)

# Ver los últimos partidos con sus resultados
cursor.execute("""
    SELECT 
        p.id_partido,
        p.ganador_equipo,
        r.sets_eq1,
        r.sets_eq2,
        r.detalle_sets
    FROM partidos p
    LEFT JOIN resultados_partidos r ON p.id_partido = r.id_partido
    WHERE p.tipo IS NULL OR p.tipo = 'amistoso'
    ORDER BY p.creado_en DESC
    LIMIT 5
""")

partidos = cursor.fetchall()
print("\n📊 ÚLTIMOS PARTIDOS:")
for p in partidos:
    print(f"  Partido {p[0]}: ganador_equipo={p[1]}, sets_eq1={p[2]}, sets_eq2={p[3]}")
    print(f"    detalle_sets: {p[4]}")

# Ver historial de rating
cursor.execute("""
    SELECT 
        h.id_partido,
        h.id_usuario,
        u.nombre_usuario,
        h.rating_antes,
        h.delta,
        h.rating_despues,
        pj.equipo
    FROM historial_rating h
    JOIN usuarios u ON h.id_usuario = u.id_usuario
    JOIN partido_jugadores pj ON h.id_partido = pj.id_partido AND h.id_usuario = pj.id_usuario
    ORDER BY h.creado_en DESC
    LIMIT 20
""")

historial = cursor.fetchall()
print("\n📈 HISTORIAL DE RATING:")
for h in historial:
    signo = "+" if h[4] > 0 else ""
    print(f"  Partido {h[0]}: {h[2]} (equipo {h[6]}): {h[3]} → {h[5]} ({signo}{h[4]})")

# Verificar si el ganador tiene delta positivo
print("\n🔍 VERIFICACIÓN:")
for h in historial:
    partido_id = h[0]
    equipo = h[6]
    delta = h[4]
    
    # Buscar el partido
    for p in partidos:
        if p[0] == partido_id:
            ganador_equipo = p[1]
            es_ganador = (equipo == ganador_equipo)
            
            if es_ganador and delta < 0:
                print(f"  ❌ ERROR: {h[2]} GANÓ pero tiene delta NEGATIVO ({delta})")
            elif not es_ganador and delta > 0:
                print(f"  ❌ ERROR: {h[2]} PERDIÓ pero tiene delta POSITIVO ({delta})")
            elif es_ganador and delta > 0:
                print(f"  ✅ OK: {h[2]} GANÓ y tiene delta POSITIVO ({delta})")
            elif not es_ganador and delta < 0:
                print(f"  ✅ OK: {h[2]} PERDIÓ y tiene delta NEGATIVO ({delta})")
            break

cursor.close()
conn.close()
