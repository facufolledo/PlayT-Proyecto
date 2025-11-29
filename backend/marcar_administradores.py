"""
Script para marcar usuarios como administradores
"""
from src.database.config import engine
from sqlalchemy import text

def marcar_administradores():
    """
    Marca usuarios específicos como administradores
    """
    conn = engine.connect()
    
    try:
        # Obtener todos los usuarios para ver quiénes son
        result = conn.execute(text("""
            SELECT id_usuario, nombre_usuario, email, es_administrador, puede_crear_torneos
            FROM usuarios
            ORDER BY id_usuario
        """))
        
        usuarios = result.fetchall()
        
        print("\n" + "="*80)
        print("USUARIOS ACTUALES:")
        print("="*80)
        for u in usuarios:
            admin_badge = "👑 ADMIN" if u[3] else ""
            torneo_badge = "🏆 ORGANIZADOR" if u[4] else ""
            print(f"ID: {u[0]:3d} | {u[1]:20s} | {u[2]:30s} {admin_badge} {torneo_badge}")
        
        print("\n" + "="*80)
        print("MARCAR ADMINISTRADORES")
        print("="*80)
        print("Ingresa los IDs de los usuarios que quieres marcar como administradores")
        print("Separados por comas (ej: 1,2,3) o 'todos' para ver opciones")
        print("Deja vacío para cancelar")
        
        ids_input = input("\nIDs: ").strip()
        
        if not ids_input:
            print("❌ Operación cancelada")
            return
        
        if ids_input.lower() == 'todos':
            print("\n📋 Opciones:")
            print("1. Marcar todos como administradores")
            print("2. Marcar todos como organizadores de torneos")
            print("3. Cancelar")
            opcion = input("\nOpción: ").strip()
            
            if opcion == '1':
                conn.execute(text("UPDATE usuarios SET es_administrador = true, puede_crear_torneos = true"))
                conn.commit()
                print("✅ Todos los usuarios son ahora administradores")
                return
            elif opcion == '2':
                conn.execute(text("UPDATE usuarios SET puede_crear_torneos = true WHERE puede_crear_torneos IS NULL OR puede_crear_torneos = false"))
                conn.commit()
                print("✅ Todos los usuarios pueden crear torneos")
                return
            else:
                print("❌ Operación cancelada")
                return
        
        # Parsear IDs
        try:
            ids = [int(id.strip()) for id in ids_input.split(',')]
        except ValueError:
            print("❌ Error: IDs inválidos")
            return
        
        # Verificar que los IDs existen
        ids_validos = [u[0] for u in usuarios]
        ids_invalidos = [id for id in ids if id not in ids_validos]
        
        if ids_invalidos:
            print(f"❌ Error: Los siguientes IDs no existen: {ids_invalidos}")
            return
        
        # Confirmar
        print(f"\n⚠️  Vas a marcar como ADMINISTRADORES a:")
        for u in usuarios:
            if u[0] in ids:
                print(f"   - {u[1]} ({u[2]})")
        
        confirmar = input("\n¿Confirmar? (si/no): ").strip().lower()
        
        if confirmar not in ['si', 's', 'yes', 'y']:
            print("❌ Operación cancelada")
            return
        
        # Marcar como administradores
        placeholders = ','.join([':id' + str(i) for i in range(len(ids))])
        params = {f'id{i}': id_val for i, id_val in enumerate(ids)}
        
        conn.execute(
            text(f"""
                UPDATE usuarios 
                SET es_administrador = true,
                    puede_crear_torneos = true
                WHERE id_usuario IN ({placeholders})
            """),
            params
        )
        conn.commit()
        
        print(f"\n✅ {len(ids)} usuario(s) marcado(s) como administradores")
        
        # Mostrar resultado
        result = conn.execute(text("""
            SELECT id_usuario, nombre_usuario, email, es_administrador, puede_crear_torneos
            FROM usuarios
            WHERE id_usuario IN ({})
        """.format(','.join(map(str, ids)))))
        
        print("\n" + "="*80)
        print("RESULTADO:")
        print("="*80)
        for u in result.fetchall():
            admin_badge = "👑 ADMIN" if u[3] else ""
            torneo_badge = "🏆 ORGANIZADOR" if u[4] else ""
            print(f"ID: {u[0]:3d} | {u[1]:20s} | {u[2]:30s} {admin_badge} {torneo_badge}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    marcar_administradores()
