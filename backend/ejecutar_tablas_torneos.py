"""
Script para crear todas las tablas del sistema de torneos
PostgreSQL / Neon
"""
from src.database.config import engine
from sqlalchemy import text
import sys


def crear_tablas_torneos():
    """Crea todas las tablas necesarias para el sistema de torneos"""
    
    print("\n" + "="*60)
    print("SISTEMA DE TORNEOS - CREACION DE TABLAS")
    print("="*60)
    print()
    
    try:
        # Leer el archivo SQL
        with open('crear_tablas_torneos.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print("[OK] Archivo SQL cargado")
        print("[...] Conectando a PostgreSQL (Neon)...")
        
        conn = engine.connect()
        trans = conn.begin()
        
        print("[OK] Conexion exitosa\n")
        print("Ejecutando SQL completo...")
        
        try:
            # Ejecutar todo el SQL de una vez
            conn.execute(text(sql_content))
            trans.commit()
            print("[OK] SQL ejecutado exitosamente\n")
            
        except Exception as e:
            trans.rollback()
            print(f"[ERROR] {str(e)[:300]}\n")
            print("Intentando ejecutar statement por statement...\n")
            
            # Si falla, intentar statement por statement
            import re
            # Dividir por CREATE TABLE o CREATE INDEX
            statements = re.split(r'(CREATE\s+(?:TABLE|INDEX))', sql_content, flags=re.IGNORECASE)
            
            tablas_creadas = 0
            indices_creados = 0
            
            i = 1
            while i < len(statements):
                if i + 1 < len(statements):
                    statement = (statements[i] + statements[i+1]).strip()
                    i += 2
                else:
                    break
                
                if not statement:
                    continue
                
                # Encontrar el final del statement (punto y coma)
                end_idx = statement.find(';')
                if end_idx > 0:
                    statement = statement[:end_idx+1]
                
                trans = conn.begin()
                
                try:
                    statement_lower = statement.lower()
                    
                    if 'create table' in statement_lower:
                        if 'if not exists' in statement_lower:
                            table_name = statement_lower.split('if not exists')[1].split('(')[0].strip()
                        else:
                            table_name = statement_lower.split('create table')[1].split('(')[0].strip()
                        print(f"  Creando tabla: {table_name}...", end=" ")
                    elif 'create index' in statement_lower:
                        if 'if not exists' in statement_lower:
                            index_name = statement_lower.split('if not exists')[1].split('on')[0].strip()
                        else:
                            index_name = statement_lower.split('create index')[1].split('on')[0].strip()
                        print(f"  Creando indice: {index_name}...", end=" ")
                    
                    conn.execute(text(statement))
                    trans.commit()
                    
                    if 'create table' in statement_lower:
                        print("[OK]")
                        tablas_creadas += 1
                    elif 'create index' in statement_lower:
                        print("[OK]")
                        indices_creados += 1
                        
                except Exception as e:
                    trans.rollback()
                    error_msg = str(e).lower()
                    if "already exists" in error_msg or "duplicate" in error_msg:
                        print("[YA EXISTE]")
                    else:
                        print("[ERROR]")
                        print(f"      {str(e)[:150]}")
        
        print("\n" + "="*60)
        print("MIGRACION COMPLETADA")
        print("="*60)
        
        # Verificar tablas creadas
        print("\nVerificando tablas en la base de datos...")
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public' 
            AND (table_name LIKE 'torneo%' OR table_name LIKE '%torneo%')
            ORDER BY table_name
        """)).fetchall()
        
        print(f"\nTablas de torneos encontradas: {len(result)}")
        for r in result:
            print(f"  - {r[0]}")
        
        conn.close()
        
        if len(result) > 0:
            print("\n[OK] Puedes continuar con la implementacion de servicios")
            print("     Siguiente paso: Implementar torneo_service.py")
            return True
        else:
            print("\n[ADVERTENCIA] No se encontraron tablas de torneos")
            return False
        
    except FileNotFoundError:
        print("\n[ERROR] No se encontro el archivo 'crear_tablas_torneos.sql'")
        print("        Asegurate de ejecutar este script desde el directorio backend/")
        return False
    
    except Exception as e:
        if 'trans' in locals():
            trans.rollback()
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    success = crear_tablas_torneos()
    sys.exit(0 if success else 1)
