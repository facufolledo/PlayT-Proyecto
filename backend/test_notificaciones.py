"""
Script de prueba para el sistema de notificaciones
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.config import SessionLocal
from src.models.Drive+_models import Usuario
from src.services.notification_service import NotificationService

def test_notificaciones():
    """Probar el sistema de notificaciones"""
    db = SessionLocal()
    
    try:
        print("\n=== TEST DE NOTIFICACIONES ===\n")
        
        # 1. Verificar que la columna fcm_token existe
        print("1. Verificando columna fcm_token...")
        usuarios = db.query(Usuario).limit(5).all()
        
        for usuario in usuarios:
            print(f"   - {usuario.nombre_usuario}: fcm_token = {usuario.fcm_token or 'No configurado'}")
        
        print("   ✓ Columna fcm_token disponible\n")
        
        # 2. Simular cambios de Elo
        print("2. Simulando envío de notificaciones...")
        
        # Obtener 4 usuarios para simular un partido
        usuarios_partido = db.query(Usuario).limit(4).all()
        
        if len(usuarios_partido) < 4:
            print("   ⚠ No hay suficientes usuarios para la prueba")
            return
        
        # Simular cambios de Elo
        cambios_elo = {}
        for i, usuario in enumerate(usuarios_partido):
            cambio = 15 if i < 2 else -15  # Primeros 2 ganan, últimos 2 pierden
            cambios_elo[usuario.id_usuario] = {
                'cambio': cambio,
                'nuevo': usuario.rating + cambio,
                'anterior': usuario.rating
            }
            print(f"   - {usuario.nombre_usuario}: {'+' if cambio > 0 else ''}{cambio} puntos")
        
        # Intentar enviar notificaciones
        ids_usuarios = [u.id_usuario for u in usuarios_partido]
        resultado = NotificationService.enviar_notificacion_elo_actualizado(
            usuarios=ids_usuarios,
            cambios_elo=cambios_elo,
            db=db
        )
        
        print(f"\n   Resultado del envío:")
        print(f"   - Success: {resultado.get('success')}")
        print(f"   - Mensajes enviados: {resultado.get('mensajes_enviados', 0)}")
        
        if resultado.get('errores'):
            print(f"   - Errores: {len(resultado.get('errores', []))}")
            for error in resultado.get('errores', [])[:3]:  # Mostrar solo los primeros 3
                print(f"     • {error}")
        
        if resultado.get('mensajes_enviados', 0) == 0:
            print("\n   ℹ Nota: No se enviaron notificaciones porque los usuarios no tienen")
            print("     tokens FCM configurados. Esto es normal si no has configurado")
            print("     Firebase en el frontend aún.")
        else:
            print("\n   ✓ Notificaciones enviadas exitosamente")
        
        print("\n=== TEST COMPLETADO ===\n")
        
    except Exception as e:
        print(f"\n✗ Error en el test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_notificaciones()
