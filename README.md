# 🚗 Car Import AI — Sistema Automático de Arbitraje de Vehículos

> **Plataforma de inteligencia de mercado para la importación de vehículos europeos.**
> Detecta automáticamente coches de oportunidad en Alemania, calcula el ROI real y presenta un dashboard de inversión limpio y profesional.

---

## 📋 Tabla de Contenidos
1. [¿Qué hace este sistema?](#-qué-hace-este-sistema)
2. [Arquitectura del Proyecto](#-arquitectura-del-proyecto)
3. [Stack Tecnológico](#-stack-tecnológico)
4. [Estructura de Carpetas](#-estructura-de-carpetas)
5. [Requisitos Previos](#-requisitos-previos)
6. [Instalación y Configuración](#-instalación-y-configuración)
7. [Cómo Ejecutar](#-cómo-ejecutar)
8. [Cómo Funciona el Pipeline](#-cómo-funciona-el-pipeline)
9. [Sistema de Control de Calidad](#-sistema-de-control-de-calidad)
10. [Cálculo del ROI](#-cálculo-del-roi)
11. [Modelos Objetivo](#-modelos-objetivo)
12. [API — Endpoints Principales](#-api--endpoints-principales)
13. [Variables de Entorno](#-variables-de-entorno)
14. [Advertencias Técnicas](#-advertencias-técnicas)

---

## 🎯 ¿Qué hace este sistema?

Este proyecto es un **sistema de arbitraje geográfico de vehículos**. Su objetivo es:

1. **Rastrear** anuncios de coches de segunda mano en portales europeos (actualmente `mobile.de` para el mercado alemán y `coches.net` para el mercado español).
2. **Filtrar agresivamente** cualquier vehículo accidentado, con daños mecánicos o con historial dudoso.
3. **Calcular** el precio medio real del vehículo en España usando una mediana estadística robusta (eliminando outliers).
4. **Estimar el ROI** neto de la importación, teniendo en cuenta transporte, ITV, gestoría y matriculación.
5. **Mostrar** únicamente las oportunidades rentables y verificadas en un dashboard premium.

---

## 🏗️ Arquitectura del Proyecto

```
mobile.de (DE) ──────┐
                      ├──► Scraper Pipeline ──► Filtro de Calidad ──► Comparison Engine ──► car_export ──► Dashboard
coches.net (ES) ─────┘         (Playwright)         (vehicle_status)     (ROI / Mediana)    (PostgreSQL)   (React)
```

El sistema funciona en **tres fases secuenciales**:

1. **Fase 1 — Baseline España**: Scrapeamos 40 coches por modelo en `coches.net` para construir la referencia de precios del mercado español.
2. **Fase 2 — Oportunidades Alemania**: Scrapeamos 40 coches por modelo en `mobile.de` buscando unidades limpias y baratas.
3. **Fase 3 — Análisis ROI**: El `ComparisonEngine` cruza ambos datasets, calcula el margen real y exporta las oportunidades rentables al dashboard.

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología |
|---|---|
| **Backend API** | FastAPI + Uvicorn |
| **Base de Datos** | PostgreSQL (Supabase) |
| **ORM** | SQLAlchemy |
| **Auth** | JWT (python-jose + passlib) |
| **Scraping** | Playwright (async) + Selenium Stealth |
| **Anti-Bot** | Selenium-Stealth, human mimicry, fingerprint evasion |
| **Frontend** | React + TypeScript + Vite |
| **Estilos** | TailwindCSS |
| **Análisis** | Python `statistics` (mediana, percentiles) |

---

## 📁 Estructura de Carpetas

```
PracticasTuateam/
│
├── backend/                        # API FastAPI
│   ├── api/
│   │   ├── routes.py               # Router principal que agrupa todos los endpoints
│   │   ├── schemas.py              # Modelos Pydantic (validación de datos)
│   │   ├── car_routes.py           # Endpoints de coches (/api/cars)
│   │   ├── auth_routes.py          # Endpoints de autenticación (/api/auth)
│   │   └── favorite_routes.py      # Endpoints de favoritos (/api/favorites)
│   ├── core/
│   │   ├── config.py               # Configuración central (DATABASE_URL, SECRET_KEY...)
│   │   └── database.py             # Motor SQLAlchemy y SessionLocal
│   ├── models/
│   │   ├── car.py                  # Modelo Car (todos los coches scrapeados)
│   │   ├── car_export.py           # Modelo CarExport (coches validados y rentables)
│   │   ├── user.py                 # Modelo User (autenticación)
│   │   └── favorite.py             # Modelo Favorite (coches guardados por usuario)
│   ├── repositories/               # Capa de acceso a datos (CRUD)
│   ├── services/                   # Lógica de negocio del backend
│   ├── main.py                     # Punto de entrada de la API
│   ├── worker.py                   # Worker de background tasks
│   └── requirements.txt            # Dependencias Python del backend
│
├── scrapers/                       # Motor de extracción y análisis
│   ├── portal_scrapers/
│   │   ├── mobile_de.py            # Scraper del mercado alemán (mobile.de)
│   │   └── coches_net.py           # Scraper del mercado español (coches.net)
│   ├── utils/
│   │   ├── comparison_engine.py    # Motor de comparación y cálculo de ROI
│   │   └── db_repository.py        # Repositorio de base de datos para scrapers
│   ├── base/
│   │   └── schemas.py              # Schemas base compartidos entre scrapers
│   └── run_scrapers.py             # Punto de entrada del pipeline completo
│
├── frontend/                       # Dashboard React
│   ├── src/
│   │   ├── api/cars.ts             # Cliente API + TypeScript interfaces
│   │   ├── components/
│   │   │   ├── CarCard.tsx         # Tarjeta de vehículo (lista principal)
│   │   │   ├── CarDetailModal.tsx  # Modal detallado con desglose de ROI
│   │   │   ├── FilterSidebar.tsx   # Filtros de búsqueda
│   │   │   └── Navbar.tsx          # Navegación principal
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx       # Vista principal del marketplace
│   │   │   └── LoginPage.tsx       # Página de login
│   │   └── index.css               # Estilos globales y design tokens
│   ├── tailwind.config.js
│   └── vite.config.ts
│
└── README.md
```

---

## 🔧 Requisitos Previos

- **Python 3.11+**
- **Node.js 18+** y npm
- **PostgreSQL** (o una cuenta en [Supabase](https://supabase.com))
- **Playwright** instalado con sus navegadores:
  ```bash
  pip install playwright
  playwright install chromium
  ```

---

## ⚙️ Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/davsalcog69/PracticasTuateam.git
cd PracticasTuateam
```

### 2. Backend
```bash
cd backend
pip install -r requirements.txt
```

Crea un archivo `.env` en la carpeta `backend/` (o configura las variables de entorno):
```env
DATABASE_URL=postgresql://usuario:password@host:puerto/basededatos
SECRET_KEY=tu_clave_secreta_muy_larga_y_segura
```

### 3. Frontend
```bash
cd frontend
npm install
```

---

## 🚀 Cómo Ejecutar

### Backend (API)
```bash
cd backend
py -m uvicorn main:app --reload
```
La API estará disponible en: `http://localhost:8000`
Documentación interactiva: `http://localhost:8000/docs`

### Frontend (Dashboard)
```bash
cd frontend
npm run dev
```
El dashboard estará disponible en: `http://localhost:5173`

### Scrapers (Pipeline completo)
```bash
cd scrapers
py run_scrapers.py
```
> ⚠️ Este proceso abre instancias de Chromium automatizadas y puede tardar **30–60 minutos** en completar el pipeline de los 7 modelos con 40 coches cada uno.

---

## 🔄 Cómo Funciona el Pipeline

```
run_scrapers.py
│
├── FASE 1: coches.net (España) — baseline de precios
│   └── 40 coches/modelo × 7 modelos = hasta 280 referencias de mercado
│
├── FASE 2: mobile.de (Alemania) — búsqueda de oportunidades
│   └── 40 coches/modelo × 7 modelos = hasta 280 candidatos
│
└── FASE 3: ComparisonEngine
    ├── Carga coches de Alemania desde la BD
    ├── Para cada coche:
    │   ├── Busca comparables en coches.net (mismo modelo, año ±2)
    │   ├── Elimina outliers (15% más barato + 15% más caro)
    │   ├── Calcula la MEDIANA de precios en España
    │   ├── Aplica ajustes (M Sport, S line, AMG Line → +1.500€)
    │   ├── Suma costes de importación (2.500€ fijos: transporte + ITV + gestoría)
    │   ├── Calcula beneficio neto = precio_mediana_españa - precio_alemania - costes
    │   └── Si beneficio > 500€ → guarda en car_export (visible en dashboard)
    └── Commit a PostgreSQL
```

---

## 🛡️ Sistema de Control de Calidad

El sistema implementa una política de **tolerancia cero** contra vehículos dañados.

### Regla de Oro
> Un coche sin badge explícito de **"Sin accidentes"** o **"Unfallfrei"** es tratado como sospechoso y **NO aparece** en el dashboard.

### Flujo de Clasificación

| Estado | Significado | ¿Visible en Dashboard? |
|---|---|---|
| `Sin accidentes` | Badge confirmado + sin palabras de lista negra | ✅ Sí |
| `Dudoso` | Sin confirmación explícita de estado | ⚠️ Solo en modo debug |
| `Descartado` | Coincide con lista negra de accidentes | ❌ No |

### Lista Negra Semántica

El scraper busca y filtra en 3 idiomas (alemán, español, inglés) palabras como:

- **Accidentes**: `unfall`, `unfallschaden`, `accidente`, `siniestro`, `crash damage`...
- **Daños mecánicos**: `motorschaden`, `motor roto`, `engine failure`, `no arranca`...
- **Problemáticos**: `bastlerfahrzeug`, `para piezas`, `export only`, `salvage`...
- **Reparaciones sospechosas**: `nachlackiert`, `repintado`, `frame damage`...

---

## 💰 Cálculo del ROI

### Fórmula
```
ROI (€) = Precio_Mediana_España - Precio_Compra_Alemania - Costes_Importación

Costes_Importación = 2.500€ (transporte + ITV + gestoría + matriculación)
```

### Protección contra sesgos (Anti-Outliers)
Para que la mediana sea robusta, el sistema:
1. Recoge todos los precios comparables de `coches.net` (mismo modelo, año ±2).
2. Ordena los precios de menor a mayor.
3. **Descarta el 15% más barato** (coches en mal estado o con trampa).
4. **Descarta el 15% más caro** (coches excepcionalmente equipados o mal tasados).
5. Calcula la **mediana** del rango central resultante.

### Ajustes por Equipamiento
Si el coche importado incluye paquetes premium, se suma un valor adicional al precio de venta estimado:
- `M Sport`, `S line`, `AMG Line`, `R-Line` → **+1.500€**

---

## 🚙 Modelos Objetivo

El sistema busca actualmente los siguientes modelos:

| Modelo | Tipo | Mercado |
|---|---|---|
| Mercedes Vito | Furgoneta | Alemania → España |
| Mercedes Sprinter | Furgoneta grande | Alemania → España |
| Mercedes Citan | Furgoneta compacta | Alemania → España |
| BMW Serie 3 | Berlina/Touring | Alemania → España |
| Audi A4 | Berlina/Avant | Alemania → España |
| Volkswagen Golf GTI | Deportivo | Alemania → España |
| Volkswagen Golf R | Deportivo | Alemania → España |

Para añadir un nuevo modelo, edita el diccionario `counts` en `scrapers/run_scrapers.py`.

---

## 🌐 API — Endpoints Principales

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/cars/export` | Lista todos los coches rentables del dashboard |
| `GET` | `/api/cars/export/{id}` | Detalle de un coche específico |
| `POST` | `/api/auth/register` | Registrar nuevo usuario |
| `POST` | `/api/auth/login` | Obtener token JWT |
| `GET` | `/api/favorites` | Coches favoritos del usuario |
| `POST` | `/api/favorites` | Añadir coche a favoritos |
| `DELETE` | `/api/favorites` | Eliminar coche de favoritos |

---

## 🔑 Variables de Entorno

| Variable | Descripción | Ejemplo |
|---|---|---|
| `DATABASE_URL` | URL de conexión PostgreSQL | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | Clave secreta para firma JWT | `una_cadena_aleatoria_muy_larga` |

---

## ⚠️ Advertencias Técnicas

### Anti-Bot en mobile.de
`mobile.de` implementa medidas anti-scraping muy agresivas. Si el scraper empieza a fallar:
1. Revisa los selectores DOM en `scrapers/portal_scrapers/mobile_de.py` (~línea 330).
2. El atributo clave para la detección del estado es `[data-testid="listing-details-attributes"]`.
3. Aumenta los tiempos de espera (`asyncio.sleep`) si detectas bloqueos frecuentes.

### Base de Datos
- La tabla `cars` almacena el historial completo de coches scrapeados.
- La tabla `car_export` es la fuente de verdad del dashboard (solo coches limpios y rentables).
- Un coche solo pasa de `cars` a `car_export` si: tiene estado `Sin accidentes` Y su beneficio estimado es **> 500€**.

### Scrapers y Sesiones de Navegador
- Los scrapers usan perfiles persistentes de Chromium guardados en `browser_profile_Worker/`.
- El estado de paginación se guarda en `scrapers/scraper_state.json` para evitar duplicados entre ejecuciones.

---

## 📄 Licencia

Proyecto privado — Todos los derechos reservados. Uso interno de Tuateam.
