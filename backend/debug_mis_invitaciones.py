#!/usr/bin/env python3
"""
Script para debuggear el endpoint mis-invitaciones
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from src.database.config import get_db
from src.models.torneo_models import TorneoPareja, Torneo
from src.models.driveplus_models import PerfilUsuario, Usuario

def debug_mis_invitaciones():
    """Debug del endpoint mis-invitaciones"""
    db = next(get_db())
    
    try:
        print("=== DEBUG MIS INVITACIONES ===")
        
        # 1. Verificar que las tablas existen
        print("\n1. Verificando estructura de TorneoPareja...")
        parejas_sample = db.query(TorneoPareja).limit(3).all()
        print(f"   - Total parejas en DB: {db.query(TorneoPareja).count()}")
        
        if parejas_sample:
            pareja = parejas_sample[0]
            print(f"   - Campos disponibles: {dir(pareja)}")
            print(f"   - Estado ejemplo: '{pareja.estado}' (tipo: {type(pareja.estado)})")
            print(f"   - Confirmado jugador1: {getattr(pareja, 'confirmado_jugador1', 'NO EXISTE')}")
            print(f"   - Confirmado jugador2: {getattr(pareja, 'confirmado_jugador2', 'NO EXISTE')}")
        
        # 2. Buscar parejas pendientes
        print("\n2. Buscando parejas con estado 'pendiente'...")
        parejas_pendientes = db.query(TorneoPareja).filter(
            TorneoPareja.estado == 'pendiente'
        ).all()
        print(f"   - Parejas pendientes: {len(parejas_pendientes)}")
        
        for p in parejas_pendientes[:3]:  # Solo primeras 3
            print(f"   - Pareja {p.id}: jugador1={p.jugador1_id}, jugador2={p.jugador2_id}, estado='{p.estado}'")
        
        # 3. Verificar usuarios existentes
        print("\n3. Verificando usuarios...")
        usuarios_count = db.query(Usuario).count()
        print(f"   - Total usuarios: {usuarios_count}")
        
        # 4. Probar la query completa con un usuario específico
        print("\n4. Probando query completa...")
        if parejas_pendientes:
            test_user_id = parejas_pendientes[0].jugador2_id
            print(f"   - Probando con usuario ID: {test_user_id}")
            
            try:
                parejas_usuario = db.query(TorneoPareja).filter(
                    TorneoPareja.jugador2_id == test_user_id,
                    TorneoPareja.estado == 'pendiente'
                ).all()
                print(f"   - Parejas para usuario {test_user_id}: {len(parejas_usuario)}")
                
                # Probar con el filtro adicional
                if hasattr(TorneoPareja, 'confirmado_jugador2'):
                    parejas_no_confirmadas = db.query(TorneoPareja).filter(
                        TorneoPareja.jugador2_id == test_user_id,
                        TorneoPareja.estado == 'pendiente',
                        TorneoPareja.confirmado_jugador2 == False
                    ).all()
                    print(f"   - Parejas no confirmadas: {len(parejas_no_confirmadas)}")
                else:
                    print("   - Campo 'confirmado_jugador2' NO EXISTE en la tabla")
                    
            except Exception as e:
                print(f"   - ERROR en query: {e}")
        
        # 5. Verificar estados únicos
        print("\n5. Estados únicos en la tabla...")
        from sqlalchemy import distinct
        estados = db.query(distinct(TorneoPareja.estado)).all()
        print(f"   - Estados encontrados: {[e[0] for e in estados]}")
        
    except Exception as e:
        print(f"ERROR GENERAL: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_mis_invitaciones()