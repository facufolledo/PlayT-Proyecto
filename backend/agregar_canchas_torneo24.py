#!/usr/bin/env python3
"""
Script para agregar 3 canchas al torneo 24
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.config import get_db
from src.models.torneo_models import Torneo, TorneoCancha

def agregar_canchas():
    """Agregar 3 canchas al torneo 24"""
    db = next(get_db())
    
    try:
        torneo_id = 24
        
        # Verificar que el torneo existe
        torneo = db.query(Torneo).filter(Torneo.id == torneo_id).first()
        if not torneo:
            print(f"❌ Torneo {torneo_id} no existe")
            return False
        
        print(f"🏆 Torneo: {torneo.nombre}")
        
        # Verificar canchas existentes
        canchas_existentes = db.query(TorneoCancha).filter(TorneoCancha.torneo_id == torneo_id).all()
        if canchas_existentes:
            print(f"⚠️ Ya existen {len(canchas_existentes)} canchas:")
            for c in canchas_existentes:
                print(f"   - {c.nombre} (ID: {c.id})")
            print(f"\n🗑️ Eliminando canchas existentes...")
            for c in canchas_existentes:
                db.delete(c)
            db.flush()
        
        # Crear 3 canchas
        print(f"\n🏟️ Creando 3 canchas...")
        canchas = []
        for i in range(1, 4):
            cancha = TorneoCancha(
                torneo_id=torneo_id,
                nombre=f"Cancha {i}",
                activa=True
            )
            db.add(cancha)
            db.flush()
            canchas.append(cancha)
            print(f"   ✅ {cancha.nombre} (ID: {cancha.id})")
        
        db.commit()
        
        print(f"\n{'='*60}")
        print(f"✅ ¡3 CANCHAS AGREGADAS AL TORNEO {torneo_id}!")
        print(f"{'='*60}")
        print(f"🏟️ Total canchas: {len(canchas)}")
        for c in canchas:
            print(f"   • {c.nombre} (ID: {c.id})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🏟️ AGREGANDO CANCHAS AL TORNEO 24")
    print("="*60)
    if agregar_canchas():
        print(f"\n✅ Canchas agregadas exitosamente")
    else:
        print(f"\n❌ Error al agregar canchas")
