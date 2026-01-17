"""
Crear torneo masivo con múltiples categorías
- Masculino: 7ma, 5ta, 3ra (16 parejas cada una)
- Femenino: 7ma, 5ta (16 parejas cada una)
- Total: 80 parejas (160 jugadores)
- 3 canchas
- Viernes 24/01: 12:00-00:00
- Sábado 25/01: 09:00-00:00
- Domingo 26/01: 09:00-00:00
- Zonas hasta sábado 17:00, playoffs después
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.database.config import get_db
from src.models.driveplus_models import Usuario, PerfilUsuario, Categoria
from src.models.torneo_models import Torneo, TorneoCategoria, TorneoPareja, TorneoCancha
from datetime import datetime, timedelta
import random
import json

def crear_torneo_masivo():
    db = next(get_db())
    
    print("\n" + "="*80)
    print("CREAR TORNEO MASIVO - DRIVE+ CHAMPIONSHIP")
    print("="*80 + "\n")
    
    # Fechas de la próxima semana (viernes a domingo)
    hoy = datetime.now()
    # Buscar el próximo viernes
    dias_hasta_viernes = (4 - hoy.weekday()) % 7  # 4 = viernes
    if dias_hasta_viernes == 0 and hoy.hour > 12:  # Si es viernes después de las 12, ir al siguiente
        dias_hasta_viernes = 7
    
    fecha_inicio = hoy + timedelta(days=dias_hasta_viernes)
    fecha_fin = fecha_inicio + timedelta(days=2)  # Domingo
    
    print(f"📅 Fechas del torneo:")
    print(f"   Inicio: {fecha_inicio.strftime('%Y-%m-%d')} (Viernes)")
    print(f"   Fin: {fecha_fin.strftime('%Y-%m-%d')} (Domingo)")
    print(f"   Zonas hasta: Sábado 17:00")
    print(f"   Playoffs: Sábado 17:00 en adelante + Domingo\n")
    
    # Horarios del torneo
    horarios_torneo = {
        "semana": [{"desde": "12:00", "hasta": "23:59"}],  # Viernes
        "finDeSemana": [{"desde": "09:00", "hasta": "23:59"}]  # Sábado y Domingo
    }
    
    # 1. CREAR EL TORNEO
    print("🏆 Creando torneo...")
    torneo = Torneo(
        nombre="Drive+ Championship - Torneo Masivo",
        descripcion="Torneo masivo con 5 categorías y 80 parejas. Fase de grupos hasta sábado 17:00, playoffs después.",
        categoria="Múltiples",  # Campo requerido
        genero="mixto",
        fecha_inicio=fecha_inicio.date(),
        fecha_fin=fecha_fin.date(),
        lugar="Club Drive+",
        estado="inscripcion",
        creado_por=14,  # Facundo
        horarios_disponibles=horarios_torneo,
        requiere_pago=True,
        monto_inscripcion=5000.0,
        alias_cbu_cvu="drive.plus.torneo",
        titular_cuenta="Club Drive Plus",
        banco="Banco Nación"
    )
    db.add(torneo)
    db.commit()
    db.refresh(torneo)
    
    print(f"✅ Torneo creado con ID: {torneo.id}")
    
    # 2. CREAR CANCHAS
    print("\n🏟️  Creando canchas...")
    canchas = []
    for i in range(1, 4):  # 3 canchas
        cancha = TorneoCancha(
            torneo_id=torneo.id,
            nombre=f"Cancha {i}",
            activa=True
        )
        db.add(cancha)
        canchas.append(cancha)
    
    db.commit()
    print(f"✅ {len(canchas)} canchas creadas")
    
    # 3. CREAR CATEGORÍAS
    print("\n📊 Creando categorías...")
    categorias_config = [
        {"nombre": "7ma Masculino", "genero": "masculino", "rating_min": 1000, "rating_max": 1199},
        {"nombre": "5ta Masculino", "genero": "masculino", "rating_min": 1400, "rating_max": 1599},
        {"nombre": "3ra Masculino", "genero": "masculino", "rating_min": 1800, "rating_max": 2199},
        {"nombre": "7ma Femenino", "genero": "femenino", "rating_min": 1000, "rating_max": 1199},
        {"nombre": "5ta Femenino", "genero": "femenino", "rating_min": 1400, "rating_max": 1599},
    ]
    
    categorias_creadas = []
    for cat_config in categorias_config:
        categoria = TorneoCategoria(
            torneo_id=torneo.id,
            nombre=cat_config["nombre"],
            genero=cat_config["genero"],
            max_parejas=16
        )
        db.add(categoria)
        categorias_creadas.append((categoria, cat_config))
    
    db.commit()
    print(f"✅ {len(categorias_creadas)} categorías creadas")
    
    # 4. CREAR USUARIOS Y PAREJAS
    print("\n👥 Creando usuarios y parejas...")
    
    # Franjas horarias posibles (aleatorias pero realistas)
    franjas_posibles = [
        # Solo viernes tarde/noche
        {"dias": ["viernes"], "horaInicio": "18:00", "horaFin": "23:00"},
        {"dias": ["viernes"], "horaInicio": "20:00", "horaFin": "23:59"},
        
        # Solo fin de semana mañana
        {"dias": ["sabado", "domingo"], "horaInicio": "09:00", "horaFin": "14:00"},
        {"dias": ["sabado", "domingo"], "horaInicio": "10:00", "horaFin": "16:00"},
        
        # Solo fin de semana tarde
        {"dias": ["sabado", "domingo"], "horaInicio": "15:00", "horaFin": "20:00"},
        {"dias": ["sabado", "domingo"], "horaInicio": "17:00", "horaFin": "23:00"},
        
        # Viernes + sábado mañana
        {"dias": ["viernes", "sabado"], "horaInicio": "12:00", "horaFin": "16:00"},
        
        # Todo el fin de semana
        {"dias": ["sabado", "domingo"], "horaInicio": "09:00", "horaFin": "23:00"},
        
        # Flexible (sin restricciones específicas - disponible siempre)
        None  # Sin restricciones
    ]
    
    total_parejas_creadas = 0
    
    for categoria, cat_config in categorias_creadas:
        print(f"\n   📋 Categoría: {categoria.nombre}")
        
        parejas_categoria = []
        usuarios_creados = 0
        
        for pareja_num in range(1, 17):  # 16 parejas por categoría
            # Crear 2 usuarios por pareja
            usuarios_pareja = []
            
            for jugador_num in range(1, 3):  # 2 jugadores por pareja
                # Generar datos del usuario
                sexo = 'M' if cat_config["genero"] == "masculino" else 'F'
                categoria_nombre = categoria.nombre.replace(" Masculino", "").replace(" Femenino", "")
                
                # Agregar timestamp para evitar duplicados
                import time
                timestamp = int(time.time())
                
                nombre_usuario = f"{categoria_nombre.lower()}_m{pareja_num}j{jugador_num}_{timestamp}"
                nombre = f"Jugador{jugador_num}"
                apellido = f"{categoria_nombre}_{pareja_num}"
                
                # Rating aleatorio dentro del rango de la categoría
                rating = random.randint(cat_config["rating_min"], cat_config["rating_max"])
                
                # Crear usuario
                usuario = Usuario(
                    nombre_usuario=nombre_usuario,
                    email=f"{nombre_usuario}@drive-plus.com",
                    password_hash="$2b$12$dummy.hash.for.tournament.users",  # Hash dummy
                    rating=rating,
                    sexo=sexo,
                    partidos_jugados=random.randint(5, 25)
                )
                db.add(usuario)
                db.flush()  # Para obtener el ID
                
                # Crear perfil
                perfil = PerfilUsuario(
                    id_usuario=usuario.id_usuario,
                    nombre=nombre,
                    apellido=apellido,
                    fecha_nacimiento=datetime(1990 + random.randint(0, 15), random.randint(1, 12), random.randint(1, 28)),
                    ciudad="Buenos Aires",
                    pais="Argentina",
                    posicion_preferida=random.choice(["drive", "reves"]),
                    mano_habil=random.choice(["derecha", "zurda"])  # Fixed: use valid values
                )
                db.add(perfil)
                
                usuarios_pareja.append(usuario)
                usuarios_creados += 1
            
            # Crear pareja
            # Disponibilidad horaria aleatoria
            disponibilidad = random.choice(franjas_posibles)
            disponibilidad_json = None
            if disponibilidad:
                disponibilidad_json = {"franjas": [disponibilidad]}
            
            pareja = TorneoPareja(
                torneo_id=torneo.id,
                categoria_id=categoria.id,
                jugador1_id=usuarios_pareja[0].id_usuario,
                jugador2_id=usuarios_pareja[1].id_usuario,
                estado="confirmada",
                disponibilidad_horaria=disponibilidad_json
            )
            db.add(pareja)
            parejas_categoria.append(pareja)
        
        db.commit()
        total_parejas_creadas += len(parejas_categoria)
        
        print(f"      ✅ {len(parejas_categoria)} parejas creadas ({usuarios_creados} usuarios)")
    
    print(f"\n✅ RESUMEN FINAL:")
    print(f"   🏆 Torneo: {torneo.nombre}")
    print(f"   📅 Fechas: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}")
    print(f"   🏟️  Canchas: 3")
    print(f"   📊 Categorías: 5")
    print(f"   👥 Parejas totales: {total_parejas_creadas}")
    print(f"   👤 Jugadores totales: {total_parejas_creadas * 2}")
    print(f"   💰 Inscripción: $5.000 por pareja")
    print(f"   💵 Recaudación total: ${total_parejas_creadas * 5000:,}")
    
    print(f"\n🎯 PRÓXIMOS PASOS:")
    print(f"   1. Generar zonas inteligentes por categoría")
    print(f"   2. Generar fixture (zonas hasta sábado 17:00)")
    print(f"   3. Simular resultados de fase de grupos")
    print(f"   4. Generar playoffs (sábado 17:00+)")
    
    print(f"\n🔧 COMANDOS ÚTILES:")
    print(f"   - Ver torneo: SELECT * FROM torneos WHERE id = {torneo.id};")
    print(f"   - Ver categorías: SELECT * FROM torneo_categorias WHERE torneo_id = {torneo.id};")
    print(f"   - Ver parejas: SELECT COUNT(*) FROM torneos_parejas WHERE torneo_id = {torneo.id};")
    
    return torneo.id

if __name__ == "__main__":
    torneo_id = crear_torneo_masivo()
    print(f"\n🎉 ¡Torneo masivo creado exitosamente! ID: {torneo_id}")