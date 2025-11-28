"""
Script para verificar que las tablas de torneos se crearon correctamente
PostgreSQL / Neon
"""
from src.database.config import engine
from sqlalchemy import text

def verificar_tablas_torneos():
    """Verifica que todas las tablas de torneos existan"""
    
    tablas_esperadas = [
        'organizadores_autorizados',
        'torneos',
        'torneos_organizadores',
        'torneos_parejas',
        'torneo_zonas',
        'torneo_zona_parejas',
        'torneo_canchas',
        'torneo_slots',
        'torneo_bloqueos_jugador',
        'torneo_partidos',
        'torneo_partido_sets',
        'torneo_tabla_posiciones',
        'torneo_historial_cambios'
    ]
    
    try:
        conn = engine.connect()
        
        print("\n" + "="*60)
        print("🔍 VERIFICACIÓN DE TABLAS DE TORNEOS")
        print("="*60)
        print()
        
        tablas_existentes = []
        tablas_faltantes = []
        
        for tabla in tablas_esperadas:
            result = conn.execute(text(f"""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = '{tabla}'
            """))
            
            existe = result.fetchone()[0] > 0
            
            if existe:
                # Obtener cantidad de columnas
                result_cols = conn.execute(text(f"""
                    SELECT COUNT(*) 
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = '{tabla}'
                """))
                num_columnas = result_cols.fetchone()[0]
                
                tablas_existentes.append((tabla, num_columnas))
                print(f"  ✅ {tabla:<35} ({num_columnas} columnas)")
            else:
                tablas_faltantes.append(tabla)
                print(f"  ❌ {tabla:<35} (NO EXISTE)")
        
        print()
        print("="*60)
        print(f"✅ Tablas existentes: {len(tablas_existentes)}/{len(tablas_esperadas)}")
        
        if tablas_faltantes:
            print(f"❌ Tablas faltantes: {len(tablas_faltantes)}")
            print()
            print("Tablas que faltan:")
            for tabla in tablas_faltantes:
                print(f"  • {tabla}")
            print()
            print("Ejecuta: python ejecutar_tablas_torneos.py")
        else:
            print()
            print("🎉 ¡Todas las tablas de torneos están creadas correctamente!")
            print()
            print("Estructura completa:")
            print()
            print("📋 Gestión de Torneos:")
            print("  • organizadores_autorizados")
            print("  • torneos")
            print("  • torneos_organizadores")
            print()
            print("👥 Parejas e Inscripciones:")
            print("  • torneos_parejas")
            print()
            print("🏆 Zonas y Clasificación:")
            print("  • torneo_zonas")
            print("  • torneo_zona_parejas")
            print("  • torneo_tabla_posiciones")
            print()
            print("🎾 Partidos y Resultados:")
            print("  • torneo_partidos")
            print("  • torneo_partido_sets")
            print()
            print("📅 Programación:")
            print("  • torneo_canchas")
            print("  • torneo_slots")
            print("  • torneo_bloqueos_jugador")
            print()
            print("📝 Auditoría:")
            print("  • torneo_historial_cambios")
        
        print("="*60)
        print()
        
        conn.close()
        
        return len(tablas_faltantes) == 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    verificar_tablas_torneos()
