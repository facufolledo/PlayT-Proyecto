import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.config import get_db
from src.models.driveplus_models import Categoria

def verificar_categorias():
    """Verificar qué categorías están realmente en la base de datos"""
    db = next(get_db())
    
    try:
        # Obtener todas las categorías
        categorias = db.query(Categoria).order_by(Categoria.id_categoria).all()
        
        print("🔍 CATEGORÍAS EN LA BASE DE DATOS:")
        print("=" * 50)
        
        if not categorias:
            print("❌ No hay categorías en la base de datos")
            return
        
        # Agrupar por sexo
        masculinas = []
        femeninas = []
        sin_sexo = []
        
        for cat in categorias:
            if hasattr(cat, 'sexo') and cat.sexo == 'femenino':
                femeninas.append(cat)
            elif hasattr(cat, 'sexo') and cat.sexo == 'masculino':
                masculinas.append(cat)
            else:
                sin_sexo.append(cat)
        
        # Mostrar categorías masculinas
        if masculinas:
            print("\n👨 CATEGORÍAS MASCULINAS:")
            for cat in masculinas:
                rating_info = ""
                if cat.rating_min is not None and cat.rating_max is not None:
                    rating_info = f" (Rating: {cat.rating_min}-{cat.rating_max})"
                elif cat.rating_min is not None:
                    rating_info = f" (Rating: {cat.rating_min}+)"
                print(f"  - ID {cat.id_categoria}: '{cat.nombre}'{rating_info}")
        
        # Mostrar categorías femeninas
        if femeninas:
            print("\n👩 CATEGORÍAS FEMENINAS:")
            for cat in femeninas:
                rating_info = ""
                if cat.rating_min is not None and cat.rating_max is not None:
                    rating_info = f" (Rating: {cat.rating_min}-{cat.rating_max})"
                elif cat.rating_min is not None:
                    rating_info = f" (Rating: {cat.rating_min}+)"
                print(f"  - ID {cat.id_categoria}: '{cat.nombre}'{rating_info}")
        
        # Mostrar categorías sin sexo específico
        if sin_sexo:
            print("\n⚪ CATEGORÍAS SIN SEXO ESPECÍFICO:")
            for cat in sin_sexo:
                rating_info = ""
                if cat.rating_min is not None and cat.rating_max is not None:
                    rating_info = f" (Rating: {cat.rating_min}-{cat.rating_max})"
                elif cat.rating_min is not None:
                    rating_info = f" (Rating: {cat.rating_min}+)"
                print(f"  - ID {cat.id_categoria}: '{cat.nombre}'{rating_info}")
        
        print("\n" + "=" * 50)
        print(f"📊 TOTAL: {len(categorias)} categorías")
        
        # Verificar si existe "Principiantes" o "Principiante"
        principiantes_plural = [c for c in categorias if c.nombre.lower() == 'principiantes']
        principiante_singular = [c for c in categorias if c.nombre.lower() == 'principiante']
        
        print(f"\n🔍 BÚSQUEDA ESPECÍFICA:")
        print(f"  - 'Principiantes' (plural): {len(principiantes_plural)} encontradas")
        print(f"  - 'Principiante' (singular): {len(principiante_singular)} encontradas")
        
        if principiantes_plural:
            for cat in principiantes_plural:
                print(f"    → ID {cat.id_categoria}: '{cat.nombre}' (sexo: {getattr(cat, 'sexo', 'no definido')})")
        
        if principiante_singular:
            for cat in principiante_singular:
                print(f"    → ID {cat.id_categoria}: '{cat.nombre}' (sexo: {getattr(cat, 'sexo', 'no definido')})")
    
    except Exception as e:
        print(f"❌ Error al verificar categorías: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verificar_categorias()