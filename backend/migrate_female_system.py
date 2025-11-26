#!/usr/bin/env python3
"""
Script de migración para integrar el sistema femenino
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.config import engine, get_db
from src.models.playt_models import Usuario, Categoria
from sqlalchemy import text

def migrate_female_system():
    """Migrar la base de datos para incluir sistema femenino"""
    
    print("🏆 MIGRACIÓN AL SISTEMA FEMENINO")
    print("=" * 50)
    
    try:
        # 1. Agregar campo sexo a usuarios
        print("\n1. 👤 AGREGANDO CAMPO SEXO A USUARIOS")
        print("-" * 40)
        
        # Verificar si el campo ya existe
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'usuarios' AND column_name = 'sexo'
            """))
            
            if result.fetchone():
                print("   ✅ Campo 'sexo' ya existe en usuarios")
            else:
                # Agregar campo sexo
                conn.execute(text("""
                    ALTER TABLE usuarios 
                    ADD COLUMN sexo VARCHAR(10) DEFAULT 'masculino' NOT NULL
                """))
                conn.commit()
                print("   ✅ Campo 'sexo' agregado a usuarios")
        
        # 2. Actualizar usuarios existentes como masculino
        print("\n2. 🔄 ACTUALIZANDO USUARIOS EXISTENTES")
        print("-" * 40)
        
        with engine.connect() as conn:
            result = conn.execute(text("""
                UPDATE usuarios 
                SET sexo = 'masculino' 
                WHERE sexo IS NULL OR sexo = ''
            """))
            conn.commit()
            print(f"   ✅ {result.rowcount} usuarios actualizados como masculino")
        
        # 3. Agregar campo sexo a categorías
        print("\n3. 🏆 AGREGANDO CAMPO SEXO A CATEGORÍAS")
        print("-" * 40)
        
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'categorias' AND column_name = 'sexo'
            """))
            
            if result.fetchone():
                print("   ✅ Campo 'sexo' ya existe en categorías")
            else:
                # Agregar campo sexo
                conn.execute(text("""
                    ALTER TABLE categorias 
                    ADD COLUMN sexo VARCHAR(10) DEFAULT 'masculino' NOT NULL
                """))
                conn.commit()
                print("   ✅ Campo 'sexo' agregado a categorías")
        
        # 4. Actualizar categorías existentes como masculino
        print("\n4. 🔄 ACTUALIZANDO CATEGORÍAS EXISTENTES")
        print("-" * 40)
        
        with engine.connect() as conn:
            result = conn.execute(text("""
                UPDATE categorias 
                SET sexo = 'masculino' 
                WHERE sexo IS NULL OR sexo = ''
            """))
            conn.commit()
            print(f"   ✅ {result.rowcount} categorías actualizadas como masculino")
        
        # 4.5. Modificar restricción única para permitir nombres duplicados con diferente sexo
        print("\n4.5 🔧 MODIFICANDO RESTRICCIÓN ÚNICA")
        print("-" * 40)
        
        with engine.connect() as conn:
            try:
                # Eliminar restricción única anterior
                conn.execute(text("""
                    ALTER TABLE categorias DROP CONSTRAINT IF EXISTS categorias_nombre_key
                """))
                # Crear nueva restricción única compuesta
                conn.execute(text("""
                    ALTER TABLE categorias ADD CONSTRAINT categorias_nombre_sexo_key UNIQUE (nombre, sexo)
                """))
                conn.commit()
                print("   ✅ Restricción única actualizada para (nombre, sexo)")
            except Exception as e:
                print(f"   ⚠️  Advertencia al modificar restricción: {e}")
                pass
        
        # 5. Crear categorías femeninas
        print("\n5. 👩 CREANDO CATEGORÍAS FEMENINAS")
        print("-" * 40)
        
        categorias_femeninas = [
            {
                "nombre": "Principiante",
                "descripcion": "Categoría para principiantes absolutos (Femenino)",
                "rating_min": 0,
                "rating_max": 499,
                "sexo": "femenino"
            },
            {
                "nombre": "8va",
                "descripcion": "Categoría inicial (Femenino)",
                "rating_min": 500,
                "rating_max": 999,
                "sexo": "femenino"
            },
            {
                "nombre": "7ma",
                "descripcion": "Categoría intermedia baja (Femenino)",
                "rating_min": 1000,
                "rating_max": 1199,
                "sexo": "femenino"
            },
            {
                "nombre": "6ta",
                "descripcion": "Categoría intermedia (Femenino)",
                "rating_min": 1200,
                "rating_max": 1399,
                "sexo": "femenino"
            },
            {
                "nombre": "5ta",
                "descripcion": "Categoría intermedia alta (Femenino)",
                "rating_min": 1400,
                "rating_max": 1599,
                "sexo": "femenino"
            },
            {
                "nombre": "Libre",
                "descripcion": "Categoría máxima (Femenino)",
                "rating_min": 1600,
                "rating_max": None,
                "sexo": "femenino"
            }
        ]
        
        with engine.connect() as conn:
            for cat in categorias_femeninas:
                # Verificar si ya existe
                result = conn.execute(text("""
                    SELECT id_categoria FROM categorias 
                    WHERE nombre = :nombre AND sexo = :sexo
                """), {"nombre": cat["nombre"], "sexo": cat["sexo"]})
                
                if result.fetchone():
                    print(f"   ⚠️  Categoría {cat['nombre']} (Femenino) ya existe")
                else:
                    # Crear categoría
                    conn.execute(text("""
                        INSERT INTO categorias (nombre, descripcion, rating_min, rating_max, sexo)
                        VALUES (:nombre, :descripcion, :rating_min, :rating_max, :sexo)
                    """), cat)
                    conn.commit()
                    print(f"   ✅ Categoría {cat['nombre']} (Femenino) creada")
        
        # 6. Crear tabla categoria_checkpoints si no existe
        print("\n6. 📊 CREANDO TABLA CATEGORIA_CHECKPOINTS")
        print("-" * 40)
        
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'categoria_checkpoints'
            """))
            
            if result.fetchone():
                print("   ✅ Tabla 'categoria_checkpoints' ya existe")
            else:
                conn.execute(text("""
                    CREATE TABLE categoria_checkpoints (
                        id_checkpoint BIGSERIAL PRIMARY KEY,
                        id_usuario BIGINT NOT NULL REFERENCES usuarios(id_usuario),
                        categoria_anterior VARCHAR(20),
                        categoria_nueva VARCHAR(20) NOT NULL,
                        rating_ascenso INTEGER NOT NULL,
                        fecha_ascenso TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        id_partido_ascenso BIGINT REFERENCES partidos(id_partido),
                        partidos_inmunidad_restantes SMALLINT DEFAULT 0
                    )
                """))
                conn.commit()
                print("   ✅ Tabla 'categoria_checkpoints' creada")
        
        # 7. Verificar migración
        print("\n7. ✅ VERIFICACIÓN DE MIGRACIÓN")
        print("-" * 40)
        
        with engine.connect() as conn:
            # Contar usuarios por sexo
            result = conn.execute(text("""
                SELECT sexo, COUNT(*) as count 
                FROM usuarios 
                GROUP BY sexo
            """))
            usuarios_por_sexo = result.fetchall()
            print("   👥 Usuarios por sexo:")
            for sexo, count in usuarios_por_sexo:
                print(f"      {sexo}: {count}")
            
            # Contar categorías por sexo
            result = conn.execute(text("""
                SELECT sexo, COUNT(*) as count 
                FROM categorias 
                GROUP BY sexo
            """))
            categorias_por_sexo = result.fetchall()
            print("   🏆 Categorías por sexo:")
            for sexo, count in categorias_por_sexo:
                print(f"      {sexo}: {count}")
        
        print("\n🎾 ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
        print("=" * 50)
        print("✅ Sistema femenino integrado")
        print("✅ Usuarios existentes marcados como masculino")
        print("✅ Categorías femeninas creadas")
        print("✅ Tabla categoria_checkpoints creada")
        print("✅ Base de datos lista para sistema mixto")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR EN MIGRACIÓN: {e}")
        return False

if __name__ == "__main__":
    migrate_female_system()
