"""
Script para configurar pago en el torneo 9
"""
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    conn.execute(text("""
        UPDATE torneos 
        SET requiere_pago = true,
            monto_inscripcion = 5000,
            alias_cbu_cvu = 'ffolledo.nx',
            titular_cuenta = 'Facundo Folledo',
            banco = 'Mercado Pago'
        WHERE id = 9
    """))
    conn.commit()
    
    print("✅ Torneo 9 configurado con sistema de pagos:")
    print("   - Monto: $5000")
    print("   - Alias: ffolledo.nx")
    print("   - Titular: Facundo Folledo")
    print("   - Banco: Mercado Pago")
    print("\nAhora al inscribirse aparecerá el modal de pago")
