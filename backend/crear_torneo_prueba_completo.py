"""
Script para crear un torneo de prueba completo con todas las características
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.database.config import SessionLocal
from src.models.torneo_models import Torneo, TorneoCategoria, TorneoPareja, TorneoCancha
from src.models.driveplus_models import Usuario
import random

def crear_torneo_prueba():
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("🏆 CREANDO TORNEO DE PRUEBA COMPLETO")
        print("=" * 80)
        
        # 1. Calcular fechas (próximo jueves a domingo)
        hoy = datetime.now().date()
        dias_hasta_jueves = (3 - hoy.weekday()) % 7  # 3 = jueves
        if dias_hasta_jueves == 0:
            dias_hasta_jueves = 7  # Si hoy es jueves, ir al próximo
        
        fecha_inicio = hoy + timedelta(days=dias_hasta_jueves)
        fecha_fin = fecha_inicio + timedelta(days=3)  # Jueves a Domingo
        
        print(f"\n📅 Fechas del torneo:")
        print(f"   Inicio: {fecha_inicio.strftime('%d/%m/%Y')} (Jueves)")
        print(f"   Fin: {fecha_fin.strftime('%d/%m/%Y')} (Domingo)")
        
        # 2. Crear torneo
        torneo = Torneo(
            nombre="Torneo de Prueba Completo - Drive+",
            descripcion="Torneo de prueba con todas las características: pagos, horarios, múltiples categorías, fixture automático",
            tipo="grupos",
            categoria="8va",  # Categoría principal
            genero="masculino",
            estado="inscripcion",
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            lugar="Club de Prueba - Drive+",
            creado_por=14,  # Usuario organizador
            # Configuración de pago
            requiere_pago=True,
            monto_inscripcion=5000.0,
            alias_cbu_cvu="torneo.prueba.mp",
            titular_cuenta="Drive+ Torneos",
            banco="Mercado Pago",
            # Horarios disponibles
            horarios_disponibles={
                "semana": [
                    {"desde": "12:00", "hasta": "23:00"}
                ],
                "finDeSemana": [
                    {"desde": "09:00", "hasta": "23:00"}
                ]
            },
            reglas_json={
                "puntos_victoria": 3,
                "puntos_derrota": 0,
                "sets_para_ganar": 2,
                "canchas_disponibles": 3
            }
        )
        
        db.add(torneo)
        db.flush()
        
        print(f"\n✅ Torneo creado: ID {torneo.id}")
        print(f"   Nombre: {torneo.nombre}")
        print(f"   Pago: ${torneo.monto_inscripcion} - Alias: {torneo.alias_cbu_cvu}")
        
        # 3. Crear categorías
        print(f"\n📋 Creando categorías...")
        
        cat_8va = TorneoCategoria(
            torneo_id=torneo.id,
            nombre="8va",
            genero="masculino",
            max_parejas=999,
            estado="activa",
            orden=1
        )
        db.add(cat_8va)
        
        cat_6ta = TorneoCategoria(
            torneo_id=torneo.id,
            nombre="6ta",
            genero="masculino",
            max_parejas=999,
            estado="activa",
            orden=2
        )
        db.add(cat_6ta)
        
        db.flush()
        
        print(f"   ✅ 8va Masculino (ID: {cat_8va.id})")
        print(f"   ✅ 6ta Masculino (ID: {cat_6ta.id})")
        
        # 4. Crear canchas
        print(f"\n🎾 Creando canchas...")
        
        canchas = []
        for i in range(1, 4):
            cancha = TorneoCancha(
                torneo_id=torneo.id,
                nombre=f"Cancha {i}",
                activa=True
            )
            db.add(cancha)
            canchas.append(cancha)
        
        db.flush()
        print(f"   ✅ 3 canchas creadas")
        
        # 5. Obtener usuarios disponibles (excluir 14 y 15)
        usuarios = db.query(Usuario).filter(
            Usuario.id_usuario.notin_([14, 15])
        ).all()
        
        print(f"\n👥 Usuarios disponibles: {len(usuarios)}")
        
        if len(usuarios) < 8:
            print("   ⚠️  Se necesitan al menos 8 usuarios para crear parejas")
            return
        
        # Mezclar usuarios
        random.shuffle(usuarios)
        
        # 6. Crear parejas para 8va (primeros 12 usuarios)
        print(f"\n🤝 Inscribiendo parejas en 8va Masculino...")
        
        parejas_8va = []
        disponibilidades_8va = [
            # Variedad de disponibilidades para probar compatibilidad
            {"franjas": [{"dias": ["jueves", "viernes"], "horaInicio": "18:00", "horaFin": "22:00"}]},
            {"franjas": [{"dias": ["sabado", "domingo"], "horaInicio": "10:00", "horaFin": "14:00"}]},
            {"franjas": [{"dias": ["viernes"], "horaInicio": "19:00", "horaFin": "23:00"}]},
            {"franjas": [{"dias": ["sabado"], "horaInicio": "09:00", "horaFin": "13:00"}]},
            {"franjas": [{"dias": ["domingo"], "horaInicio": "15:00", "horaFin": "20:00"}]},
            {},  # Sin restricciones (disponible siempre)
        ]
        
        for i in range(0, min(12, len(usuarios)), 2):
            if i + 1 >= len(usuarios):
                break
            
            disponibilidad = disponibilidades_8va[i // 2 % len(disponibilidades_8va)]
            
            pareja = TorneoPareja(
                torneo_id=torneo.id,
                categoria_id=cat_8va.id,
                jugador1_id=usuarios[i].id_usuario,
                jugador2_id=usuarios[i + 1].id_usuario,
                estado="confirmada",
                disponibilidad_horaria=disponibilidad,
                pago_estado="aprobado",
                pago_monto=5000.0
            )
            db.add(pareja)
            parejas_8va.append(pareja)
        
        db.flush()
        print(f"   ✅ {len(parejas_8va)} parejas inscritas en 8va")
        
        # Guardar info de parejas 8va para reporte
        info_parejas_8va = []
        for idx, pareja in enumerate(parejas_8va):
            u1 = db.query(Usuario).filter(Usuario.id_usuario == pareja.jugador1_id).first()
            u2 = db.query(Usuario).filter(Usuario.id_usuario == pareja.jugador2_id).first()
            info_parejas_8va.append({
                "pareja": pareja,
                "nombre": f"{u1.nombre_usuario}/{u2.nombre_usuario}",
                "disponibilidad": pareja.disponibilidad_horaria
            })
        
        # 7. Crear parejas para 6ta (siguientes 8 usuarios)
        print(f"\n🤝 Inscribiendo parejas en 6ta Masculino...")
        
        parejas_6ta = []
        for i in range(12, min(20, len(usuarios)), 2):
            if i + 1 >= len(usuarios):
                break
            
            disponibilidad = disponibilidades_8va[i // 2 % len(disponibilidades_8va)]
            
            pareja = TorneoPareja(
                torneo_id=torneo.id,
                categoria_id=cat_6ta.id,
                jugador1_id=usuarios[i].id_usuario,
                jugador2_id=usuarios[i + 1].id_usuario,
                estado="confirmada",
                disponibilidad_horaria=disponibilidad,
                pago_estado="aprobado",
                pago_monto=5000.0
            )
            db.add(pareja)
            parejas_6ta.append(pareja)
        
        db.flush()
        print(f"   ✅ {len(parejas_6ta)} parejas inscritas en 6ta")
        
        # Guardar info de parejas 6ta para reporte
        info_parejas_6ta = []
        for idx, pareja in enumerate(parejas_6ta):
            u1 = db.query(Usuario).filter(Usuario.id_usuario == pareja.jugador1_id).first()
            u2 = db.query(Usuario).filter(Usuario.id_usuario == pareja.jugador2_id).first()
            info_parejas_6ta.append({
                "pareja": pareja,
                "nombre": f"{u1.nombre_usuario}/{u2.nombre_usuario}",
                "disponibilidad": pareja.disponibilidad_horaria
            })
        
        db.commit()
        
        print("\n" + "=" * 80)
        print("✅ TORNEO DE PRUEBA CREADO EXITOSAMENTE")
        print("=" * 80)
        print(f"\n📌 ID del torneo: {torneo.id}")
        print(f"📌 Nombre: {torneo.nombre}")
        print(f"📌 Fechas: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}")
        print(f"📌 Categorías: 8va Masc ({len(parejas_8va)} parejas), 6ta Masc ({len(parejas_6ta)} parejas)")
        print(f"📌 Pago: ${torneo.monto_inscripcion} - Alias: {torneo.alias_cbu_cvu}")
        print(f"📌 Canchas: 3")
        print(f"📌 Horarios: Semana 12-23h, Fin de semana 9-23h")
        print(f"\n💡 Usuarios 14 y 15 están libres para que te inscribas y pruebes")
        print(f"💡 Puedes ver el torneo en: /torneos/{torneo.id}")
        print("\n" + "=" * 80)
        
        # REPORTE DE DISPONIBILIDAD HORARIA Y ZONAS
        print("\n" + "=" * 80)
        print("📊 REPORTE DE DISPONIBILIDAD HORARIA DE PAREJAS")
        print("=" * 80)
        
        # Reporte 8va
        print(f"\n🏆 CATEGORÍA 8VA MASCULINO ({len(parejas_8va)} parejas)")
        print("-" * 80)
        
        for idx, info in enumerate(info_parejas_8va, 1):
            pareja = info['pareja']
            nombre = info['nombre']
            disp = info['disponibilidad']
            
            if not disp or not disp.get('franjas'):
                horarios_str = "✅ Disponible SIEMPRE (sin restricciones)"
            else:
                franjas = disp.get('franjas', [])
                horarios_list = []
                for franja in franjas:
                    dias = ", ".join(franja.get('dias', []))
                    desde = franja.get('horaInicio', '')
                    hasta = franja.get('horaFin', '')
                    horarios_list.append(f"{dias}: {desde}-{hasta}")
                horarios_str = " | ".join(horarios_list)
            
            print(f"   {idx}. {nombre:30} → {horarios_str}")
        
        # Reporte 6ta
        print(f"\n🏆 CATEGORÍA 6TA MASCULINO ({len(parejas_6ta)} parejas)")
        print("-" * 80)
        
        for idx, info in enumerate(info_parejas_6ta, 1):
            pareja = info['pareja']
            nombre = info['nombre']
            disp = info['disponibilidad']
            
            if not disp or not disp.get('franjas'):
                horarios_str = "✅ Disponible SIEMPRE (sin restricciones)"
            else:
                franjas = disp.get('franjas', [])
                horarios_list = []
                for franja in franjas:
                    dias = ", ".join(franja.get('dias', []))
                    desde = franja.get('horaInicio', '')
                    hasta = franja.get('horaFin', '')
                    horarios_list.append(f"{dias}: {desde}-{hasta}")
                horarios_str = " | ".join(horarios_list)
            
            print(f"   {idx}. {nombre:30} → {horarios_str}")
        
        print("\n" + "=" * 80)
        print("💡 PRÓXIMOS PASOS")
        print("=" * 80)
        print("\n1. Ve al torneo en la web: /torneos/{torneo.id}")
        print("2. En la pestaña 'Zonas', genera las zonas usando el botón 'Generar Zonas Inteligente'")
        print("3. El sistema agrupará parejas con horarios compatibles automáticamente")
        print("4. Luego genera el fixture en la pestaña 'Fixture'")
        print("5. El fixture respetará:")
        print("   - Máximo 3 partidos simultáneos (3 canchas)")
        print("   - Disponibilidad horaria de cada pareja")
        print("   - Duración de 50 minutos por partido")
        print("   - Horarios del torneo (Semana 12-23h, Fin de semana 9-23h)")
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    crear_torneo_prueba()
