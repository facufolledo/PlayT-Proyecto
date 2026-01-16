"""
Test de la nueva lógica de disponibilidad
"""

# Simular la lógica
def verificar_disponibilidad(dia, hora_mins, disp):
    """
    Verifica si una pareja está disponible en un día/hora específico
    """
    if len(disp['dias_restringidos']) == 0:
        # Sin restricciones, disponible siempre
        return True
    elif dia in disp['dias_restringidos']:
        # Día con restricción, verificar si la hora está en algún rango
        return any(
            inicio <= hora_mins < fin 
            for inicio, fin in disp['rangos'].get(dia, [])
        )
    else:
        # Día sin restricción, disponible todo el día
        return True

# Caso de prueba
print("=" * 80)
print("TEST: NUEVA LÓGICA DE DISPONIBILIDAD")
print("=" * 80)

# Pareja 1: jueves y viernes de 18:00 a 22:00
disp1 = {
    'dias_restringidos': {'jueves', 'viernes'},
    'rangos': {
        'jueves': [(18*60, 22*60)],  # 1080-1320 minutos
        'viernes': [(18*60, 22*60)]
    }
}

# Pareja 2: viernes de 19:00 a 23:00
disp2 = {
    'dias_restringidos': {'viernes'},
    'rangos': {
        'viernes': [(19*60, 23*60)]  # 1140-1380 minutos
    }
}

print("\n📋 Pareja 1: jueves y viernes de 18:00 a 22:00")
print(f"   Días restringidos: {disp1['dias_restringidos']}")
print(f"   Rangos: {disp1['rangos']}")

print("\n📋 Pareja 2: viernes de 19:00 a 23:00")
print(f"   Días restringidos: {disp2['dias_restringidos']}")
print(f"   Rangos: {disp2['rangos']}")

# Probar diferentes slots
slots_prueba = [
    ('jueves', '12:00'),
    ('jueves', '18:00'),
    ('jueves', '19:30'),
    ('jueves', '21:00'),
    ('viernes', '12:00'),
    ('viernes', '18:00'),
    ('viernes', '19:30'),
    ('viernes', '21:00'),
    ('sabado', '12:00'),
    ('sabado', '19:00'),
    ('domingo', '15:00'),
]

print("\n" + "=" * 80)
print("PRUEBAS DE COMPATIBILIDAD")
print("=" * 80)

for dia, hora in slots_prueba:
    hora_mins = int(hora.split(':')[0]) * 60 + int(hora.split(':')[1])
    
    p1_disp = verificar_disponibilidad(dia, hora_mins, disp1)
    p2_disp = verificar_disponibilidad(dia, hora_mins, disp2)
    compatible = p1_disp and p2_disp
    
    status = "✅" if compatible else "❌"
    print(f"{status} {dia:10} {hora:5} | P1: {'✓' if p1_disp else '✗'}  P2: {'✓' if p2_disp else '✗'}  | {'COMPATIBLE' if compatible else 'NO COMPATIBLE'}")

print("\n" + "=" * 80)
print("RESUMEN")
print("=" * 80)
print("Según la nueva lógica:")
print("- Pareja 1 puede jugar:")
print("  • Jueves: 18:00-22:00")
print("  • Viernes: 18:00-22:00")
print("  • Sábado: TODO EL DÍA (no está restringido)")
print("  • Domingo: TODO EL DÍA (no está restringido)")
print("\n- Pareja 2 puede jugar:")
print("  • Viernes: 19:00-23:00")
print("  • Jueves: TODO EL DÍA (no está restringido)")
print("  • Sábado: TODO EL DÍA (no está restringido)")
print("  • Domingo: TODO EL DÍA (no está restringido)")
print("\n✅ Pueden jugar juntas:")
print("  • Viernes: 19:00-22:00 (intersección)")
print("  • Sábado: TODO EL DÍA")
print("  • Domingo: TODO EL DÍA")
