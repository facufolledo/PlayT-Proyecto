"""
Script para simular un torneo completo "Prueba" con todos los usuarios
- Máximo 3 parejas por zona, mínimo 2
- Genera zonas, fixture, resultados y playoffs
- Creador: Usuario ID 14
"""
import os
import sys
import random
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.models.Drive+_models import Usuario, Partido
from src.models.torneo_models import TorneoZona, TorneoZonaPareja
from src.services.torneo_resultado_service import TorneoResultadoService

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

CREADOR_ID = 14
PAREJAS_POR_ZONA_MIN = 2
PAREJAS_POR_ZONA_MAX = 3


def generar_resultado_aleatorio():
    """Genera un resultado de pádel aleatorio válido"""
    es_tres_sets = random.choice([True, False])
    resultados_validos = [(6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (7, 5), (7, 6)]
    sets = []
    
    if es_tres_sets:
        ganador = random.choice(['equipoA', 'equipoB'])
        perdedor = 'equipoB' if ganador == 'equipoA' else 'equipoA'
        orden_sets = [ganador, ganador, perdedor]
        random.shuffle(orden_sets)
        
        for set_ganador in orden_sets:
            resultado = random.choice(resultados_validos)
            if set_ganador == 'equipoA':
                sets.append({"gamesEquipoA": resultado[0], "gamesEquipoB": resultado[1], "ganador": "equipoA", "completado": True})
            else:
                sets.append({"gamesEquipoA": resultado[1], "gamesEquipoB": resultado[0], "ganador": "equipoB", "completado": True})
    else:
        ganador = random.choice(['equipoA', 'equipoB'])
        for _ in range(2):
            resultado = random.choice(resultados_validos)
            if ganador == 'equipoA':
                sets.append({"gamesEquipoA": resultado[0], "gamesEquipoB": resultado[1], "ganador": "equipoA", "completado": True})
            else:
                sets.append({"gamesEquipoA": resultado[1], "gamesEquipoB": resultado[0], "ganador": "equipoB", "completado": True})
    
    return {"sets": sets}


def limpiar_torneos_anteriores():
    """Limpia torneos de prueba anteriores"""
    print("\n🧹 Limpiando torneos anteriores...")
    
    # Obtener IDs de torneos de prueba
    result = db.execute(text("SELECT id FROM torneos WHERE nombre LIKE '%Prueba%' OR nombre LIKE '%Simulado%'"))
    torneo_ids = [row[0] for row in result]
    
    if not torneo_ids:
        print("   No hay torneos anteriores para limpiar")
        return
    
    for tid in torneo_ids:
        # Eliminar en orden correcto por foreign keys
        db.execute(text("DELETE FROM historial_rating WHERE id_partido IN (SELECT id_partido FROM partidos WHERE id_torneo = :tid)"), {'tid': tid})
        db.execute(text("DELETE FROM partidos WHERE id_torneo = :tid"), {'tid': tid})
        db.execute(text("DELETE FROM torneo_zona_parejas WHERE zona_id IN (SELECT id FROM torneo_zonas WHERE torneo_id = :tid)"), {'tid': tid})
        db.execute(text("DELETE FROM torneo_zonas WHERE torneo_id = :tid"), {'tid': tid})
        db.execute(text("DELETE FROM torneos_parejas WHERE torneo_id = :tid"), {'tid': tid})
        db.execute(text("DELETE FROM torneos_organizadores WHERE torneo_id = :tid"), {'tid': tid})
        db.execute(text("DELETE FROM torneos WHERE id = :tid"), {'tid': tid})
    
    db.commit()
    print(f"   ✅ Eliminados {len(torneo_ids)} torneos anteriores")


def crear_torneo():
    """Crea el torneo 'Prueba'"""
    print("\n🏆 Creando torneo 'Prueba'...")
    
    result = db.execute(text("""
        INSERT INTO torneos (nombre, descripcion, tipo, categoria, genero, estado, fecha_inicio, fecha_fin, lugar, creado_por)
        VALUES ('Prueba', 'Torneo de prueba con ELO', 'clasico', 'Libre', 'masculino', 'inscripcion', :fecha_inicio, :fecha_fin, 'Club Drive+', :creador)
        RETURNING id
    """), {
        'fecha_inicio': date.today(),
        'fecha_fin': date.today() + timedelta(days=7),
        'creador': CREADOR_ID
    })
    torneo_id = result.fetchone()[0]
    
    # Agregar organizador
    db.execute(text("""
        INSERT INTO torneos_organizadores (torneo_id, user_id, rol)
        VALUES (:tid, :uid, 'owner')
    """), {'tid': torneo_id, 'uid': CREADOR_ID})
    
    db.commit()
    print(f"   ✅ Torneo creado: ID={torneo_id}")
    return torneo_id


def crear_parejas(torneo_id):
    """Crea parejas con todos los usuarios"""
    print("\n👥 Creando parejas...")
    
    usuarios = db.query(Usuario).all()
    usuarios_ids = [u.id_usuario for u in usuarios]
    random.shuffle(usuarios_ids)
    
    num_parejas = len(usuarios_ids) // 2
    parejas = []
    
    for i in range(0, num_parejas * 2, 2):
        if i + 1 < len(usuarios_ids):
            result = db.execute(text("""
                INSERT INTO torneos_parejas (torneo_id, jugador1_id, jugador2_id, estado, categoria_asignada)
                VALUES (:tid, :j1, :j2, 'CONFIRMADA', 'Libre')
                RETURNING id, jugador1_id, jugador2_id
            """), {'tid': torneo_id, 'j1': usuarios_ids[i], 'j2': usuarios_ids[i + 1]})
            row = result.fetchone()
            parejas.append({'id': row[0], 'j1': row[1], 'j2': row[2]})
    
    db.commit()
    print(f"   ✅ {len(parejas)} parejas creadas")
    return parejas


def crear_zonas(torneo_id, parejas):
    """Crea zonas con máximo 3 parejas por zona"""
    print("\n🗂️ Creando zonas (máx 3 parejas por zona)...")
    
    num_parejas = len(parejas)
    # Calcular número de zonas necesarias (máximo 3 parejas por zona)
    num_zonas = (num_parejas + PAREJAS_POR_ZONA_MAX - 1) // PAREJAS_POR_ZONA_MAX
    
    zonas = []
    for i in range(num_zonas):
        zona = TorneoZona(
            torneo_id=torneo_id,
            nombre=f"Zona {chr(65 + i)}",
            numero_orden=i + 1
        )
        db.add(zona)
        zonas.append(zona)
    
    db.flush()
    
    # Distribuir parejas en zonas (máximo 3 por zona)
    random.shuffle(parejas)
    for i, pareja in enumerate(parejas):
        zona_idx = i // PAREJAS_POR_ZONA_MAX
        if zona_idx < len(zonas):
            zona_pareja = TorneoZonaPareja(
                zona_id=zonas[zona_idx].id,
                pareja_id=pareja['id']
            )
            db.add(zona_pareja)
    
    db.commit()
    
    print(f"   ✅ {num_zonas} zonas creadas")
    for z in zonas:
        count = db.query(TorneoZonaPareja).filter(TorneoZonaPareja.zona_id == z.id).count()
        print(f"      - {z.nombre}: {count} parejas")
    
    return zonas


def generar_partidos_zona(torneo_id, zona):
    """Genera partidos todos contra todos en una zona"""
    zona_parejas = db.query(TorneoZonaPareja).filter(TorneoZonaPareja.zona_id == zona.id).all()
    pareja_ids = [zp.pareja_id for zp in zona_parejas]
    
    partidos = []
    for i in range(len(pareja_ids)):
        for j in range(i + 1, len(pareja_ids)):
            partido = Partido(
                id_torneo=torneo_id,
                zona_id=zona.id,
                pareja1_id=pareja_ids[i],
                pareja2_id=pareja_ids[j],
                fase='zona',
                estado='pendiente',
                tipo='torneo',
                fecha=datetime.now(),
                id_creador=CREADOR_ID
            )
            db.add(partido)
            partidos.append(partido)
    
    db.flush()
    return partidos


def simular_partidos(partidos):
    """Simula resultados de partidos"""
    exitos = 0
    errores = 0
    
    for partido in partidos:
        try:
            resultado = generar_resultado_aleatorio()
            partido_actualizado = TorneoResultadoService.cargar_resultado(
                db, partido.id_partido, resultado, CREADOR_ID
            )
            if partido_actualizado.elo_aplicado:
                exitos += 1
            else:
                errores += 1
        except Exception as e:
            errores += 1
            print(f"   ❌ Error partido {partido.id_partido}: {e}")
            db.rollback()
    
    return exitos, errores


def obtener_clasificados_zona(zona_id):
    """Obtiene los 2 primeros clasificados de una zona basado en victorias"""
    # Obtener parejas de la zona
    zona_parejas = db.query(TorneoZonaPareja).filter(TorneoZonaPareja.zona_id == zona_id).all()
    pareja_ids = [zp.pareja_id for zp in zona_parejas]
    
    # Contar victorias por pareja
    victorias = {}
    for pid in pareja_ids:
        victorias[pid] = 0
    
    # Obtener partidos de la zona
    partidos = db.query(Partido).filter(
        Partido.zona_id == zona_id,
        Partido.estado == 'confirmado'
    ).all()
    
    for p in partidos:
        if p.ganador_pareja_id:
            if p.ganador_pareja_id in victorias:
                victorias[p.ganador_pareja_id] += 1
    
    # Ordenar por victorias
    clasificados = sorted(victorias.items(), key=lambda x: x[1], reverse=True)
    
    # Retornar los 2 primeros (o menos si hay menos parejas)
    return [c[0] for c in clasificados[:2]]


def generar_playoffs(torneo_id, zonas):
    """Genera el cuadro de playoffs con los clasificados de cada zona, manejando byes correctamente"""
    print("\n🏅 Generando playoffs...")
    
    # Obtener clasificados de cada zona (2 por zona)
    clasificados = []
    for zona in zonas:
        zona_clasificados = obtener_clasificados_zona(zona.id)
        for i, pareja_id in enumerate(zona_clasificados):
            clasificados.append({
                'pareja_id': pareja_id,
                'zona': zona.nombre,
                'posicion': i + 1
            })
        print(f"   {zona.nombre}: {len(zona_clasificados)} clasificados")
    
    print(f"   Total clasificados: {len(clasificados)}")
    
    if len(clasificados) < 2:
        print("   ⚠️ No hay suficientes clasificados para playoffs")
        return []
    
    num_clasificados = len(clasificados)
    
    # Calcular potencia de 2 más cercana para el bracket
    import math
    potencia = 2 ** math.ceil(math.log2(num_clasificados))
    num_byes = potencia - num_clasificados
    
    # Determinar fase inicial según potencia
    fase_map = {2: 'final', 4: 'semis', 8: '4tos', 16: '8vos', 32: '16avos'}
    siguiente_fase_map = {'16avos': '8vos', '8vos': '4tos', '4tos': 'semis', 'semis': 'final'}
    fase_inicial = fase_map.get(potencia, '4tos')
    
    print(f"   Bracket size: {potencia}, Fase inicial: {fase_inicial}")
    print(f"   Byes necesarios: {num_byes}")
    
    # Asignar seeds: primeros de zona tienen mejor seed
    primeros = [c for c in clasificados if c['posicion'] == 1]
    segundos = [c for c in clasificados if c['posicion'] == 2]
    random.shuffle(primeros)
    random.shuffle(segundos)
    
    clasificados_ordenados = []
    seed = 1
    for c in primeros:
        c['seed'] = seed
        clasificados_ordenados.append(c)
        seed += 1
    for c in segundos:
        c['seed'] = seed
        clasificados_ordenados.append(c)
        seed += 1
    
    clasificados_dict = {c['seed']: c for c in clasificados_ordenados}
    
    # Calcular emparejamientos estándar de bracket
    def calcular_emparejamientos(n):
        if n == 2: return [(1, 2)]
        elif n == 4: return [(1, 4), (2, 3)]
        elif n == 8: return [(1, 8), (4, 5), (2, 7), (3, 6)]
        elif n == 16: return [(1, 16), (8, 9), (4, 13), (5, 12), (2, 15), (7, 10), (3, 14), (6, 11)]
        else:
            return [(i + 1, n - i) for i in range(n // 2)]
    
    emparejamientos = calcular_emparejamientos(potencia)
    
    partidos_playoff = []
    partidos_primera_ronda = []  # Info de cada slot de primera ronda
    
    # Crear partidos de primera ronda
    for i, (seed1, seed2) in enumerate(emparejamientos):
        c1 = clasificados_dict.get(seed1)
        c2 = clasificados_dict.get(seed2)
        
        if c1 and c2:
            # Partido normal
            partido = Partido(
                id_torneo=torneo_id,
                pareja1_id=c1['pareja_id'],
                pareja2_id=c2['pareja_id'],
                fase=fase_inicial,
                numero_partido=i + 1,
                estado='pendiente',
                tipo='torneo',
                fecha=datetime.now(),
                id_creador=CREADOR_ID
            )
            db.add(partido)
            partidos_playoff.append(partido)
            partidos_primera_ronda.append({'numero': i + 1, 'tipo': 'normal', 'partido': partido})
            print(f"   Partido {i+1}: Seed {seed1} vs Seed {seed2}")
        elif c1:
            # c2 es bye, c1 avanza
            partidos_primera_ronda.append({'numero': i + 1, 'tipo': 'bye', 'ganador': c1['pareja_id']})
            print(f"   BYE: Seed {seed1} (pareja {c1['pareja_id']}) avanza automáticamente")
        elif c2:
            # c1 es bye, c2 avanza
            partidos_primera_ronda.append({'numero': i + 1, 'tipo': 'bye', 'ganador': c2['pareja_id']})
            print(f"   BYE: Seed {seed2} (pareja {c2['pareja_id']}) avanza automáticamente")
    
    db.flush()
    
    # Crear partidos de siguiente fase con byes pre-asignados
    if potencia > 2:
        siguiente_fase = siguiente_fase_map.get(fase_inicial)
        if siguiente_fase:
            num_partidos_siguiente = potencia // 4
            
            for i in range(num_partidos_siguiente):
                partido_origen_1 = i * 2 + 1  # Impar
                partido_origen_2 = i * 2 + 2  # Par
                
                pareja1_id = None
                pareja2_id = None
                
                # Buscar si alguno es bye
                for pr in partidos_primera_ronda:
                    if pr['numero'] == partido_origen_1 and pr['tipo'] == 'bye':
                        pareja1_id = pr['ganador']
                    elif pr['numero'] == partido_origen_2 and pr['tipo'] == 'bye':
                        pareja2_id = pr['ganador']
                
                partido_siguiente = Partido(
                    id_torneo=torneo_id,
                    pareja1_id=pareja1_id,
                    pareja2_id=pareja2_id,
                    fase=siguiente_fase,
                    numero_partido=i + 1,
                    estado='pendiente',
                    tipo='torneo',
                    fecha=datetime.now(),
                    id_creador=CREADOR_ID
                )
                db.add(partido_siguiente)
                
                if pareja1_id or pareja2_id:
                    print(f"   {siguiente_fase} #{i+1}: pareja1={pareja1_id or 'TBD'}, pareja2={pareja2_id or 'TBD'}")
    
    db.commit()
    
    print(f"   ✅ {len(partidos_playoff)} partidos de playoff creados")
    return partidos_playoff


def simular_playoffs(partidos_playoff, torneo_id):
    """Simula los playoffs completos hasta la final, manejando byes correctamente"""
    print("\n🎯 Simulando playoffs...")
    
    fases = ['16avos', '8vos', '4tos', 'semis', 'final']
    
    for fase in fases:
        # Obtener partidos pendientes de esta fase
        partidos_fase = db.query(Partido).filter(
            Partido.id_torneo == torneo_id,
            Partido.fase == fase,
            Partido.estado == 'pendiente'
        ).order_by(Partido.numero_partido).all()
        
        if not partidos_fase:
            continue
        
        print(f"   Fase: {fase} ({len(partidos_fase)} partidos)")
        
        for partido in partidos_fase:
            # Verificar si el partido tiene ambas parejas
            if partido.pareja1_id and partido.pareja2_id:
                # Partido normal - simular
                try:
                    resultado = generar_resultado_aleatorio()
                    partido_actualizado = TorneoResultadoService.cargar_resultado(
                        db, partido.id_partido, resultado, CREADOR_ID
                    )
                    if partido_actualizado.ganador_pareja_id:
                        print(f"     ✅ Partido {partido.numero_partido}: Ganador pareja {partido_actualizado.ganador_pareja_id}")
                except Exception as e:
                    print(f"     ❌ Error partido {partido.id_partido}: {e}")
                    db.rollback()
            elif partido.pareja1_id or partido.pareja2_id:
                # Solo una pareja - esperar a que se complete
                print(f"     ⏳ Partido {partido.numero_partido}: Esperando rival (pareja1={partido.pareja1_id}, pareja2={partido.pareja2_id})")
            else:
                # Sin parejas - esperar
                print(f"     ⏳ Partido {partido.numero_partido}: Sin parejas asignadas")
        
        # Verificar si es la final y hay ganador
        if fase == 'final':
            final = db.query(Partido).filter(
                Partido.id_torneo == torneo_id,
                Partido.fase == 'final',
                Partido.estado == 'confirmado'
            ).first()
            
            if final and final.ganador_pareja_id:
                print(f"   🏆 ¡Campeón: Pareja {final.ganador_pareja_id}!")
            break
        
        db.commit()


def mostrar_resumen(torneo_id, usuarios_antes):
    """Muestra resumen de cambios de rating"""
    print("\n📊 RESUMEN DE CAMBIOS DE RATING:")
    print("-" * 60)
    
    db.expire_all()
    
    cambios = []
    for uid, rating_antes in usuarios_antes.items():
        usuario = db.query(Usuario).filter(Usuario.id_usuario == uid).first()
        if usuario:
            cambio = (usuario.rating or 1200) - rating_antes
            cambios.append({
                'nombre': usuario.nombre_usuario,
                'antes': rating_antes,
                'despues': usuario.rating or 1200,
                'cambio': cambio,
                'partidos': usuario.partidos_jugados or 0
            })
    
    cambios.sort(key=lambda x: x['cambio'], reverse=True)
    
    for c in cambios[:15]:  # Top 15
        signo = "+" if c['cambio'] >= 0 else ""
        print(f"   {c['nombre'][:20]:<20} | {c['antes']:>4} → {c['despues']:>4} ({signo}{c['cambio']:>3}) | {c['partidos']} partidos")


def main():
    print("=" * 60)
    print("🎮 SIMULADOR DE TORNEO 'PRUEBA' CON PLAYOFFS")
    print("=" * 60)
    
    # Guardar ratings antes
    usuarios = db.query(Usuario).all()
    usuarios_antes = {u.id_usuario: (u.rating or 1200) for u in usuarios}
    print(f"\n📋 Usuarios: {len(usuarios)}")
    
    # Limpiar torneos anteriores
    limpiar_torneos_anteriores()
    
    # Crear torneo
    torneo_id = crear_torneo()
    
    # Cambiar estado
    db.execute(text("UPDATE torneos SET estado = 'armando_zonas' WHERE id = :tid"), {'tid': torneo_id})
    db.commit()
    
    # Crear parejas
    parejas = crear_parejas(torneo_id)
    
    # Crear zonas
    zonas = crear_zonas(torneo_id, parejas)
    
    # Cambiar estado a fase de grupos
    db.execute(text("UPDATE torneos SET estado = 'fase_grupos' WHERE id = :tid"), {'tid': torneo_id})
    db.commit()
    
    # Generar y simular partidos de zona
    print("\n📅 Generando fixture de zonas...")
    todos_partidos = []
    for zona in zonas:
        partidos_zona = generar_partidos_zona(torneo_id, zona)
        todos_partidos.extend(partidos_zona)
        print(f"   - {zona.nombre}: {len(partidos_zona)} partidos")
    
    db.commit()
    
    print(f"\n🎾 Simulando {len(todos_partidos)} partidos de zona...")
    exitos, errores = simular_partidos(todos_partidos)
    print(f"   ✅ Exitosos: {exitos}, ❌ Errores: {errores}")
    
    # Generar playoffs
    partidos_playoff = generar_playoffs(torneo_id, zonas)
    
    # Simular playoffs
    if partidos_playoff:
        simular_playoffs(partidos_playoff, torneo_id)
    
    # Cambiar estado a finalizado
    db.execute(text("UPDATE torneos SET estado = 'finalizado' WHERE id = :tid"), {'tid': torneo_id})
    db.commit()
    
    # Mostrar resumen
    mostrar_resumen(torneo_id, usuarios_antes)
    
    print("\n" + "=" * 60)
    print("✅ TORNEO 'PRUEBA' COMPLETADO!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()
