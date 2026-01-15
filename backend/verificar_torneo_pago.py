"""
Script para verificar configuración de pago del torneo 9
"""
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT id, nombre, requiere_pago, monto_inscripcion, 
               alias_cbu_cvu, titular_cuenta, banco
        FROM torneos 
        WHERE id = 9
    """))
    
    torneo = result.fetchone()
    
    if torneo:
        print(f"\n{'='*60}")
        print(f"Torneo: {torneo[1]} (ID: {torneo[0]})")
        print(f"{'='*60}")
        print(f"Requiere pago: {torneo[2]}")
        print(f"Monto: ${torneo[3] if torneo[3] else 'No configurado'}")
        print(f"Alias/CBU/CVU: {torneo[4] if torneo[4] else 'No configurado'}")
        print(f"Titular: {torneo[5] if torneo[5] else 'No configurado'}")
        print(f"Banco: {torneo[6] if torneo[6] else 'No configurado'}")
        print(f"{'='*60}\n")
        
        if not torneo[2]:
            print("⚠️  El torneo NO requiere pago")
            print("Para habilitar pagos, ejecutá:")
            print(f"  UPDATE torneos SET requiere_pago = true, monto_inscripcion = 5000,")
            print(f"    alias_cbu_cvu = 'tu.alias', titular_cuenta = 'Tu Nombre',")
            print(f"    banco = 'Banco' WHERE id = 9;")
    else:
        print("Torneo 9 no encontrado")
