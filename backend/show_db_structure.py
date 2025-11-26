#!/usr/bin/env python3
"""
Script para mostrar la estructura completa de la base de datos PlayT
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.schema import MetaData

# Cargar variables de entorno
load_dotenv()

def show_database_structure():
    """Mostrar la estructura completa de la base de datos"""
    
    # Obtener URL de la base de datos
    database_url = os.getenv("DATABASE_URL", "postgresql+pg8000://neondb_owner:npg_i2uqcNEZbk4M@ep-dawn-frost-ac67h4ke-pooler.sa-east-1.aws.neon.tech/neondb")
    
    print("🔍 Conectando a la base de datos...")
    print(f"📡 URL: {database_url}")
    print("=" * 80)
    
    try:
        # Crear engine
        engine = create_engine(database_url)
        
        # Crear inspector
        inspector = inspect(engine)
        
        # Obtener todas las tablas
        tables = inspector.get_table_names()
        
        print(f"📊 Total de tablas encontradas: {len(tables)}")
        print("=" * 80)
        
        if not tables:
            print("❌ No se encontraron tablas en la base de datos")
            return
        
        # Mostrar información de cada tabla
        for table_name in tables:
            print(f"\n📋 TABLA: {table_name}")
            print("-" * 50)
            
            # Obtener columnas
            columns = inspector.get_columns(table_name)
            print(f"Columnas ({len(columns)}):")
            
            for column in columns:
                nullable = "NULL" if column['nullable'] else "NOT NULL"
                default = f" DEFAULT {column['default']}" if column['default'] else ""
                print(f"  • {column['name']}: {column['type']} {nullable}{default}")
            
            # Obtener índices
            indexes = inspector.get_indexes(table_name)
            if indexes:
                print(f"\nÍndices ({len(indexes)}):")
                for index in indexes:
                    print(f"  • {index['name']}: {', '.join(index['column_names'])}")
            
            # Obtener claves foráneas
            foreign_keys = inspector.get_foreign_keys(table_name)
            if foreign_keys:
                print(f"\nClaves foráneas ({len(foreign_keys)}):")
                for fk in foreign_keys:
                    print(f"  • {', '.join(fk['constrained_columns'])} → {fk['referred_table']}.{', '.join(fk['referred_columns'])}")
            
            # Obtener claves primarias
            primary_keys = inspector.get_pk_constraint(table_name)
            if primary_keys['constrained_columns']:
                print(f"\nClave primaria: {', '.join(primary_keys['constrained_columns'])}")
            
            print("-" * 50)
        
        # Mostrar información general de la base de datos
        print("\n" + "=" * 80)
        print("📊 INFORMACIÓN GENERAL DE LA BASE DE DATOS")
        print("=" * 80)
        
        with engine.connect() as conn:
            # Obtener versión de PostgreSQL
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"🐘 Versión PostgreSQL: {version}")
            
            # Obtener nombre de la base de datos
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print(f"🗄️ Base de datos actual: {db_name}")
            
            # Obtener usuario actual
            result = conn.execute(text("SELECT current_user"))
            user = result.fetchone()[0]
            print(f"👤 Usuario actual: {user}")
            
            # Obtener esquema actual
            result = conn.execute(text("SELECT current_schema()"))
            schema = result.fetchone()[0]
            print(f"📁 Esquema actual: {schema}")
        
        print("\n✅ Estructura de la base de datos mostrada exitosamente")
        
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        print(f"🔍 Detalles del error: {type(e).__name__}")

if __name__ == "__main__":
    show_database_structure()
