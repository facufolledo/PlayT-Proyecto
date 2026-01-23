"""
Eliminar torneo 35 (torneo de prueba)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import text
from src.database.config import get_db

TORNEO_ID = 35

def eliminar_torneo():
    db = next(get_db())
    
    try:
        print("=" * 80)
        print(f"ELIMINAR TORNEO {TORNEO_ID}")
        print("=" * 80)
        
        # Verificar que existe
        result = db.execute(text("""
            SELECT nombre, estado, fecha_inicio, fecha_fin
            FROM torneos
            WHERE id = :torneo_id
        """), {"torneo_id": TORNEO_ID})
        
        torneo = result.fetchone()
        
        if not torneo:
            print(f"\nEl torneo {TORNEO_ID} no existe")
            return
        
        print(f"\nTorneo encontrado:")
        print(f"  Nombre: {torneo[0]}")
        print(f"  Estado: {torneo[1]}")
        print(f"  Fecha inicio: {torneo[2]}")
        print(f"  Fecha fin: {torneo[3]}")
        
        # Contar datos relacionados
        result = db.execute(text("""
            SELECT 
                (SELECT COUNT(*) FROM torneos_parejas WHERE torneo_id = :torneo_id) as parejas,
                (SELECT COUNT(*) FROM torneo_zonas WHERE torneo_id = :torneo_id) as zonas,
                (SELECT COUNT(*) FROM partidos WHERE id_torneo = :torneo_id) as partidos,
                (SELECT COUNT(*) FROM torneo_canchas WHERE torneo_id = :torneo_id) as canchas,
                (SELECT COUNT(*) FROM torneo_categorias WHERE torneo_id = :torneo_id) as categorias
        """), {"torneo_id": TORNEO_ID})
        
        datos = result.fetchone()
        
        print(f"\nDatos relacionados:")
        print(f"  Parejas: {datos[0]}")
        print(f"  Zonas: {datos[1]}")
        print(f"  Partidos: {datos[2]}")
        print(f"  Canchas: {datos[3]}")
        print(f"  Categorias: {datos[4]}")
        
        # Confirmar
        print("\n" + "=" * 80)
        confirmar = input(f"\nConfirmar eliminacion del torneo {TORNEO_ID}? (si/no): ").strip().lower()
        
        if confirmar != 'si':
            print("\nEliminacion cancelada")
            return
        
        # Eliminar en orden correcto
        print("\nEliminando datos relacionados...")
        
        # 1. Eliminar partidos
        db.execute(text("DELETE FROM partidos WHERE id_torneo = :torneo_id"), {"torneo_id": TORNEO_ID})
        print("  Partidos eliminados")
        
        # 2. Eliminar zonas (esto eliminara zona_parejas por CASCADE)
        db.execute(text("DELETE FROM torneo_zonas WHERE torneo_id = :torneo_id"), {"torneo_id": TORNEO_ID})
        print("  Zonas eliminadas")
        
        # 3. Eliminar parejas
        db.execute(text("DELETE FROM torneos_parejas WHERE torneo_id = :torneo_id"), {"torneo_id": TORNEO_ID})
        print("  Parejas eliminadas")
        
        # 4. Eliminar canchas
        db.execute(text("DELETE FROM torneo_canchas WHERE torneo_id = :torneo_id"), {"torneo_id": TORNEO_ID})
        print("  Canchas eliminadas")
        
        # 5. Eliminar categorias
        db.execute(text("DELETE FROM torneo_categorias WHERE torneo_id = :torneo_id"), {"torneo_id": TORNEO_ID})
        print("  Categorias eliminadas")
        
        # 6. Eliminar torneo
        db.execute(text("DELETE FROM torneos WHERE id = :torneo_id"), {"torneo_id": TORNEO_ID})
        print("  Torneo eliminado")
        
        db.commit()
        print(f"\nTorneo {TORNEO_ID} eliminado exitosamente")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    eliminar_torneo()
