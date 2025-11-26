"""
Script para verificar la conexión a la base de datos y mostrar datos de prueba
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Cargar variables de entorno
load_dotenv()

def test_connection():
    """Probar conexión a la base de datos"""
    print("=" * 60)
    print("🔍 VERIFICANDO CONEXIÓN A BASE DE DATOS")
    print("=" * 60)
    
    # Obtener URL de la base de datos
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ ERROR: No se encontró DATABASE_URL en .env")
        return False
    
    print(f"\n📍 URL de conexión: {database_url[:50]}...")
    
    try:
        # Crear engine
        engine = create_engine(database_url)
        
        # Probar conexión
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Conexión exitosa a la base de datos\n")
            
            # Verificar tablas
            print("=" * 60)
            print("📊 TABLAS EN LA BASE DE DATOS")
            print("=" * 60)
            
            tables_query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            
            tables = conn.execute(tables_query).fetchall()
            
            if not tables:
                print("⚠️  No se encontraron tablas en la base de datos")
                return False
            
            print(f"\n✅ Se encontraron {len(tables)} tablas:\n")
            for table in tables:
                print(f"   • {table[0]}")
            
            # Verificar datos de prueba
            print("\n" + "=" * 60)
            print("👥 DATOS DE PRUEBA - USUARIOS")
            print("=" * 60)
            
            usuarios_query = text("""
                SELECT 
                    u.id_usuario,
                    u.nombre_usuario,
                    u.email,
                    u.rating,
                    p.nombre,
                    p.apellido,
                    p.genero
                FROM usuarios u
                LEFT JOIN perfil_usuario p ON u.id_usuario = p.id_usuario
                LIMIT 10
            """)
            
            usuarios = conn.execute(usuarios_query).fetchall()
            
            if not usuarios:
                print("\n⚠️  No hay usuarios en la base de datos")
                print("\n💡 Ejecuta el script para crear datos de prueba:")
                print("   python backend/create_test_user.py")
            else:
                print(f"\n✅ Se encontraron {len(usuarios)} usuarios:\n")
                for u in usuarios:
                    print(f"   ID: {u[0]} | Usuario: {u[1]} | Email: {u[2]}")
                    print(f"   Rating: {u[3]} | Nombre: {u[4]} {u[5]} | Género: {u[6]}")
                    print()
            
            # Verificar salas
            print("=" * 60)
            print("🏠 DATOS DE PRUEBA - SALAS")
            print("=" * 60)
            
            salas_query = text("""
                SELECT 
                    s.id_sala,
                    s.nombre,
                    s.codigo_invitacion,
                    s.estado,
                    s.fecha,
                    COUNT(sj.id_usuario) as jugadores
                FROM salas s
                LEFT JOIN sala_jugadores sj ON s.id_sala = sj.id_sala
                GROUP BY s.id_sala
                ORDER BY s.creado_en DESC
                LIMIT 10
            """)
            
            salas = conn.execute(salas_query).fetchall()
            
            if not salas:
                print("\n⚠️  No hay salas en la base de datos")
                print("\n💡 Las salas se crean desde la aplicación")
            else:
                print(f"\n✅ Se encontraron {len(salas)} salas:\n")
                for s in salas:
                    print(f"   ID: {s[0]} | Nombre: {s[1]}")
                    print(f"   Código: {s[2]} | Estado: {s[3]}")
                    print(f"   Fecha: {s[4]} | Jugadores: {s[5]}/4")
                    print()
            
            # Verificar partidos
            print("=" * 60)
            print("🎾 DATOS DE PRUEBA - PARTIDOS")
            print("=" * 60)
            
            partidos_query = text("""
                SELECT 
                    p.id_partido,
                    p.fecha,
                    p.estado,
                    p.resultado_equipo_1,
                    p.resultado_equipo_2,
                    COUNT(pj.id_usuario) as jugadores
                FROM partidos p
                LEFT JOIN partido_jugadores pj ON p.id_partido = pj.id_partido
                GROUP BY p.id_partido
                ORDER BY p.fecha DESC
                LIMIT 10
            """)
            
            partidos = conn.execute(partidos_query).fetchall()
            
            if not partidos:
                print("\n⚠️  No hay partidos en la base de datos")
            else:
                print(f"\n✅ Se encontraron {len(partidos)} partidos:\n")
                for p in partidos:
                    print(f"   ID: {p[0]} | Fecha: {p[1]} | Estado: {p[2]}")
                    print(f"   Resultado: {p[3]} - {p[4]} | Jugadores: {p[5]}")
                    print()
            
            print("=" * 60)
            print("✅ VERIFICACIÓN COMPLETADA")
            print("=" * 60)
            
            return True
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\n💡 Verifica que:")
        print("   1. La URL de la base de datos sea correcta")
        print("   2. Las credenciales sean válidas")
        print("   3. La base de datos esté accesible")
        return False

if __name__ == "__main__":
    test_connection()
