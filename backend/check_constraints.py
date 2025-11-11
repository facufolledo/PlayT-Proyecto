#!/usr/bin/env python3
"""
Script para verificar las restricciones CHECK de la base de datos
"""
from sqlalchemy import text
from src.database.config import engine

def check_constraints():
    """Verificar las restricciones CHECK de la base de datos"""
    
    print("🔍 Verificando restricciones CHECK de la base de datos...")
    print("=" * 60)
    
    try:
        with engine.connect() as conn:
            # Consultar restricciones CHECK de la tabla partidos
            query = text("""
                SELECT 
                    conname as constraint_name,
                    pg_get_constraintdef(oid) as constraint_definition
                FROM pg_constraint 
                WHERE conrelid = 'partidos'::regclass 
                AND contype = 'c'
                ORDER BY conname;
            """)
            
            result = conn.execute(query)
            constraints = result.fetchall()
            
            if constraints:
                print("📋 Restricciones CHECK encontradas en tabla 'partidos':")
                for constraint in constraints:
                    print(f"  • {constraint[0]}: {constraint[1]}")
            else:
                print("❌ No se encontraron restricciones CHECK en la tabla 'partidos'")
            
            # Verificar valores únicos en el campo estado
            print("\n📊 Valores únicos en campo 'estado' de tabla 'partidos':")
            query2 = text("SELECT DISTINCT estado FROM partidos ORDER BY estado;")
            result2 = conn.execute(query2)
            estados = result2.fetchall()
            
            if estados:
                for estado in estados:
                    print(f"  • '{estado[0]}'")
            else:
                print("  • Tabla 'partidos' está vacía")
            
            # Verificar si podemos insertar diferentes valores
            print("\n🧪 Probando inserción de diferentes estados...")
            test_values = ['pendiente', 'finalizado', 'cancelado', 'en_curso']
            
            for valor in test_values:
                try:
                    # Intentar insertar un partido de prueba
                    test_query = text("""
                        INSERT INTO partidos (fecha, estado, id_creador) 
                        VALUES (NOW(), :estado, 1)
                        ON CONFLICT DO NOTHING;
                    """)
                    conn.execute(test_query, {"estado": valor})
                    print(f"  ✅ '{valor}' - INSERT exitoso")
                except Exception as e:
                    print(f"  ❌ '{valor}' - Error: {str(e)[:100]}...")
            
            conn.commit()
            
    except Exception as e:
        print(f"💥 Error al verificar restricciones: {e}")

if __name__ == "__main__":
    check_constraints()

