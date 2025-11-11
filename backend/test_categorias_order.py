import requests
import json

def test_categorias_order():
    """Probar el endpoint de categorías para verificar el orden"""
    try:
        response = requests.get('http://localhost:8000/auth/categorias')
        
        if response.status_code == 200:
            categorias = response.json()
            print("✅ Categorías ordenadas por id_categoria:")
            print()
            
            for cat in categorias:
                print(f"ID: {cat['id_categoria']} - {cat['nombre']}")
                print(f"  Descripción: {cat['descripcion']}")
                
                if cat['rating_min'] is not None and cat['rating_max'] is not None:
                    print(f"  Rating: {cat['rating_min']}-{cat['rating_max']} pts")
                elif cat['rating_min'] is not None:
                    print(f"  Rating: {cat['rating_min']}+ pts")
                elif cat['rating_max'] is not None:
                    print(f"  Rating: hasta {cat['rating_max']} pts")
                else:
                    print(f"  Rating: Sin límites específicos")
                print()
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error al conectar con el servidor: {e}")

if __name__ == "__main__":
    test_categorias_order()



