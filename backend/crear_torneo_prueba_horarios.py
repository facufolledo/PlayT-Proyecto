"""
Script para crear un torneo de prueba con restricciones horarias
para testear el botón de ver horarios en el frontend
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv

load_dotenv()

# Configuración de la base de datos
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ Error: DATABASE_URL no está configurada")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def crear_torneo_prueba():
    session = Session()
    
    try:
        print("\n" + "="*80)
        print("CREAR TORNEO DE PRUEBA - Restricciones Horarias")
        print("="*80)
        
        # 1. Crear torneo
        print("\n📋 Creando torneo...")
        fecha_inicio = datetime.now() + timedelta(days=7)
        fecha_fin = fecha_inicio + timedelta(days=2)
        
        # Horarios del torneo: Viernes 18:00-22:00, Sábado 10:00-22:00
        horarios_torneo = {
            "franjas": [
                {
                    "dias": ["viernes"],
                    "horaInicio": "18:00",
                    "horaFin": "22:00"
                },
                {
                    "dias": ["sabado"],
                    "horaInicio": "10:00",
                    "horaFin": "22:00"
                }
            ]
        }
        
        query_torneo = text("""
            INSERT INTO torneos (
                nombre, descripcion, fecha_inicio, fecha_fin,
                monto_inscripcion, estado, categoria, genero,
                creado_por, horarios_disponibles
            ) VALUES (
                :nombre, :descripcion, :fecha_inicio, :fecha_fin,
                :monto, :estado, :categoria, :genero,
                :organizador, :horarios
            ) RETURNING id
        """)
        
        result = session.execute(query_torneo, {
            'nombre': 'Torneo Prueba Horarios',
            'descripcion': 'Torneo para probar visualización de restricciones horarias',
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'monto': 1000.0,
            'estado': 'inscripcion',
            'categoria': 'Múltiples',
            'genero': 'mixto',
            'organizador': 1,  # Usuario admin
            'horarios': json.dumps(horarios_torneo)
        })
        torneo_id = result.fetchone()[0]
        session.commit()
        print(f"✅ Torneo creado (ID: {torneo_id})")
        
        # 2. Crear categoría
        print("\n📋 Creando categoría...")
        query_cat = text("""
            INSERT INTO torneo_categorias (torneo_id, nombre, genero, max_parejas)
            VALUES (:torneo_id, :nombre, :genero, :max_parejas)
            RETURNING id
        """)
        result = session.execute(query_cat, {
            'torneo_id': torneo_id,
            'nombre': 'Masculino',
            'genero': 'masculino',
            'max_parejas': 4
        })
        categoria_id = result.fetchone()[0]
        session.commit()
        print(f"✅ Categoría creada (ID: {categoria_id})")
        
        # 3. Agregar canchas
        print("\n🎾 Agregando canchas...")
        for i in range(1, 3):
            query_cancha = text("""
                INSERT INTO torneo_canchas (torneo_id, nombre, activa)
                VALUES (:torneo_id, :nombre, true)
            """)
            session.execute(query_cancha, {
                'torneo_id': torneo_id,
                'nombre': f'Cancha {i}'
            })
        session.commit()
        print("✅ 2 canchas agregadas")
        
        # 4. Obtener usuarios existentes
        print("\n👥 Buscando usuarios...")
        query_usuarios = text("""
            SELECT u.id_usuario, COALESCE(p.nombre, 'Usuario'), COALESCE(p.apellido, ''), COALESCE(u.nombre_usuario, 'user')
            FROM usuarios u
            LEFT JOIN perfil_usuarios p ON u.id_usuario = p.id_usuario
            WHERE u.id_usuario IN (1, 2, 3, 4, 5, 6, 7, 8)
            ORDER BY u.id_usuario
            LIMIT 8
        """)
        usuarios = session.execute(query_usuarios).fetchall()
        
        if len(usuarios) < 8:
            print(f"⚠️  Solo hay {len(usuarios)} usuarios disponibles, necesitamos 8")
            print("Usando los usuarios disponibles...")
        
        # 5. Crear parejas con diferentes restricciones horarias
        print("\n👫 Creando parejas con restricciones horarias...")
        
        parejas_config = [
            {
                'nombre': 'Pareja Viernes Tarde',
                'jugadores': (0, 1),
                'disponibilidad': {
                    "franjas": [
                        {
                            "dias": ["viernes"],
                            "horaInicio": "18:00",
                            "horaFin": "22:00"
                        }
                    ]
                }
            },
            {
                'nombre': 'Pareja Sábado Mañana',
                'jugadores': (2, 3),
                'disponibilidad': {
                    "franjas": [
                        {
                            "dias": ["sabado"],
                            "horaInicio": "10:00",
                            "horaFin": "14:00"
                        }
                    ]
                }
            },
            {
                'nombre': 'Pareja Sábado Tarde',
                'jugadores': (4, 5),
                'disponibilidad': {
                    "franjas": [
                        {
                            "dias": ["sabado"],
                            "horaInicio": "16:00",
                            "horaFin": "22:00"
                        }
                    ]
                }
            },
            {
                'nombre': 'Pareja Sin Restricciones',
                'jugadores': (6, 7) if len(usuarios) >= 8 else (0, 1),
                'disponibilidad': None  # Sin restricciones
            }
        ]
        
        parejas_ids = []
        for config in parejas_config:
            j1_idx, j2_idx = config['jugadores']
            if j1_idx >= len(usuarios) or j2_idx >= len(usuarios):
                continue
                
            j1 = usuarios[j1_idx]
            j2 = usuarios[j2_idx]
            
            query_pareja = text("""
                INSERT INTO torneos_parejas (
                    torneo_id, jugador1_id, jugador2_id,
                    estado, categoria_id, disponibilidad_horaria
                ) VALUES (
                    :torneo_id, :j1_id, :j2_id,
                    'confirmada', :categoria_id, :disponibilidad
                ) RETURNING id
            """)
            
            result = session.execute(query_pareja, {
                'torneo_id': torneo_id,
                'j1_id': j1[0],
                'j2_id': j2[0],
                'categoria_id': categoria_id,
                'disponibilidad': json.dumps(config['disponibilidad']) if config['disponibilidad'] else None
            })
            pareja_id = result.fetchone()[0]
            parejas_ids.append(pareja_id)
            session.commit()
            
            # Mostrar info de la pareja
            disp_text = "Sin restricciones" if not config['disponibilidad'] else \
                        ", ".join([f"{f['dias'][0]} {f['horaInicio']}-{f['horaFin']}" 
                                  for f in config['disponibilidad']['franjas']])
            print(f"  ✅ {config['nombre']}")
            print(f"     {j1[1]} {j1[2]} (@{j1[3]}) / {j2[1]} {j2[2]} (@{j2[3]})")
            print(f"     📅 {disp_text}")
        
        session.commit()
        print(f"✅ 4 parejas creadas con diferentes restricciones horarias")
        
        # Resumen final
        print("\n" + "="*80)
        print("✅ TORNEO CREADO EXITOSAMENTE")
        print("="*80)
        print(f"\n📋 ID del Torneo: {torneo_id}")
        print(f"📋 Nombre: Torneo Prueba Horarios")
        print(f"📋 Categoría: Masculino (ID: {categoria_id})")
        print(f"\n👫 Parejas inscritas: {len(parejas_ids)}")
        print(f"🎾 Canchas disponibles: 2")
        print(f"\n📅 Horarios del torneo:")
        print(f"   • Viernes: 18:00 - 22:00")
        print(f"   • Sábado: 10:00 - 22:00")
        print(f"\n📅 Restricciones de parejas:")
        print(f"   • Pareja 1: Solo viernes 18:00-22:00")
        print(f"   • Pareja 2: Solo sábado 10:00-14:00")
        print(f"   • Pareja 3: Solo sábado 16:00-22:00")
        print(f"   • Pareja 4: Sin restricciones (cualquier horario)")
        print(f"\n🌐 Accede al torneo en:")
        print(f"   http://localhost:5173/torneos/{torneo_id}")
        print(f"\n💡 Ahora puedes:")
        print(f"   1. Ir a la pestaña 'Parejas' y hacer click en el botón de reloj 🕐")
        print(f"   2. Generar las zonas desde el frontend (2 parejas por zona)")
        print(f"   3. Ver las zonas y hacer click en el botón de reloj de cada pareja")
        print(f"   4. Generar el fixture y ver los horarios en cada partido")
        print("="*80 + "\n")
        
        return torneo_id
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        session.close()

if __name__ == '__main__':
    crear_torneo_prueba()
