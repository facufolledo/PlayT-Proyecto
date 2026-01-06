import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.config import get_db
from src.models.Drive+_models import Categoria

def check_and_populate_categorias():
    """Verificar y poblar categorías si es necesario"""
    db = next(get_db())
    
    try:
        # Verificar si ya existen categorías
        existing_categorias = db.query(Categoria).all()
        
        if existing_categorias:
            print(f"✅ Ya existen {len(existing_categorias)} categorías en la base de datos:")
            for cat in existing_categorias:
                print(f"  - {cat.nombre} (ID: {cat.id_categoria})")
                if cat.rating_min is not None and cat.rating_max is not None:
                    print(f"    Rating: {cat.rating_min}-{cat.rating_max} pts")
                elif cat.rating_min is not None:
                    print(f"    Rating: {cat.rating_min}+ pts")
                else:
                    print(f"    Rating: Sin límites")
        else:
            print("❌ No hay categorías en la base de datos. Creando categorías por defecto...")
            
            # Crear categorías por defecto
            categorias_default = [
                Categoria(
                    nombre="8va",
                    descripcion="Categoría inicial para principiantes",
                    rating_min=0,
                    rating_max=899
                ),
                Categoria(
                    nombre="7ma",
                    descripcion="Categoría intermedia baja",
                    rating_min=900,
                    rating_max=1099
                ),
                Categoria(
                    nombre="6ta",
                    descripcion="Categoría intermedia",
                    rating_min=1100,
                    rating_max=1299
                ),
                Categoria(
                    nombre="5ta",
                    descripcion="Categoría intermedia alta",
                    rating_min=1300,
                    rating_max=1499
                ),
                Categoria(
                    nombre="Libre",
                    descripcion="Categoría avanzada",
                    rating_min=1500,
                    rating_max=None
                ),
            ]
            
            for categoria in categorias_default:
                db.add(categoria)
            
            db.commit()
            print("✅ Categorías creadas exitosamente!")
            
            # Mostrar las categorías creadas
            categorias_creadas = db.query(Categoria).all()
            print("\nCategorías disponibles:")
            for cat in categorias_creadas:
                print(f"  - {cat.nombre} (ID: {cat.id_categoria})")
                if cat.rating_min is not None and cat.rating_max is not None:
                    print(f"    Rating: {cat.rating_min}-{cat.rating_max} pts")
                elif cat.rating_min is not None:
                    print(f"    Rating: {cat.rating_min}+ pts")
                else:
                    print(f"    Rating: Sin límites")
    
    except Exception as e:
        print(f"❌ Error al verificar/poblar categorías: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    check_and_populate_categorias()



