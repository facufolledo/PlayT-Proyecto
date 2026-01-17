"""
Verificar el torneo masivo ID 17
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.database.config import get_db
from sqlalchemy import text

def verificar_torneo_17():
    db = next(get_db())
    
    try:
        # Verificar torneo 17
        print('🔍 VERIFICANDO TORNEO 17...')
        result = db.execute(text('SELECT * FROM torneos WHERE id = 17')).fetchone()
        if result:
            print(f'✅ Torneo encontrado: {result.nombre}')
        else:
            print('❌ Torneo 17 no encontrado')
            return
        
        # Verificar categorías
        print('\n📊 CATEGORÍAS:')
        categorias = db.execute(text('SELECT * FROM torneo_categorias WHERE torneo_id = 17')).fetchall()
        for cat in categorias:
            print(f'   - {cat.nombre} (ID: {cat.id})')
        
        # Verificar parejas
        print('\n👥 PAREJAS:')
        parejas = db.execute(text('SELECT COUNT(*) as total FROM torneos_parejas WHERE torneo_id = 17')).fetchone()
        print(f'   Total parejas: {parejas.total}')
        
        if parejas.total > 0:
            # Parejas por categoría
            print('\n📋 PAREJAS POR CATEGORÍA:')
            por_categoria = db.execute(text('''
                SELECT tc.nombre, COUNT(tp.id) as parejas
                FROM torneo_categorias tc
                LEFT JOIN torneos_parejas tp ON tc.id = tp.categoria_id
                WHERE tc.torneo_id = 17
                GROUP BY tc.id, tc.nombre
                ORDER BY tc.id
            ''')).fetchall()
            
            for cat in por_categoria:
                print(f'   - {cat.nombre}: {cat.parejas} parejas')
            
            # Mostrar algunas parejas de ejemplo
            print('\n🔍 EJEMPLOS DE PAREJAS:')
            ejemplos = db.execute(text('''
                SELECT tp.id, tc.nombre as categoria, u1.nombre_usuario as j1, u2.nombre_usuario as j2, tp.estado
                FROM torneos_parejas tp
                JOIN torneo_categorias tc ON tp.categoria_id = tc.id
                JOIN usuarios u1 ON tp.jugador1_id = u1.id_usuario
                JOIN usuarios u2 ON tp.jugador2_id = u2.id_usuario
                WHERE tp.torneo_id = 17
                LIMIT 5
            ''')).fetchall()
            
            for ej in ejemplos:
                print(f'   - {ej.categoria}: {ej.j1} & {ej.j2} ({ej.estado})')
        else:
            print('❌ No se encontraron parejas para este torneo')
            
            # Verificar si hay usuarios creados
            print('\n🔍 VERIFICANDO USUARIOS CREADOS:')
            usuarios_nuevos = db.execute(text('''
                SELECT COUNT(*) as total 
                FROM usuarios 
                WHERE nombre_usuario LIKE '%_m%j%_%'
                AND creado_en > NOW() - INTERVAL '1 hour'
            ''')).fetchone()
            print(f'   Usuarios creados en la última hora: {usuarios_nuevos.total}')
            
            if usuarios_nuevos.total > 0:
                print('\n❓ Los usuarios se crearon pero las parejas no. Posible error en el script.')
            else:
                print('\n❓ No se crearon usuarios. El script falló antes de crear las parejas.')
    
    finally:
        db.close()

if __name__ == "__main__":
    verificar_torneo_17()