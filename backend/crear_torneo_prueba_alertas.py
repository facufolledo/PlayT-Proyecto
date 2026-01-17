"""
Crear un torneo pequeño para probar las alertas mejoradas
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.database.config import get_db
from src.models.driveplus_models import Usuario, PerfilUsuario
from src.models.torneo_models import Torneo, TorneoCategoria, TorneoPareja, TorneoCancha
from datetime import datetime, timedelta
import json

def crear_torneo_prueba_alertas():
    db = next(get_db())
    
    print("🔍 CREANDO TORNEO DE PRUEBA PARA ALERTAS...")
    
    # Fechas de mañana
    fecha_inicio = datetime.now().date() + timedelta(days=1)
    fecha_fin = fecha_inicio + timedelta(days=1)
    
    # Horarios del torneo (solo mañana para forzar conflictos)
    horarios_torneo = {
        "semana": [{"desde": "09:00", "hasta": "12:00"}],  # Solo 3 horas
        "finDeSemana": [{"desde": "09:00", "hasta": "12:00"}]
    }
    
    # 1. CREAR EL TORNEO
    torneo = Torneo(
        nombre="Torneo Prueba Alertas",
        descripcion="Torneo pequeño para probar alertas de incompatibilidad horaria",
        categoria="Múltiples",
        genero="mixto",
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        lugar="Club Test",
        estado="inscripcion",
        creado_por=14,  # Facundo
        horarios_disponibles=horarios_torneo,
        requiere_pago=False
    )
    db.add(torneo)
    db.commit()
    db.refresh(torneo)
    
    print(f"✅ Torneo creado con ID: {torneo.id}")
    
    # 2. CREAR CANCHA (solo 1 para forzar conflictos)
    cancha = TorneoCancha(
        torneo_id=torneo.id,
        nombre="Cancha Única",
        activa=True
    )
    db.add(cancha)
    db.commit()
    
    # 3. CREAR CATEGORÍA
    categoria = TorneoCategoria(
        torneo_id=torneo.id,
        nombre="Prueba Masculino",
        genero="masculino",
        max_parejas=8
    )
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    
    print(f"✅ Categoría creada: {categoria.nombre}")
    
    # 4. USAR USUARIOS EXISTENTES (Facundo y Facundito)
    # Buscar usuarios existentes
    usuarios_existentes = db.query(Usuario).filter(
        Usuario.id_usuario.in_([14, 15])  # Facundo y Facundito
    ).all()
    
    if len(usuarios_existentes) < 2:
        print("❌ No se encontraron usuarios 14 y 15")
        return None
    
    # 5. CREAR PAREJAS CON DISPONIBILIDADES CONFLICTIVAS
    parejas_data = [
        {
            "jugador1_id": 14,
            "jugador2_id": 15,
            "disponibilidad": {"franjas": [{"dias": ["lunes"], "horaInicio": "19:00", "horaFin": "22:00"}]}  # Solo lunes noche
        },
        # Crear más usuarios para más parejas
    ]
    
    # Crear usuarios adicionales para más parejas
    usuarios_nuevos = []
    for i in range(6):  # 6 usuarios más = 3 parejas más
        usuario = Usuario(
            nombre_usuario=f"test_user_{i+1}_{torneo.id}",
            email=f"test{i+1}@test.com",
            password_hash="$2b$12$dummy.hash",
            rating=1200 + i * 50,
            sexo='M',
            partidos_jugados=0
        )
        db.add(usuario)
        db.flush()
        
        # Crear perfil
        perfil = PerfilUsuario(
            id_usuario=usuario.id_usuario,
            nombre=f"Test{i+1}",
            apellido="User",
            ciudad="Test City",
            pais="Argentina",
            mano_habil="derecha"
        )
        db.add(perfil)
        usuarios_nuevos.append(usuario)
    
    db.commit()
    
    # Crear parejas con disponibilidades conflictivas
    disponibilidades = [
        {"franjas": [{"dias": ["lunes"], "horaInicio": "19:00", "horaFin": "22:00"}]},  # Solo lunes noche
        {"franjas": [{"dias": ["martes"], "horaInicio": "14:00", "horaFin": "18:00"}]},  # Solo martes tarde
        {"franjas": [{"dias": ["miercoles"], "horaInicio": "20:00", "horaFin": "23:00"}]},  # Solo miércoles noche
        None  # Sin restricciones
    ]
    
    parejas = []
    
    # Pareja 1: Facundo y Facundito
    pareja1 = TorneoPareja(
        torneo_id=torneo.id,
        categoria_id=categoria.id,
        jugador1_id=14,
        jugador2_id=15,
        estado="confirmada",
        disponibilidad_horaria=disponibilidades[0]
    )
    db.add(pareja1)
    parejas.append(pareja1)
    
    # Parejas adicionales
    for i in range(0, 6, 2):  # Crear 3 parejas más
        pareja = TorneoPareja(
            torneo_id=torneo.id,
            categoria_id=categoria.id,
            jugador1_id=usuarios_nuevos[i].id_usuario,
            jugador2_id=usuarios_nuevos[i+1].id_usuario,
            estado="confirmada",
            disponibilidad_horaria=disponibilidades[(i//2 + 1) % len(disponibilidades)]
        )
        db.add(pareja)
        parejas.append(pareja)
    
    db.commit()
    
    print(f"✅ {len(parejas)} parejas creadas con disponibilidades conflictivas")
    print(f"🎯 Torneo listo para probar alertas: ID {torneo.id}")
    
    return torneo.id

if __name__ == "__main__":
    torneo_id = crear_torneo_prueba_alertas()
    if torneo_id:
        print(f"\n🚀 Ahora puedes probar:")
        print(f"   1. Generar zonas: POST /torneos/{torneo_id}/generar-zonas-inteligente")
        print(f"   2. Generar fixture: POST /torneos/{torneo_id}/generar-fixture")
        print(f"   3. Ver alertas mejoradas en el frontend")