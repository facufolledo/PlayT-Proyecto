"""
Script para verificar el estado de las salas
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Cargar variables de entorno
load_dotenv()

# Configurar base de datos
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL no está configurada en .env")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def verificar_salas():
    """Verificar el estado de todas las salas"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("ESTADO DE LAS SALAS")
        print("=" * 80)
        
        # Obtener todas las salas
        query = text("""
            SELECT 
                s.id_sala,
                s.nombre,
                s.estado,
                s.id_partido,
                p.estado_confirmacion,
                p.elo_aplicado,
                COUNT(DISTINCT sj.id_usuario) as jugadores
            FROM salas s
            LEFT JOIN sala_jugadores sj ON s.id_sala = sj.id_sala
            LEFT JOIN partidos p ON s.id_partido = p.id_partido
            GROUP BY s.id_sala, s.nombre, s.estado, s.id_partido, p.estado_confirmacion, p.elo_aplicado
            ORDER BY s.creado_en DESC
        """)
        
        result = db.execute(query)
        salas = result.fetchall()
        
        if not salas:
            print("\n❌ No hay salas en la base de datos")
            return
        
        print(f"\n📊 Total de salas: {len(salas)}\n")
        
        # Agrupar por estado
        por_estado = {}
        for sala in salas:
            estado = sala.estado
            if estado not in por_estado:
                por_estado[estado] = []
            por_estado[estado].append(sala)
        
        # Mostrar resumen
        print("RESUMEN POR ESTADO:")
        print("-" * 80)
        for estado, lista in por_estado.items():
            print(f"  {estado.upper()}: {len(lista)} salas")
        
        print("\n" + "=" * 80)
        print("DETALLE DE SALAS")
        print("=" * 80)
        
        for sala in salas:
            print(f"\n🎾 Sala #{sala.id_sala}: {sala.nombre}")
            print(f"   Estado: {sala.estado}")
            print(f"   Jugadores: {sala.jugadores}/4")
            
            if sala.id_partido:
                print(f"   Partido ID: {sala.id_partido}")
                print(f"   Estado confirmación: {sala.estado_confirmacion or 'sin_resultado'}")
                print(f"   Elo aplicado: {'✅ Sí' if sala.elo_aplicado else '❌ No'}")
            else:
                print(f"   Partido: No iniciado")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    verificar_salas()
