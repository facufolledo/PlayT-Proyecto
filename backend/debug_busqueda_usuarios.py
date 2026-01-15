"""
Script para debuggear búsqueda de usuarios
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from src.database.config import SessionLocal
from src.models.driveplus_models import Usuario, PerfilUsuario
from sqlalchemy import or_

def debug_busqueda():
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("DEBUG: Búsqueda de Usuarios")
        print("=" * 60)
        
        # 1. Contar usuarios totales
        total_usuarios = db.query(Usuario).count()
        print(f"\n✅ Total usuarios en tabla 'usuarios': {total_usuarios}")
        
        # 2. Contar perfiles totales
        total_perfiles = db.query(PerfilUsuario).count()
        print(f"✅ Total perfiles en tabla 'perfil_usuarios': {total_perfiles}")
        
        # 3. Listar primeros 5 usuarios con sus datos
        print("\n📋 Primeros 5 usuarios:")
        usuarios = db.query(Usuario).limit(5).all()
        for u in usuarios:
            print(f"  - ID: {u.id_usuario}, Username: {u.nombre_usuario}, Email: {u.email}")
        
        # 4. Listar primeros 5 perfiles
        print("\n📋 Primeros 5 perfiles:")
        perfiles = db.query(PerfilUsuario).limit(5).all()
        for p in perfiles:
            print(f"  - ID Usuario: {p.id_usuario}, Nombre: {p.nombre} {p.apellido}")
        
        # 5. Probar búsqueda con "fac"
        search_term = "%fac%"
        print(f"\n🔍 Buscando usuarios con término: 'fac'")
        
        # Buscar en usuarios
        usuarios_match = db.query(Usuario).filter(
            Usuario.nombre_usuario.ilike(search_term)
        ).all()
        print(f"  - Usuarios con username que contiene 'fac': {len(usuarios_match)}")
        for u in usuarios_match:
            print(f"    * {u.nombre_usuario}")
        
        # Buscar en perfiles
        perfiles_match = db.query(PerfilUsuario).filter(
            or_(
                PerfilUsuario.nombre.ilike(search_term),
                PerfilUsuario.apellido.ilike(search_term)
            )
        ).all()
        print(f"  - Perfiles con nombre/apellido que contiene 'fac': {len(perfiles_match)}")
        for p in perfiles_match:
            print(f"    * {p.nombre} {p.apellido} (ID: {p.id_usuario})")
        
        # 6. Probar JOIN como en el endpoint
        print(f"\n🔗 Probando JOIN Usuario + PerfilUsuario:")
        resultados = db.query(Usuario, PerfilUsuario).outerjoin(
            PerfilUsuario, Usuario.id_usuario == PerfilUsuario.id_usuario
        ).filter(
            or_(
                Usuario.nombre_usuario.ilike(search_term),
                PerfilUsuario.nombre.ilike(search_term),
                PerfilUsuario.apellido.ilike(search_term)
            )
        ).limit(20).all()
        
        print(f"  - Resultados del JOIN: {len(resultados)}")
        for usuario, perfil in resultados:
            if perfil:
                print(f"    * {usuario.nombre_usuario} -> {perfil.nombre} {perfil.apellido}")
            else:
                print(f"    * {usuario.nombre_usuario} -> SIN PERFIL")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_busqueda()
