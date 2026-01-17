#!/usr/bin/env python3
"""
Test de optimización de salas - Verificar mejoras de performance
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_performance_salas():
    """Test básico de performance de salas"""
    print("🚀 TEST DE OPTIMIZACIÓN DE SALAS")
    print("=" * 50)
    
    try:
        from src.database.config import get_db
        from sqlalchemy import text
        
        db = next(get_db())
        
        # Test 1: Verificar conexión
        print("✅ Conexión a base de datos: OK")
        
        # Test 2: Contar salas
        start_time = time.time()
        result = db.execute(text("SELECT COUNT(*) FROM sala"))
        count = result.scalar()
        query_time = (time.time() - start_time) * 1000
        
        print(f"✅ Query básica salas: {query_time:.2f}ms ({count} salas)")
        
        # Test 3: Query compleja (similar a listar_salas)
        start_time = time.time()
        result = db.execute(text("""
            SELECT s.id_sala, s.nombre, s.estado, COUNT(sj.id_usuario) as jugadores
            FROM sala s
            LEFT JOIN sala_jugador sj ON s.id_sala = sj.id_sala
            WHERE s.estado IN ('esperando', 'activa', 'programada', 'en_juego')
            GROUP BY s.id_sala, s.nombre, s.estado
            ORDER BY s.creado_en DESC
            LIMIT 10
        """))
        
        salas = result.fetchall()
        query_time = (time.time() - start_time) * 1000
        
        print(f"✅ Query compleja salas: {query_time:.2f}ms ({len(salas)} salas)")
        
        # Test 4: Verificar índices existentes
        result = db.execute(text("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename IN ('sala', 'sala_jugador') 
            AND indexname LIKE 'idx_%'
        """))
        
        indices = [row[0] for row in result.fetchall()]
        print(f"✅ Índices encontrados: {len(indices)}")
        for idx in indices:
            print(f"   - {idx}")
        
        # Evaluación de performance
        if query_time < 100:
            print(f"\n🎉 PERFORMANCE: EXCELENTE (<100ms)")
        elif query_time < 500:
            print(f"\n✅ PERFORMANCE: BUENA (<500ms)")
        elif query_time < 1000:
            print(f"\n⚠️ PERFORMANCE: ACEPTABLE (<1s)")
        else:
            print(f"\n❌ PERFORMANCE: LENTA (>1s)")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()

def crear_indices_basicos():
    """Crear índices básicos si no existen"""
    print("\n🔧 CREANDO ÍNDICES BÁSICOS...")
    
    try:
        from src.database.config import get_db
        from sqlalchemy import text
        
        db = next(get_db())
        
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_sala_jugador_id_sala ON sala_jugador(id_sala)",
            "CREATE INDEX IF NOT EXISTS idx_sala_jugador_id_usuario ON sala_jugador(id_usuario)",
            "CREATE INDEX IF NOT EXISTS idx_sala_codigo_invitacion ON sala(codigo_invitacion)",
            "CREATE INDEX IF NOT EXISTS idx_sala_estado ON sala(estado)",
        ]
        
        for i, sql in enumerate(indices):
            try:
                db.execute(text(sql))
                print(f"   ✅ Índice {i+1}/{len(indices)} creado")
            except Exception as e:
                print(f"   ⚠️ Índice {i+1}/{len(indices)}: {e}")
        
        db.commit()
        print("✅ Índices básicos aplicados")
        db.close()
        
    except Exception as e:
        print(f"❌ Error creando índices: {e}")

if __name__ == "__main__":
    test_performance_salas()
    crear_indices_basicos()
    print("\n" + "=" * 50)
    print("🔄 Ejecutando test post-optimización...")
    test_performance_salas()