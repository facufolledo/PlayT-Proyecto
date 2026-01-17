"""
Algoritmo de fixture corregido - Parche para el servicio existente
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.database.config import get_db
from src.models.torneo_models import Torneo, TorneoCancha, TorneoPareja, TorneoCategoria
from src.models.driveplus_models import Partido, Usuario
from datetime import datetime, timedelta
import json
from typing import List, Dict

def generar_fixture_corregido(torneo_id: int):
    """
    Genera fixture corregido respetando disponibilidad y tiempo entre partidos
    """
    db = next(get_db())
    
    print(f"🔧 GENERANDO FIXTURE CORREGIDO PARA TORNEO {torneo_id}")
    print("="*60)
    
    # 1. Obtener datos del torneo
    torneo = db.query(Torneo).filter(Torneo.id == torneo_id).first()
    if not torneo:
        print("❌ Torneo no encontrado")
        return
    
    canchas = db.query(TorneoCancha).filter(TorneoCancha.torneo_id == torneo_id).all()
    if not canchas:
        print("❌ No hay canchas configuradas")
        return
    
    print(f"🏟️ Canchas disponibles: {len(canchas)}")
    
    # 2. Obtener partidos de zonas
    partidos_zonas = db.execute("""
        SELECT 
            tz.id as zona_id,
            tz.nombre as zona_nombre,
            tc.id as categoria_id,
            tc.nombre as categoria_nombre,
            tp1.id as pareja1_id,
            tp2.id as pareja2_id
        FROM torneo_zonas tz
        JOIN torneo_categorias tc ON tz.categoria_id = tc.id
        JOIN torneo_zona_parejas tzp1 ON tz.id = tzp1.zona_id
        JOIN torneo_zona_parejas tzp2 ON tz.id = tzp2.zona_id
        JOIN torneos_parejas tp1 ON tzp1.pareja_id = tp1.id
        JOIN torneos_parejas tp2 ON tzp2.pareja_id = tp2.id
        WHERE tz.torneo_id = :torneo_id
        AND tp1.id < tp2.id  -- Evitar duplicados
        ORDER BY tc.id, tz.id, tp1.id, tp2.id
    """, {"torneo_id": torneo_id}).fetchall()
    
    print(f"⚽ Partidos a programar: {len(partidos_zonas)}")
    
    # 3. Generar slots de tiempo
    slots_disponibles = generar_slots_tiempo(torneo)
    print(f"⏰ Slots disponibles: {len(slots_disponibles)}")
    
    # 4. Programar partidos con algoritmo mejorado
    partidos_programados = []
    partidos_no_programados = []
    
    # Tracking de ocupación
    ocupacion_canchas = {slot: [] for slot in slots_disponibles}  # {(fecha, hora): [cancha_ids]}
    partidos_por_jugador = {}  # {jugador_id: [datetime]}
    
    for partido_data in partidos_zonas:
        # Obtener parejas
        pareja1 = db.query(TorneoPareja).filter(TorneoPareja.id == partido_data.pareja1_id).first()
        pareja2 = db.query(TorneoPareja).filter(TorneoPareja.id == partido_data.pareja2_id).first()
        
        if not pareja1 or not pareja2:
            continue
        
        # Obtener jugadores
        jugadores = [pareja1.jugador1_id, pareja1.jugador2_id, pareja2.jugador1_id, pareja2.jugador2_id]
        
        # Obtener disponibilidad
        disp1 = obtener_disponibilidad_pareja(pareja1)
        disp2 = obtener_disponibilidad_pareja(pareja2)
        
        # Buscar slot compatible
        slot_asignado = None
        cancha_asignada = None
        
        for fecha, hora in slots_disponibles:
            # 1. Verificar disponibilidad horaria
            if not verificar_disponibilidad_slot(fecha, hora, disp1):
                continue
            if not verificar_disponibilidad_slot(fecha, hora, disp2):
                continue
            
            # 2. Verificar tiempo mínimo entre partidos (60 minutos)
            fecha_hora_slot = datetime.combine(fecha, datetime.strptime(hora, '%H:%M').time())
            
            conflicto_tiempo = False
            for jugador_id in jugadores:
                if jugador_id in partidos_por_jugador:
                    for fecha_hora_existente in partidos_por_jugador[jugador_id]:
                        diferencia = abs((fecha_hora_slot - fecha_hora_existente).total_seconds() / 60)
                        if diferencia < 60:  # Mínimo 60 minutos
                            conflicto_tiempo = True
                            break
                if conflicto_tiempo:
                    break
            
            if conflicto_tiempo:
                continue
            
            # 3. Verificar cancha disponible
            canchas_ocupadas = ocupacion_canchas[(fecha, hora)]
            cancha_libre = None
            
            for cancha in canchas:
                if cancha.id not in canchas_ocupadas:
                    cancha_libre = cancha
                    break
            
            if not cancha_libre:
                continue
            
            # ✅ Slot válido encontrado
            slot_asignado = (fecha, hora)
            cancha_asignada = cancha_libre
            break
        
        if slot_asignado and cancha_asignada:
            # Programar partido
            fecha, hora = slot_asignado
            fecha_hora_slot = datetime.combine(fecha, datetime.strptime(hora, '%H:%M').time())
            
            # Marcar ocupación
            ocupacion_canchas[(fecha, hora)].append(cancha_asignada.id)
            
            # Registrar partidos de jugadores
            for jugador_id in jugadores:
                if jugador_id not in partidos_por_jugador:
                    partidos_por_jugador[jugador_id] = []
                partidos_por_jugador[jugador_id].append(fecha_hora_slot)
            
            # Crear partido en BD
            import pytz
            tz_argentina = pytz.timezone('America/Argentina/Buenos_Aires')
            fecha_hora_localizada = tz_argentina.localize(fecha_hora_slot)
            
            partido = Partido(
                id_torneo=torneo_id,
                zona_id=partido_data.zona_id,
                fase='zona',
                pareja1_id=partido_data.pareja1_id,
                pareja2_id=partido_data.pareja2_id,
                cancha_id=cancha_asignada.id,
                fecha_hora=fecha_hora_localizada,
                fecha=fecha_hora_localizada,
                estado='pendiente',
                tipo='torneo',
                id_creador=torneo.creado_por,
                categoria_id=partido_data.categoria_id
            )
            db.add(partido)
            
            partidos_programados.append({
                'zona': partido_data.zona_nombre,
                'categoria': partido_data.categoria_nombre,
                'fecha_hora': fecha_hora_slot,
                'cancha': cancha_asignada.nombre
            })
            
        else:
            # No se pudo programar
            # Obtener nombres de jugadores
            j1_p1 = db.query(Usuario).filter(Usuario.id_usuario == pareja1.jugador1_id).first()
            j2_p1 = db.query(Usuario).filter(Usuario.id_usuario == pareja1.jugador2_id).first()
            j1_p2 = db.query(Usuario).filter(Usuario.id_usuario == pareja2.jugador1_id).first()
            j2_p2 = db.query(Usuario).filter(Usuario.id_usuario == pareja2.jugador2_id).first()
            
            pareja1_nombres = f"{j1_p1.nombre_usuario} & {j2_p1.nombre_usuario}" if j1_p1 and j2_p1 else "Pareja 1"
            pareja2_nombres = f"{j1_p2.nombre_usuario} & {j2_p2.nombre_usuario}" if j1_p2 and j2_p2 else "Pareja 2"
            
            partidos_no_programados.append({
                'zona': partido_data.zona_nombre,
                'categoria': partido_data.categoria_nombre,
                'pareja1': pareja1_nombres,
                'pareja2': pareja2_nombres,
                'motivo': 'Sin horarios compatibles o conflicto de tiempo'
            })
    
    # Guardar cambios
    db.commit()
    
    # 5. Mostrar resultados
    print(f"\n✅ PARTIDOS PROGRAMADOS: {len(partidos_programados)}")
    for p in partidos_programados[:5]:  # Mostrar solo los primeros 5
        print(f"   📅 {p['fecha_hora'].strftime('%Y-%m-%d %H:%M')} - {p['categoria']} {p['zona']} - {p['cancha']}")
    
    if len(partidos_programados) > 5:
        print(f"   ... y {len(partidos_programados) - 5} más")
    
    if partidos_no_programados:
        print(f"\n❌ PARTIDOS NO PROGRAMADOS: {len(partidos_no_programados)}")
        for p in partidos_no_programados:
            print(f"   🚨 {p['categoria']} {p['zona']}: {p['pareja1']} vs {p['pareja2']}")
            print(f"      Motivo: {p['motivo']}")
    
    print(f"\n📊 RESUMEN:")
    print(f"   ✅ Programados: {len(partidos_programados)}")
    print(f"   ❌ No programados: {len(partidos_no_programados)}")
    print(f"   📈 Tasa de éxito: {len(partidos_programados)/(len(partidos_programados)+len(partidos_no_programados))*100:.1f}%")
    
    db.close()


def generar_slots_tiempo(torneo):
    """Genera slots de tiempo basados en horarios del torneo"""
    slots = []
    
    horarios = torneo.horarios_disponibles or {}
    fecha_actual = torneo.fecha_inicio
    
    while fecha_actual <= torneo.fecha_fin:
        dia_semana = fecha_actual.strftime('%A').lower()
        
        # Determinar horarios del día
        if dia_semana in ['saturday', 'sunday']:
            horarios_dia = horarios.get('finDeSemana', [])
        else:
            horarios_dia = horarios.get('semana', [])
        
        for horario in horarios_dia:
            hora_inicio = datetime.strptime(horario['desde'], '%H:%M').time()
            hora_fin = datetime.strptime(horario['hasta'], '%H:%M').time()
            
            # Generar slots cada 50 minutos
            hora_actual = datetime.combine(fecha_actual, hora_inicio)
            hora_limite = datetime.combine(fecha_actual, hora_fin)
            
            while hora_actual + timedelta(minutes=50) <= hora_limite:
                slots.append((fecha_actual, hora_actual.strftime('%H:%M')))
                hora_actual += timedelta(minutes=50)
        
        fecha_actual += timedelta(days=1)
    
    return slots


def obtener_disponibilidad_pareja(pareja):
    """Obtiene disponibilidad de una pareja"""
    if not pareja.disponibilidad_horaria:
        return None
    
    disp = pareja.disponibilidad_horaria
    if isinstance(disp, str):
        disp = json.loads(disp)
    
    if not disp or 'franjas' not in disp:
        return None
    
    # Convertir a formato interno
    rangos = {}
    for franja in disp['franjas']:
        for dia in franja.get('dias', []):
            if dia not in rangos:
                rangos[dia] = []
            
            hora_inicio = franja['horaInicio']
            hora_fin = franja['horaFin']
            
            inicio_mins = int(hora_inicio.split(':')[0]) * 60 + int(hora_inicio.split(':')[1])
            fin_mins = int(hora_fin.split(':')[0]) * 60 + int(hora_fin.split(':')[1])
            
            rangos[dia].append((inicio_mins, fin_mins))
    
    return {'rangos': rangos}


def verificar_disponibilidad_slot(fecha, hora, disponibilidad):
    """Verifica si un slot es compatible con la disponibilidad"""
    if not disponibilidad:
        return True  # Sin restricciones
    
    dia_semana = fecha.strftime('%A').lower()
    dias_map = {
        'monday': 'lunes', 'tuesday': 'martes', 'wednesday': 'miercoles',
        'thursday': 'jueves', 'friday': 'viernes', 'saturday': 'sabado', 'sunday': 'domingo'
    }
    dia_es = dias_map.get(dia_semana, dia_semana)
    
    # Si el día NO está en las restricciones, está disponible todo el día
    if dia_es not in disponibilidad['rangos']:
        return True
    
    # Si el día SÍ está en restricciones, verificar horario
    hora_mins = int(hora.split(':')[0]) * 60 + int(hora.split(':')[1])
    
    for inicio_mins, fin_mins in disponibilidad['rangos'][dia_es]:
        if inicio_mins <= hora_mins <= fin_mins:
            return True
    
    return False


if __name__ == "__main__":
    generar_fixture_corregido(17)