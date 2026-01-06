#!/usr/bin/env python3
"""
Script para crear la tabla topsemanal y agregar datos de ejemplo
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Agregar el directorio src al path
sys.path.append(str(Path(__file__).parent / "src"))

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, ForeignKey, Text, BigInteger
from sqlalchemy.orm import sessionmaker
from src.database.config import engine
from src.models.Drive+_models import Usuario

def create_topsemanal_table():
    """Crear la tabla topsemanal"""
    
    metadata = MetaData()
    
    # Definir la tabla topsemanal
    topsemanal = Table(
        'topsemanal',
        metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('id_usuario', BigInteger, ForeignKey('usuarios.id_usuario'), nullable=False),
        Column('nombre', String(100), nullable=False),
        Column('ciudad', String(100)),
        Column('puntos', Integer, nullable=False),
        Column('imagen_url', Text),  # URL de la imagen del usuario
        Column('posicion', Integer, nullable=False),
        Column('fecha_semana', DateTime, nullable=False),  # Fecha de inicio de la semana
        Column('created_at', DateTime, default=datetime.utcnow),
        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    )
    
    try:
        # Crear la tabla
        metadata.create_all(engine)
        print("✅ Tabla topsemanal creada exitosamente")
        
        # Insertar datos de ejemplo
        insert_sample_data()
        
    except Exception as e:
        print(f"❌ Error al crear la tabla: {e}")

def insert_sample_data():
    """Insertar datos de ejemplo en la tabla topsemanal"""
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Obtener usuarios existentes
        usuarios = session.query(Usuario).limit(10).all()
        
        if not usuarios:
            print("⚠️ No hay usuarios en la base de datos para crear el ranking semanal")
            return
        
        # Fecha de inicio de la semana actual
        fecha_semana = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_semana = fecha_semana - timedelta(days=fecha_semana.weekday())
        
        # Datos de ejemplo para el ranking semanal
        sample_data = [
            {
                'id_usuario': usuarios[0].id_usuario if len(usuarios) > 0 else 1,
                'nombre': 'Alejandro Martín',
                'ciudad': 'Madrid',
                'puntos': 1850,
                'imagen_url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face',
                'posicion': 1
            },
            {
                'id_usuario': usuarios[1].id_usuario if len(usuarios) > 1 else 2,
                'nombre': 'Isabel Garcia',
                'ciudad': 'Barcelona',
                'puntos': 1820,
                'imagen_url': 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face',
                'posicion': 2
            },
            {
                'id_usuario': usuarios[2].id_usuario if len(usuarios) > 2 else 3,
                'nombre': 'Miguel Rodriguez',
                'ciudad': 'Valencia',
                'puntos': 1790,
                'imagen_url': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face',
                'posicion': 3
            },
            {
                'id_usuario': usuarios[3].id_usuario if len(usuarios) > 3 else 4,
                'nombre': 'Carmen López',
                'ciudad': 'Sevilla',
                'puntos': 1760,
                'imagen_url': 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face',
                'posicion': 4
            },
            {
                'id_usuario': usuarios[4].id_usuario if len(usuarios) > 4 else 5,
                'nombre': 'David Fernández',
                'ciudad': 'Madrid',
                'puntos': 1745,
                'imagen_url': 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face',
                'posicion': 5
            }
        ]
        
        # Insertar datos
        for data in sample_data:
            # Verificar si ya existe un registro para esta semana y usuario
            existing = session.execute(
                "SELECT id FROM topsemanal WHERE id_usuario = :id_usuario AND fecha_semana = :fecha_semana",
                {'id_usuario': data['id_usuario'], 'fecha_semana': fecha_semana}
            ).fetchone()
            
            if not existing:
                session.execute(
                    """INSERT INTO topsemanal 
                       (id_usuario, nombre, ciudad, puntos, imagen_url, posicion, fecha_semana) 
                       VALUES (:id_usuario, :nombre, :ciudad, :puntos, :imagen_url, :posicion, :fecha_semana)""",
                    {
                        'id_usuario': data['id_usuario'],
                        'nombre': data['nombre'],
                        'ciudad': data['ciudad'],
                        'puntos': data['puntos'],
                        'imagen_url': data['imagen_url'],
                        'posicion': data['posicion'],
                        'fecha_semana': fecha_semana
                    }
                )
        
        session.commit()
        print("✅ Datos de ejemplo insertados en topsemanal")
        print(f"📅 Semana: {fecha_semana.strftime('%d/%m/%Y')}")
        
    except Exception as e:
        print(f"❌ Error al insertar datos: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    print("🚀 Creando tabla topsemanal...")
    create_topsemanal_table()
