"""
Test para verificar que las restricciones se guardan correctamente al inscribir
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.database.config import get_db
from src.models.torneo_models import TorneoPareja, Torneo
from src.models.driveplus_models import Usuario
import json

def test_inscripcion():
    db = next(get_db())
    
    try:
        print("=" * 80)
        print("TEST: Inscripción con restricciones horarias")
        print("=" * 80)
        
        # Crear un torneo de prueba
        from datetime import datetime, timedelta
        
        torneo = Torneo(
            nombre="Test Restricciones",
            descripcion="Torneo de prueba",
            categoria="5ta",
            estado="inscripcion",
            fecha_inicio=datetime.now().date(),
            fecha_fin=(datetime.now() + timedelta(days=7)).date(),
            creado_por=1
        )
        db.add(torneo)
        db.flush()
        
        torneo_id = torneo.id
        print(f"\nTorneo creado: ID {torneo_id}")
        
        # Obtener 2 usuarios para la pareja
        usuarios = db.query(Usuario).limit(2).all()
        
        if len(usuarios) < 2:
            print("\nNo hay suficientes usuarios en la BD para el test")
            db.rollback()
            return
        
        jugador1_id = usuarios[0].id_usuario
        jugador2_id = usuarios[1].id_usuario
        
        print(f"Jugador 1: ID {jugador1_id}")
        print(f"Jugador 2: ID {jugador2_id}")
        
        # Crear pareja con restricciones (simulando lo que envía el frontend)
        restricciones = [
            {
                "dias": ["viernes", "sabado"],
                "horaInicio": "09:00",
                "horaFin": "14:00"
            },
            {
                "dias": ["domingo"],
                "horaInicio": "16:00",
                "horaFin": "20:00"
            }
        ]
        
        print(f"\nRestricciones a guardar:")
        print(json.dumps(restricciones, indent=2, ensure_ascii=False))
        
        pareja = TorneoPareja(
            torneo_id=torneo_id,
            jugador1_id=jugador1_id,
            jugador2_id=jugador2_id,
            estado='confirmada',
            disponibilidad_horaria=restricciones
        )
        
        db.add(pareja)
        db.flush()
        
        pareja_id = pareja.id
        print(f"\nPareja creada: ID {pareja_id}")
        
        # Verificar que se guardó correctamente
        pareja_verificada = db.query(TorneoPareja).filter(
            TorneoPareja.id == pareja_id
        ).first()
        
        print(f"\nRestricciones guardadas en BD:")
        if pareja_verificada.disponibilidad_horaria:
            print(json.dumps(pareja_verificada.disponibilidad_horaria, indent=2, ensure_ascii=False))
            print("\n✅ Las restricciones se guardaron correctamente")
            
            # Verificar que el formato es correcto
            if isinstance(pareja_verificada.disponibilidad_horaria, list):
                print("✅ El formato es un array (correcto)")
                
                for i, restriccion in enumerate(pareja_verificada.disponibilidad_horaria):
                    if 'dias' in restriccion and 'horaInicio' in restriccion and 'horaFin' in restriccion:
                        print(f"✅ Restricción {i+1} tiene todos los campos necesarios")
                    else:
                        print(f"❌ Restricción {i+1} le faltan campos")
            else:
                print("❌ El formato NO es un array")
        else:
            print("❌ Las restricciones NO se guardaron (NULL)")
        
        # Limpiar
        db.rollback()
        print("\n✅ Test completado (cambios revertidos)")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_inscripcion()
