# ✈ Itinerary — Sistema de Gestión de Itinerarios de Viaje

Aplicación web para planificar itinerarios de viaje entre aeropuertos nacionales e internacionales, desarrollada como proyecto de Ingeniería de Software II en la Universidad Central.

---

## 🏗 Arquitectura Utilizada

El sistema implementa una **Arquitectura de Microservicios** con **Arquitectura Hexagonal** en cada servicio y el **Patrón Adapter** para el desacoplamiento de fuentes externas.
┌─────────────────────────────────────────────────────────┐
│                     Navegador Web                        │
│              Frontend SPA (HTML/CSS/JS)                  │
│                    Leaflet.js                            │
└───────────────┬─────────────────┬───────────────────────┘
│ REST HTTP        │ REST HTTP
▼                  ▼
┌──────────────────────┐  ┌──────────────────────────────┐
│  API Aeropuertos     │  │   API Itinerarios             │
│  Puerto 8001         │◄─┤   Puerto 8002                 │
│                      │  │   (valida IATA via HTTP)      │
│  ┌────────────────┐  │  │  ┌────────────────────────┐  │
│  │ domain/        │  │  │  │ domain/                │  │
│  │ ports/         │  │  │  │ ports/                 │  │
│  │ adapters/      │  │  │  │ adapters/              │  │
│  │ infrastructure/│  │  │  │ infrastructure/        │  │
│  └────────────────┘  │  │  └────────────────────────┘  │
│                      │  │                               │
│  SQLite airports.db  │  │  SQLite itineraries.db        │
└──────────────────────┘  └──────────────────────────────┘
│                              │
▼
┌──────────────────┐
│  API Colombia    │
│  (fuente externa)│
└──────────────────┘

### Decisión sobre Leaflet vs Plotly
El sistema utiliza **Leaflet.js** en lugar de Plotly JS por su especialización en cartografía interactiva, soporte nativo de tiles geográficos (OpenStreetMap, CartoDB) y capacidad para renderizar rutas de vuelo como curvas de Bézier cuadráticas. Plotly es superior para gráficas estadísticas pero no para mapas de viaje interactivos.

---

## 🔌 Patrón Adapter Implementado

El patrón Adapter desacopla el dominio de las fuentes externas de datos.
┌─────────────────┐     ┌─────────────────────┐     ┌──────────────────┐
│   <<interface>> │     │     <<Adapter>>      │     │    <<Adaptee>>   │
│   AirportPort   │◄────│ ApiColombiaAdapter   │────►│   API Colombia   │
│                 │     │                      │     │ api-colombia.com │
│ + get_all()     │     │ + _fetch(url)        │     │                  │
│ + get_by_id()   │     │ + _map(data)         │     │ GET /Airport     │
│ + get_by_iata() │     │ + get_all()          │     │ GET /Airport/{id}│
└─────────────────┘     │ + get_by_id()        │     └──────────────────┘
▲              │ + get_by_iata()      │
│              └─────────────────────┘
│
│              ┌─────────────────────┐
└──────────────│ SQLiteAirportAdapter │
│ (adapter alternativo)│
└─────────────────────┘

**Componentes del patrón:**
- **Target (Puerto):** `AirportPort` — interfaz abstracta que define el contrato del dominio
- **Adaptee:** API Colombia — fuente externa con estructura JSON propia
- **Adapter:** `ApiColombiaAdapter` — traduce la respuesta de API Colombia al modelo `Airport`
- **Client:** endpoints de FastAPI — solo conocen `AirportPort`, nunca la API externa

**Endpoint de sincronización:**
POST /airports/sync
Consume API Colombia, traduce los datos mediante el Adapter e importa los aeropuertos colombianos al catálogo local.

---

## 🗂 Estructura del Proyecto
ItinerariosAeropuertos2026-1/
├── airport_service/              # Microservicio Aeropuertos :8001
│   ├── domain/
│   │   └── models.py             # Entidad Airport
│   ├── ports/
│   │   └── airport_port.py       # Interfaz AirportPort (Puerto)
│   ├── adapters/
│   │   └── api_colombia_adapter.py  # Adapter API Colombia
│   ├── infrastructure/
│   │   └── database.py           # SQLiteAirportAdapter
│   ├── tests/
│   │   └── test_airports.py      # Pruebas unitarias
│   ├── main.py                   # API FastAPI (capa de entrada)
│   ├── seed.py                   # Carga inicial de aeropuertos
│   ├── Dockerfile
│   └── requirements.txt
├── itinerary_service/            # Microservicio Itinerarios :8002
│   ├── domain/
│   │   └── models.py             # Entidades Itinerary y Leg
│   ├── ports/
│   │   └── itinerary_port.py     # Interfaz ItineraryPort (Puerto)
│   ├── adapters/
│   │   └── airport_validator.py  # Adapter validacion IATA
│   ├── infrastructure/
│   │   └── database.py           # SQLiteItineraryAdapter
│   ├── tests/
│   │   └── test_itineraries.py   # Pruebas unitarias
│   ├── main.py                   # API FastAPI (capa de entrada)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                     # SPA Vanilla JS
│   ├── index.html
│   ├── styles.css
│   ├── app.js
│   └── datepicker.js
├── docker-compose.yml
└── README.md

---

## 📊 Diagrama de Componentes
[Frontend SPA]──GET /airports──►[API Aeropuertos :8001]──►[airports.db]
[Frontend SPA]──POST/GET/DELETE /itineraries──►[API Itinerarios :8002]──►[itineraries.db]
[API Itinerarios]──GET /airports/iata/{code}──►[API Aeropuertos :8001]
[API Aeropuertos]──POST /airports/sync──►[API Colombia Externa]
[GitHub Actions]──build & push──►[GHCR: airport-service:latest]
[GitHub Actions]──build & push──►[GHCR: itinerary-service:latest]

---

## 📐 Diagrama de Clases
Airport                          Itinerary
────────────────────             ──────────────────────

id: int                        + id: int
name: str                      + title: str
city: str                      + user_name: str
department: str                + legs: List[Leg]
iata_code: str                 + to_dict()
latitude: float
longitude: float               Leg
to_dict()                      ──────────────────────
+ id: int
AirportPort <<interface>>        + itinerary_id: int
────────────────────             + origin_iata: str
get_all()                      + destination_iata: str
get_by_id()                    + departure_datetime: str
get_by_iata()                  + arrival_datetime: str
▲                          + to_dict()
│
├── ApiColombiaAdapter
└── SQLiteAirportAdapter


---

## 🗄 Diagrama Relacional
airports (airports.db)
────────────────────────────────────
id          INTEGER  PK AUTOINCREMENT
name        TEXT     NOT NULL
city        TEXT     NOT NULL
department  TEXT     NOT NULL
iata_code   TEXT     UNIQUE NOT NULL
latitude    REAL     NOT NULL
longitude   REAL     NOT NULL
itineraries (itineraries.db)          legs (itineraries.db)
──────────────────────────────        ────────────────────────────────────────
id        INTEGER  PK                 id                  INTEGER  PK
title     TEXT     NOT NULL           itinerary_id        INTEGER  FK → itineraries(id)
user_name TEXT     NOT NULL           origin_iata         TEXT     NOT NULL
destination_iata    TEXT     NOT NULL
departure_datetime  TEXT     NOT NULL
arrival_datetime    TEXT     NOT NULL

---

## 🚀 Instrucciones de Ejecución

### Opción 1 — Ejecución directa

```bash
# 1. Clonar el repositorio
git clone https://github.com/SanttySala03/ItinerariosAeropuertos2026-1.git
cd ItinerariosAeropuertos2026-1

# 2. Instalar dependencias
pip install -r airport_service/requirements.txt
pip install -r itinerary_service/requirements.txt

# 3. Terminal 1 — API Aeropuertos
cd airport_service
python -m uvicorn main:app --reload --port 8001

# 4. Terminal 2 — API Itinerarios
cd itinerary_service
python -m uvicorn main:app --reload --port 8002

# 5. Cargar aeropuertos iniciales
python airport_service/seed.py

# 6. (Opcional) Sincronizar con API Colombia
# POST http://127.0.0.1:8001/airports/sync

# 7. Abrir frontend/index.html con Live Server en VS Code
```

### Opción 2 — Docker Compose

```bash
docker-compose up --build
```

### URLs disponibles

| Servicio | URL |
|---|---|
| Frontend | Abrir frontend/index.html con Live Server |
| API Aeropuertos | http://127.0.0.1:8001 |
| API Itinerarios | http://127.0.0.1:8002 |
| Swagger Aeropuertos | http://127.0.0.1:8001/docs |
| Swagger Itinerarios | http://127.0.0.1:8002/docs |

---

## 🧪 Pruebas Unitarias

```bash
# Airport Service
cd airport_service
pytest tests/ -v --cov=. --cov-report=term-missing

# Itinerary Service
cd itinerary_service
pytest tests/ -v --cov=. --cov-report=term-missing
```

---

## ⚙️ Pipeline CI/CD

GitHub Actions ejecuta automáticamente en cada push:

1. **Test Airport Service** — PyTest con reporte de cobertura
2. **Test Itinerary Service** — PyTest con reporte de cobertura
3. **Build Docker Images** — Solo si pasan los tests
4. **Validate Frontend** — Verifica estructura de archivos
5. **Pipeline Summary** — Estado de todos los jobs

Imágenes publicadas en GitHub Container Registry:
- `ghcr.io/santysala03/itinerariosaeropuertos2026-1/airport-service:latest`
- `ghcr.io/santysala03/itinerariosaeropuertos2026-1/itinerary-service:latest`

---

## ✈ Aeropuertos incluidos

| País | Códigos IATA |
|---|---|
| Colombia | BOG, MDE, CLO, CTG, BAQ, PEI, CUC, ADZ |
| Europa | LIS, MAD, BCN, CDG, LHR |
| Norteamérica | JFK, MIA, ORD |
| Latinoamérica | PTY, LIM, GRU, EZE |

Adicionalmente, `POST /airports/sync` importa todos los aeropuertos colombianos desde API Colombia.

---

## 👨‍💻 Autor

**David Santiago Carrillo Salamanca**  
Ingeniería de Software II · Universidad Central · 2026

**Docente:** Otoniel Humberto Castañeda Rodriguez