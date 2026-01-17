#!/usr/bin/env python3
"""
Test script para verificar el sistema de restricciones en el torneo 22
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.config import get_db
from src.services.torneo_zona_horarios_service import TorneoZonaHorariosService
from src.services.torneo_fixture_global_service import TorneoFixtureGlobalService
from src.models.torneo_models import TorneoPareja

def test_sistema_restricciones():
    """Test del sistema de restricciones en torneo 22"""
    db = next(get_db())
    
    try:
        torneo_id = 22
        
        print(f"🧪 Probando sistema de RESTRICCIONES en torneo {torneo_id}...")
        
        # 1. Verificar parejas y sus restricciones
        print(f"\n📊 Analizando restricciones de parejas...")
        
        parejas = db.query(TorneoPareja).filter(
            TorneoPareja.torneo_id == torneo_id
        ).all()
        
        sin_restricciones = 0
        con_restricciones = 0
        tipos_restricciones = {}
        
        for pareja in parejas[:10]:  # Mostrar solo las primeras 10
            restricciones = pareja.disponibilidad_horaria or []
            
            if not restricciones:
                sin_restricciones += 1
                print(f"   ✅ Pareja {pareja.id}: Sin restricciones (disponible siempre)")
            else:
                con_restricciones += 1
                for restriccion in restricciones:
                    dia = restriccion.get('dia', 'unknown')
                    inicio = restriccion.get('inicio', 'unknown')
                    fin = restriccion.get('fin', 'unknown')
                    key = f"{dia} {inicio}-{fin}"
                    tipos_restricciones[key] = tipos_restricciones.get(key, 0) + 1
                    
                print(f"   🚫 Pareja {pareja.id}: {len(restricciones)} restricción(es)")
                for r in restricciones:
                    print(f"      - No puede {r['dia']} {r['inicio']}-{r['fin']}")
        
        total_parejas = len(parejas)
        print(f"\n📈 Estadísticas generales:")
        print(f"   👥 Total parejas: {total_parejas}")
        print(f"   ✅ Sin restricciones: {sin_restricciones} ({sin_restricciones/total_parejas*100:.1f}%)")
        print(f"   🚫 Con restricciones: {con_restricciones} ({con_restricciones/total_parejas*100:.1f}%)")
        
        print(f"\n🔍 Tipos de restricciones más comunes:")
        for tipo, count in sorted(tipos_restricciones.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   - {tipo}: {count} parejas")
        
        # 2. Probar generación de zonas inteligentes
        print(f"\n🎯 Probando generación de zonas inteligentes...")
        
        try:
            # Obtener primera categoría
            primera_categoria = parejas[0].categoria_id
            parejas_categoria = [p for p in parejas if p.categoria_id == primera_categoria]
            pareja_ids = [p.id for p in parejas_categoria]
            
            print(f"   📂 Categoría {primera_categoria}: {len(parejas_categoria)} parejas")
            
            # Generar zonas con compatibilidad horaria
            resultado_zonas = TorneoZonaHorariosService.generar_zonas_con_horarios(
                db, torneo_id, 1, categoria_id=primera_categoria
            )
            
            print(f"   ✅ Resultado: {resultado_zonas.get('message', 'Zonas generadas')}")
            zonas = resultado_zonas.get('zonas', [])
            
            print(f"   ✅ Zonas generadas: {len(zonas)}")
            
            # Analizar compatibilidad en cada zona
            for zona in zonas[:3]:  # Solo las primeras 3 zonas
                print(f"\n   🏆 {zona.nombre}:")
                
                # Obtener parejas de esta zona
                from src.models.torneo_models import TorneoZonaPareja
                asignaciones = db.query(TorneoZonaPareja).filter(
                    TorneoZonaPareja.zona_id == zona.id
                ).all()
                
                parejas_zona = []
                for asig in asignaciones:
                    pareja = db.query(TorneoPareja).filter(
                        TorneoPareja.id == asig.pareja_id
                    ).first()
                    if pareja:
                        parejas_zona.append(pareja)
                
                print(f"      👥 Parejas: {len(parejas_zona)}")
                
                # Analizar restricciones en la zona
                restricciones_zona = []
                for pareja in parejas_zona:
                    restricciones = pareja.disponibilidad_horaria or []
                    restricciones_zona.extend(restricciones)
                
                if not restricciones_zona:
                    print(f"      ✅ Zona sin restricciones (máxima flexibilidad)")
                else:
                    print(f"      🚫 Total restricciones en zona: {len(restricciones_zona)}")
                    
                    # Contar restricciones por día
                    por_dia = {}
                    for r in restricciones_zona:
                        dia = r.get('dia', 'unknown')
                        por_dia[dia] = por_dia.get(dia, 0) + 1
                    
                    for dia, count in por_dia.items():
                        print(f"         - {dia}: {count} restricciones")
        
        except Exception as e:
            print(f"   ❌ Error generando zonas: {e}")
        
        # 3. Probar fixture global con restricciones
        print(f"\n⚡ Probando fixture global con restricciones...")
        
        try:
            # Generar fixture considerando restricciones
            resultado = TorneoFixtureGlobalService.generar_fixture_completo(
                db, torneo_id, 1, categoria_id=primera_categoria
            )
            
            print(f"   ✅ Fixture generado:")
            print(f"      📅 Partidos programados: {resultado['partidos_programados']}")
            print(f"      ⚠️ Partidos no programados: {resultado['partidos_no_programados']}")
            print(f"      📊 Tasa de éxito: {resultado['partidos_programados']/(resultado['partidos_programados']+resultado['partidos_no_programados'])*100:.1f}%")
            
            if resultado['partidos_no_programados'] > 0:
                print(f"      🔍 Razones de no programación:")
                for razon, count in resultado.get('razones_no_programacion', {}).items():
                    print(f"         - {razon}: {count} partidos")
        
        except Exception as e:
            print(f"   ❌ Error generando fixture: {e}")
        
        print(f"\n✅ Test del sistema de restricciones completado")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_sistema_restricciones()