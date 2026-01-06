"""
Script para simular resultados de un torneo existente.
Usa el torneo ID 7 que ya tiene parejas inscritas.
"""
import os
import sys
import random
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL no configurada")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def generar_resultado_aleatorio():
    """Genera un resultado de partido aleatorio (best of 3)"""
    sets = []
    sets_ganados = [0, 0]
    
    while sets_ganados[0] < 2 and sets_ganados[1] < 2:
        ganador = random.choice([0, 1])
        perdedor = 1 - ganador
        
        tipo_set = random.choice(['normal', 'tiebreak', 'aplastante'])
        
        if tipo_set == 'normal':
            games_ganador = 6
            games_perdedor = random.randint(0, 4)
        elif tipo_set == 'tiebreak':
            games_ganador = 7
            games_perdedor = 6
        else:
            games_ganador = 6
            games_perdedor = random.randint(0, 2)
        
        set_data = {
            'gamesEquipoA': games_ganador if ganador == 0 else games_perdedor,
            'gamesEquipoB': games_perdedor if ganador == 0 else games_ganador,
            'ganador': 'equipoA' if ganador == 0 else 'equipoB',
            'completado': True
        }
        
        if games_ganador == 7 and games_perdedor == 6:
            tiebreak_ganador = random.randint(7, 12)
            tiebreak_perdedor = tiebreak_ganador - 2
            set_data['tiebreakEquipoA'] = tiebreak_ganador if ganador == 0 else tiebreak_perdedor
            set_data['tiebreakEquipoB'] = tiebreak_perdedor if ganador == 0 else tiebreak_ganador
        
        sets.append(set_data)
        sets_ganados[ganador] += 1
    
    ganador_final = 'equipoA' if sets_ganados[0] > sets_ganados[1] else 'equipoB'
    
    return {
        'sets': sets,
        'ganador': ganador_final,
        'completado': True,
        'formato': 'best_of_3'
    }


def main():
    db = Session()
    TORNEO_ID = 7  # Torneo existente
    
    try:
        print("=" * 60)
        print("🏆 SIMULADOR DE TORNEO - Usando torneo existente")
        print("=" * 60)
        
        # 1. Obtener parejas del torneo
        parejas = db.execute(text("""
            SELECT tp.id, tp.jugador1_id, tp.jugador2_id,
                   p1.nombre || ' ' || p1.apellido as j1_nombre,
                   p2.nombre || ' ' || p2.apellido as j2_nombre,
                   u1.rating as r1, u2.rating as r2
            FROM torneos_parejas tp
            JOIN perfil_usuarios p1 ON tp.jugador1_id = p1.id_usuario
            JOIN perfil_usuarios p2 ON tp.jugador2_id = p2.id_usuario
            JOIN usuarios u1 ON tp.jugador1_id = u1.id_usuario
            JOIN usuarios u2 ON tp.jugador2_id = u2.id_usuario
            WHERE tp.torneo_id = :tid AND tp.estado = 'confirmada'
            ORDER BY tp.id
        """), {'tid': TORNEO_ID}).fetchall()
        
        print(f"\n📊 Parejas en torneo {TORNEO_ID}: {len(parejas)}")
        
        if len(parejas) < 2:
            print("❌ Se necesitan al menos 2 parejas")
            return
        
        parejas_list = []
        for p in parejas:
            parejas_list.append({
                'id': p[0],
                'j1_id': p[1],
                'j2_id': p[2],
                'j1_nombre': p[3],
                'j2_nombre': p[4],
                'rating_promedio': (p[5] + p[6]) / 2
            })
            print(f"  👫 {p[3]} / {p[4]} (Rating: {(p[5]+p[6])//2})")
        
        # 2. Obtener partidos pendientes del torneo
        partidos_pendientes = db.execute(text("""
            SELECT id_partido, pareja1_id, pareja2_id, estado
            FROM partidos
            WHERE id_torneo = :tid AND tipo = 'torneo' AND estado = 'pendiente'
            ORDER BY id_partido
        """), {'tid': TORNEO_ID}).fetchall()
        
        print(f"\n📅 Partidos pendientes encontrados: {len(partidos_pendientes)}")
        
        # Filtrar solo partidos con parejas válidas del torneo
        pareja_ids = {p['id'] for p in parejas_list}
        partidos_validos = [p for p in partidos_pendientes if p[1] in pareja_ids and p[2] in pareja_ids]
        print(f"📅 Partidos válidos: {len(partidos_validos)}")
        
        if len(partidos_validos) == 0:
            print("⚠️ No hay partidos pendientes. Creando partidos de prueba...")
            partidos_validos = []  # Reset
            
            # Crear partidos todos contra todos
            for i, p1 in enumerate(parejas_list):
                for p2 in parejas_list[i+1:]:
                    result = db.execute(text("""
                        INSERT INTO partidos (tipo, estado, fecha, creado_en, id_creador, pareja1_id, pareja2_id, id_torneo)
                        VALUES ('torneo', 'pendiente', NOW(), NOW(), :creador, :p1, :p2, :tid)
                        RETURNING id_partido
                    """), {
                        'creador': p1['j1_id'],
                        'p1': p1['id'],
                        'p2': p2['id'],
                        'tid': TORNEO_ID
                    })
                    pid = result.fetchone()[0]
                    partidos_validos.append((pid, p1['id'], p2['id'], 'pendiente'))
            
            db.commit()
            print(f"✅ Creados {len(partidos_validos)} partidos")
        
        # 3. Simular resultados
        print("\n🎾 Simulando partidos...")
        
        from src.services.torneo_resultado_service import TorneoResultadoService
        
        for partido in partidos_validos:
            partido_id = partido[0]
            p1_id = partido[1]
            p2_id = partido[2]
            
            p1 = next((p for p in parejas_list if p['id'] == p1_id), None)
            p2 = next((p for p in parejas_list if p['id'] == p2_id), None)
            
            if not p1 or not p2:
                print(f"  ⚠️ Partido {partido_id}: Pareja no encontrada")
                continue
            
            # Generar resultado
            resultado = generar_resultado_aleatorio()
            resultado_json = json.dumps(resultado)
            
            # Guardar resultado
            db.execute(text("""
                UPDATE partidos 
                SET estado = 'confirmado', 
                    resultado_padel = CAST(:resultado AS jsonb)
                WHERE id_partido = :pid
            """), {
                'pid': partido_id,
                'resultado': resultado_json
            })
            db.commit()
            
            # Aplicar Elo usando el método del servicio
            try:
                from src.models.Drive+_models import Partido as PartidoModel
                partido_obj = db.query(PartidoModel).filter(PartidoModel.id_partido == partido_id).first()
                
                if partido_obj:
                    # Determinar ganador
                    ganador_pareja_id = p1_id if resultado['ganador'] == 'equipoA' else p2_id
                    
                    elo_result = TorneoResultadoService._aplicar_elo_torneo(
                        db, partido_obj, resultado, ganador_pareja_id
                    )
                    db.commit()
                    
                    ganador_nombre = p1['j1_nombre'].split()[0] if resultado['ganador'] == 'equipoA' else p2['j1_nombre'].split()[0]
                    
                    # Mostrar cambios de Elo
                    cambios_str = ""
                    if elo_result:
                        for uid, data in elo_result.items():
                            signo = '+' if data['cambio'] > 0 else ''
                            cambios_str += f"[{signo}{data['cambio']}]"
                    
                    print(f"  ✅ {p1['j1_nombre'][:10]} vs {p2['j1_nombre'][:10]} → {ganador_nombre} {cambios_str}")
                
            except Exception as e:
                print(f"  ⚠️ Partido {partido_id}: {str(e)[:60]}")
                db.rollback()
        
        # 4. Verificar historial guardado
        print("\n📈 Verificando historial de Elo...")
        historial = db.execute(text("""
            SELECT h.id_usuario, u.nombre_usuario, h.id_partido, h.rating_antes, h.delta, h.rating_despues
            FROM historial_rating h
            JOIN usuarios u ON h.id_usuario = u.id_usuario
            JOIN partidos p ON h.id_partido = p.id_partido
            WHERE p.id_torneo = :tid
            ORDER BY h.id_partido DESC
            LIMIT 20
        """), {'tid': TORNEO_ID}).fetchall()
        
        if historial:
            print(f"✅ {len(historial)} registros de historial encontrados:")
            for h in historial[:10]:
                signo = '+' if h[4] > 0 else ''
                print(f"   @{h[1]}: {h[3]} → {h[5]} ({signo}{h[4]}) - Partido {h[2]}")
        else:
            print("⚠️ No se encontró historial de Elo")
        
        print(f"\n✅ Simulación completada!")
        print(f"   Ver torneo en: /torneos/{TORNEO_ID}")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
