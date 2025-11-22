"""
Script para probar el guardado de resultado directamente en la BD
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import json

# Cargar variables de entorno
load_dotenv()

# Configurar base de datos
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def verificar_resultado_sala(id_sala: int = 18):
    """Verificar si la sala tiene resultado guardado"""
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print(f"VERIFICANDO RESULTADO DE SALA {id_sala}")
        print("=" * 60)
        
        # Obtener información de la sala y partido
        query = text("""
            SELECT 
                s.id_sala,
                s.nombre,
                s.estado,
                s.id_partido,
                p.resultado_padel,
                p.estado_confirmacion,
                p.ganador_equipo
            FROM salas s
            LEFT JOIN partidos p ON s.id_partido = p.id_partido
            WHERE s.id_sala = :id_sala
        """)
        
        result = db.execute(query, {"id_sala": id_sala})
        sala = result.fetchone()
        
        if not sala:
            print(f"\n❌ No se encontró la sala {id_sala}")
            return
        
        print(f"\n📊 Información de la sala:")
        print(f"   ID Sala: {sala.id_sala}")
        print(f"   Nombre: {sala.nombre}")
        print(f"   Estado: {sala.estado}")
        print(f"   ID Partido: {sala.id_partido}")
        
        if sala.id_partido:
            print(f"\n📊 Información del partido:")
            print(f"   Estado confirmación: {sala.estado_confirmacion}")
            print(f"   Ganador equipo: {sala.ganador_equipo}")
            
            if sala.resultado_padel:
                print(f"\n✅ RESULTADO GUARDADO:")
                resultado = sala.resultado_padel
                if isinstance(resultado, str):
                    resultado = json.loads(resultado)
                print(json.dumps(resultado, indent=2))
            else:
                print(f"\n❌ NO HAY RESULTADO GUARDADO")
        else:
            print(f"\n❌ La sala no tiene partido asociado")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        id_sala = int(sys.argv[1])
    else:
        id_sala = 18
    
    verificar_resultado_sala(id_sala)
