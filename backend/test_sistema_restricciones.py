"""
Test del nuevo sistema de restricciones horarias
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.database.config import get_db
from src.services.torneo_fixture_global_service import TorneoFixtureGlobalService
from src.models.torneo_models import TorneoPareja
import json

def test_sistema_restricciones():
    """
    Prueba el nuevo sistema de restricciones
    """
    db = next(get_db())
    
    print("🧪 TEST SISTEMA DE RESTRICCIONES")
    print("="*60)
    
    # Crear datos de prueba
    restricciones_test = {
        "franjas": [
            {
                "dias": ["lunes", "martes"],
                "horaInicio": "08:00",
                "horaFin": "12:00"
            },
            {
                "dias": ["viernes"],
                "horaInicio": "18:00",
                "horaFin": "22:00"
            }
        ]
    }
    
    # Simular partidos de prueba
    partidos_mock = [{'pareja1_id': 1, 'pareja2_id': 2}]
    
    # Crear pareja mock con restricciones
    class ParejaTest:
        def __init__(self, disponibilidad):
            self.id = 1
            self.disponibilidad_horaria = disponibilidad
    
    # Simular query de pareja
    original_query = db.query
    def mock_query(model):
        if model == TorneoPareja:
            class MockQuery:
                def filter(self, *args):
                    return self
                def first(self):
                    return ParejaTest(restricciones_test)
            return MockQuery()
        return original_query(model)
    
    db.query = mock_query
    
    try:
        # Probar la función de obtener disponibilidad
        disponibilidad = TorneoFixtureGlobalService._obtener_disponibilidad_parejas(
            db, partidos_mock, None
        )
        
        print("📋 DISPONIBILIDAD PROCESADA:")
        for pareja_id, disp in disponibilidad.items():
            print(f"   Pareja {pareja_id}: {disp}")
        
        # Probar verificación de disponibilidad
        print(f"\n🔍 PRUEBAS DE VERIFICACIÓN:")
        
        test_cases = [
            ('lunes', '10:00', False, "Dentro de restricción lunes 08:00-12:00"),
            ('lunes', '14:00', True, "Fuera de restricción lunes"),
            ('miercoles', '10:00', True, "Día sin restricciones"),
            ('viernes', '20:00', False, "Dentro de restricción viernes 18:00-22:00"),
            ('viernes', '16:00', True, "Fuera de restricción viernes"),
            ('sabado', '15:00', True, "Día sin restricciones"),
        ]
        
        disp_pareja = disponibilidad[1]
        
        for dia, hora, esperado, descripcion in test_cases:
            hora_mins = int(hora.split(':')[0]) * 60 + int(hora.split(':')[1])
            resultado = TorneoFixtureGlobalService._verificar_disponibilidad_pareja(
                dia, hora_mins, disp_pareja
            )
            
            status = "✅" if resultado == esperado else "❌"
            print(f"   {status} {dia} {hora}: {resultado} (esperado: {esperado}) - {descripcion}")
        
        print(f"\n💡 LÓGICA DEL NUEVO SISTEMA:")
        print("   • Sin restricciones = disponible en todos los horarios del torneo")
        print("   • Con restricciones = NO disponible solo en esos horarios específicos")
        print("   • Días no mencionados = disponible todo el día")
        print("   • Horarios fuera de restricciones = disponible")
        
    finally:
        db.query = original_query
        db.close()

if __name__ == "__main__":
    test_sistema_restricciones()