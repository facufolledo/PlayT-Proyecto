"""
Script para limpiar el historial de enfrentamientos entre jugadores específicos
Esto permite probar el sistema sin restricciones del anti-trampa
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

def limpiar_historial_jugadores(nombres_usuarios: list):
    """
    Elimina el historial de enfrentamientos para los jugadores especificados
    
    Args:
        nombres_usuarios: Lista de nombres de usuario (ej: ['facundo', 'facundo2', 'ffolledo'])
    """
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("LIMPIEZA DE HISTORIAL DE ENFRENTAMIENTOS")
        print("=" * 60)
        
        # 1. Obtener IDs de los usuarios
        print(f"\n1. Buscando usuarios: {', '.join(nombres_usuarios)}")
        
        placeholders = ', '.join([f':user{i}' for i in range(len(nombres_usuarios))])
        query = text(f"""
            SELECT id_usuario, nombre_usuario 
            FROM usuarios 
            WHERE nombre_usuario IN ({placeholders})
        """)
        
        params = {f'user{i}': nombre for i, nombre in enumerate(nombres_usuarios)}
        result = db.execute(query, params)
        usuarios = result.fetchall()
        
        if len(usuarios) != len(nombres_usuarios):
            print(f"⚠️  Advertencia: Solo se encontraron {len(usuarios)} de {len(nombres_usuarios)} usuarios")
            for usuario in usuarios:
                print(f"   ✓ {usuario.nombre_usuario} (ID: {usuario.id_usuario})")
            
            faltantes = set(nombres_usuarios) - {u.nombre_usuario for u in usuarios}
            if faltantes:
                print(f"   ✗ No encontrados: {', '.join(faltantes)}")
        else:
            print(f"✅ Todos los usuarios encontrados:")
            for usuario in usuarios:
                print(f"   • {usuario.nombre_usuario} (ID: {usuario.id_usuario})")
        
        if len(usuarios) < 2:
            print("\n❌ Se necesitan al menos 2 usuarios para limpiar el historial")
            return
        
        usuario_ids = [u.id_usuario for u in usuarios]
        
        # 2. Buscar enfrentamientos que involucren a estos jugadores
        print(f"\n2. Buscando enfrentamientos...")
        
        id_placeholders = ', '.join([f':id{i}' for i in range(len(usuario_ids))])
        query_historial = text(f"""
            SELECT 
                id_historial,
                id_partido,
                fecha,
                jugador1_id,
                jugador2_id,
                jugador3_id,
                jugador4_id,
                tipo_partido
            FROM historial_enfrentamientos
            WHERE 
                jugador1_id IN ({id_placeholders}) OR
                jugador2_id IN ({id_placeholders}) OR
                jugador3_id IN ({id_placeholders}) OR
                jugador4_id IN ({id_placeholders})
            ORDER BY fecha DESC
        """)
        
        params_ids = {f'id{i}': uid for i, uid in enumerate(usuario_ids)}
        result_historial = db.execute(query_historial, params_ids)
        enfrentamientos = result_historial.fetchall()
        
        if not enfrentamientos:
            print("✅ No hay enfrentamientos registrados para estos jugadores")
            return
        
        print(f"📊 Encontrados {len(enfrentamientos)} enfrentamientos:")
        for enf in enfrentamientos[:5]:  # Mostrar solo los primeros 5
            print(f"   • ID: {enf.id_historial} | Partido: {enf.id_partido} | Fecha: {enf.fecha} | Tipo: {enf.tipo_partido}")
        
        if len(enfrentamientos) > 5:
            print(f"   ... y {len(enfrentamientos) - 5} más")
        
        # 3. Confirmar eliminación
        print(f"\n⚠️  ¿Deseas eliminar {len(enfrentamientos)} registros del historial?")
        confirmacion = input("Escribe 'SI' para confirmar: ")
        
        if confirmacion.upper() != 'SI':
            print("❌ Operación cancelada")
            return
        
        # 4. Eliminar registros
        print(f"\n3. Eliminando registros...")
        
        delete_query = text(f"""
            DELETE FROM historial_enfrentamientos
            WHERE 
                jugador1_id IN ({id_placeholders}) OR
                jugador2_id IN ({id_placeholders}) OR
                jugador3_id IN ({id_placeholders}) OR
                jugador4_id IN ({id_placeholders})
        """)
        
        result_delete = db.execute(delete_query, params_ids)
        db.commit()
        
        print(f"✅ Eliminados {result_delete.rowcount} registros del historial")
        
        # 5. Verificar
        print(f"\n4. Verificando...")
        result_verificar = db.execute(query_historial, params_ids)
        restantes = result_verificar.fetchall()
        
        if len(restantes) == 0:
            print("✅ Historial limpiado correctamente")
            print("\n🎾 Ahora puedes crear partidos entre estos jugadores sin restricciones")
        else:
            print(f"⚠️  Aún quedan {len(restantes)} registros")
        
        print("\n" + "=" * 60)
        print("LIMPIEZA COMPLETADA")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def limpiar_todo_historial():
    """
    Elimina TODOS los registros del historial de enfrentamientos
    ⚠️ USAR CON PRECAUCIÓN - Solo para desarrollo/testing
    """
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("⚠️  LIMPIEZA TOTAL DEL HISTORIAL")
        print("=" * 60)
        
        # Contar registros
        count_query = text("SELECT COUNT(*) as total FROM historial_enfrentamientos")
        result = db.execute(count_query)
        total = result.fetchone().total
        
        if total == 0:
            print("\n✅ El historial ya está vacío")
            return
        
        print(f"\n📊 Hay {total} registros en el historial")
        print("\n⚠️  ¿Deseas eliminar TODOS los registros?")
        print("⚠️  Esta acción NO se puede deshacer")
        confirmacion = input("Escribe 'ELIMINAR TODO' para confirmar: ")
        
        if confirmacion != 'ELIMINAR TODO':
            print("❌ Operación cancelada")
            return
        
        # Eliminar todo
        delete_query = text("DELETE FROM historial_enfrentamientos")
        result_delete = db.execute(delete_query)
        db.commit()
        
        print(f"\n✅ Eliminados {result_delete.rowcount} registros")
        print("\n🎾 El historial está completamente limpio")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    print("\n🧹 LIMPIADOR DE HISTORIAL DE ENFRENTAMIENTOS")
    print("=" * 60)
    print("\nOpciones:")
    print("1. Limpiar historial de jugadores específicos")
    print("2. Limpiar TODO el historial (⚠️  PELIGROSO)")
    print("3. Salir")
    
    opcion = input("\nSelecciona una opción (1-3): ")
    
    if opcion == "1":
        print("\n📝 Ingresa los nombres de usuario separados por comas")
        print("Ejemplo: facundo,facundo2,ffolledo")
        nombres = input("\nNombres de usuario: ")
        
        if nombres.strip():
            lista_nombres = [n.strip() for n in nombres.split(',')]
            limpiar_historial_jugadores(lista_nombres)
        else:
            print("❌ No se ingresaron nombres de usuario")
    
    elif opcion == "2":
        limpiar_todo_historial()
    
    elif opcion == "3":
        print("👋 Saliendo...")
    
    else:
        print("❌ Opción inválida")
