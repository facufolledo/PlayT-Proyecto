"""
Script para verificar y corregir categoria_id en zonas existentes
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.database.config import SessionLocal
from src.models.torneo_models import TorneoZona, TorneoPareja, TorneoZonaPareja

def verificar_y_corregir_zonas():
    db: Session = SessionLocal()
    
    try:
        torneo_id = 11
        
        print(f"\n{'='*60}")
        print(f"VERIFICACIÓN DE ZONAS - TORNEO {torneo_id}")
        print(f"{'='*60}\n")
        
        # Obtener todas las zonas del torneo
        zonas = db.query(TorneoZona).filter(
            TorneoZona.torneo_id == torneo_id
        ).order_by(TorneoZona.numero_orden).all()
        
        print(f"📊 Zonas encontradas: {len(zonas)}\n")
        
        for zona in zonas:
            print(f"Zona: {zona.nombre} (ID: {zona.id})")
            print(f"  categoria_id actual: {zona.categoria_id}")
            
            # Obtener parejas de esta zona
            parejas = db.query(TorneoPareja).join(
                TorneoZonaPareja,
                TorneoZonaPareja.pareja_id == TorneoPareja.id
            ).filter(
                TorneoZonaPareja.zona_id == zona.id
            ).all()
            
            print(f"  Parejas en zona: {len(parejas)}")
            
            if parejas:
                # Verificar categorías de las parejas
                categorias_parejas = set()
                for pareja in parejas:
                    print(f"    - Pareja {pareja.id}: categoria_id={pareja.categoria_id}")
                    if pareja.categoria_id:
                        categorias_parejas.add(pareja.categoria_id)
                
                # Si todas las parejas tienen la misma categoría y la zona no la tiene
                if len(categorias_parejas) == 1 and not zona.categoria_id:
                    categoria_correcta = list(categorias_parejas)[0]
                    print(f"  ⚠️  CORRECCIÓN NECESARIA: Asignar categoria_id={categoria_correcta}")
                    
                    # Actualizar zona
                    zona.categoria_id = categoria_correcta
                    db.commit()
                    print(f"  ✅ Zona actualizada con categoria_id={categoria_correcta}")
                elif len(categorias_parejas) > 1:
                    print(f"  ❌ ERROR: Parejas de diferentes categorías en la misma zona!")
                elif zona.categoria_id:
                    print(f"  ✅ Zona ya tiene categoria_id correcto")
                else:
                    print(f"  ⚠️  Parejas sin categoria_id asignado")
            
            print()
        
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verificar_y_corregir_zonas()
