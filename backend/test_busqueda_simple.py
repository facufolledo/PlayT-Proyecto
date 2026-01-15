"""
Test simple de búsqueda sin imports complejos
"""
import pg8000
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Parsear URL de PostgreSQL
url = urlparse(DATABASE_URL)

try:
    conn = pg8000.connect(
        host=url.hostname,
        port=url.port or 5432,
        user=url.username,
        password=url.password,
        database=url.path[1:]
    )
    cur = conn.cursor()
    
    print("=" * 60)
    print("TEST: Búsqueda de Usuarios")
    print("=" * 60)
    
    # 1. Contar usuarios
    cur.execute("SELECT COUNT(*) FROM usuarios")
    total_usuarios = cur.fetchone()[0]
    print(f"\n✅ Total usuarios: {total_usuarios}")
    
    # 2. Contar perfiles
    cur.execute("SELECT COUNT(*) FROM perfil_usuarios")
    total_perfiles = cur.fetchone()[0]
    print(f"✅ Total perfiles: {total_perfiles}")
    
    # 3. Buscar usuarios con "fac"
    cur.execute("""
        SELECT u.id_usuario, u.nombre_usuario, p.nombre, p.apellido
        FROM usuarios u
        LEFT JOIN perfil_usuarios p ON u.id_usuario = p.id_usuario
        WHERE LOWER(u.nombre_usuario) LIKE %s
           OR LOWER(p.nombre) LIKE %s
           OR LOWER(p.apellido) LIKE %s
        LIMIT 10
    """, ('%fac%', '%fac%', '%fac%'))
    
    resultados = cur.fetchall()
    print(f"\n🔍 Búsqueda con 'fac': {len(resultados)} resultados")
    for row in resultados:
        print(f"  - ID: {row[0]}, Username: {row[1]}, Nombre: {row[2]} {row[3]}")
    
    # 4. Verificar usuarios sin perfil
    cur.execute("""
        SELECT COUNT(*)
        FROM usuarios u
        LEFT JOIN perfil_usuarios p ON u.id_usuario = p.id_usuario
        WHERE p.id_usuario IS NULL
    """)
    sin_perfil = cur.fetchone()[0]
    print(f"\n⚠️  Usuarios sin perfil: {sin_perfil}")
    
    print("\n" + "=" * 60)
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
