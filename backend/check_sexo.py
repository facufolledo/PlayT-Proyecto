from src.database.config import get_db
from src.models.Drive+_models import Usuario

db = next(get_db())
usuarios = db.query(Usuario.sexo).limit(10).all()
print("Valores de sexo en la BD:")
for u in usuarios:
    print(f"  - '{u.sexo}'")
