"""
Verificación completa del fixture - Detectar todos los problemas
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.database.config import get_db
from sqlalchemy import text
from datetime import datetime, timedelta
import json

def verificar_fixture_completo(torneo_id=17):
    db = next(get_db())
    
    print("🔍 VERIFICACIÓN COMPLETA DEL FIXTURE")
    print("="*60)
    print(f"🎾 Verificando Torneo ID: {torneo_id}")
    
    # 1. VERIFICAR VIOLACIONES DE DISPONIBILIDAD HORARIA
    print("\n1️⃣ VERIFICANDO DISPONIBILIDAD HORARIA...")
    
    violaciones_horario = db.execute(text("""
        SELECT 
            p.id_partido,
            p.fecha_hora,
            p.cancha_id,
            tc.nombre as categoria,
            tz.nombre as zona,
            tp1.id as pareja1_id,
            tp2.id as pareja2_id,
            u1.nombre_usuario as j1_p1,
            u2.nombre_usuario as j2_p1,
            u3.nombre_usuario as j1_p2,
            u4.nombre_usuario as j2_p2,
            tp1.disponibilidad_horaria as disp_p1,
            tp2.disponibilidad_horaria as disp_p2
        FROM partidos p
        JOIN torneo_zonas tz ON p.zona_id = tz.id
        JOIN torneo_categorias tc ON tz.categoria_id = tc.id
        JOIN torneos_parejas tp1 ON p.pareja1_id = tp1.id
        JOIN torneos_parejas tp2 ON p.pareja2_id = tp2.id
        JOIN usuarios u1 ON tp1.jugador1_id = u1.id_usuario
        JOIN usuarios u2 ON tp1.jugador2_id = u2.id_usuario
        JOIN usuarios u3 ON tp2.jugador1_id = u3.id_usuario
        JOIN usuarios u4 ON tp2.jugador2_id = u4.id_usuario
        WHERE p.fase = 'zona'
        AND p.id_torneo = :torneo_id
        AND p.fecha_hora IS NOT NULL
        ORDER BY p.fecha_hora
    """), {"torneo_id": torneo_id}).fetchall()
    
    violaciones_encontradas = []
    
    for partido in violaciones_horario:
        fecha_hora = partido.fecha_hora
        dia_semana = fecha_hora.strftime('%A').lower()
        hora_partido = fecha_hora.hour
        minuto_partido = fecha_hora.minute
        
        # Mapear días en español
        dias_map = {
            'monday': 'lunes', 'tuesday': 'martes', 'wednesday': 'miercoles',
            'thursday': 'jueves', 'friday': 'viernes', 'saturday': 'sabado', 'sunday': 'domingo'
        }
        dia_es = dias_map.get(dia_semana, dia_semana)
        
        # Verificar pareja 1
        if partido.disp_p1:
            disp_p1 = json.loads(partido.disp_p1) if isinstance(partido.disp_p1, str) else partido.disp_p1
            if 'franjas' in disp_p1:
                for franja in disp_p1['franjas']:
                    if dia_es in franja.get('dias', []):
                        hora_inicio = int(franja['horaInicio'].split(':')[0])
                        hora_fin = int(franja['horaFin'].split(':')[0])
                        
                        if not (hora_inicio <= hora_partido <= hora_fin):
                            violaciones_encontradas.append({
                                'partido_id': partido.id_partido,
                                'fecha_hora': fecha_hora,
                                'categoria': partido.categoria,
                                'zona': partido.zona,
                                'pareja': f"{partido.j1_p1} & {partido.j2_p1}",
                                'disponibilidad': f"{dia_es} {franja['horaInicio']}-{franja['horaFin']}",
                                'problema': f"Partido a las {fecha_hora.strftime('%H:%M')} fuera del horario permitido"
                            })
        
        # Verificar pareja 2 (similar)
        if partido.disp_p2:
            disp_p2 = json.loads(partido.disp_p2) if isinstance(partido.disp_p2, str) else partido.disp_p2
            if 'franjas' in disp_p2:
                for franja in disp_p2['franjas']:
                    if dia_es in franja.get('dias', []):
                        hora_inicio = int(franja['horaInicio'].split(':')[0])
                        hora_fin = int(franja['horaFin'].split(':')[0])
                        
                        if not (hora_inicio <= hora_partido <= hora_fin):
                            violaciones_encontradas.append({
                                'partido_id': partido.id_partido,
                                'fecha_hora': fecha_hora,
                                'categoria': partido.categoria,
                                'zona': partido.zona,
                                'pareja': f"{partido.j1_p2} & {partido.j2_p2}",
                                'disponibilidad': f"{dia_es} {franja['horaInicio']}-{franja['horaFin']}",
                                'problema': f"Partido a las {fecha_hora.strftime('%H:%M')} fuera del horario permitido"
                            })
    
    if violaciones_encontradas:
        print(f"❌ ENCONTRADAS {len(violaciones_encontradas)} VIOLACIONES DE HORARIO:")
        for v in violaciones_encontradas:
            print(f"   🚨 Partido {v['partido_id']} - {v['categoria']} {v['zona']}")
            print(f"      Pareja: {v['pareja']}")
            print(f"      Programado: {v['fecha_hora'].strftime('%Y-%m-%d %H:%M')}")
            print(f"      Disponibilidad: {v['disponibilidad']}")
            print(f"      Problema: {v['problema']}")
            print()
    else:
        print("✅ No se encontraron violaciones de disponibilidad horaria")
    
    # 2. VERIFICAR PARTIDOS CONSECUTIVOS SIN DESCANSO
    print("\n2️⃣ VERIFICANDO PARTIDOS CONSECUTIVOS...")
    
    partidos_por_jugador = {}
    
    for partido in violaciones_horario:
        jugadores = [partido.j1_p1, partido.j2_p1, partido.j1_p2, partido.j2_p2]
        
        for jugador in jugadores:
            if jugador not in partidos_por_jugador:
                partidos_por_jugador[jugador] = []
            
            partidos_por_jugador[jugador].append({
                'partido_id': partido.id_partido,
                'fecha_hora': partido.fecha_hora,
                'categoria': partido.categoria,
                'zona': partido.zona
            })
    
    # Ordenar partidos por jugador y verificar intervalos
    partidos_consecutivos = []
    
    for jugador, partidos in partidos_por_jugador.items():
        if len(partidos) > 1:
            partidos_ordenados = sorted(partidos, key=lambda x: x['fecha_hora'])
            
            for i in range(len(partidos_ordenados) - 1):
                partido_actual = partidos_ordenados[i]
                partido_siguiente = partidos_ordenados[i + 1]
                
                # Calcular diferencia en minutos
                diferencia = (partido_siguiente['fecha_hora'] - partido_actual['fecha_hora']).total_seconds() / 60
                
                # Mínimo recomendado: 60 minutos (50 min partido + 10 min descanso)
                if diferencia < 60:
                    partidos_consecutivos.append({
                        'jugador': jugador,
                        'partido1': partido_actual,
                        'partido2': partido_siguiente,
                        'diferencia_minutos': int(diferencia),
                        'problema': f"Solo {int(diferencia)} minutos entre partidos (mínimo recomendado: 60)"
                    })
    
    if partidos_consecutivos:
        print(f"❌ ENCONTRADOS {len(partidos_consecutivos)} PROBLEMAS DE PARTIDOS CONSECUTIVOS:")
        for pc in partidos_consecutivos:
            print(f"   ⚠️ Jugador: {pc['jugador']}")
            print(f"      Partido 1: {pc['partido1']['fecha_hora'].strftime('%H:%M')} - {pc['partido1']['categoria']} {pc['partido1']['zona']}")
            print(f"      Partido 2: {pc['partido2']['fecha_hora'].strftime('%H:%M')} - {pc['partido2']['categoria']} {pc['partido2']['zona']}")
            print(f"      Problema: {pc['problema']}")
            print()
    else:
        print("✅ No se encontraron problemas de partidos consecutivos")
    
    # 3. VERIFICAR CONFLICTOS DE CANCHA
    print("\n3️⃣ VERIFICANDO CONFLICTOS DE CANCHA...")
    
    conflictos_cancha = db.execute(text("""
        SELECT 
            p1.id_partido as partido1_id,
            p2.id_partido as partido2_id,
            p1.fecha_hora,
            p1.cancha_id,
            tc1.nombre as categoria1,
            tc2.nombre as categoria2,
            tz1.nombre as zona1,
            tz2.nombre as zona2
        FROM partidos p1
        JOIN partidos p2 ON p1.cancha_id = p2.cancha_id 
            AND p1.fecha_hora = p2.fecha_hora 
            AND p1.id_partido != p2.id_partido
        JOIN torneo_zonas tz1 ON p1.zona_id = tz1.id
        JOIN torneo_zonas tz2 ON p2.zona_id = tz2.id
        JOIN torneo_categorias tc1 ON tz1.categoria_id = tc1.id
        JOIN torneo_categorias tc2 ON tz2.categoria_id = tc2.id
        WHERE p1.fase = 'zona' AND p2.fase = 'zona'
        AND p1.id_torneo = :torneo_id AND p2.id_torneo = :torneo_id
        ORDER BY p1.fecha_hora, p1.cancha_id
    """), {"torneo_id": torneo_id}).fetchall()
    
    if conflictos_cancha:
        print(f"❌ ENCONTRADOS {len(conflictos_cancha)} CONFLICTOS DE CANCHA:")
        for conflicto in conflictos_cancha:
            print(f"   🚨 Cancha {conflicto.cancha_id} - {conflicto.fecha_hora.strftime('%Y-%m-%d %H:%M')}")
            print(f"      Partido {conflicto.partido1_id}: {conflicto.categoria1} {conflicto.zona1}")
            print(f"      Partido {conflicto.partido2_id}: {conflicto.categoria2} {conflicto.zona2}")
            print()
    else:
        print("✅ No se encontraron conflictos de cancha")
    
    # 4. RESUMEN FINAL
    print("\n" + "="*60)
    print("📊 RESUMEN DE VERIFICACIÓN:")
    print(f"   🚨 Violaciones de horario: {len(violaciones_encontradas)}")
    print(f"   ⚠️ Partidos consecutivos: {len(partidos_consecutivos)}")
    print(f"   🏟️ Conflictos de cancha: {len(conflictos_cancha)}")
    
    total_problemas = len(violaciones_encontradas) + len(partidos_consecutivos) + len(conflictos_cancha)
    
    if total_problemas == 0:
        print("✅ ¡FIXTURE PERFECTO! No se encontraron problemas.")
    else:
        print(f"❌ TOTAL DE PROBLEMAS: {total_problemas}")
        print("\n💡 RECOMENDACIONES:")
        print("   1. Eliminar el fixture actual")
        print("   2. Corregir el algoritmo de programación")
        print("   3. Regenerar el fixture con las correcciones")
    
    db.close()

if __name__ == "__main__":
    verificar_fixture_completo(17)