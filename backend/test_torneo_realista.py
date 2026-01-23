"""
Test REALISTA de torneo con zonas
Simula exactamente cómo funciona en producción:
- 35 parejas divididas en zonas de 3-4 parejas
- Cada zona genera su fixture independiente
- Programación respetando horarios y restricciones
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simular_programacion_horarios import SimuladorProgramacionHorarios
import random

# Nombres de parejas
NOMBRES = [
    "Juan", "Pedro", "Carlos", "Luis", "Ana", "María", "Diego", "Martín",
    "Laura", "Sofia", "Miguel", "Fernando", "Lucía", "Valentina", "Santiago",
    "Mateo", "Isabella", "Camila", "Sebastián", "Nicolás", "Emma", "Olivia",
    "Lucas", "Benjamín", "Mia", "Ava", "Liam", "Noah", "Ethan", "Mason",
    "Alexander", "Daniel", "Matthew", "David", "Joseph", "Samuel", "Henry",
    "Owen", "Wyatt", "Jack", "Leo", "Gabriel", "Julian", "Isaac", "Anthony"
]

def generar_disponibilidad_aleatoria():
    """Genera disponibilidad en formato del frontend"""
    # 30% sin restricciones
    if random.random() < 0.3:
        return None
    
    # 70% con restricciones
    dias_posibles = ["viernes", "sabado", "domingo"]
    num_franjas = random.choice([1, 1, 2])
    franjas = []
    
    for _ in range(num_franjas):
        num_dias = random.randint(1, 3)
        dias = random.sample(dias_posibles, num_dias)
        
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


def dividir_en_zonas(parejas, parejas_por_zona=3):
    """Divide parejas en zonas (como hace el sistema real)"""
    zonas = []
    zona_actual = []
    
    for i, pareja in enumerate(parejas):
        zona_actual.append(pareja)
        
        # Cuando llegamos al tamaño deseado o es la última pareja
        if len(zona_actual) == parejas_por_zona or i == len(parejas) - 1:
            zonas.append(zona_actual)
            zona_actual = []
    
    return zonas


def test_torneo_realista():
    """Test con zonas como en producción"""
    
    print(f"\n{'='*80}")
    print(f"TEST REALISTA DE TORNEO CON ZONAS")
    print(f"35 parejas divididas en zonas de 3-4 parejas")
    print(f"{'='*80}\n")
    
    # Horarios del torneo
    horarios_torneo = {
        "viernes": [{"desde": "15:00", "hasta": "23:30"}],
        "sabado": [{"desde": "09:00", "hasta": "23:30"}],
        "domingo": [{"desde": "09:00", "hasta": "23:30"}]
    }
    
    # Generar 35 parejas con disponibilidades
    random.seed(42)
    parejas_data = []
    
    for i in range(35):
        nombre1 = random.choice(NOMBRES)
        nombre2 = random.choice([n for n in NOMBRES if n != nombre1])
        nombre_pareja = f"{nombre1}/{nombre2} #{i+1}"
        disponibilidad = generar_disponibilidad_aleatoria()
        
        parejas_data.append({
            "nombre": nombre_pareja,
            "disponibilidad": disponibilidad
        })
    
    # Dividir en zonas de 3 parejas (como hace el sistema)
    zonas = dividir_en_zonas(parejas_data, parejas_por_zona=3)
    
    print(f"📊 CONFIGURACIÓN DEL TORNEO")
    print(f"{'─'*80}")
    print(f"• Total de parejas: {len(parejas_data)}")
    print(f"• Zonas generadas: {len(zonas)}")
    print(f"• Parejas por zona: {[len(z) for z in zonas]}")
    print(f"• Canchas disponibles: 3")
    
    # Simular cada zona
    resultados_zonas = []
    total_programados = 0
    total_sin_programar = 0
    total_partidos = 0
    
    for idx, zona_parejas in enumerate(zonas):
        print(f"\n{'='*80}")
        print(f"ZONA {chr(65 + idx)} - {len(zona_parejas)} parejas")
        print(f"{'='*80}")
        
        # Crear simulador para esta zona
        sim = SimuladorProgramacionHorarios()
        sim.configurar_torneo(horarios_torneo)
        sim.agregar_canchas(3)
        
        # Agregar parejas de esta zona
        for pareja_data in zona_parejas:
            sim.agregar_pareja(pareja_data["nombre"], pareja_data["disponibilidad"])
        
        # Simular
        sim.simular()
        
        # Guardar resultados
        programados = len(sim.partidos_programados)
        sin_programar = len(sim.partidos_sin_programar)
        partidos_zona = programados + sin_programar
        
        resultados_zonas.append({
            "zona": chr(65 + idx),
            "parejas": len(zona_parejas),
            "partidos": partidos_zona,
            "programados": programados,
            "sin_programar": sin_programar,
            "porcentaje": (programados / partidos_zona * 100) if partidos_zona > 0 else 0
        })
        
        total_programados += programados
        total_sin_programar += sin_programar
        total_partidos += partidos_zona
    
    # Resumen final
    print(f"\n{'='*80}")
    print(f"RESUMEN FINAL DEL TORNEO")
    print(f"{'='*80}\n")
    
    print(f"📊 RESULTADOS POR ZONA:")
    print(f"{'─'*80}")
    for res in resultados_zonas:
        emoji = "✅" if res['porcentaje'] >= 80 else "⚠️" if res['porcentaje'] >= 50 else "❌"
        print(f"{emoji} Zona {res['zona']}: {res['programados']}/{res['partidos']} partidos ({res['porcentaje']:.1f}%)")
        if res['sin_programar'] > 0:
            print(f"   └─ {res['sin_programar']} partidos sin programar")
    
    print(f"\n📈 TOTALES:")
    print(f"{'─'*80}")
    print(f"• Total de zonas: {len(zonas)}")
    print(f"• Total de parejas: {len(parejas_data)}")
    print(f"• Total de partidos: {total_partidos}")
    print(f"• Partidos programados: {total_programados} ({total_programados/total_partidos*100:.1f}%)")
    print(f"• Partidos sin programar: {total_sin_programar} ({total_sin_programar/total_partidos*100:.1f}%)")
    
    # Calcular capacidad utilizada
    total_slots = 0
    for dia, franjas in horarios_torneo.items():
        for franja in franjas:
            desde = SimuladorProgramacionHorarios()._parse_hora(franja['desde'])
            hasta = SimuladorProgramacionHorarios()._parse_hora(franja['hasta'])
            duracion = (hasta - desde).total_seconds() / 60
            slots_dia = int(duracion / 50)
            total_slots += slots_dia
    
    capacidad_total = total_slots * 3  # 3 canchas
    
    print(f"\n⏰ CAPACIDAD DEL TORNEO:")
    print(f"{'─'*80}")
    print(f"• Slots disponibles: {total_slots} × 3 canchas = {capacidad_total} partidos")
    print(f"• Partidos programados: {total_programados}")
    print(f"• Utilización: {total_programados/capacidad_total*100:.1f}%")
    print(f"• Slots libres: {capacidad_total - total_programados}")
    
    # Análisis de problemas
    if total_sin_programar > 0:
        print(f"\n⚠️  ANÁLISIS DE PARTIDOS SIN PROGRAMAR:")
        print(f"{'─'*80}")
        print(f"• {total_sin_programar} partidos no se pudieron programar")
        print(f"• Causas principales:")
        print(f"  - Parejas con horarios incompatibles")
        print(f"  - Restricciones muy estrictas")
        print(f"\n💡 Recomendaciones:")
        print(f"  - Pedir a las parejas más flexibilidad horaria")
        print(f"  - Considerar agregar más días al torneo")
        print(f"  - Programar manualmente los partidos conflictivos")
    else:
        print(f"\n✅ ¡PERFECTO! Todos los partidos se programaron exitosamente")
    
    print()


if __name__ == "__main__":
    test_torneo_realista()
