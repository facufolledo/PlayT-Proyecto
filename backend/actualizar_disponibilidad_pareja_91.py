"""
Actualizar disponibilidad de la pareja 91 (Facundo y Facundito)
"""
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.models.torneo_models import TorneoPareja

load_dotenv()

def actualizar_disponibilidad():
    print("=" * 80)
    print("ACTUALIZAR DISPONIBILIDAD: PAREJA 91")
    print("=" * 80)
    
    try:
        database_url = os.getenv("DATABASE_URL")
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        # Buscar la pareja
        pareja = db.query(TorneoPareja).filter(TorneoPareja.id == 91).first()
        
        if not pareja:
            print("\n❌ No se encontró la pareja")
            return
        
        print(f"\n🎾 Pareja encontrada:")
        print(f"   ID: {pareja.id}")
        print(f"   Jugador 1: {pareja.jugador1_id}")
        print(f"   Jugador 2: {pareja.jugador2_id}")
        print(f"   Disponibilidad actual: {pareja.disponibilidad_horaria}")
        
        # Actualizar disponibilidad: jueves y viernes de 19:00 a 22:00
        nueva_disponibilidad = {
            'franjas': [
                {
                    'dias': ['jueves', 'viernes'],
                    'horaInicio': '19:00',
                    'horaFin': '22:00'
                }
            ]
        }
        
        pareja.disponibilidad_horaria = nueva_disponibilidad
        db.commit()
        
        print(f"\n✅ Disponibilidad actualizada:")
        print(f"   {nueva_disponibilidad}")
        print(f"\n   Esto significa:")
        print(f"   • Jueves: 19:00-22:00")
        print(f"   • Viernes: 19:00-22:00")
        print(f"   • Sábado: TODO EL DÍA (no restringido)")
        print(f"   • Domingo: TODO EL DÍA (no restringido)")
        
        db.close()
        
        print(f"\n✅ Ahora debes ELIMINAR y REGENERAR el fixture para que tome efecto")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    actualizar_disponibilidad()
