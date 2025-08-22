# PlayT-Proyecto
es una aplicación de pádel (webapp, app móvil y PWA) que permite a los jugadores crear partidos, reportar resultados y mantener un sistema de ranking dinámico basado en el algoritmo Elo.
La solución busca dar a jugadores y clubes una herramienta simple, transparente y justa para medir el rendimiento, organizar partidos y consultar rankings, todo en tiempo real y desde cualquier dispositivo.

Objetivos

Brindar un MVP funcional que permita:
Registrar jugadores.
Crear partidos (single o doble).
Reportar resultados set por set.
Confirmar resultados por el rival.
Actualizar automáticamente el rating Elo de los jugadores.
Consultar el ranking global, por ciudad o por club.

Usuarios Objetivo

Jugador amateur → quiere trackear su nivel y competir con amigos.
Club de pádel → desea rankings internos para torneos o ligas sociales.

Stack tecnológico

Backend: Python + FastAPI + MySQL (SQLAlchemy + Alembic).
Frontend/App: Flutter → Android, iOS y Web/PWA desde un solo codebase.
Infraestructura: Railway/Render (backend), Cloudflare Pages (PWA).

Alcance

Registro y login de usuarios.
Creación de partidos.
Reporte de resultados + confirmación del rival.
Cálculo y actualización de rating Elo.
Ranking global/club/ciudad.
Historial de rating por jugador.

Futuras mejoras

Reservas de cancha y pagos.
Retos y logros (gamificación).
Evidencia de tanteador (foto).
Moderación de resultados sospechosos.
Estadísticas avanzadas de juego.
