#!/usr/bin/env python3
"""
Script para corregir todas las importaciones de Drive+_models a driveplus_models
"""
import os
import re

def fix_imports_in_file(filepath):
    """Corrige las importaciones en un archivo"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Reemplazar Drive+_models con driveplus_models
        original_content = content
        content = content.replace('Drive+_models', 'driveplus_models')
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed: {filepath}")
            return True
        else:
            return False
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")
        return False

def main():
    """Función principal"""
    backend_dir = "backend"
    fixed_count = 0
    
    # Buscar todos los archivos .py en backend
    for root, dirs, files in os.walk(backend_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if fix_imports_in_file(filepath):
                    fixed_count += 1
    
    print(f"\n🎉 Proceso completado. {fixed_count} archivos corregidos.")

if __name__ == "__main__":
    main()