#!/usr/bin/env python3
"""
Script para crear un torneo masivo usando el sistema de RESTRICCIONES horarias
Similar al torneo 17 pero con restricciones en lugar de disponibilidad
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.config import get_db
from src.models.driveplus_models import Usuario, PerfilUsuario
from src.models.torneo_models import Torneo, TorneoCategoria, TorneoPareja
from datetime import datetime, timedelta
import random
import json

def crear_torneo_con_restricciones():
    """Crear torneo masivo con sistema de restricciones horarias"""
    db = next(get_db())
    
    try:
        print("🏆 Creando torneo masivo con sistema de RESTRICCIONES...")
        
        # Fechas del torneo (próxima semana)
        hoy = datetime.now()
        inicio = hoy + timedelta(days=7)  # Próximo viernes
        fin = inicio + timedelta(days=2)  # Domingo
        
        # Crear torneo
        torneo = Torneo(
            nombre="Torneo Restricciones - Drive+ Open",
            descripcion="Torneo de prueba usando sistema de restricciones horarias. Los jugadores especifican cuándo NO pueden jugar.",
            categoria="Múltiples",
            genero="mixto",
            fecha_inicio=inicio.date(),
            fecha_fin=fin.date(),
            lugar="Club Drive+ - Canchas 1, 2 y 3",
            monto_inscripcion=5000.0,
            requiere_pago=True,
            alias_cbu_cvu="drive.plus.test",
            titular_cuenta="Club Drive Plus",
            banco="Banco Test",
            estado="inscripcion",
            creado_por=1,  # Usuario admin
            # Horarios del torneo
            horarios_disponibles={
                "viernes": {"inicio": "12:00", "fin": "23:00"},
                "sabado": {"inicio": "09:00", "fin": "23:00"},
                "domingo": {"inicio": "09:00", "fin": "23:00"}
            }
        )
        
        db.add(torneo)
        db.flush()  # Para obtener el ID
        
        print(f"✅ Torneo creado con ID: {torneo.id}")
        
        # Crear categorías (mismas que torneo 17)
        categorias_config = [
            {"nombre": "7ma Masculino", "genero": "masculino", "nivel_min": 7, "nivel_max": 7, "parejas": 16},
            {"nombre": "5ta Masculino", "genero": "masculino", "nivel_min": 5, "nivel_max": 5, "parejas": 16},
            {"nombre": "3ra Masculino", "genero": "masculino", "nivel_min": 3, "nivel_max": 3, "parejas": 16},
            {"nombre": "7ma Femenino", "genero": "femenino", "nivel_min": 7, "nivel_max": 7, "parejas": 16},
            {"nombre": "5ta Femenino", "genero": "femenino", "nivel_min": 5, "nivel_max": 5, "parejas": 16}
        ]
        
        categorias_creadas = []
        
        for cat_config in categorias_config:
            categoria = TorneoCategoria(
                torneo_id=torneo.id,
                nombre=cat_config["nombre"],
                genero=cat_config["genero"],
                max_parejas=cat_config["parejas"]
            )
            db.add(categoria)
            db.flush()
            categorias_creadas.append((categoria, cat_config["parejas"]))
            print(f"📂 Categoría creada: {categoria.nombre} (ID: {categoria.id})")
        
        # Crear usuarios y parejas
        timestamp = int(datetime.now().timestamp())
        usuario_id_counter = 1000  # Empezar desde 1000 para evitar conflictos
        
        # Definir tipos de restricciones más realistas
        restricciones_comunes = [
            # Sin restricciones (disponible siempre)
            [],
            # Restricciones laborales típicas
            [{"dia": "viernes", "inicio": "12:00", "fin": "17:00"}],  # No puede viernes tarde
            [{"dia": "sabado", "inicio": "09:00", "fin": "14:00"}],   # No puede sábado mañana
            [{"dia": "domingo", "inicio": "18:00", "fin": "23:00"}],  # No puede domingo noche
            # Restricciones familiares
            [{"dia": "sabado", "inicio": "09:00", "fin": "12:00"}],   # No puede sábado muy temprano
            [{"dia": "domingo", "inicio": "09:00", "fin": "15:00"}],  # No puede domingo hasta tarde
            # Restricciones múltiples
            [
                {"dia": "viernes", "inicio": "12:00", "fin": "15:00"},
                {"dia": "domingo", "inicio": "20:00", "fin": "23:00"}
            ],
            [
                {"dia": "sabado", "inicio": "09:00", "fin": "11:00"},
                {"dia": "domingo", "inicio": "21:00", "fin": "23:00"}
            ]
        ]
        
        for categoria, num_parejas in categorias_creadas:
            print(f"\n👥 Creando {num_parejas} parejas para {categoria.nombre}...")
            
            # Encontrar la configuración de esta categoría
            cat_config = next(c for c in categorias_config if c["nombre"] == categoria.nombre)
            
            for i in range(num_parejas):
                # Crear jugador 1
                usuario1 = Usuario(
                    id_usuario=usuario_id_counter,
                    nombre_usuario=f"jugador_{categoria.nombre.lower().replace(' ', '_')}_{i+1}_1_{timestamp}",
                    email=f"jugador_{categoria.nombre.lower().replace(' ', '_')}_{i+1}_1_{timestamp}@test.com",
                    password_hash="dummy_hash_for_testing",
                    rating=cat_config["nivel_min"] * 100 + random.randint(-50, 50),
                    sexo=categoria.genero
                )
                db.add(usuario1)
                
                perfil1 = PerfilUsuario(
                    id_usuario=usuario1.id_usuario,
                    nombre=f"Jugador1",
                    apellido=f"{categoria.nombre.split()[0]}_{i+1}",
                    telefono=f"11{random.randint(10000000, 99999999)}",
                    fecha_nacimiento=datetime(1990, 1, 1).date(),
                    mano_habil=random.choice(["derecha", "zurda"])
                )
                db.add(perfil1)
                usuario_id_counter += 1
                
                # Crear jugador 2
                usuario2 = Usuario(
                    id_usuario=usuario_id_counter,
                    nombre_usuario=f"jugador_{categoria.nombre.lower().replace(' ', '_')}_{i+1}_2_{timestamp}",
                    email=f"jugador_{categoria.nombre.lower().replace(' ', '_')}_{i+1}_2_{timestamp}@test.com",
                    password_hash="dummy_hash_for_testing",
                    rating=cat_config["nivel_min"] * 100 + random.randint(-50, 50),
                    sexo=categoria.genero
                )
                db.add(usuario2)
                
                perfil2 = PerfilUsuario(
                    id_usuario=usuario2.id_usuario,
                    nombre=f"Jugador2",
                    apellido=f"{categoria.nombre.split()[0]}_{i+1}",
                    telefono=f"11{random.randint(10000000, 99999999)}",
                    fecha_nacimiento=datetime(1990, 1, 1).date(),
                    mano_habil=random.choice(["derecha", "zurda"])
                )
                db.add(perfil2)
                usuario_id_counter += 1
                
                # Asignar restricciones horarias (NUEVO SISTEMA)
                # 30% sin restricciones, 70% con restricciones variadas
                if random.random() < 0.3:
                    restricciones = []  # Sin restricciones
                    tipo_restriccion = "Sin restricciones"
                else:
                    restricciones = random.choice(restricciones_comunes[1:])  # Con restricciones
                    if len(restricciones) == 0:
                        tipo_restriccion = "Sin restricciones"
                    elif len(restricciones) == 1:
                        r = restricciones[0]
                        tipo_restriccion = f"No puede {r['dia']} {r['inicio']}-{r['fin']}"
                    else:
                        tipo_restriccion = f"{len(restricciones)} restricciones"
                
                # Crear pareja con restricciones
                pareja = TorneoPareja(
                    torneo_id=torneo.id,
                    categoria_id=categoria.id,
                    jugador1_id=usuario1.id_usuario,
                    jugador2_id=usuario2.id_usuario,
                    estado="confirmada",
                    # RESTRICCIONES en lugar de disponibilidad
                    disponibilidad_horaria=restricciones  # Ahora son restricciones
                )
                db.add(pareja)
                
                if i < 3:  # Mostrar detalles de las primeras 3 parejas
                    nombre_pareja = f"{perfil1.nombre} {perfil1.apellido} / {perfil2.nombre} {perfil2.apellido}"
                    print(f"   👫 Pareja {i+1}: {nombre_pareja}")
                    print(f"      🚫 {tipo_restriccion}")
        
        # Dejar libres a los usuarios 14 y 15 como solicitado
        print(f"\n🆓 Dejando libres a usuarios 14 y 15 para pruebas manuales...")
        
        db.commit()
        
        # Mostrar resumen
        print(f"\n🎉 ¡Torneo creado exitosamente!")
        print(f"📊 Resumen:")
        print(f"   🏆 Torneo ID: {torneo.id}")
        print(f"   📅 Fechas: {torneo.fecha_inicio} al {torneo.fecha_fin}")
        print(f"   ⏰ Horarios: Vie 12-23h, Sáb/Dom 9-23h")
        print(f"   🏟️ Canchas: 3 (configuradas en fixture)")
        print(f"   📂 Categorías: {len(categorias_creadas)}")
        print(f"   👥 Total parejas: {sum(num for _, num in categorias_creadas)}")
        print(f"   👤 Total jugadores: {sum(num for _, num in categorias_creadas) * 2}")
        
        print(f"\n🔄 Sistema de restricciones:")
        print(f"   ✅ 30% parejas sin restricciones (disponibles siempre)")
        print(f"   🚫 70% parejas con restricciones variadas")
        print(f"   📝 Restricciones típicas: laborales, familiares, múltiples")
        
        print(f"\n🧪 Para probar:")
        print(f"   1. Generar zonas inteligentes por categoría")
        print(f"   2. Generar fixture global considerando restricciones")
        print(f"   3. Verificar que se respeten las restricciones horarias")
        print(f"   4. Comparar con sistema anterior de disponibilidad")
        
        return torneo.id
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    torneo_id = crear_torneo_con_restricciones()
    if torneo_id:
        print(f"\n✅ Torneo {torneo_id} creado exitosamente con sistema de restricciones")
    else:
        print(f"\n❌ Error al crear el torneo")