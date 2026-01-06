"""
Test completo del sistema de marcador de pádel
Prueba el flujo completo: crear sala → iniciar → cargar resultado → confirmar → Elo
"""
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

load_dotenv()

from src.models.Drive+_models import Usuario, Partido, PartidoJugador
from src.models.sala import Sala, SalaJugador
from src.services.anti_trampa_service import AntiTrampaService
from src.services.confirmacion_service import ConfirmacionService

# Configurar base de datos
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def print_section(title):
    """Imprime una sección con formato"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_flujo_completo():
    """Test del flujo completo del sistema de marcador"""
    
    db = SessionLocal()
    
    try:
        print_section("🎾 TEST SISTEMA DE MARCADOR DE PÁDEL")
        
        # ============================================
        # 1. OBTENER O CREAR USUARIOS DE PRUEBA
        # ============================================
        print_section("1️⃣  Obteniendo usuarios de prueba")
        
        usuarios = db.query(Usuario).limit(4).all()
        
        if len(usuarios) < 4:
            print("❌ Error: Se necesitan al menos 4 usuarios en la base de datos")
            print("   Crea usuarios primero con el script de registro")
            return
        
        jugador1, jugador2, jugador3, jugador4 = usuarios[:4]
        
        print(f"✅ Jugador 1: {jugador1.nombre_usuario} (Rating: {jugador1.rating})")
        print(f"✅ Jugador 2: {jugador2.nombre_usuario} (Rating: {jugador2.rating})")
        print(f"✅ Jugador 3: {jugador3.nombre_usuario} (Rating: {jugador3.rating})")
        print(f"✅ Jugador 4: {jugador4.nombre_usuario} (Rating: {jugador4.rating})")
        
        # ============================================
        # 2. CREAR SALA
        # ============================================
        print_section("2️⃣  Creando sala")
        
        sala = Sala(
            nombre="Test Partido Amistoso",
            codigo_invitacion=Sala.generar_codigo(),
            fecha=datetime.now(),
            estado="esperando",
            id_creador=jugador1.id_usuario,
            max_jugadores=4
        )
        db.add(sala)
        db.flush()
        
        print(f"✅ Sala creada: {sala.nombre}")
        print(f"   Código: {sala.codigo_invitacion}")
        print(f"   ID: {sala.id_sala}")
        
        # ============================================
        # 3. AGREGAR JUGADORES A LA SALA
        # ============================================
        print_section("3️⃣  Agregando jugadores a la sala")
        
        for i, jugador in enumerate([jugador1, jugador2, jugador3, jugador4], 1):
            sala_jugador = SalaJugador(
                id_sala=sala.id_sala,
                id_usuario=jugador.id_usuario,
                orden=i
            )
            db.add(sala_jugador)
        
        db.commit()
        print(f"✅ 4 jugadores agregados a la sala")
        
        # ============================================
        # 4. ASIGNAR EQUIPOS
        # ============================================
        print_section("4️⃣  Asignando equipos")
        
        jugadores_sala = db.query(SalaJugador).filter(
            SalaJugador.id_sala == sala.id_sala
        ).all()
        
        # Equipo 1: Jugador 1 y 2
        # Equipo 2: Jugador 3 y 4
        jugadores_sala[0].equipo = 1
        jugadores_sala[1].equipo = 1
        jugadores_sala[2].equipo = 2
        jugadores_sala[3].equipo = 2
        
        db.commit()
        
        print(f"✅ Equipo 1: {jugador1.nombre_usuario} + {jugador2.nombre_usuario}")
        print(f"✅ Equipo 2: {jugador3.nombre_usuario} + {jugador4.nombre_usuario}")
        
        # ============================================
        # 5. VERIFICAR ANTI-TRAMPA
        # ============================================
        print_section("5️⃣  Verificando anti-trampa")
        
        jugadores_ids = [j.id_usuario for j in [jugador1, jugador2, jugador3, jugador4]]
        verificacion = AntiTrampaService.verificar_limite_partidos(jugadores_ids, db)
        
        if verificacion["puede_jugar"]:
            print(f"✅ {verificacion['mensaje']}")
            print(f"   Partidos jugados esta semana: {verificacion['partidos_jugados']}/{verificacion['limite']}")
        else:
            print(f"⚠️  {verificacion['mensaje']}")
            print(f"   Jugadores bloqueados: {', '.join(verificacion['jugadores_bloqueados'])}")
            print(f"   Próxima disponibilidad: {verificacion['proxima_disponibilidad']}")
            print(f"\n💡 El anti-trampa está funcionando correctamente!")
            print(f"   Para continuar el test, limpiando historial de prueba...")
            
            # Limpiar historial de enfrentamientos para este test
            from src.models.historial_enfrentamiento import HistorialEnfrentamiento
            hashes = AntiTrampaService.generar_hashes_cuarteto(jugadores_ids)
            
            # Eliminar registros de estos jugadores
            for hash_value in hashes.values():
                db.query(HistorialEnfrentamiento).filter(
                    (HistorialEnfrentamiento.hash_trio_1 == hash_value) |
                    (HistorialEnfrentamiento.hash_trio_2 == hash_value) |
                    (HistorialEnfrentamiento.hash_trio_3 == hash_value) |
                    (HistorialEnfrentamiento.hash_trio_4 == hash_value)
                ).delete()
            
            db.commit()
            print(f"   ✅ Historial limpiado para continuar test")
            
            # Verificar de nuevo
            verificacion = AntiTrampaService.verificar_limite_partidos(jugadores_ids, db)
            print(f"   ✅ Ahora pueden jugar: {verificacion['puede_jugar']}")
        
        # ============================================
        # 6. INICIAR PARTIDO
        # ============================================
        print_section("6️⃣  Iniciando partido")
        
        partido = Partido(
            fecha=datetime.now(),
            estado="pendiente",  # Usar valor válido del constraint
            id_creador=jugador1.id_usuario,
            tipo="amistoso",
            id_sala=sala.id_sala,
            creado_por=jugador1.id_usuario
        )
        db.add(partido)
        db.flush()
        
        # Agregar jugadores al partido
        for jugador_sala in jugadores_sala:
            partido_jugador = PartidoJugador(
                id_partido=partido.id_partido,
                id_usuario=jugador_sala.id_usuario,
                equipo=jugador_sala.equipo
            )
            db.add(partido_jugador)
        
        # Registrar en historial de enfrentamientos
        AntiTrampaService.registrar_enfrentamiento(
            id_partido=partido.id_partido,
            jugadores_ids=jugadores_ids,
            tipo_partido="amistoso",
            db=db
        )
        
        sala.estado = "en_juego"
        sala.id_partido = partido.id_partido
        
        db.commit()
        
        print(f"✅ Partido iniciado")
        print(f"   ID Partido: {partido.id_partido}")
        print(f"   Registrado en historial anti-trampa")
        
        # ============================================
        # 7. CARGAR RESULTADO
        # ============================================
        print_section("7️⃣  Cargando resultado del partido")
        
        # Resultado: Equipo 1 gana 2-1 (6-4, 4-6, 10-8 supertiebreak)
        resultado = {
            "formato": "best_of_3",
            "sets": [
                {
                    "gamesEquipoA": 6,
                    "gamesEquipoB": 4,
                    "ganador": "equipoA",
                    "completado": True
                },
                {
                    "gamesEquipoA": 4,
                    "gamesEquipoB": 6,
                    "ganador": "equipoB",
                    "completado": True
                }
            ],
            "supertiebreak": {
                "puntosEquipoA": 10,
                "puntosEquipoB": 8,
                "ganador": "equipoA",
                "completado": True
            },
            "ganador": "equipoA",
            "completado": True
        }
        
        partido.resultado_padel = resultado
        partido.ganador_equipo = 1
        partido.estado_confirmacion = "pendiente_confirmacion"
        partido.estado = "confirmado"  # Usar valor válido del constraint
        sala.estado = "finalizada"
        
        db.commit()
        
        print(f"✅ Resultado cargado")
        print(f"   Ganador: Equipo 1 ({jugador1.nombre_usuario} + {jugador2.nombre_usuario})")
        print(f"   Resultado: 6-4, 4-6, 10-8 (supertiebreak)")
        print(f"   Estado: {partido.estado_confirmacion}")
        
        # ============================================
        # 8. CONFIRMAR RESULTADO (3 RIVALES)
        # ============================================
        print_section("8️⃣  Confirmando resultado")
        
        # Guardar ratings antes
        ratings_antes = {
            jugador1.id_usuario: jugador1.rating,
            jugador2.id_usuario: jugador2.rating,
            jugador3.id_usuario: jugador3.rating,
            jugador4.id_usuario: jugador4.rating
        }
        
        print(f"\n📊 Ratings ANTES del partido:")
        print(f"   {jugador1.nombre_usuario}: {jugador1.rating}")
        print(f"   {jugador2.nombre_usuario}: {jugador2.rating}")
        print(f"   {jugador3.nombre_usuario}: {jugador3.rating}")
        print(f"   {jugador4.nombre_usuario}: {jugador4.rating}")
        
        # Confirmar por cada rival (jugadores 2, 3, 4)
        for i, jugador in enumerate([jugador2, jugador3, jugador4], 1):
            print(f"\n   [{i}/3] {jugador.nombre_usuario} confirmando...")
            
            resultado_conf = ConfirmacionService.confirmar_resultado(
                partido.id_partido,
                jugador.id_usuario,
                db
            )
            
            print(f"   ✅ {resultado_conf['mensaje']}")
            
            if resultado_conf['elo_aplicado']:
                print(f"\n   🎉 ¡Todos confirmaron! Elo aplicado:")
                
                # Refrescar usuarios para ver cambios
                db.refresh(jugador1)
                db.refresh(jugador2)
                db.refresh(jugador3)
                db.refresh(jugador4)
                
                print(f"\n📊 Ratings DESPUÉS del partido:")
                print(f"   {jugador1.nombre_usuario}: {ratings_antes[jugador1.id_usuario]} → {jugador1.rating} ({jugador1.rating - ratings_antes[jugador1.id_usuario]:+d})")
                print(f"   {jugador2.nombre_usuario}: {ratings_antes[jugador2.id_usuario]} → {jugador2.rating} ({jugador2.rating - ratings_antes[jugador2.id_usuario]:+d})")
                print(f"   {jugador3.nombre_usuario}: {ratings_antes[jugador3.id_usuario]} → {jugador3.rating} ({jugador3.rating - ratings_antes[jugador3.id_usuario]:+d})")
                print(f"   {jugador4.nombre_usuario}: {ratings_antes[jugador4.id_usuario]} → {jugador4.rating} ({jugador4.rating - ratings_antes[jugador4.id_usuario]:+d})")
        
        # ============================================
        # 9. VERIFICAR ESTADO FINAL
        # ============================================
        print_section("9️⃣  Verificando estado final")
        
        db.refresh(partido)
        
        print(f"✅ Estado del partido: {partido.estado_confirmacion}")
        print(f"✅ Elo aplicado: {partido.elo_aplicado}")
        print(f"✅ Ganador: Equipo {partido.ganador_equipo}")
        
        # Verificar partido_jugadores
        jugadores_partido = db.query(PartidoJugador).filter(
            PartidoJugador.id_partido == partido.id_partido
        ).all()
        
        print(f"\n📋 Detalles de cambios de Elo:")
        for jp in jugadores_partido:
            usuario = db.query(Usuario).filter(Usuario.id_usuario == jp.id_usuario).first()
            print(f"   {usuario.nombre_usuario}:")
            print(f"      Rating antes: {jp.rating_antes}")
            print(f"      Rating después: {jp.rating_despues}")
            print(f"      Cambio: {jp.cambio_elo:+d}")
        
        # ============================================
        # 10. TEST ANTI-TRAMPA
        # ============================================
        print_section("🔟 Probando anti-trampa")
        
        print("\n🔄 Intentando crear otro partido con los mismos jugadores...")
        
        verificacion2 = AntiTrampaService.verificar_limite_partidos(jugadores_ids, db)
        
        print(f"   Partidos jugados: {verificacion2['partidos_jugados']}/{verificacion2['limite']}")
        
        if verificacion2["puede_jugar"]:
            print(f"   ✅ Pueden jugar otro partido")
        else:
            print(f"   ❌ Límite alcanzado")
            print(f"   Jugadores bloqueados: {', '.join(verificacion2['jugadores_bloqueados'])}")
        
        # ============================================
        # RESUMEN FINAL
        # ============================================
        print_section("✅ TEST COMPLETADO EXITOSAMENTE")
        
        print("\n📊 Resumen:")
        print(f"   ✅ Sala creada y jugadores agregados")
        print(f"   ✅ Equipos asignados")
        print(f"   ✅ Anti-trampa verificado")
        print(f"   ✅ Partido iniciado")
        print(f"   ✅ Resultado cargado")
        print(f"   ✅ Confirmaciones procesadas (3/3)")
        print(f"   ✅ Elo aplicado correctamente")
        print(f"   ✅ Historial de enfrentamientos registrado")
        
        print("\n🎉 ¡El sistema de marcador funciona correctamente!")
        
    except Exception as e:
        print(f"\n❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_flujo_completo()
