"""
Script para crear un torneo de prueba completo con todas las características
"""
import requests
import json
from datetime import datetime, timedelta
import random

# Configuración
BACKEND_URL = "https://drive-plus-production.up.railway.app"

# IDs de usuarios a excluir (para que te inscribas manualmente)
USUARIOS_EXCLUIDOS = [14, 15]

def obtener_usuarios():
    """Obtener todos los usuarios de la base de datos usando múltiples búsquedas"""
    try:
        todos_usuarios = {}
        
        # Términos de búsqueda basados en nombres comunes
        terminos = [
            'fac', 'san', 'die', 'mag', 'cas', 'nac', 'rom', 'fol', 
            'lib', 'oct', 'dem', 'luc', 'oca', 'mar', 'jua', 'ped',
            'car', 'lui', 'fer', 'ale', 'gab', 'mat', 'nic', 'tom'
        ]
        
        print(f"   Buscando con {len(terminos)} términos...")
        
        for termino in terminos:
            url = f"{BACKEND_URL}/usuarios/buscar-publico?q={termino}&limit=100"
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    usuarios = response.json()
                    for u in usuarios:
                        uid = u.get('id_usuario')
                        if uid and uid not in USUARIOS_EXCLUIDOS:
                            todos_usuarios[uid] = u
            except:
                pass
        
        usuarios_lista = list(todos_usuarios.values())
        print(f"✅ Encontrados {len(usuarios_lista)} usuarios únicos (excluyendo IDs {USUARIOS_EXCLUIDOS})")
        
        # Mostrar info de debug
        response = requests.get(f"{BACKEND_URL}/usuarios/debug-busqueda", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   (Total en BD: {data.get('total_usuarios', 0)} usuarios, {data.get('total_perfiles', 0)} perfiles)")
        
        return usuarios_lista
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def crear_torneo():
    """Crear el torneo con todas las características"""
    
    # Fechas: del jueves al domingo próximo
    hoy = datetime.now()
    # Encontrar el próximo jueves
    dias_hasta_jueves = (3 - hoy.weekday()) % 7
    if dias_hasta_jueves == 0 and hoy.hour >= 12:
        dias_hasta_jueves = 7
    fecha_inicio = hoy + timedelta(days=dias_hasta_jueves)
    fecha_fin = fecha_inicio + timedelta(days=3)  # Jueves a Domingo
    
    torneo_data = {
        "nombre": "Torneo Test Completo - Drive+",
        "descripcion": "Torneo de prueba con todas las características: múltiples categorías, horarios, canchas, pagos por transferencia",
        "fecha_inicio": fecha_inicio.strftime("%Y-%m-%d"),
        "fecha_fin": fecha_fin.strftime("%Y-%m-%d"),
        "lugar": "Club de Prueba - Drive+",
        "formato": "grupos_playoffs",
        "genero": "mixto",
        "categoria": "8va",  # Categoría principal
        "precio_inscripcion": 5000,
        "metodo_pago": "transferencia",
        "alias_transferencia": "DRIVEPLUS.TEST",
        "horarios_disponibles": {
            "semana": [
                {"desde": "12:00", "hasta": "23:00"}
            ],
            "finDeSemana": [
                {"desde": "09:00", "hasta": "23:00"}
            ]
        },
        "duracion_partido": 60,  # minutos
        "descanso_entre_partidos": 15  # minutos
    }
    
    print("\n📋 Datos del torneo:")
    print(json.dumps(torneo_data, indent=2, ensure_ascii=False))
    
    try:
        # Nota: Este endpoint requiere autenticación
        # Deberás crear el torneo manualmente desde la UI o agregar el token
        print("\n⚠️ Para crear el torneo, usa estos datos en la UI de Drive+")
        print("   O ejecuta este script con un token de autenticación válido")
        return torneo_data
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def generar_franjas_horarias_jugadores(usuarios):
    """
    Generar franjas horarias variadas para los jugadores
    Esto simula diferentes disponibilidades
    """
    
    franjas_posibles = [
        # Jugadores que solo pueden de tarde (después del trabajo)
        {
            "nombre": "Solo tardes",
            "semana": [{"desde": "18:00", "hasta": "23:00"}],
            "finDeSemana": [{"desde": "09:00", "hasta": "23:00"}]
        },
        # Jugadores que pueden todo el día los fines de semana
        {
            "nombre": "Fines de semana completos",
            "semana": [{"desde": "20:00", "hasta": "23:00"}],
            "finDeSemana": [{"desde": "09:00", "hasta": "23:00"}]
        },
        # Jugadores con horario flexible
        {
            "nombre": "Horario flexible",
            "semana": [{"desde": "12:00", "hasta": "23:00"}],
            "finDeSemana": [{"desde": "09:00", "hasta": "23:00"}]
        },
        # Jugadores que solo pueden mañanas de finde
        {
            "nombre": "Mañanas de finde",
            "semana": [{"desde": "20:00", "hasta": "23:00"}],
            "finDeSemana": [{"desde": "09:00", "hasta": "14:00"}]
        },
        # Jugadores que solo pueden tardes de finde
        {
            "nombre": "Tardes de finde",
            "semana": [{"desde": "19:00", "hasta": "23:00"}],
            "finDeSemana": [{"desde": "15:00", "hasta": "23:00"}]
        },
        # Jugadores nocturnos
        {
            "nombre": "Nocturnos",
            "semana": [{"desde": "21:00", "hasta": "23:00"}],
            "finDeSemana": [{"desde": "20:00", "hasta": "23:00"}]
        }
    ]
    
    asignaciones = []
    for i, usuario in enumerate(usuarios):
        franja = franjas_posibles[i % len(franjas_posibles)]
        asignaciones.append({
            "usuario_id": usuario['id_usuario'],
            "nombre": f"{usuario.get('nombre', '')} {usuario.get('apellido', '')}",
            "username": usuario.get('nombre_usuario', ''),
            "franja_tipo": franja['nombre'],
            "horarios": {
                "semana": franja['semana'],
                "finDeSemana": franja['finDeSemana']
            }
        })
    
    return asignaciones

def main():
    print("=" * 60)
    print("🏆 CREADOR DE TORNEO DE PRUEBA - DRIVE+")
    print("=" * 60)
    
    # 1. Obtener usuarios
    print("\n1️⃣ Obteniendo usuarios...")
    usuarios = obtener_usuarios()
    
    if not usuarios:
        print("❌ No se encontraron usuarios. Verifica la conexión al backend.")
        return
    
    # 2. Crear datos del torneo
    print("\n2️⃣ Preparando datos del torneo...")
    torneo_data = crear_torneo()
    
    # 3. Generar franjas horarias para jugadores
    print("\n3️⃣ Generando franjas horarias para jugadores...")
    franjas = generar_franjas_horarias_jugadores(usuarios)
    
    # 4. Mostrar resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DEL TORNEO")
    print("=" * 60)
    
    print(f"""
🏆 TORNEO: {torneo_data['nombre']}
📅 Fechas: {torneo_data['fecha_inicio']} al {torneo_data['fecha_fin']}
📍 Lugar: {torneo_data['lugar']}
💰 Precio: ${torneo_data['precio_inscripcion']}
💳 Pago: Transferencia a {torneo_data['alias_transferencia']}

⏰ HORARIOS DEL TORNEO:
   • Lun-Vie: 12:00 - 23:00
   • Sáb-Dom: 09:00 - 23:00

🎾 CATEGORÍAS A CREAR:
   1. 8va Masculino
   2. 6ta Femenino

🏟️ CANCHAS A CREAR:
   1. Cancha 1
   2. Cancha 2
   3. Cancha 3

👥 JUGADORES: {len(usuarios)} (excluyendo IDs {USUARIOS_EXCLUIDOS})
""")
    
    print("\n" + "=" * 60)
    print("📋 FRANJAS HORARIAS POR JUGADOR")
    print("=" * 60)
    
    # Agrupar por tipo de franja
    por_tipo = {}
    for f in franjas:
        tipo = f['franja_tipo']
        if tipo not in por_tipo:
            por_tipo[tipo] = []
        por_tipo[tipo].append(f)
    
    for tipo, jugadores in por_tipo.items():
        print(f"\n🕐 {tipo}:")
        horarios = jugadores[0]['horarios']
        print(f"   Semana: {horarios['semana'][0]['desde']} - {horarios['semana'][0]['hasta']}")
        print(f"   Finde:  {horarios['finDeSemana'][0]['desde']} - {horarios['finDeSemana'][0]['hasta']}")
        print(f"   Jugadores ({len(jugadores)}):")
        for j in jugadores[:5]:  # Mostrar solo los primeros 5
            print(f"      - {j['nombre']} (@{j['username']})")
        if len(jugadores) > 5:
            print(f"      ... y {len(jugadores) - 5} más")
    
    print("\n" + "=" * 60)
    print("📝 INSTRUCCIONES PARA CREAR EL TORNEO")
    print("=" * 60)
    print("""
1. Ve a Drive+ → Torneos → Crear Torneo

2. Completa los datos:
   • Nombre: Torneo Test Completo - Drive+
   • Fechas: Del próximo jueves al domingo
   • Lugar: Club de Prueba - Drive+
   • Formato: Grupos + Playoffs
   • Precio: $5000
   • Método de pago: Transferencia
   • Alias: DRIVEPLUS.TEST

3. Configura horarios:
   • Lun-Vie: 12:00 - 23:00
   • Sáb-Dom: 09:00 - 23:00

4. Agrega categorías:
   • 8va Masculino
   • 6ta Femenino

5. Agrega canchas:
   • Cancha 1
   • Cancha 2
   • Cancha 3

6. Inscribe las parejas manualmente o usa el script de inscripción
""")
    
    # Guardar datos para uso posterior
    output = {
        "torneo": torneo_data,
        "usuarios": [{"id": u['id_usuario'], "nombre": f"{u.get('nombre', '')} {u.get('apellido', '')}"} for u in usuarios],
        "franjas_horarias": franjas
    }
    
    with open("DrivePlus/torneo_prueba_datos.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print("\n✅ Datos guardados en: DrivePlus/torneo_prueba_datos.json")

if __name__ == "__main__":
    main()
