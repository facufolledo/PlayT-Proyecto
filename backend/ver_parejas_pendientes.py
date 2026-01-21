"""
Script para ver parejas pendientes de confirmación en torneos
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def ver_parejas_pendientes(torneo_id=None):
    """Ver parejas pendientes de confirmación"""
    session = Session()
    
    try:
        print(f"\n{'='*100}")
        print(f"PAREJAS PENDIENTES DE CONFIRMACIÓN")
        print(f"{'='*100}\n")
        
        # Query para obtener parejas pendientes
        query = text("""
            SELECT 
                pt.id_pareja,
                pt.id_torneo,
                t.nombre as torneo_nombre,
                pt.nombre_pareja,
                pt.jugador1_id,
                u1.nombre_usuario as jugador1_username,
                p1.nombre as jugador1_nombre,
                p1.apellido as jugador1_apellido,
                pt.jugador2_id,
                u2.nombre_usuario as jugador2_username,
                p2.nombre as jugador2_nombre,
                p2.apellido as jugador2_apellido,
                pt.confirmado_jugador1,
                pt.confirmado_jugador2,
                pt.estado,
                pt.created_at
            FROM parejas_torneo pt
            INNER JOIN torneos t ON pt.id_torneo = t.id_torneo
            LEFT JOIN usuarios u1 ON pt.jugador1_id = u1.id_usuario
            LEFT JOIN perfil_usuario p1 ON u1.id_usuario = p1.id_usuario
            LEFT JOIN usuarios u2 ON pt.jugador2_id = u2.id_usuario
            LEFT JOIN perfil_usuario p2 ON u2.id_usuario = p2.id_usuario
            WHERE pt.estado = 'pendiente'
            """ + (f" AND pt.id_torneo = {torneo_id}" if torneo_id else "") + """
            ORDER BY pt.created_at DESC
        """)
        
        result = session.execute(query)
        parejas = result.fetchall()
        
        if not parejas:
            print("✅ No hay parejas pendientes de confirmación")
            return
        
        print(f"⚠️  Encontradas {len(parejas)} parejas pendientes:\n")
        
        for pareja in parejas:
            print(f"{'─'*100}")
            print(f"ID Pareja: {pareja.id_pareja}")
            print(f"Torneo: {pareja.torneo_nombre} (ID: {pareja.id_torneo})")
            print(f"Nombre Pareja: {pareja.nombre_pareja}")
            print(f"\nJugador 1:")
            print(f"  ID: {pareja.jugador1_id}")
            print(f"  Username: @{pareja.jugador1_username}")
            print(f"  Nombre: {pareja.jugador1_nombre} {pareja.jugador1_apellido}")
            print(f"  Confirmado: {'✅ SÍ' if pareja.confirmado_jugador1 else '❌ NO'}")
            
            print(f"\nJugador 2:")
            print(f"  ID: {pareja.jugador2_id}")
            print(f"  Username: @{pareja.jugador2_username}")
            print(f"  Nombre: {pareja.jugador2_nombre} {pareja.jugador2_apellido}")
            print(f"  Confirmado: {'✅ SÍ' if pareja.confirmado_jugador2 else '❌ NO'}")
            
            print(f"\nEstado: {pareja.estado}")
            print(f"Fecha creación: {pareja.created_at}")
            
            # Determinar quién falta confirmar
            if not pareja.confirmado_jugador1 and not pareja.confirmado_jugador2:
                print(f"\n⚠️  AMBOS jugadores deben confirmar")
            elif not pareja.confirmado_jugador1:
                print(f"\n⚠️  Falta confirmar: {pareja.jugador1_nombre} {pareja.jugador1_apellido} (@{pareja.jugador1_username})")
            elif not pareja.confirmado_jugador2:
                print(f"\n⚠️  Falta confirmar: {pareja.jugador2_nombre} {pareja.jugador2_apellido} (@{pareja.jugador2_username})")
            
            print()
        
        # Resumen por torneo
        print(f"\n{'='*100}")
        print("RESUMEN POR TORNEO")
        print(f"{'='*100}\n")
        
        query_resumen = text("""
            SELECT 
                t.id_torneo,
                t.nombre,
                COUNT(*) as parejas_pendientes,
                COUNT(CASE WHEN NOT pt.confirmado_jugador1 THEN 1 END) as falta_j1,
                COUNT(CASE WHEN NOT pt.confirmado_jugador2 THEN 1 END) as falta_j2
            FROM parejas_torneo pt
            INNER JOIN torneos t ON pt.id_torneo = t.id_torneo
            WHERE pt.estado = 'pendiente'
            GROUP BY t.id_torneo, t.nombre
            ORDER BY parejas_pendientes DESC
        """)
        
        result_resumen = session.execute(query_resumen)
        resumen = result_resumen.fetchall()
        
        for r in resumen:
            print(f"Torneo: {r.nombre} (ID: {r.id_torneo})")
            print(f"  Parejas pendientes: {r.parejas_pendientes}")
            print(f"  Falta confirmar jugador 1: {r.falta_j1}")
            print(f"  Falta confirmar jugador 2: {r.falta_j2}")
            print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()


def ver_parejas_confirmadas(torneo_id=None):
    """Ver parejas ya confirmadas"""
    session = Session()
    
    try:
        print(f"\n{'='*100}")
        print(f"PAREJAS CONFIRMADAS")
        print(f"{'='*100}\n")
        
        query = text("""
            SELECT 
                pt.id_pareja,
                pt.id_torneo,
                t.nombre as torneo_nombre,
                pt.nombre_pareja,
                u1.nombre_usuario as jugador1_username,
                p1.nombre as jugador1_nombre,
                p1.apellido as jugador1_apellido,
                u2.nombre_usuario as jugador2_username,
                p2.nombre as jugador2_nombre,
                p2.apellido as jugador2_apellido,
                pt.estado
            FROM parejas_torneo pt
            INNER JOIN torneos t ON pt.id_torneo = t.id_torneo
            LEFT JOIN usuarios u1 ON pt.jugador1_id = u1.id_usuario
            LEFT JOIN perfil_usuario p1 ON u1.id_usuario = p1.id_usuario
            LEFT JOIN usuarios u2 ON pt.jugador2_id = u2.id_usuario
            LEFT JOIN perfil_usuario p2 ON u2.id_usuario = p2.id_usuario
            WHERE pt.estado = 'confirmada'
            """ + (f" AND pt.id_torneo = {torneo_id}" if torneo_id else "") + """
            ORDER BY pt.created_at DESC
        """)
        
        result = session.execute(query)
        parejas = result.fetchall()
        
        if not parejas:
            print("⚠️  No hay parejas confirmadas todavía")
            return
        
        print(f"✅ Encontradas {len(parejas)} parejas confirmadas:\n")
        
        for pareja in parejas:
            print(f"• {pareja.nombre_pareja}")
            print(f"  Torneo: {pareja.torneo_nombre}")
            print(f"  Jugadores: {pareja.jugador1_nombre} {pareja.jugador1_apellido} (@{pareja.jugador1_username}) + {pareja.jugador2_nombre} {pareja.jugador2_apellido} (@{pareja.jugador2_username})")
            print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()


if __name__ == "__main__":
    import sys
    
    torneo_id = None
    if len(sys.argv) > 1:
        try:
            torneo_id = int(sys.argv[1])
            print(f"\n🎾 Filtrando por torneo ID: {torneo_id}")
        except:
            print("⚠️  ID de torneo inválido, mostrando todos los torneos")
    
    ver_parejas_pendientes(torneo_id)
    ver_parejas_confirmadas(torneo_id)
    
    print(f"\n{'='*100}")
    print("INSTRUCCIONES")
    print(f"{'='*100}")
    print("\nPara filtrar por un torneo específico:")
    print("  python ver_parejas_pendientes.py <ID_TORNEO>")
    print("\nEjemplo:")
    print("  python ver_parejas_pendientes.py 1")
    print()
