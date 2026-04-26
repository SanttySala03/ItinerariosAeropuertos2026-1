const AIRPORT_API   = 'http://127.0.0.1:8001';
const ITINERARY_API = 'http://127.0.0.1:8002';

// ── Icono personalizado ───────────────────────────────────────────
const airportIcon = L.divIcon({
  className: '',
  html: `<div style="
    background:#2563eb;
    border:2px solid #93c5fd;
    border-radius:50% 50% 50% 0;
    transform:rotate(-45deg);
    width:28px;height:28px;
    box-shadow:0 2px 8px rgba(37,99,235,0.5);
    display:flex;align-items:center;justify-content:center;
  "><span style="transform:rotate(45deg);font-size:13px;">✈</span></div>`,
  iconSize: [28, 28],
  iconAnchor: [14, 28],
  popupAnchor: [0, -30]
});

// ── Mapa ──────────────────────────────────────────────────────────
const map = L.map('map', { zoomControl: false }).setView([4.7016, -74.1469], 6);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap'
}).addTo(map);

L.control.zoom({ position: 'bottomleft' }).addTo(map);

if (navigator.geolocation) {
  navigator.geolocation.getCurrentPosition(
    pos => map.setView([pos.coords.latitude, pos.coords.longitude], 10),
    () => map.setView([4.7016, -74.1469], 6)
  );
}

// ── Variables globales ────────────────────────────────────────────
let panelOpen  = false;
let legCount   = 0;
let airports   = [];
let routeLayers = [];

// ── Aeropuertos ───────────────────────────────────────────────────
async function loadAirports() {
  try {
    const res = await fetch(`${AIRPORT_API}/airports`);
    airports = await res.json();
    airports.forEach(a => {
      L.marker([a.latitude, a.longitude], { icon: airportIcon })
        .addTo(map)
        .bindPopup(`
          <div style="font-family:'Segoe UI',sans-serif;min-width:160px;">
            <div style="font-size:16px;font-weight:700;color:#2563eb">${a.iata_code}</div>
            <div style="font-size:13px;font-weight:600;margin:2px 0;color:#1e293b">${a.name}</div>
            <div style="font-size:12px;color:#64748b">${a.city}, ${a.country}</div>
          </div>
        `);
    });
  } catch (e) {
    console.warn('No se pudo conectar con el servicio de aeropuertos');
  }
}

async function loadAirportOptions() {
  try {
    if (airports.length === 0) {
      const res = await fetch(`${AIRPORT_API}/airports`);
      airports = await res.json();
    }
  } catch (e) {
    console.warn('No se pudo cargar aeropuertos');
  }
}

function airportOptions() {
  return airports.map(a =>
    `<option value="${a.iata_code}">${a.iata_code} — ${a.city}</option>`
  ).join('');
}

// ── Modal ─────────────────────────────────────────────────────────
function openAbout(e) {
  document.getElementById('about-modal').classList.add('open');
}

function closeAbout() {
  document.getElementById('about-modal').classList.remove('open');
}

// ── Panel ─────────────────────────────────────────────────────────
function togglePanel() {
  panelOpen = !panelOpen;
  document.body.classList.toggle('panel-open', panelOpen);
  if (panelOpen) {
    loadItineraries();
    loadAirportOptions();
  }
  setTimeout(() => map.invalidateSize(), 380);
}

// ── Tramos ────────────────────────────────────────────────────────
function addLegForm() {
  const id  = legCount++;
  const div = document.createElement('div');
  div.id        = `leg-${id}`;
  div.className = 'leg-form';
  div.innerHTML = `
    <div class="leg-form-header">
      <span class="leg-form-title">Tramo ${id + 1}</span>
      <button class="btn-danger" onclick="removeLeg(${id})">✕</button>
    </div>
    <div class="form-group">
      <label>Origen</label>
      <select id="origin-${id}">${airportOptions()}</select>
    </div>
    <div class="form-group">
      <label>Destino</label>
      <select id="destination-${id}">${airportOptions()}</select>
    </div>
    <div class="form-group">
      <label>Salida (YYYY-MM-DD HH:MM)</label>
      <input type="text" id="departure-${id}" placeholder="2026-06-01 10:00"/>
    </div>
    <div class="form-group">
      <label>Llegada (YYYY-MM-DD HH:MM)</label>
      <input type="text" id="arrival-${id}" placeholder="2026-06-01 14:00"/>
    </div>
  `;
  document.getElementById('legs-container').appendChild(div);
}

function removeLeg(id) {
  document.getElementById(`leg-${id}`)?.remove();
}

// ── Crear itinerario ──────────────────────────────────────────────
async function createItinerary() {
  const title = document.getElementById('itin-title').value.trim();
  if (!title) return alert('Escribe un título para el itinerario');

  const legs = [];
  for (let i = 0; i < legCount; i++) {
    const origin = document.getElementById(`origin-${i}`);
    if (!origin) continue;
    legs.push({
      origin_iata:        origin.value,
      destination_iata:   document.getElementById(`destination-${i}`).value,
      departure_datetime: document.getElementById(`departure-${i}`).value,
      arrival_datetime:   document.getElementById(`arrival-${i}`).value,
    });
  }

  if (legs.length === 0) return alert('Agrega al menos un tramo');

  const res = await fetch(`${ITINERARY_API}/itineraries`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, legs })
  });

  if (res.ok) {
    document.getElementById('itin-title').value = '';
    document.getElementById('legs-container').innerHTML = '';
    legCount = 0;
    loadItineraries();
  } else {
    const err = await res.json();
    alert('Error: ' + err.detail);
  }
}

// ── Cargar itinerarios ────────────────────────────────────────────
async function loadItineraries() {
  try {
    const res         = await fetch(`${ITINERARY_API}/itineraries`);
    const itineraries = await res.json();
    const container   = document.getElementById('itineraries-list');

    if (itineraries.length === 0) {
      container.innerHTML = '<p class="empty-state">No tienes itinerarios guardados</p>';
      clearRoutes();
      return;
    }

    container.innerHTML = itineraries.map(itin => `
      <div class="itinerary-card">
        <div class="itinerary-card-header">
          <span class="itinerary-title">${itin.title}</span>
          <button class="btn-danger" onclick="deleteItinerary(${itin.id})">Eliminar</button>
        </div>
        ${itin.legs.map(leg => `
          <div class="leg">
            <span class="iata">${leg.origin_iata}</span>
            <span class="arrow">→</span>
            <span class="iata">${leg.destination_iata}</span>
            <div class="leg-times">
              <div>${leg.departure_datetime}</div>
              <div>${leg.arrival_datetime}</div>
            </div>
          </div>
        `).join('')}
      </div>
    `).join('');

    drawRoutes(itineraries);
  } catch (e) {
    console.warn('No se pudo cargar itinerarios');
  }
}

// ── Eliminar ──────────────────────────────────────────────────────
async function deleteItinerary(id) {
  if (!confirm('¿Eliminar este itinerario?')) return;
  await fetch(`${ITINERARY_API}/itineraries/${id}`, { method: 'DELETE' });
  loadItineraries();
}

// ── Rutas en el mapa ──────────────────────────────────────────────
function clearRoutes() {
  routeLayers.forEach(l => map.removeLayer(l));
  routeLayers = [];
}

function drawRoutes(itineraries) {
  clearRoutes();
  itineraries.forEach(itin => {
    itin.legs.forEach(leg => {
      const origin      = airports.find(a => a.iata_code === leg.origin_iata);
      const destination = airports.find(a => a.iata_code === leg.destination_iata);
      if (!origin || !destination) return;

      const latlngs = createCurvedLine(
        [origin.latitude, origin.longitude],
        [destination.latitude, destination.longitude]
      );

      const line = L.polyline(latlngs, {
        color: '#2563eb',
        weight: 2,
        opacity: 0.6,
        dashArray: '6 4'
      }).addTo(map);

      routeLayers.push(line);
    });
  });
}

function createCurvedLine(from, to) {
  const points = [];
  const steps  = 50;
  const midLat = (from[0] + to[0]) / 2 + Math.abs(to[1] - from[1]) * 0.3;
  const midLng = (from[1] + to[1]) / 2;

  for (let i = 0; i <= steps; i++) {
    const t  = i / steps;
    const t1 = 1 - t;
    const lat = t1 * t1 * from[0] + 2 * t1 * t * midLat + t * t * to[0];
    const lng = t1 * t1 * from[1] + 2 * t1 * t * midLng + t * t * to[1];
    points.push([lat, lng]);
  }

  return points;
}

// ── Inicializar ───────────────────────────────────────────────────
loadAirports();