"""
Script para actualizar el estado de una sala específica
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Cargar variables de entorno
load_dotenv()

# Configurar base de datos
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL no está configurada en .env")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def actualizar_sala(id_sala: int, nuevo_estado: str = "en_juego"):
    """
    Actualizar el estado de una sala específica
    
    Args:
        id_sala: ID de la sala a actualizar
        nuevo_estado: Nuevo estado (en_juego, esperando, finalizada, etc.)
    """
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("ACTUALIZAR ESTADO DE SALA")
        print("=" * 60)
        
        # Verificar que la sala existe
        query_verificar = text("""
            SELECT 
                s.id_sala,
                s.nombre,
                s.estado,
                s.id_partido,
                p.estado_confirmacion,
                p.elo_aplicado
            FROM salas s
            LEFT JOIN partidos p ON s.id_partido = p.id_partido
            WHERE s.id_sala = :id_sala
        """)
        
        result = db.execute(query_verificar, {"id_sala": id_sala})
        sala = result.fetchone()
        
        if not sala:
            print(f"\n❌ No se encontró la sala con ID {id_sala}")
            return
        
        print(f"\n📊 Sala encontrada:")
        print(f"   ID: {sala.id_sala}")
        print(f"   Nombre: {sala.nombre}")
        print(f"   Estado actual: {sala.estado}")
        print(f"   ID Partido: {sala.id_partido}")
        
        if sala.id_partido:
            print(f"   Estado confirmación: {sala.estado_confirmacion or 'sin_resultado'}")
            print(f"   Elo aplicado: {'✅ Sí' if sala.elo_aplicado else '❌ No'}")
        
        # Confirmar cambio
        print(f"\n⚠️  ¿Deseas cambiar el estado de '{sala.estado}' a '{nuevo_estado}'?")
        confirmacion = input("Escribe 'SI' para confirmar: ")
        
        if confirmacion.upper() != 'SI':
            print("❌ Operación cancelada")
            return
        
        # Actualizar estado
        query_actualizar = text("""
            UPDATE salas 
            SET estado = :nuevo_estado
            WHERE id_sala = :id_sala
        """)
        
        db.execute(query_actualizar, {
            "id_sala": id_sala,
            "nuevo_estado": nuevo_estado
        })
        db.commit()
        
        print(f"\n✅ Estado actualizado correctamente")
        
        # Verificar cambio
        result_verificar = db.execute(query_verificar, {"id_sala": id_sala})
        sala_actualizada = result_verificar.fetchone()
        
        print(f"\n📊 Estado actual:")
        print(f"   Estado: {sala_actualizada.estado}")
        
        print("\n" + "=" * 60)
        print("ACTUALIZACIÓN COMPLETADA")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def actualizar_salas_finalizadas_sin_elo():
    """
    Actualizar todas las salas finalizadas que no tienen Elo aplicado
    """
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("ACTUALIZAR SALAS FINALIZADAS SIN ELO")
        print("=" * 60)
        
        # Buscar salas finalizadas sin Elo aplicado
        query = text("""
            SELECT 
                s.id_sala,
                s.nombre,
                s.estado,
                p.estado_confirmacion,
                p.elo_aplicado
            FROM salas s
            LEFT JOIN partidos p ON s.id_partido = p.id_partido
            WHERE s.estado = 'finalizada'
            AND (p.elo_aplicado = false OR p.elo_aplicado IS NULL)
        """)
        
        result = db.execute(query)
        salas = result.fetchall()
        
        if not salas:
            print("\n✅ No hay salas finalizadas sin Elo aplicado")
            return
        
        print(f"\n📊 Encontradas {len(salas)} salas:")
        for sala in salas:
            print(f"\n   • Sala #{sala.id_sala}: {sala.nombre}")
            print(f"     Estado: {sala.estado}")
            print(f"     Estado confirmación: {sala.estado_confirmacion or 'sin_resultado'}")
            print(f"     Elo aplicado: {'✅ Sí' if sala.elo_aplicado else '❌ No'}")
        
        print(f"\n⚠️  ¿Deseas cambiar todas estas salas a estado 'en_juego'?")
        confirmacion = input("Escribe 'SI' para confirmar: ")
        
        if confirmacion.upper() != 'SI':
            print("❌ Operación cancelada")
            return
        
        # Actualizar todas
        query_actualizar = text("""
            UPDATE salas 
            SET estado = 'en_juego'
            WHERE estado = 'finalizada'
            AND id_partido IN (
                SELECT id_partido 
                FROM partidos 
                WHERE elo_aplicado = false OR elo_aplicado IS NULL
            )
        """)
        
        result_update = db.execute(query_actualizar)
        db.commit()
        
        print(f"\n✅ Actualizadas {result_update.rowcount} salas")
        
        print("\n" + "=" * 60)
        print("ACTUALIZACIÓN COMPLETADA")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    print("\n🔧 ACTUALIZAR ESTADO DE SALAS")
    print("=" * 60)
    print("\nOpciones:")
    print("1. Actualizar una sala específica")
    print("2. Actualizar todas las salas finalizadas sin Elo")
    print("3. Salir")
    
    opcion = input("\nSelecciona una opción (1-3): ")
    
    if opcion == "1":
        id_sala = input("\nIngresa el ID de la sala: ")
        try:
            id_sala = int(id_sala)
            actualizar_sala(id_sala, "en_juego")
        except ValueError:
            print("❌ ID inválido")
    
    elif opcion == "2":
        actualizar_salas_finalizadas_sin_elo()
    
    elif opcion == "3":
        print("👋 Saliendo...")
    
    else:
        print("❌ Opción inválida")
