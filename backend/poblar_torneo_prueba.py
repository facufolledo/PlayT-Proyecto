"""
Script para crear un torneo de prueba con todos los usuarios
Administrador: Usuario 14
"""
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def main():
    with engine.connect() as conn:
        # 1. Obtener todos los usuarios activos con su perfil
        result = conn.execute(text("""
            SELECT u.id_usuario, COALESCE(p.nombre, u.nombre_usuario) as nombre, COALESCE(p.apellido, '') as apellido
            FROM usuarios u
            LEFT JOIN perfil_usuarios p ON u.id_usuario = p.id_usuario
            WHERE u.id_usuario != 14
            ORDER BY u.id_usuario
        """))
        usuarios = result.fetchall()
        print(f"✅ Encontrados {len(usuarios)} usuarios (excluyendo admin 14)")
        
        for u in usuarios:
            print(f"   - ID {u[0]}: {u[1]} {u[2]}")
        
        # 2. Autorizar al usuario 14 como organizador
        conn.execute(text("""
            INSERT INTO organizadores_autorizados (user_id, autorizado_por, activo)
            VALUES (14, 14, true)
            ON CONFLICT (user_id) DO UPDATE SET activo = true
        """))
        print("✅ Usuario 14 autorizado como organizador")
        
        # 3. Crear el torneo
        fecha_inicio = datetime.now().date()
        fecha_fin = fecha_inicio + timedelta(days=30)
        
        result = conn.execute(text("""
            INSERT INTO torneos (nombre, descripcion, tipo, categoria, estado, fecha_inicio, fecha_fin, lugar, creado_por)
            VALUES (
                'Torneo de Prueba Drive+',
                'Torneo para probar todas las funcionalidades: zonas, playoffs, cambios de último momento',
                'clasico',
                '4ta',
                'inscripcion',
                :fecha_inicio,
                :fecha_fin,
                'Club de Pádel Test',
                14
            )
            RETURNING id
        """), {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin})
        
        torneo_id = result.fetchone()[0]
        print(f"✅ Torneo creado con ID: {torneo_id}")
        
        # 4. Agregar usuario 14 como owner del torneo
        conn.execute(text("""
            INSERT INTO torneos_organizadores (torneo_id, user_id, rol)
            VALUES (:torneo_id, 14, 'owner')
        """), {"torneo_id": torneo_id})
        print("✅ Usuario 14 asignado como owner del torneo")
        
        # 5. Crear parejas con los usuarios disponibles
        parejas_creadas = 0
        usuario_ids = [u[0] for u in usuarios]
        
        # Necesitamos pares de usuarios para formar parejas
        for i in range(0, len(usuario_ids) - 1, 2):
            jugador1_id = usuario_ids[i]
            jugador2_id = usuario_ids[i + 1]
            
            conn.execute(text("""
                INSERT INTO torneos_parejas (torneo_id, jugador1_id, jugador2_id, estado, categoria_asignada)
                VALUES (:torneo_id, :j1, :j2, 'confirmada', '4ta')
            """), {"torneo_id": torneo_id, "j1": jugador1_id, "j2": jugador2_id})
            
            parejas_creadas += 1
            print(f"   Pareja {parejas_creadas}: Usuario {jugador1_id} + Usuario {jugador2_id}")
        
        print(f"✅ {parejas_creadas} parejas creadas y confirmadas")
        
        # 6. Crear algunas canchas para el torneo
        for i in range(1, 5):
            conn.execute(text("""
                INSERT INTO torneo_canchas (torneo_id, nombre, activa)
                VALUES (:torneo_id, :nombre, true)
            """), {"torneo_id": torneo_id, "nombre": f"Cancha {i}"})
        print("✅ 4 canchas creadas")
        
        # 7. Crear slots de horarios (próximos 7 días, 4 horarios por día por cancha)
        result = conn.execute(text("""
            SELECT id FROM torneo_canchas WHERE torneo_id = :torneo_id
        """), {"torneo_id": torneo_id})
        canchas = result.fetchall()
        
        slots_creados = 0
        for cancha in canchas:
            cancha_id = cancha[0]
            for dia in range(7):
                fecha = datetime.now() + timedelta(days=dia)
                for hora in [9, 11, 15, 17, 19]:  # 5 horarios por día
                    hora_inicio = fecha.replace(hour=hora, minute=0, second=0, microsecond=0)
                    hora_fin = hora_inicio + timedelta(hours=1, minutes=30)
                    
                    conn.execute(text("""
                        INSERT INTO torneo_slots (torneo_id, cancha_id, fecha_hora_inicio, fecha_hora_fin, ocupado)
                        VALUES (:torneo_id, :cancha_id, :inicio, :fin, false)
                    """), {
                        "torneo_id": torneo_id,
                        "cancha_id": cancha_id,
                        "inicio": hora_inicio,
                        "fin": hora_fin
                    })
                    slots_creados += 1
        
        print(f"✅ {slots_creados} slots de horarios creados")
        
        conn.commit()
        
        print("\n" + "="*50)
        print(f"🎾 TORNEO DE PRUEBA CREADO EXITOSAMENTE")
        print("="*50)
        print(f"ID del Torneo: {torneo_id}")
        print(f"Administrador: Usuario 14")
        print(f"Parejas inscritas: {parejas_creadas}")
        print(f"Estado: inscripcion")
        print(f"\nPróximos pasos:")
        print(f"1. Ir a /torneos/{torneo_id} en el frontend")
        print(f"2. Generar zonas")
        print(f"3. Generar fixture")
        print(f"4. Probar cargar resultados")
        print(f"5. Probar playoffs")

if __name__ == "__main__":
    main()
