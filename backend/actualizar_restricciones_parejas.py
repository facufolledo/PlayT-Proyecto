"""
Script para actualizar restricciones horarias de parejas ya inscritas
Busca parejas por nombres de jugadores en el torneo 25
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from src.database.config import get_db
from src.models.torneo_models import TorneoPareja
from src.models.driveplus_models import Usuario, PerfilUsuario

TORNEO_ID = 25  # ID del torneo

def normalizar_nombre(nombre):
    """Normaliza un nombre para comparación (minúsculas, sin acentos)"""
    import unicodedata
    nombre = nombre.lower().strip()
    # Remover acentos
    nombre = ''.join(
        c for c in unicodedata.normalize('NFD', nombre)
        if unicodedata.category(c) != 'Mn'
    )
    return nombre

def buscar_pareja_por_nombres(db, nombre1, apellido1, nombre2, apellido2):
    """Busca una pareja en el torneo por nombres de jugadores"""
    
    # Normalizar nombres para búsqueda
    n1 = normalizar_nombre(nombre1)
    a1 = normalizar_nombre(apellido1)
    n2 = normalizar_nombre(nombre2)
    a2 = normalizar_nombre(apellido2)
    
    # Obtener todas las parejas del torneo
    parejas = db.query(TorneoPareja).filter(
        TorneoPareja.torneo_id == TORNEO_ID,
        TorneoPareja.estado.in_(['inscripta', 'confirmada'])
    ).all()
    
    for pareja in parejas:
        # Obtener perfiles
        p1 = db.query(PerfilUsuario).filter(
            PerfilUsuario.id_usuario == pareja.jugador1_id
        ).first()
        p2 = db.query(PerfilUsuario).filter(
            PerfilUsuario.id_usuario == pareja.jugador2_id
        ).first()
        
        if not p1 or not p2:
            continue
        
        # Normalizar nombres de la pareja
        pn1 = normalizar_nombre(p1.nombre)
        pa1 = normalizar_nombre(p1.apellido)
        pn2 = normalizar_nombre(p2.nombre)
        pa2 = normalizar_nombre(p2.apellido)
        
        # Verificar coincidencia (en cualquier orden)
        if ((pn1 == n1 and pa1 == a1 and pn2 == n2 and pa2 == a2) or
            (pn1 == n2 and pa1 == a2 and pn2 == n1 and pa2 == a1)):
            return pareja, p1, p2
    
    return None, None, None

def actualizar_restricciones():
    """Actualiza restricciones horarias de parejas específicas"""
    
    db = next(get_db())
    
    try:
        print("=" * 80)
        print(f"ACTUALIZAR RESTRICCIONES HORARIAS - Torneo {TORNEO_ID}")
        print("=" * 80)
        
        # Lista de parejas con sus restricciones
        # Formato: (nombre1, apellido1, nombre2, apellido2, [restricciones])
        parejas_restricciones = [
            # Juan Martin Rovira y Marcelo Rearte - Viernes 09:00 a 22:00 (YA ACTUALIZADA)
            # ("juan martin", "rovira", "marcelo", "rearte", [
            #     {"dias": ["viernes"], "horaInicio": "09:00", "horaFin": "22:00"}
            # ]),
            
            # Valentina Videla y Nazarena Juarez - Viernes 09:00 a 22:00
            ("valentina", "videla", "nazarena", "juarez", [
                {"dias": ["viernes"], "horaInicio": "09:00", "horaFin": "22:00"}
            ]),
            
            # Axel Nieto y Jere Zalazar - NO ENCONTRADOS (no están en el torneo)
            
            # Sebastian Bestani y Carlos Gavio Gomez - Viernes 09:00 a 16:00
            ("sebastian", "bestani", "carlos", "gavio gomez", [
                {"dias": ["viernes"], "horaInicio": "09:00", "horaFin": "16:00"}
            ]),
            
            # Sofía Salomón y Esther Reyes - Viernes 09:00 a 22:30
            ("sofia", "salomon", "esther", "reyes", [
                {"dias": ["viernes"], "horaInicio": "09:00", "horaFin": "22:30"}
            ]),
            
            # Magali Ocaña y Mariana Serena Figueras - Viernes 09:00 a 21:30 y Sábado 09:00 a 16:00
            ("magali", "ocaña", "mariana serena", "figueras", [
                {"dias": ["viernes"], "horaInicio": "09:00", "horaFin": "21:30"},
                {"dias": ["sabado"], "horaInicio": "09:00", "horaFin": "16:00"}
            ]),
        ]
        
        print(f"\n📋 Parejas a buscar y actualizar: {len(parejas_restricciones)}")
        
        actualizadas = 0
        no_encontradas = 0
        errores = 0
        
        for nombre1, apellido1, nombre2, apellido2, restricciones in parejas_restricciones:
            try:
                print(f"\n🔍 Buscando: {nombre1.title()} {apellido1.title()} / {nombre2.title()} {apellido2.title()}")
                
                pareja, p1, p2 = buscar_pareja_por_nombres(db, nombre1, apellido1, nombre2, apellido2)
                
                if not pareja:
                    print(f"   ❌ NO ENCONTRADA en el torneo {TORNEO_ID}")
                    no_encontradas += 1
                    continue
                
                nombre_j1 = f"{p1.nombre} {p1.apellido}"
                nombre_j2 = f"{p2.nombre} {p2.apellido}"
                
                print(f"   ✅ ENCONTRADA - Pareja ID: {pareja.id}")
                print(f"      Jugadores: {nombre_j1} / {nombre_j2}")
                print(f"      Estado: {pareja.estado}")
                print(f"      Restricciones anteriores: {pareja.disponibilidad_horaria}")
                
                # Actualizar restricciones
                pareja.disponibilidad_horaria = restricciones
                
                print(f"      Nuevas restricciones:")
                for r in restricciones:
                    dias_str = ", ".join([d.title() for d in r["dias"]])
                    print(f"         🚫 {dias_str}: {r['horaInicio']} - {r['horaFin']}")
                
                actualizadas += 1
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                errores += 1
        
        # Resumen y confirmación
        print(f"\n{'=' * 80}")
        print(f"📊 RESUMEN:")
        print(f"   ✅ Encontradas y actualizadas: {actualizadas}")
        print(f"   ❓ No encontradas: {no_encontradas}")
        print(f"   ❌ Errores: {errores}")
        print(f"{'=' * 80}")
        
        if actualizadas > 0:
            confirmar = input("\n¿Confirmar cambios en la base de datos? (si/no): ").strip().lower()
            
            if confirmar == 'si':
                db.commit()
                print("\n✅ Cambios guardados exitosamente en la base de datos")
            else:
                db.rollback()
                print("\n❌ Cambios descartados")
        else:
            print("\n⚠️  No se actualizó ninguna pareja")
        
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    actualizar_restricciones()
