"""
Script para corregir current_user en torneo_controller.py
"""

# Leer el archivo
with open('src/controllers/torneo_controller.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar current_user: dict por current_user: Usuario
content = content.replace('current_user: dict = Depends(get_current_user)', 
                         'current_user: Usuario = Depends(get_current_user)')

# Reemplazar current_user.get("id_usuario") por current_user.id_usuario
content = content.replace('current_user.get("id_usuario")', 
                         'current_user.id_usuario')

# Guardar el archivo
with open('src/controllers/torneo_controller.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Archivo corregido exitosamente")
