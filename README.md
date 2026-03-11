# Car Arbitration App

Plataforma unificada para la detección de coches rentables para importar a España.

## Estructura de Carpetas

- `backend/`: API y lógica de negocio.
- `frontend/`: Interfaz de usuario.
- `scrapers/`: Motores de extracción de datos.
- `database/`: Definición de datos y migraciones.
- `workers/`: Análisis de rentabilidad automatizado.
- `infrastructure/`: Configuración de despliegue (Docker).

## Cómo empezar

1. Entra en `car-arbitration-app`.
2. Revisa el `README.md` (este archivo) para entender los módulos.
3. El `backend` se puede ejecutar con `uvicorn main:app --reload`.
