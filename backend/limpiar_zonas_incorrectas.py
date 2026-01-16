"""
Script para eliminar zonas con parejas de diferentes categorías
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.database.config import SessionLocal
from src.models.torneo_models import TorneoZona, TorneoPareja, TorneoZonaPareja, TorneoTablaPosiciones
from src.models.driveplus_models import Partido

def limpiar_zonas_incorrectas():
    db: Session = SessionLocal()
    
    try:
        torneo_id = 11
        
        print(f"\n{'='*60}")
        print(f"LIMPIEZA DE ZONAS INCORRECTAS - TORNEO {torneo_id}")
        print(f"{'='*60}\n")
        
        # Obtener todas las zonas del torneo
        zonas = db.query(TorneoZona).filter(
            TorneoZona.torneo_id == torneo_id
        ).order_by(TorneoZona.numero_orden).all()
        
        zonas_a_eliminar = []
        
        for zona in zonas:
            # Obtener parejas de esta zona
            parejas = db.query(TorneoPareja).join(
                TorneoZonaPareja,
                TorneoZonaPareja.pareja_id == TorneoPareja.id
            ).filter(
                TorneoZonaPareja.zona_id == zona.id
            ).all()
            
            if not parejas:
                print(f"⚠️  Zona {zona.nombre} (ID: {zona.id}) está vacía - ELIMINAR")
                zonas_a_eliminar.append(zona.id)
                continue
            
            # Verificar categorías de las parejas
            categorias_parejas = set()
            for pareja in parejas:
                if pareja.categoria_id:
                    categorias_parejas.add(pareja.categoria_id)
            
            # Si hay más de una categoría, la zona está mal
            if len(categorias_parejas) > 1:
                print(f"❌ Zona {zona.nombre} (ID: {zona.id}) tiene parejas de {len(categorias_parejas)} categorías diferentes - ELIMINAR")
                zonas_a_eliminar.append(zona.id)
            elif len(categorias_parejas) == 0:
                print(f"⚠️  Zona {zona.nombre} (ID: {zona.id}) tiene parejas sin categoría - ELIMINAR")
                zonas_a_eliminar.append(zona.id)
            else:
                print(f"✅ Zona {zona.nombre} (ID: {zona.id}) está correcta (categoría {list(categorias_parejas)[0]})")
        
        if not zonas_a_eliminar:
            print(f"\n✅ No hay zonas incorrectas para eliminar")
            return
        
        print(f"\n{'='*60}")
        print(f"ELIMINANDO {len(zonas_a_eliminar)} ZONAS INCORRECTAS")
        print(f"{'='*60}\n")
        
        # Eliminar partidos de estas zonas
        partidos_eliminados = db.query(Partido).filter(
            Partido.zona_id.in_(zonas_a_eliminar)
        ).delete(synchronize_session=False)
        print(f"✅ Eliminados {partidos_eliminados} partidos")
        
        # Eliminar tablas de posiciones
        tablas_eliminadas = db.query(TorneoTablaPosiciones).filter(
            TorneoTablaPosiciones.zona_id.in_(zonas_a_eliminar)
        ).delete(synchronize_session=False)
        print(f"✅ Eliminadas {tablas_eliminadas} tablas de posiciones")
        
        # Eliminar relaciones zona-pareja
        relaciones_eliminadas = db.query(TorneoZonaPareja).filter(
            TorneoZonaPareja.zona_id.in_(zonas_a_eliminar)
        ).delete(synchronize_session=False)
        print(f"✅ Eliminadas {relaciones_eliminadas} relaciones zona-pareja")
        
        # Eliminar zonas
        zonas_eliminadas = db.query(TorneoZona).filter(
            TorneoZona.id.in_(zonas_a_eliminar)
        ).delete(synchronize_session=False)
        print(f"✅ Eliminadas {zonas_eliminadas} zonas")
        
        db.commit()
        
        print(f"\n{'='*60}")
        print(f"LIMPIEZA COMPLETADA")
        print(f"{'='*60}")
        print(f"\n✅ Ahora puedes regenerar las zonas por categoría desde el frontend")
        print(f"   - Categoría 11: 8va Masc (6 parejas)")
        print(f"   - Categoría 12: 6ta Masc (4 parejas)")
        print(f"\n{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    limpiar_zonas_incorrectas()
