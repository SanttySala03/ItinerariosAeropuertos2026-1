# ✈ Itinerary — Sistema de gestión de itinerarios de viaje

Aplicación web para planificar itinerarios de viaje entre aeropuertos nacionales e internacionales, desarrollada como proyecto de **Ingeniería de Software II** en la Universidad Central.

---

## 🏗 Arquitectura

El sistema está construido sobre una **arquitectura de microservicios**, separando responsabilidades en servicios independientes que se comunican mediante APIs REST.

ItinerariosAeropuertos2026-1/
├── airport_service/        → Microservicio de aeropuertos (puerto 8001)
│   ├── main.py             → API REST con FastAPI
│   ├── seed.py             → Script de carga inicial de datos
│   └── requirements.txt
├── itinerary_service/      → Microservicio de itinerarios (puerto 8002)
│   ├── main.py             → API REST con FastAPI
│   └── requirements.txt
├── frontend/               → Interfaz web
│   ├── index.html
│   ├── styles.css
│   ├── app.js
│   └── assets/
└── docs/                   → Documentación del proyecto

---

## 🛠 Tecnologías

| Capa | Tecnología |
|------|-----------|
| Backend | Python + FastAPI |
| Base de datos | SQLite |
| Frontend | HTML, CSS, JavaScript vanilla |
| Mapa | Leaflet.js + OpenStreetMap |
| Control de versiones | Git + GitHub |

---

## 🚀 Cómo correr el proyecto

### 1. Clonar el repositorio

```bash
git clone https://github.com/SanttySala03/ItinerariosAeropuertos2026-1.git
cd ItinerariosAeropuertos2026-1
```

### 2. Instalar dependencias

```bash
pip3 install -r airport_service/requirements.txt
pip3 install -r itinerary_service/requirements.txt
```

### 3. Correr los microservicios

En una terminal:
```bash
python3 -m uvicorn airport_service.main:app --reload --port 8001
```

En otra terminal:
```bash
python3 -m uvicorn itinerary_service.main:app --reload --port 8002
```

### 4. Cargar aeropuertos iniciales

```bash
python3 airport_service/seed.py
```

Esto carga 20 aeropuertos preconfigurados de Colombia, Europa, Norteamérica y Latinoamérica.

### 5. Abrir el frontend

Abre `frontend/index.html` con Live Server en VS Code.

---

## 📡 Endpoints disponibles

### Microservicio de aeropuertos (puerto 8001)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/airports` | Lista todos los aeropuertos |
| GET | `/airports/{id}` | Obtiene un aeropuerto por ID |
| POST | `/airports` | Crea un aeropuerto |
| PUT | `/airports/{id}` | Edita un aeropuerto |
| DELETE | `/airports/{id}` | Elimina un aeropuerto |

### Microservicio de itinerarios (puerto 8002)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/itineraries` | Lista todos los itinerarios |
| GET | `/itineraries/{id}` | Obtiene un itinerario con sus tramos |
| POST | `/itineraries` | Crea un itinerario con uno o más tramos |
| PUT | `/itineraries/{id}` | Edita un itinerario completo |
| DELETE | `/itineraries/{id}` | Elimina un itinerario y sus tramos |

La documentación interactiva de cada servicio está disponible en:
- `http://127.0.0.1:8001/docs`
- `http://127.0.0.1:8002/docs`

---

## ✈ Aeropuertos incluidos

| País | Aeropuertos |
|------|-------------|
| Colombia | BOG, MDE, CLO, CTG, BAQ, PEI, CUC, ADZ |
| Europa | LIS, MAD, BCN, CDG, LHR |
| Norteamérica | JFK, MIA, ORD |
| Latinoamérica | PTY, LIM, GRU, EZE |

---

## 👨‍💻 Autor

**David Santiago Carrillo Salamanca**  
Ingeniería de Software II · Universidad Central · 2026