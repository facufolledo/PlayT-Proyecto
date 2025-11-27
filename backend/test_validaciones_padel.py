"""
Test de validaciones de pádel
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.padel_validator import PadelValidator

def test_supertiebreak():
    """Test de validación de supertiebreak"""
    
    print("\n=== TEST DE VALIDACIONES DE SUPERTIEBREAK ===\n")
    
    casos_validos = [
        (10, 0, "10-0 (victoria rápida)"),
        (10, 1, "10-1"),
        (10, 5, "10-5"),
        (10, 8, "10-8"),
        (11, 9, "11-9 (diferencia de 2)"),
        (13, 11, "13-11 (diferencia de 2)"),
        (15, 13, "15-13 (diferencia de 2)"),
        (0, 10, "0-10 (victoria rápida rival)"),
        (8, 10, "8-10"),
        (9, 11, "9-11 (diferencia de 2)"),
    ]
    
    casos_invalidos = [
        (10, 9, "10-9 (debe continuar)"),
        (9, 10, "9-10 (debe continuar)"),
        (11, 10, "11-10 (diferencia de 1, debe ser 2)"),
        (12, 11, "12-11 (diferencia de 1, debe ser 2)"),
        (9, 8, "9-8 (no llegó a 10)"),
        (5, 3, "5-3 (incompleto)"),
    ]
    
    print("✅ CASOS VÁLIDOS:")
    for puntos_eq1, puntos_eq2, descripcion in casos_validos:
        es_valido, mensaje = PadelValidator.validar_supertiebreak(puntos_eq1, puntos_eq2)
        resultado = "✓" if es_valido else "✗"
        print(f"  {resultado} {descripcion}: {puntos_eq1}-{puntos_eq2}")
        if not es_valido:
            print(f"     ERROR: {mensaje}")
    
    print("\n❌ CASOS INVÁLIDOS (deben ser rechazados):")
    for puntos_eq1, puntos_eq2, descripcion in casos_invalidos:
        es_valido, mensaje = PadelValidator.validar_supertiebreak(puntos_eq1, puntos_eq2)
        resultado = "✓" if not es_valido else "✗"
        print(f"  {resultado} {descripcion}: {puntos_eq1}-{puntos_eq2}")
        if es_valido:
            print(f"     ERROR: Debería ser inválido pero fue aceptado")
        else:
            print(f"     Mensaje: {mensaje}")
    
    print("\n=== TEST COMPLETADO ===\n")

def test_sets():
    """Test de validación de sets"""
    
    print("\n=== TEST DE VALIDACIONES DE SETS ===\n")
    
    casos_validos = [
        (6, 0, "6-0"),
        (6, 1, "6-1"),
        (6, 2, "6-2"),
        (6, 3, "6-3"),
        (6, 4, "6-4"),
        (7, 5, "7-5"),
        (7, 6, "7-6 (con tiebreak)"),
        (0, 6, "0-6"),
        (4, 6, "4-6"),
        (5, 7, "5-7"),
        (6, 7, "6-7 (con tiebreak)"),
    ]
    
    casos_invalidos = [
        (6, 5, "6-5 (debe continuar)"),
        (6, 6, "6-6 (debe jugar tiebreak)"),
        (7, 4, "7-4 (imposible)"),
        (8, 6, "8-6 (más de 7 juegos)"),
        (10, 0, "10-0 (imposible)"),
        (5, 3, "5-3 (incompleto)"),
    ]
    
    print("✅ CASOS VÁLIDOS:")
    for juegos_eq1, juegos_eq2, descripcion in casos_validos:
        es_valido, mensaje = PadelValidator.validar_set(juegos_eq1, juegos_eq2)
        resultado = "✓" if es_valido else "✗"
        print(f"  {resultado} {descripcion}: {juegos_eq1}-{juegos_eq2}")
        if not es_valido:
            print(f"     ERROR: {mensaje}")
    
    print("\n❌ CASOS INVÁLIDOS (deben ser rechazados):")
    for juegos_eq1, juegos_eq2, descripcion in casos_invalidos:
        es_valido, mensaje = PadelValidator.validar_set(juegos_eq1, juegos_eq2)
        resultado = "✓" if not es_valido else "✗"
        print(f"  {resultado} {descripcion}: {juegos_eq1}-{juegos_eq2}")
        if es_valido:
            print(f"     ERROR: Debería ser inválido pero fue aceptado")
        else:
            print(f"     Mensaje: {mensaje}")
    
    print("\n=== TEST COMPLETADO ===\n")

if __name__ == "__main__":
    test_sets()
    test_supertiebreak()
