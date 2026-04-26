const AIRPORT_API   = 'http://127.0.0.1:8001';
const ITINERARY_API = 'http://127.0.0.1:8002';

// ── Icono personalizado ───────────────────────────────────────────
const airportIcon = L.divIcon({
  className: '',
  html: `<div style="
    background:#1d4ed8;
    border:2px solid #93c5fd;
    border-radius:50% 50% 50% 0;
    transform:rotate(-45deg);
    width:28px;height:28px;
    box-shadow:0 2px 8px rgba(29,78,216,0.5);
    display:flex;align-items:center;justify-content:center;
  "><span style="transform:rotate(45deg);font-size:13px;">✈</span></div>`,
  iconSize: [28, 28],
  iconAnchor: [14, 28],
  popupAnchor: [0, -30]
});

// ── Mapa ──────────────────────────────────────────────────────────
const map = L.map('map', { zoomControl: false }).setView([4.7016, -74.1469], 4);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap'
}).addTo(map);

L.control.zoom({ position: 'bottomleft' }).addTo(map);

async function loadAirports() {
  const res = await fetch(`${AIRPORT_API}/airports`);
  const airports = await res.json();
  airports.forEach(a => {
    L.marker([a.latitude, a.longitude], { icon: airportIcon })
      .addTo(map)
      .bindPopup(`
        <div style="font-family:'Segoe UI',sans-serif;min-width:160px;">
          <div style="font-size:18px;font-weight:700;color:#1d4ed8">${a.iata_code}</div>
          <div style="font-size:13px;font-weight:600;margin:2px 0">${a.name}</div>
          <div style="font-size:12px;color:#64748b">${a.city}, ${a.country}</div>
        </div>
      `);
  });
}

// ── Navbar ────────────────────────────────────────────────────────
function showMap() {
  document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
  event.target.classList.add('active');
}

function openAbout(e) {
  document.getElementById('about-modal').classList.add('open');
}

function closeAbout() {
  document.getElementById('about-modal').classList.remove('open');
}

// ── Panel ─────────────────────────────────────────────────────────
let panelOpen = false;

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
let legCount = 0;
let airports  = [];

async function loadAirportOptions() {
  const res = await fetch(`${AIRPORT_API}/airports`);
  airports = await res.json();
}

function airportOptions() {
  return airports.map(a =>
    `<option value="${a.iata_code}">${a.iata_code} — ${a.city}</option>`
  ).join('');
}

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
  const res         = await fetch(`${ITINERARY_API}/itineraries`);
  const itineraries = await res.json();
  const container   = document.getElementById('itineraries-list');

  if (itineraries.length === 0) {
    container.innerHTML = '<p class="empty-state">No tienes itinerarios guardados</p>';
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
}

// ── Eliminar ──────────────────────────────────────────────────────
async function deleteItinerary(id) {
  if (!confirm('¿Eliminar este itinerario?')) return;
  await fetch(`${ITINERARY_API}/itineraries/${id}`, { method: 'DELETE' });
  loadItineraries();
}

// ── Inicializar ───────────────────────────────────────────────────
loadAirports();
loadAirportOptions();