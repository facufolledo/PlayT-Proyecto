"""
Test para verificar que las restricciones se respetan al programar partidos
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.services.torneo_zona_horarios_service import TorneoZonaHorariosService

def test_extraer_slots():
    print("=" * 80)
    print("TEST: Extracción de slots con restricciones")
    print("=" * 80)
    
    # Horarios del torneo
    horarios_torneo = {
        "viernes": [{"desde": "18:00", "hasta": "22:00"}],
        "sabado": [{"desde": "10:00", "hasta": "22:00"}],
        "domingo": [{"desde": "10:00", "hasta": "22:00"}]
    }
    
    print("\nHorarios del torneo:")
    print("  Viernes: 18:00-22:00")
    print("  Sábado: 10:00-22:00")
    print("  Domingo: 10:00-22:00")
    
    # Test 1: Sin restricciones
    print("\n" + "-" * 80)
    print("TEST 1: Pareja SIN restricciones")
    print("-" * 80)
    
    slots_sin_restricciones = TorneoZonaHorariosService._extraer_slots_disponibles(
        None, horarios_torneo
    )
    
    print(f"Slots disponibles: {len(slots_sin_restricciones)}")
    print(f"Ejemplo: {list(slots_sin_restricciones)[:5]}")
    
    # Test 2: Con restricciones (formato nuevo - array)
    print("\n" + "-" * 80)
    print("TEST 2: Pareja CON restricciones (formato array)")
    print("-" * 80)
    
    restricciones_array = [
        {"dias": ["viernes"], "horaInicio": "18:00", "horaFin": "22:00"}
    ]
    
    print(f"Restricciones: Viernes 18:00-22:00 (NO puede jugar)")
    
    slots_con_restricciones = TorneoZonaHorariosService._extraer_slots_disponibles(
        restricciones_array, horarios_torneo
    )
    
    print(f"Slots disponibles: {len(slots_con_restricciones)}")
    
    # Verificar que NO incluye viernes
    slots_viernes = [s for s in slots_con_restricciones if s[0] == 'viernes']
    print(f"Slots en viernes: {len(slots_viernes)} (debería ser 0)")
    
    if len(slots_viernes) == 0:
        print("✅ Restricción respetada: NO hay slots en viernes")
    else:
        print(f"❌ ERROR: Hay {len(slots_viernes)} slots en viernes")
    
    # Verificar que SÍ incluye sábado y domingo
    slots_sabado = [s for s in slots_con_restricciones if s[0] == 'sabado']
    slots_domingo = [s for s in slots_con_restricciones if s[0] == 'domingo']
    
    print(f"Slots en sábado: {len(slots_sabado)}")
    print(f"Slots en domingo: {len(slots_domingo)}")
    
    if len(slots_sabado) > 0 and len(slots_domingo) > 0:
        print("✅ Disponibilidad correcta: SÍ hay slots en sábado y domingo")
    else:
        print("❌ ERROR: Faltan slots en sábado o domingo")
    
    # Test 3: Restricción parcial
    print("\n" + "-" * 80)
    print("TEST 3: Restricción parcial (solo mañana del sábado)")
    print("-" * 80)
    
    restricciones_parcial = [
        {"dias": ["sabado"], "horaInicio": "10:00", "horaFin": "14:00"}
    ]
    
    print(f"Restricciones: Sábado 10:00-14:00 (NO puede jugar)")
    
    slots_parcial = TorneoZonaHorariosService._extraer_slots_disponibles(
        restricciones_parcial, horarios_torneo
    )
    
    slots_sabado_manana = [s for s in slots_parcial if s[0] == 'sabado' and s[1] < '14:00']
    slots_sabado_tarde = [s for s in slots_parcial if s[0] == 'sabado' and s[1] >= '14:00']
    
    print(f"Slots sábado mañana (10:00-14:00): {len(slots_sabado_manana)} (debería ser 0)")
    print(f"Slots sábado tarde (14:00+): {len(slots_sabado_tarde)} (debería ser > 0)")
    
    if len(slots_sabado_manana) == 0 and len(slots_sabado_tarde) > 0:
        print("✅ Restricción parcial respetada correctamente")
    else:
        print("❌ ERROR en restricción parcial")
    
    # Test 4: Formato antiguo (objeto con franjas)
    print("\n" + "-" * 80)
    print("TEST 4: Formato antiguo (objeto con 'franjas')")
    print("-" * 80)
    
    restricciones_antiguo = {
        "franjas": [
            {"dias": ["viernes"], "horaInicio": "18:00", "horaFin": "22:00"}
        ]
    }
    
    slots_antiguo = TorneoZonaHorariosService._extraer_slots_disponibles(
        restricciones_antiguo, horarios_torneo
    )
    
    slots_viernes_antiguo = [s for s in slots_antiguo if s[0] == 'viernes']
    
    if len(slots_viernes_antiguo) == 0:
        print("✅ Formato antiguo también funciona correctamente")
    else:
        print("❌ ERROR: Formato antiguo no funciona")
    
    print("\n" + "=" * 80)
    print("TESTS COMPLETADOS")
    print("=" * 80)

if __name__ == "__main__":
    test_extraer_slots()
