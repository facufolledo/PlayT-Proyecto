# SOLUCIÓN CORS - Agregar a main.py

from fastapi.middleware.cors import CORSMiddleware

# VERIFICAR que en main.py esté exactamente así:
origins = [
    "http://localhost:3000",
    "http://localhost:5173",  # ← ESTE DEBE ESTAR (Vite dev server)
    "https://kioskito.click",
    "https://www.kioskito.click"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Si sigue fallando, usar temporalmente:
# allow_origins=["*"]  # SOLO PARA TESTING, NO PARA PRODUCCIÓN

print("✅ CORS configurado correctamente")
print(f"Orígenes permitidos: {origins}")