const AIRPORT_API   = 'http://127.0.0.1:8001';
const ITINERARY_API = 'http://127.0.0.1:8002';

// ── Variables globales ────────────────────────────────────────────
let panelOpen      = false;
let legCount       = 0;
let airports       = [];
let routeLayers    = [];
let activeRoutes   = [];
let currentPicker  = null;
let currentLegId   = null;
let activeItinId   = null;

// ── Toast ─────────────────────────────────────────────────────────
function showToast(msg, type = 'success') {
  let toast = document.getElementById('toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toast';
    document.body.appendChild(toast);
  }
  toast.textContent = type === 'success' ? `✓ ${msg}` : `✕ ${msg}`;
  toast.className = type;
  requestAnimationFrame(() => {
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3000);
  });
}

// ── Iconos del mapa ───────────────────────────────────────────────
function makeIcon(color, border) {
  return L.divIcon({
    className: '',
    html: `<div style="
      background:${color};
      border:2px solid ${border};
      border-radius:50% 50% 50% 0;
      transform:rotate(-45deg);
      width:24px;height:24px;
      box-shadow:0 2px 8px rgba(0,0,0,0.2);
      display:flex;align-items:center;justify-content:center;
    "><span style="transform:rotate(45deg);font-size:11px;color:white;">✈</span></div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 24],
    popupAnchor: [0, -28]
  });
}

const iconDefault = makeIcon('#2563EB', '#93C5FD');
const iconActive  = makeIcon('#059669', '#6EE7B7');

// ── Mapa ──────────────────────────────────────────────────────────
const map = L.map('map', { zoomControl: false }).setView([4.7016, -74.1469], 6);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap',
  opacity: 0.85
}).addTo(map);

L.control.zoom({ position: 'bottomleft' }).addTo(map);

if (navigator.geolocation) {
  navigator.geolocation.getCurrentPosition(
    pos => map.setView([pos.coords.latitude, pos.coords.longitude], 12),
    () => map.setView([4.7016, -74.1469], 10)
  );
}

// ── Aeropuertos ───────────────────────────────────────────────────
async function loadAirports() {
  try {
    const res = await fetch(`${AIRPORT_API}/airports`);
    airports = await res.json();
    airports.forEach(a => {
      L.marker([a.latitude, a.longitude], { icon: iconDefault })
        .addTo(map)
        .bindPopup(`
          <div style="font-family:'Segoe UI',sans-serif;min-width:150px;">
            <div style="font-size:15px;font-weight:700;color:#2563EB;margin-bottom:2px">${a.iata_code}</div>
            <div style="font-size:12px;font-weight:600;color:#111827;margin-bottom:2px">${a.name}</div>
            <div style="font-size:11px;color:#6B7280">${a.city}, ${a.country}</div>
          </div>
        `);
    });
  } catch (e) {
    console.warn('No se pudo conectar con el servicio de aeropuertos');
  }
}

function airportOptions() {
  return airports.map(a =>
    `<option value="${a.iata_code}">${a.iata_code} — ${a.city}</option>`
  ).join('');
}

// ── Modal ─────────────────────────────────────────────────────────
function openAbout() {
  document.getElementById('about-modal').classList.add('open');
}

function closeAbout() {
  document.getElementById('about-modal').classList.remove('open');
}

// ── Panel ─────────────────────────────────────────────────────────
function togglePanel() {
  panelOpen = !panelOpen;
  document.body.classList.toggle('panel-open', panelOpen);
  if (panelOpen) loadItineraries();
  setTimeout(() => map.invalidateSize(), 380);
}

// ── Date Picker ───────────────────────────────────────────────────
function openDatePicker(legId) {
  currentLegId = legId;
  if (!currentPicker) {
    currentPicker = new DateRangePicker((dep, arr) => {
      const depEl = document.getElementById(`departure-${currentLegId}`);
      const arrEl = document.getElementById(`arrival-${currentLegId}`);
      if (depEl) depEl.value = dep;
      if (arrEl) arrEl.value = arr;
      const btn = document.getElementById(`date-btn-${currentLegId}`);
      if (btn) {
        btn.textContent = `📅 ${dep} → ${arr}`;
        btn.style.borderColor = '#2563EB';
        btn.style.color = '#2563EB';
      }
    });
  }
  currentPicker.startDate  = null;
  currentPicker.endDate    = null;
  currentPicker.hoverDate  = null;
  currentPicker.selecting  = 'start';
  currentPicker._updateSummary();
  currentPicker._renderAll();
  currentPicker.open();
}

// ── Formulario de tramos ──────────────────────────────────────────
function addLegForm() {
  const id  = legCount++;
  const div = document.createElement('div');
  div.id        = `leg-${id}`;
  div.className = 'leg-form';
  div.style.opacity = '0';
  div.style.transform = 'translateY(8px)';
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
    <input type="hidden" id="departure-${id}"/>
    <input type="hidden" id="arrival-${id}"/>
    <button class="btn-datepicker" id="date-btn-${id}" onclick="openDatePicker(${id})">
      📅 Seleccionar fechas y horas
    </button>
  `;
  document.getElementById('legs-container').appendChild(div);
  requestAnimationFrame(() => {
    div.style.transition = 'opacity 0.25s ease, transform 0.25s ease';
    div.style.opacity = '1';
    div.style.transform = 'translateY(0)';
  });
}

function removeLeg(id) {
  document.getElementById(`leg-${id}`)?.remove();
}

// ── Crear itinerario ──────────────────────────────────────────────
async function createItinerary() {
  const title = document.getElementById('itin-title').value.trim();
  if (!title) return showToast('Escribe un título para el itinerario', 'error');

  const legs = [];
  for (let i = 0; i < legCount; i++) {
    const origin = document.getElementById(`origin-${i}`);
    if (!origin) continue;
    const dep = document.getElementById(`departure-${i}`).value;
    const arr = document.getElementById(`arrival-${i}`).value;
    if (!dep || !arr) {
      showToast(`Selecciona las fechas del tramo ${i + 1}`, 'error');
      return;
    }
    legs.push({
      origin_iata:        origin.value,
      destination_iata:   document.getElementById(`destination-${i}`).value,
      departure_datetime: dep,
      arrival_datetime:   arr,
    });
  }

  if (legs.length === 0) return showToast('Agrega al menos un tramo', 'error');

  try {
    const res = await fetch(`${ITINERARY_API}/itineraries`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, legs })
    });

    if (res.ok) {
      document.getElementById('itin-title').value = '';
      document.getElementById('legs-container').innerHTML = '';
      legCount = 0;
      showToast('Itinerario guardado correctamente');
      loadItineraries();
    } else {
      const err = await res.json();
      showToast(err.detail || 'Error al guardar', 'error');
    }
  } catch (e) {
    showToast('No se pudo conectar con el servidor', 'error');
  }
}

// ── Duración entre fechas ─────────────────────────────────────────
function calcDuration(dep, arr) {
  const d1 = new Date(dep.replace(' ', 'T'));
  const d2 = new Date(arr.replace(' ', 'T'));
  const diffMs = d2 - d1;
  if (isNaN(diffMs) || diffMs < 0) return '';
  const hours = Math.floor(diffMs / 3600000);
  const mins  = Math.floor((diffMs % 3600000) / 60000);
  if (hours >= 24) {
    const days = Math.floor(hours / 24);
    return `${days}d ${hours % 24}h`;
  }
  return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
}

function calcTotalDays(legs) {
  if (!legs || legs.length === 0) return '';
  const first = new Date(legs[0].departure_datetime.replace(' ', 'T'));
  const last  = new Date(legs[legs.length - 1].arrival_datetime.replace(' ', 'T'));
  const days  = Math.round((last - first) / 86400000);
  return days > 0 ? `${days} día${days > 1 ? 's' : ''}` : '';
}

// ── Timeline ──────────────────────────────────────────────────────
function buildTimeline(itin) {
  if (!itin.legs || itin.legs.length === 0) return '';

  const legs  = itin.legs;
  const total = legs.length;
  let html    = '<div class="timeline">';

  legs.forEach((leg, i) => {
    const originAirport = airports.find(a => a.iata_code === leg.origin_iata);
    const isLast        = i === total - 1;
    const nodeClass     = i === 0 ? 'origin' : 'stopover';
    const duration      = calcDuration(leg.departure_datetime, leg.arrival_datetime);

    html += `
      <div class="timeline-item" onclick="focusLeg('${leg.origin_iata}','${leg.destination_iata}', ${itin.id})">
        <div class="timeline-left">
          <div class="timeline-node ${nodeClass}"></div>
          <div class="timeline-line"></div>
          <div class="timeline-plane">✈</div>
          <div class="timeline-line"></div>
          ${isLast ? `<div class="timeline-node destination"></div>` : ''}
        </div>
        <div class="timeline-content">
          <div style="display:flex;align-items:center;gap:6px;">
            <div class="timeline-iata">${leg.origin_iata}</div>
            <span style="color:#9CA3AF;font-size:10px;">→</span>
            <div class="timeline-iata">${leg.destination_iata}</div>
            ${duration ? `<span class="leg-duration">⏱ ${duration}</span>` : ''}
          </div>
          <div class="timeline-city">${originAirport ? originAirport.city : ''}</div>
          <div class="timeline-time">${leg.departure_datetime}</div>
        </div>
      </div>
    `;

    if (isLast) {
      const destAirport = airports.find(a => a.iata_code === leg.destination_iata);
      html += `
        <div class="timeline-item" style="padding-bottom:0">
          <div class="timeline-left">
            <div class="timeline-node destination"></div>
          </div>
          <div class="timeline-content">
            <div class="timeline-iata">${leg.destination_iata}</div>
            <div class="timeline-city">${destAirport ? destAirport.city : ''}</div>
            <div class="timeline-time">${leg.arrival_datetime}</div>
          </div>
        </div>
      `;
    }
  });

  html += '</div>';
  return html;
}

// ── Foco en tramo ─────────────────────────────────────────────────
function focusLeg(originIata, destIata, itinId) {
  const origin = airports.find(a => a.iata_code === originIata);
  const dest   = airports.find(a => a.iata_code === destIata);
  if (!origin || !dest) return;
  const midLat = (origin.latitude  + dest.latitude)  / 2;
  const midLng = (origin.longitude + dest.longitude) / 2;
  map.flyTo([midLat, midLng], 5, { duration: 1.2 });
  setActiveItinerary(itinId);
}

// ── Itinerario activo ─────────────────────────────────────────────
function setActiveItinerary(id) {
  activeItinId = id;
  document.querySelectorAll('.itinerary-card').forEach(card => {
    card.classList.toggle('active', card.dataset.id === String(id));
  });
}

// ── Cargar itinerarios ────────────────────────────────────────────
async function loadItineraries() {
  try {
    const res         = await fetch(`${ITINERARY_API}/itineraries`);
    const itineraries = await res.json();
    const container   = document.getElementById('itineraries-list');

    if (itineraries.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <span class="empty-icon">✈</span>
          <span>No tienes itinerarios guardados</span>
          <span style="font-size:11px;color:#9CA3AF;">Crea tu primer itinerario arriba</span>
        </div>`;
      clearRoutes();
      return;
    }

    container.innerHTML = itineraries.map(itin => {
      const totalDays = calcTotalDays(itin.legs);
      const route = itin.legs.map(l => l.origin_iata).join(' → ') +
                    (itin.legs.length ? ` → ${itin.legs[itin.legs.length-1].destination_iata}` : '');
      return `
        <div class="itinerary-card ${activeItinId === itin.id ? 'active' : ''}"
             data-id="${itin.id}"
             onclick="setActiveItinerary(${itin.id})">
          <div class="itinerary-card-header">
            <div>
              <div class="itinerary-title">${itin.title}</div>
              <div class="itinerary-summary">${route}${totalDays ? ` · ${totalDays}` : ''}</div>
            </div>
            <button class="btn-danger" onclick="deleteItinerary(event, ${itin.id})">Eliminar</button>
          </div>
          ${buildTimeline(itin)}
        </div>
      `;
    }).join('');

    drawRoutes(itineraries);
  } catch (e) {
    console.warn('No se pudo cargar itinerarios');
  }
}

// ── Eliminar ──────────────────────────────────────────────────────
async function deleteItinerary(e, id) {
  e.stopPropagation();
  if (!confirm('¿Eliminar este itinerario?')) return;

  const card = document.querySelector(`.itinerary-card[data-id="${id}"]`);
  if (card) {
    card.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    card.style.opacity = '0';
    card.style.transform = 'translateX(20px)';
    await new Promise(r => setTimeout(r, 300));
  }

  await fetch(`${ITINERARY_API}/itineraries/${id}`, { method: 'DELETE' });
  showToast('Itinerario eliminado');
  if (activeItinId === id) activeItinId = null;
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
      const origin = airports.find(a => a.iata_code === leg.origin_iata);
      const dest   = airports.find(a => a.iata_code === leg.destination_iata);
      if (!origin || !dest) return;

      const latlngs = createCurvedLine(
        [origin.latitude,  origin.longitude],
        [dest.latitude, dest.longitude]
      );

      const isActive = activeItinId === itin.id;
      const line = L.polyline(latlngs, {
        color:     isActive ? '#2563EB' : '#93C5FD',
        weight:    isActive ? 3 : 2,
        opacity:   isActive ? 0.9 : 0.45,
        dashArray: isActive ? null : '6 5'
      }).addTo(map);

      routeLayers.push(line);
    });
  });
}

function createCurvedLine(from, to) {
  const points = [];
  const steps  = 60;
  const midLat = (from[0] + to[0]) / 2 + Math.abs(to[1] - from[1]) * 0.3;
  const midLng = (from[1] + to[1]) / 2;

  for (let i = 0; i <= steps; i++) {
    const t  = i / steps;
    const t1 = 1 - t;
    points.push([
      t1 * t1 * from[0] + 2 * t1 * t * midLat + t * t * to[0],
      t1 * t1 * from[1] + 2 * t1 * t * midLng + t * t * to[1]
    ]);
  }
  return points;
}

// ── Inicializar ───────────────────────────────────────────────────
loadAirports();
currentPicker = new DateRangePicker((dep, arr) => {
  const depEl = document.getElementById(`departure-${currentLegId}`);
  const arrEl = document.getElementById(`arrival-${currentLegId}`);
  if (depEl) depEl.value = dep;
  if (arrEl) arrEl.value = arr;
  const btn = document.getElementById(`date-btn-${currentLegId}`);
  if (btn) {
    btn.textContent = `📅 ${dep} → ${arr}`;
    btn.style.borderColor = '#2563EB';
    btn.style.color = '#2563EB';
  }
});