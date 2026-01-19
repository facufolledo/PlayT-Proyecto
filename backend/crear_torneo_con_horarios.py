#!/usr/bin/env python3
"""
Script para crear torneo con horarios y 3 canchas
Viernes 15:00-23:59, Sábado y Domingo 09:00-23:59
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.config import get_db
from src.models.driveplus_models import Usuario, PerfilUsuario
from src.models.torneo_models import Torneo, TorneoCategoria, TorneoPareja, TorneoCancha
from datetime import datetime, timedelta
import random
import json

def crear_torneo_con_horarios():
    """Crear torneo con 3 canchas y horarios específicos"""
    db = next(get_db())
    
    try:
        print("🏆 Creando torneo con horarios y 3 canchas...")
        
        # Fechas del torneo (23-25 de enero - Viernes a Domingo)
        inicio = datetime(2026, 1, 23)  # Viernes 23
        fin = datetime(2026, 1, 25)     # Domingo 25
        
        # Crear torneo
        torneo = Torneo(
            nombre="🎾 Torneo Weekend - 3 Canchas",
            descripcion="Torneo de fin de semana con 3 canchas. Viernes tarde, Sábado y Domingo completo. Sistema optimizado de horarios.",
            categoria="Múltiples",
            genero="mixto",
            fecha_inicio=inicio.date(),
            fecha_fin=fin.date(),
            lugar="Club Drive+ - Canchas 1, 2 y 3",
            monto_inscripcion=3500.0,
            requiere_pago=True,
            alias_cbu_cvu="drive.plus.weekend",
            titular_cuenta="Club Drive Plus",
            banco="Banco Test",
            estado="inscripcion",
            creado_por=1,  # Usuario admin
            # Horarios del torneo
            horarios_disponibles={
                "viernes": {"inicio": "15:00", "fin": "23:59"},
                "sabado": {"inicio": "09:00", "fin": "23:59"},
                "domingo": {"inicio": "09:00", "fin": "23:59"}
            }
        )
        
        db.add(torneo)
        db.flush()
        
        print(f"✅ Torneo creado con ID: {torneo.id}")
        print(f"📅 Fechas: {inicio.strftime('%d/%m/%Y')} al {fin.strftime('%d/%m/%Y')}")
        
        # Crear 3 canchas
        print(f"\n🏟️ Creando canchas...")
        canchas = []
        for i in range(1, 4):
            cancha = TorneoCancha(
                torneo_id=torneo.id,
                nombre=f"Cancha {i}",
                activa=True
            )
            db.add(cancha)
            db.flush()
            canchas.append(cancha)
            print(f"   ✅ {cancha.nombre} (ID: {cancha.id})")
        
        print(f"🏟️ Total canchas: {len(canchas)}")
        
        # Crear categorías
        categorias_config = [
            {"nombre": "7ma Masculino", "genero": "masculino", "nivel_min": 7, "nivel_max": 7, "parejas": 12},
            {"nombre": "6ta Masculino", "genero": "masculino", "nivel_min": 6, "nivel_max": 6, "parejas": 12},
            {"nombre": "5ta Masculino", "genero": "masculino", "nivel_min": 5, "nivel_max": 5, "parejas": 12},
            {"nombre": "4ta Masculino", "genero": "masculino", "nivel_min": 4, "nivel_max": 4, "parejas": 12},
            {"nombre": "7ma Femenino", "genero": "femenino", "nivel_min": 7, "nivel_max": 7, "parejas": 8},
            {"nombre": "5ta Femenino", "genero": "femenino", "nivel_min": 5, "nivel_max": 5, "parejas": 8}
        ]
        
        categorias_creadas = []
        
        for cat_config in categorias_config:
            categoria = TorneoCategoria(
                torneo_id=torneo.id,
                nombre=cat_config["nombre"],
                genero=cat_config["genero"],
                max_parejas=999  # Sin límite
            )
            db.add(categoria)
            db.flush()
            categorias_creadas.append((categoria, cat_config["parejas"]))
            print(f"📂 Categoría: {categoria.nombre} - {cat_config['parejas']} parejas")
        
        # Crear usuarios y parejas
        timestamp = int(datetime.now().timestamp())
        usuario_id_counter = 3000  # Empezar desde 3000 para evitar conflictos
        
        # Restricciones realistas para fin de semana
        restricciones_weekend = [
            # Sin restricciones (30%)
            [],
            # Restricciones viernes (30%)
            [{"dia": "viernes", "inicio": "15:00", "fin": "19:00"}],  # No puede viernes tarde
            [{"dia": "viernes", "inicio": "20:00", "fin": "23:59"}],  # No puede viernes noche
            # Restricciones sábado (20%)
            [{"dia": "sabado", "inicio": "09:00", "fin": "13:00"}],   # No puede sábado mañana
            [{"dia": "sabado", "inicio": "19:00", "fin": "23:59"}],   # No puede sábado noche
            # Restricciones domingo (10%)
            [{"dia": "domingo", "inicio": "09:00", "fin": "13:00"}],  # No puede domingo mañana
            [{"dia": "domingo", "inicio": "18:00", "fin": "23:59"}],  # No puede domingo tarde
            # Restricciones múltiples (10%)
            [
                {"dia": "viernes", "inicio": "15:00", "fin": "18:00"},
                {"dia": "domingo", "inicio": "20:00", "fin": "23:59"}
            ],
            [
                {"dia": "sabado", "inicio": "09:00", "fin": "12:00"},
                {"dia": "domingo", "inicio": "19:00", "fin": "23:59"}
            ]
        ]
        
        total_parejas = 0
        
        for categoria, num_parejas in categorias_creadas:
            print(f"\n👥 Creando parejas para {categoria.nombre}...")
            
            cat_config = next(c for c in categorias_config if c["nombre"] == categoria.nombre)
            
            for i in range(num_parejas):
                # Crear jugador 1
                usuario1 = Usuario(
                    id_usuario=usuario_id_counter,
                    nombre_usuario=f"weekend_{categoria.nombre.lower().replace(' ', '_')}_{i+1}_j1_{timestamp}",
                    email=f"weekend_{categoria.nombre.lower().replace(' ', '_')}_{i+1}_j1_{timestamp}@driveplus.com",
                    password_hash="dummy_hash_weekend",
                    rating=cat_config["nivel_min"] * 100 + random.randint(-30, 30),
                    sexo=categoria.genero
                )
                db.add(usuario1)
                
                perfil1 = PerfilUsuario(
                    id_usuario=usuario1.id_usuario,
                    nombre=f"Test{i+1}",
                    apellido=f"{categoria.nombre.split()[0]}A",
                    telefono=f"11{random.randint(10000000, 99999999)}",
                    fecha_nacimiento=datetime(1995, 1, 1).date(),
                    mano_habil=random.choice(["derecha", "zurda"]),
                    ciudad="Buenos Aires",
                    pais="Argentina"
                )
                db.add(perfil1)
                usuario_id_counter += 1
                
                # Crear jugador 2
                usuario2 = Usuario(
                    id_usuario=usuario_id_counter,
                    nombre_usuario=f"weekend_{categoria.nombre.lower().replace(' ', '_')}_{i+1}_j2_{timestamp}",
                    email=f"weekend_{categoria.nombre.lower().replace(' ', '_')}_{i+1}_j2_{timestamp}@driveplus.com",
                    password_hash="dummy_hash_weekend",
                    rating=cat_config["nivel_min"] * 100 + random.randint(-30, 30),
                    sexo=categoria.genero
                )
                db.add(usuario2)
                
                perfil2 = PerfilUsuario(
                    id_usuario=usuario2.id_usuario,
                    nombre=f"Test{i+1}",
                    apellido=f"{categoria.nombre.split()[0]}B",
                    telefono=f"11{random.randint(10000000, 99999999)}",
                    fecha_nacimiento=datetime(1995, 1, 1).date(),
                    mano_habil=random.choice(["derecha", "zurda"]),
                    ciudad="Buenos Aires",
                    pais="Argentina"
                )
                db.add(perfil2)
                usuario_id_counter += 1
                
                # Asignar restricciones (30% sin, 70% con restricciones)
                if random.random() < 0.3:
                    restricciones = []
                    tipo = "✅ Disponible siempre"
                else:
                    restricciones = random.choice(restricciones_weekend[1:])
                    if len(restricciones) == 1:
                        r = restricciones[0]
                        tipo = f"🚫 No: {r['dia']} {r['inicio']}-{r['fin']}"
                    else:
                        tipo = f"🚫 {len(restricciones)} restricciones"
                
                # Crear pareja
                pareja = TorneoPareja(
                    torneo_id=torneo.id,
                    categoria_id=categoria.id,
                    jugador1_id=usuario1.id_usuario,
                    jugador2_id=usuario2.id_usuario,
                    estado="confirmada",
                    disponibilidad_horaria=restricciones
                )
                db.add(pareja)
                total_parejas += 1
                
                if i < 2:  # Mostrar primeras 2 parejas
                    print(f"   {i+1}. {perfil1.nombre} {perfil1.apellido} / {perfil2.nombre} {perfil2.apellido} - {tipo}")
        
        db.commit()
        
        # Resumen final
        print(f"\n{'='*60}")
        print(f"🎉 ¡TORNEO WEEKEND CREADO!")
        print(f"{'='*60}")
        print(f"🏆 ID: {torneo.id}")
        print(f"📅 Fechas: 23-25 Enero 2026 (Vie-Dom)")
        print(f"⏰ Horarios:")
        print(f"   • Viernes: 15:00-23:59 (9 horas)")
        print(f"   • Sábado: 09:00-23:59 (15 horas)")
        print(f"   • Domingo: 09:00-23:59 (15 horas)")
        print(f"   • Total: 39 horas de juego")
        print(f"🏟️ Canchas: 3 disponibles")
        print(f"📂 Categorías: {len(categorias_creadas)}")
        print(f"👥 Parejas: {total_parejas}")
        print(f"👤 Jugadores: {total_parejas * 2}")
        print(f"\n🔄 Distribución de restricciones:")
        print(f"   ✅ 30% sin restricciones")
        print(f"   🚫 70% con restricciones variadas")
        print(f"\n📊 Capacidad estimada:")
        print(f"   • 3 canchas × 39 horas = 117 horas-cancha")
        print(f"   • Partidos de 1.5h promedio = ~78 partidos")
        print(f"   • {total_parejas} parejas = suficiente capacidad")
        print(f"\n🧪 Próximos pasos:")
        print(f"   1. Generar zonas por categoría")
        print(f"   2. Generar fixture global con horarios")
        print(f"   3. Verificar respeto de restricciones")
        print(f"   4. Verificar distribución en 3 canchas")
        print(f"\n🚀 ¡Listo para jugar!")
        
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
    print("🏆 CREANDO TORNEO WEEKEND CON HORARIOS")
    print("="*60)
    torneo_id = crear_torneo_con_horarios()
    if torneo_id:
        print(f"\n✅ Torneo {torneo_id} creado exitosamente")
        print(f"🔗 Accede en: https://drive-plus.com.ar/torneos/{torneo_id}")
    else:
        print(f"\n❌ Error al crear el torneo")
