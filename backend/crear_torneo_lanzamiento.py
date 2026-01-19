#!/usr/bin/env python3
"""
Script para crear torneo de prueba para el LANZAMIENTO
Torneo con restricciones horarias para probar el sistema antes del torneo del 23
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

def crear_torneo_lanzamiento():
    """Crear torneo de prueba para el lanzamiento con restricciones horarias"""
    db = next(get_db())
    
    try:
        print("🚀 Creando torneo de LANZAMIENTO con restricciones horarias...")
        
        # Fechas del torneo (20-22 de enero - antes del torneo real del 23)
        inicio = datetime(2026, 1, 20)  # Lunes 20
        fin = datetime(2026, 1, 22)     # Miércoles 22
        
        # Crear torneo
        torneo = Torneo(
            nombre="🚀 Torneo Lanzamiento - Drive+ Test",
            descripcion="Torneo de prueba para el lanzamiento. Sistema de restricciones horarias optimizado. ¡Preparados para el torneo del 23!",
            categoria="Múltiples",
            genero="mixto",
            fecha_inicio=inicio.date(),
            fecha_fin=fin.date(),
            lugar="Club Drive+ - Canchas 1, 2, 3 y 4",
            monto_inscripcion=3000.0,
            requiere_pago=True,
            alias_cbu_cvu="drive.plus.lanzamiento",
            titular_cuenta="Club Drive Plus",
            banco="Banco Test",
            estado="inscripcion",
            creado_por=1,  # Usuario admin
            # Horarios del torneo (más amplios para testing)
            horarios_disponibles={
                "lunes": {"inicio": "14:00", "fin": "23:00"},
                "martes": {"inicio": "09:00", "fin": "23:00"},
                "miercoles": {"inicio": "09:00", "fin": "22:00"}
            }
        )
        
        db.add(torneo)
        db.flush()
        
        print(f"✅ Torneo creado con ID: {torneo.id}")
        print(f"📅 Fechas: {inicio.strftime('%d/%m/%Y')} al {fin.strftime('%d/%m/%Y')}")
        
        # Crear categorías (menos parejas para testing rápido)
        categorias_config = [
            {"nombre": "7ma Masculino", "genero": "masculino", "nivel_min": 7, "nivel_max": 7, "parejas": 12},
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
                max_parejas=cat_config["parejas"]
            )
            db.add(categoria)
            db.flush()
            categorias_creadas.append((categoria, cat_config["parejas"]))
            print(f"📂 Categoría: {categoria.nombre} - {cat_config['parejas']} parejas")
        
        # Crear usuarios y parejas
        timestamp = int(datetime.now().timestamp())
        usuario_id_counter = 2000  # Empezar desde 2000 para evitar conflictos
        
        # Restricciones realistas para el lanzamiento
        restricciones_lanzamiento = [
            # Sin restricciones (20%)
            [],
            # Restricciones laborales (40%)
            [{"dia": "lunes", "inicio": "14:00", "fin": "18:00"}],     # No puede lunes tarde
            [{"dia": "martes", "inicio": "09:00", "fin": "13:00"}],    # No puede martes mañana
            [{"dia": "miercoles", "inicio": "18:00", "fin": "22:00"}], # No puede miércoles noche
            # Restricciones familiares (20%)
            [{"dia": "lunes", "inicio": "20:00", "fin": "23:00"}],     # No puede lunes noche
            [{"dia": "martes", "inicio": "19:00", "fin": "23:00"}],    # No puede martes noche
            # Restricciones múltiples (20%)
            [
                {"dia": "lunes", "inicio": "14:00", "fin": "17:00"},
                {"dia": "miercoles", "inicio": "20:00", "fin": "22:00"}
            ],
            [
                {"dia": "martes", "inicio": "09:00", "fin": "12:00"},
                {"dia": "miercoles", "inicio": "19:00", "fin": "22:00"}
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
                    nombre_usuario=f"lanzamiento_{categoria.nombre.lower().replace(' ', '_')}_{i+1}_j1_{timestamp}",
                    email=f"lanzamiento_{categoria.nombre.lower().replace(' ', '_')}_{i+1}_j1_{timestamp}@driveplus.com",
                    password_hash="dummy_hash_lanzamiento",
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
                    nombre_usuario=f"lanzamiento_{categoria.nombre.lower().replace(' ', '_')}_{i+1}_j2_{timestamp}",
                    email=f"lanzamiento_{categoria.nombre.lower().replace(' ', '_')}_{i+1}_j2_{timestamp}@driveplus.com",
                    password_hash="dummy_hash_lanzamiento",
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
                
                # Asignar restricciones (20% sin, 80% con restricciones)
                if random.random() < 0.2:
                    restricciones = []
                    tipo = "✅ Disponible siempre"
                else:
                    restricciones = random.choice(restricciones_lanzamiento[1:])
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
        print(f"🎉 ¡TORNEO DE LANZAMIENTO CREADO!")
        print(f"{'='*60}")
        print(f"🏆 ID: {torneo.id}")
        print(f"📅 Fechas: 20-22 Enero 2026 (Lun-Mié)")
        print(f"⏰ Horarios:")
        print(f"   • Lunes: 14:00-23:00")
        print(f"   • Martes: 09:00-23:00")
        print(f"   • Miércoles: 09:00-22:00")
        print(f"🏟️ Canchas: 4 disponibles")
        print(f"📂 Categorías: {len(categorias_creadas)}")
        print(f"👥 Parejas: {total_parejas}")
        print(f"👤 Jugadores: {total_parejas * 2}")
        print(f"\n🔄 Distribución de restricciones:")
        print(f"   ✅ 20% sin restricciones")
        print(f"   🚫 80% con restricciones variadas")
        print(f"\n🧪 Próximos pasos:")
        print(f"   1. Generar zonas por categoría")
        print(f"   2. Generar fixture global")
        print(f"   3. Verificar respeto de restricciones")
        print(f"   4. Probar sistema completo")
        print(f"\n🚀 ¡Listo para el lanzamiento!")
        
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
    print("🚀 CREANDO TORNEO DE LANZAMIENTO")
    print("="*60)
    torneo_id = crear_torneo_lanzamiento()
    if torneo_id:
        print(f"\n✅ Torneo {torneo_id} creado exitosamente")
        print(f"🔗 Accede en: https://drive-plus.com.ar/torneos/{torneo_id}")
    else:
        print(f"\n❌ Error al crear el torneo")
