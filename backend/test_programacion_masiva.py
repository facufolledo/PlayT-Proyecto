"""
Test de programación masiva con 30+ parejas
Simula el formato exacto que viene del frontend
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simular_programacion_horarios import SimuladorProgramacionHorarios
import random

# Nombres de parejas para generar
NOMBRES = [
    "Juan", "Pedro", "Carlos", "Luis", "Ana", "María", "Diego", "Martín",
    "Laura", "Sofia", "Miguel", "Fernando", "Lucía", "Valentina", "Santiago",
    "Mateo", "Isabella", "Camila", "Sebastián", "Nicolás", "Emma", "Olivia",
    "Lucas", "Benjamín", "Mia", "Ava", "Liam", "Noah", "Ethan", "Mason",
    "Alexander", "Daniel", "Matthew", "David", "Joseph", "Samuel", "Henry",
    "Owen", "Wyatt", "Jack", "Leo", "Gabriel", "Julian", "Isaac", "Anthony"
]

def generar_disponibilidad_aleatoria():
    """
    Genera disponibilidad en el formato exacto del frontend
    
    Formato:
    {
        "franjas": [
            {"dias": ["viernes", "sabado"], "horaInicio": "18:00", "horaFin": "22:00"}
        ]
    }
    """
    # 30% sin restricciones (disponible todo el torneo)
    if random.random() < 0.3:
        return None
    
    # 70% con restricciones
    dias_posibles = ["viernes", "sabado", "domingo"]
    
    # Generar 1-2 franjas
    num_franjas = random.choice([1, 1, 2])  # Más probabilidad de 1 franja
    franjas = []
    
    for _ in range(num_franjas):
        # Seleccionar días aleatorios
        num_dias = random.randint(1, 3)
        dias = random.sample(dias_posibles, num_dias)
        
        # Generar horarios
        # Opciones comunes:
        # - Mañana: 09:00-14:00
        # - Tarde: 15:00-19:00
        # - Noche: 18:00-23:00
        # - Todo el día: 09:00-23:00
        
        opciones_horarios = [
            ("09:00", "14:00"),  # Mañana
            ("15:00", "19:00"),  # Tarde
            ("18:00", "23:00"),  # Noche
            ("09:00", "23:00"),  # Todo el día
            ("10:00", "16:00"),  # Mediodía
            ("19:00", "23:00"),  # Solo noche
        ]
        
        hora_inicio, hora_fin = random.choice(opciones_horarios)
        
        franjas.append({
            "dias": dias,
            "horaInicio": hora_inicio,
            "horaFin": hora_fin
        })
    
    return {"franjas": franjas}


def test_programacion_masiva():
    """Test con 30+ parejas y formato real del frontend"""
    
    print(f"\n{'='*80}")
    print(f"TEST DE PROGRAMACIÓN MASIVA - 30+ PAREJAS")
    print(f"Formato exacto del frontend")
    print(f"{'='*80}\n")
    
    sim = SimuladorProgramacionHorarios()
    
    # 1. Configurar horarios del torneo (formato del backend)
    # Este es el formato que se guarda en la BD
    horarios_torneo = {
        "viernes": [{"desde": "15:00", "hasta": "23:30"}],
        "sabado": [{"desde": "09:00", "hasta": "23:30"}],
        "domingo": [{"desde": "09:00", "hasta": "23:30"}]
    }
    
    sim.configurar_torneo(horarios_torneo)
    
    # 2. Configurar canchas
    sim.agregar_canchas(3)
    
    # 3. Generar 35 parejas con disponibilidades aleatorias
    print(f"\n{'─'*80}")
    print(f"GENERANDO 35 PAREJAS CON DISPONIBILIDADES ALEATORIAS")
    print(f"{'─'*80}")
    
    random.seed(42)  # Para reproducibilidad
    
    for i in range(35):
        nombre1 = random.choice(NOMBRES)
        nombre2 = random.choice([n for n in NOMBRES if n != nombre1])
        nombre_pareja = f"{nombre1}/{nombre2} #{i+1}"
        
        disponibilidad = generar_disponibilidad_aleatoria()
        sim.agregar_pareja(nombre_pareja, disponibilidad)
    
    # 4. Ejecutar simulación
    print(f"\n{'─'*80}")
    print(f"EJECUTANDO SIMULACIÓN")
    print(f"{'─'*80}")
    
    sim.simular()
    
    # 5. Análisis adicional
    print(f"\n{'='*80}")
    print(f"ANÁLISIS DETALLADO")
    print(f"{'='*80}\n")
    
    # Contar parejas por tipo de disponibilidad
    sin_restricciones = sum(1 for p in sim.parejas if not p['disponibilidad'])
    con_restricciones = len(sim.parejas) - sin_restricciones
    
    print(f"📊 Distribución de disponibilidades:")
    print(f"   • Sin restricciones: {sin_restricciones} parejas ({sin_restricciones/len(sim.parejas)*100:.1f}%)")
    print(f"   • Con restricciones: {con_restricciones} parejas ({con_restricciones/len(sim.parejas)*100:.1f}%)")
    
    # Calcular total de partidos posibles
    n = len(sim.parejas)
    total_partidos = n * (n - 1) // 2
    
    print(f"\n📈 Estadísticas de programación:")
    print(f"   • Total de parejas: {n}")
    print(f"   • Total de partidos (round-robin): {total_partidos}")
    print(f"   • Partidos por pareja: {n - 1}")
    
    # Calcular slots totales disponibles
    total_slots = 0
    for dia, franjas in horarios_torneo.items():
        for franja in franjas:
            desde = sim._parse_hora(franja['desde'])
            hasta = sim._parse_hora(franja['hasta'])
            duracion = (hasta - desde).total_seconds() / 60
            slots_dia = int(duracion / sim.DURACION_PARTIDO_MINUTOS)
            total_slots += slots_dia
    
    capacidad_total = total_slots * len(sim.canchas)
    
    print(f"\n⏰ Capacidad del torneo:")
    print(f"   • Slots de tiempo disponibles: {total_slots}")
    print(f"   • Canchas: {len(sim.canchas)}")
    print(f"   • Capacidad total: {capacidad_total} partidos")
    print(f"   • Utilización: {len(sim.partidos_programados)}/{capacidad_total} ({len(sim.partidos_programados)/capacidad_total*100:.1f}%)")
    
    # Verificar si hay suficiente capacidad
    if total_partidos > capacidad_total:
        print(f"\n⚠️  ADVERTENCIA: No hay suficiente capacidad para todos los partidos!")
        print(f"   Se necesitan {total_partidos} slots pero solo hay {capacidad_total}")
        print(f"   Faltan {total_partidos - capacidad_total} slots")
        print(f"\n💡 Soluciones:")
        print(f"   • Agregar más canchas")
        print(f"   • Extender horarios del torneo")
        print(f"   • Dividir en zonas más pequeñas")
    else:
        print(f"\n✅ Hay suficiente capacidad teórica para todos los partidos")
    
    print()


if __name__ == "__main__":
    test_programacion_masiva()
