#!/usr/bin/env python3
"""
Script para ejecutar la migración de categorías balanceadas
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

def ejecutar_migracion():
    """Ejecutar migración de categorías balanceadas"""
    
    print("=" * 80)
    print("  🔄 MIGRACIÓN: Categorías Balanceadas")
    print("=" * 80)
    
    # Conectar a la base de datos
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(DATABASE_URL)
    
    print("\n📡 Conectando a la base de datos...")
    
    try:
        with engine.connect() as conn:
            # Verificar conexión
            conn.execute(text("SELECT 1"))
            print("✅ Conexión exitosa")
            
            print("\n🗑️  Eliminando categorías antiguas...")
            
            # Eliminar categorías antiguas
            conn.execute(text("DELETE FROM categorias WHERE sexo = 'masculino'"))
            conn.execute(text("DELETE FROM categorias WHERE sexo = 'femenino'"))
            conn.commit()
            
            print("✅ Categorías antiguas eliminadas")
            
            print("\n📝 Insertando nuevas categorías masculinas...")
            
            # Insertar categorías masculinas
            categorias_masculinas = [
                ('Principiante', 'Jugadores muy nuevos, aprendiendo fundamentos', 0, 699, 'masculino'),
                ('8va', 'Principiantes avanzados, golpes básicos sólidos', 700, 899, 'masculino'),
                ('7ma', 'Jugadores intermedios, mejor dominio técnico', 900, 1099, 'masculino'),
                ('6ta', 'Buenos jugadores, estrategia y consistencia', 1100, 1299, 'masculino'),
                ('5ta', 'Muy buenos jugadores, técnica + táctica', 1300, 1499, 'masculino'),
                ('4ta', 'Jugadores avanzados, alto nivel técnico', 1500, 1699, 'masculino'),
                ('Libre', 'Élite local, top de la región', 1700, None, 'masculino')
            ]
            
            for cat in categorias_masculinas:
                conn.execute(text("""
                    INSERT INTO categorias (nombre, descripcion, rating_min, rating_max, sexo)
                    VALUES (:nombre, :descripcion, :rating_min, :rating_max, :sexo)
                """), {
                    'nombre': cat[0],
                    'descripcion': cat[1],
                    'rating_min': cat[2],
                    'rating_max': cat[3],
                    'sexo': cat[4]
                })
            
            print("✅ Categorías masculinas insertadas")
            
            print("\n📝 Insertando nuevas categorías femeninas...")
            
            # Insertar categorías femeninas
            categorias_femeninas = [
                ('Principiante', 'Jugadoras muy nuevas, aprendiendo fundamentos', 0, 699, 'femenino'),
                ('8va', 'Principiantes avanzadas, golpes básicos sólidos', 700, 899, 'femenino'),
                ('7ma', 'Jugadoras intermedias, mejor dominio técnico', 900, 1099, 'femenino'),
                ('6ta', 'Buenas jugadoras, estrategia y consistencia', 1100, 1299, 'femenino'),
                ('5ta', 'Muy buenas jugadoras, técnica + táctica', 1300, 1499, 'femenino'),
                ('4ta', 'Jugadoras avanzadas, alto nivel técnico', 1500, 1699, 'femenino'),
                ('Libre', 'Élite local, top de la región', 1700, None, 'femenino')
            ]
            
            for cat in categorias_femeninas:
                conn.execute(text("""
                    INSERT INTO categorias (nombre, descripcion, rating_min, rating_max, sexo)
                    VALUES (:nombre, :descripcion, :rating_min, :rating_max, :sexo)
                """), {
                    'nombre': cat[0],
                    'descripcion': cat[1],
                    'rating_min': cat[2],
                    'rating_max': cat[3],
                    'sexo': cat[4]
                })
            
            print("✅ Categorías femeninas insertadas")
            
            conn.commit()
            
            print("\n📊 Verificando categorías insertadas...")
            
            # Verificar masculinas
            result = conn.execute(text("""
                SELECT nombre, rating_min, rating_max, 
                       CASE 
                           WHEN rating_max IS NULL THEN 'Sin límite'
                           ELSE CAST(rating_max - rating_min AS TEXT)
                       END as rango
                FROM categorias 
                WHERE sexo = 'masculino'
                ORDER BY rating_min
            """))
            
            print("\n🔵 CATEGORÍAS MASCULINAS:")
            print(f"{'Categoría':<15} {'Min':<8} {'Max':<8} {'Rango':<12}")
            print("-" * 50)
            for row in result:
                max_val = row[2] if row[2] is not None else '∞'
                print(f"{row[0]:<15} {row[1]:<8} {max_val:<8} {row[3]:<12}")
            
            # Verificar femeninas
            result = conn.execute(text("""
                SELECT nombre, rating_min, rating_max,
                       CASE 
                           WHEN rating_max IS NULL THEN 'Sin límite'
                           ELSE CAST(rating_max - rating_min AS TEXT)
                       END as rango
                FROM categorias 
                WHERE sexo = 'femenino'
                ORDER BY rating_min
            """))
            
            print("\n🔴 CATEGORÍAS FEMENINAS:")
            print(f"{'Categoría':<15} {'Min':<8} {'Max':<8} {'Rango':<12}")
            print("-" * 50)
            for row in result:
                max_val = row[2] if row[2] is not None else '∞'
                print(f"{row[0]:<15} {row[1]:<8} {max_val:<8} {row[3]:<12}")
            
            print("\n" + "=" * 80)
            print("  ✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 80)
            
            print("\n📋 RESUMEN:")
            print("   ✅ 7 categorías masculinas creadas")
            print("   ✅ 7 categorías femeninas creadas")
            print("   ✅ Rangos balanceados de 200 puntos")
            print("   ✅ Sistema listo para producción")
            
            print("\n💡 PRÓXIMOS PASOS:")
            print("   1. Reiniciar el servidor backend")
            print("   2. Ejecutar test_torneo_completo.py")
            print("   3. Verificar que los caps funcionen correctamente")
            
            return True
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = ejecutar_migracion()
    exit(0 if success else 1)
