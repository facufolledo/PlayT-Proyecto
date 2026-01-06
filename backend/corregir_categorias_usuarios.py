#!/usr/bin/env python3
"""
Script para corregir las categorías de usuarios según su rating actual
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from src.database.config import SessionLocal
from src.models.driveplus_models import Usuario, Categoria
from src.services.categoria_service import obtener_categoria_por_rating

def corregir_categorias():
    """Corrige las categorías de todos los usuarios según su rating actual"""
    db = SessionLocal()
    
    try:
        print("🔍 Verificando categorías de usuarios...")
        
        # Obtener todos los usuarios activos
        usuarios = db.query(Usuario).filter(Usuario.activo == True).all()
        
        usuarios_corregidos = 0
        
        for usuario in usuarios:
            if not usuario.sexo:
                print(f"⚠️  Usuario {usuario.nombre_usuario} no tiene sexo definido, saltando...")
                continue
                
            # Obtener la categoría correcta según el rating
            categoria_correcta = obtener_categoria_por_rating(
                db, usuario.rating or 1200, usuario.sexo
            )
            
            if not categoria_correcta:
                print(f"⚠️  No se encontró categoría para {usuario.nombre_usuario} (Rating: {usuario.rating}, Sexo: {usuario.sexo})")
                continue
            
            # Verificar si la categoría actual es incorrecta
            if usuario.id_categoria != categoria_correcta.id_categoria:
                categoria_anterior = None
                if usuario.id_categoria:
                    categoria_anterior = db.query(Categoria).filter(
                        Categoria.id_categoria == usuario.id_categoria
                    ).first()
                
                print(f"🔧 Corrigiendo {usuario.nombre_usuario}:")
                print(f"   Rating: {usuario.rating}")
                print(f"   Categoría anterior: {categoria_anterior.nombre if categoria_anterior else 'Ninguna'}")
                print(f"   Categoría correcta: {categoria_correcta.nombre}")
                
                # Actualizar la categoría
                usuario.id_categoria = categoria_correcta.id_categoria
                usuarios_corregidos += 1
            else:
                categoria_actual = db.query(Categoria).filter(
                    Categoria.id_categoria == usuario.id_categoria
                ).first()
                print(f"✅ {usuario.nombre_usuario}: Rating {usuario.rating} - {categoria_actual.nombre if categoria_actual else 'Sin categoría'} (Correcto)")
        
        if usuarios_corregidos > 0:
            db.commit()
            print(f"\n✅ Se corrigieron {usuarios_corregidos} usuarios")
        else:
            print("\n✅ Todas las categorías están correctas")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

def mostrar_rangos_categorias():
    """Muestra los rangos de rating de cada categoría"""
    db = SessionLocal()
    
    try:
        print("\n📊 RANGOS DE CATEGORÍAS:")
        print("-" * 50)
        
        categorias = db.query(Categoria).order_by(
            Categoria.sexo, Categoria.rating_min.desc()
        ).all()
        
        for categoria in categorias:
            rating_min = categoria.rating_min or "Sin límite"
            rating_max = categoria.rating_max or "Sin límite"
            print(f"{categoria.nombre} ({categoria.sexo}): {rating_min} - {rating_max}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🚗⚡ CORRECCIÓN DE CATEGORÍAS - Drive+")
    print("=" * 50)
    
    mostrar_rangos_categorias()
    corregir_categorias()