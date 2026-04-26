class DateRangePicker {
  constructor(onConfirm) {
    this.onConfirm     = onConfirm;
    this.startDate     = null;
    this.endDate       = null;
    this.hoverDate     = null;
    this.leftMonth     = new Date();
    this.rightMonth    = new Date(new Date().getFullYear(), new Date().getMonth() + 1, 1);
    this.departureTime = '10:00';
    this.arrivalTime   = '14:00';
    this.selecting     = 'start';
    this.el            = null;
    this._build();
  }
_clickDay(dateStr) {
    const clicked = new Date(dateStr + 'T00:00:00');
    if (this.selecting === 'start' || (this.startDate && this.endDate)) {
      this.startDate = clicked;
      this.endDate   = null;
      this.selecting = 'end';
    } else {
      if (clicked <= this.startDate) {
        this.startDate = clicked;
        this.endDate   = null;
        this.selecting = 'end';
      } else {
        this.endDate   = clicked;
        this.selecting = 'start';
      }
    }
    this._render();
  }
  
  _build() {
    const el = document.createElement('div');
    el.id = 'drp-overlay';
    document.body.appendChild(el);
    this.el = el;
    window._drp = this;
    this._render();
  }

  _render() {
    const MONTHS = ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
                    'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];
    const DAYS   = ['Do','Lu','Ma','Mi','Ju','Vi','Sa'];
    const today  = new Date(); today.setHours(0,0,0,0);

    const renderMonth = (date) => {
      const y = date.getFullYear();
      const m = date.getMonth();
      const firstDay    = new Date(y, m, 1).getDay();
      const daysInMonth = new Date(y, m + 1, 0).getDate();

      let days = DAYS.map(d => `<div class="drp-dn">${d}</div>`).join('');
      for (let i = 0; i < firstDay; i++) days += `<div class="drp-d"></div>`;

      for (let d = 1; d <= daysInMonth; d++) {
        const cur = new Date(y, m, d);
        cur.setHours(0,0,0,0);
        const ts      = cur.getTime();
        const isPast  = cur < today;
        const isToday = ts === today.getTime();
        const isStart = this.startDate && ts === this.startDate.getTime();
        const isEnd   = this.endDate   && ts === this.endDate.getTime();
        const inRange = this.startDate && this.endDate && cur > this.startDate && cur < this.endDate;
        const inHover = this.startDate && !this.endDate && this.hoverDate &&
                        cur > this.startDate && cur <= this.hoverDate;
        const dateStr = `${y}-${String(m+1).padStart(2,'0')}-${String(d).padStart(2,'0')}`;

        let cls = 'drp-d';
        if (isPast)   cls += ' drp-past';
        if (!isPast)  cls += ' drp-active';
        if (isToday)  cls += ' drp-today';
        if (isStart)  cls += ' drp-start';
        if (isEnd)    cls += ' drp-end';
        if (inRange)  cls += ' drp-range';
        if (inHover)  cls += ' drp-hover';

        days += `<div class="${cls}" ${!isPast ? `data-date="${dateStr}" onclick="window._drp._clickDay('${dateStr}')"` : ''}>${d}</div>`;
      }

      return `
        <div class="drp-month-nav">
          <button class="drp-nav-btn" type="button" data-action="prev-${date === this.leftMonth ? 'left' : 'right'}">‹</button>
          <span class="drp-month-name">${MONTHS[m]} ${y}</span>
          <button class="drp-nav-btn" type="button" data-action="next-${date === this.leftMonth ? 'left' : 'right'}">›</button>
        </div>
        <div class="drp-grid">${days}</div>
      `;
    };

    const fmt = d => d
      ? d.toLocaleDateString('es-CO', { day:'numeric', month:'short', year:'numeric' })
      : null;

    this.el.innerHTML = `
      <div id="drp-modal">
        <div id="drp-header">
          <div id="drp-tabs">
            <button class="drp-tab ${this.selecting === 'start' ? 'active' : ''}" type="button" data-action="tab-dep">✈ Salida</button>
            <button class="drp-tab ${this.selecting === 'end' ? 'active' : ''}" type="button" data-action="tab-arr">🏁 Llegada</button>
          </div>
          <button id="drp-close" type="button" data-action="close">✕</button>
        </div>

        <div id="drp-summary">
          <div class="drp-summary-item ${this.selecting === 'start' ? 'active' : ''}">
            <span class="drp-sum-label">Salida</span>
            <span class="drp-sum-val">${this.startDate ? `${fmt(this.startDate)} · ${this.departureTime}` : 'Selecciona una fecha'}</span>
          </div>
          <div class="drp-summary-arrow">→</div>
          <div class="drp-summary-item ${this.selecting === 'end' ? 'active' : ''}">
            <span class="drp-sum-label">Llegada</span>
            <span class="drp-sum-val">${this.endDate ? `${fmt(this.endDate)} · ${this.arrivalTime}` : 'Selecciona una fecha'}</span>
          </div>
        </div>

        <div id="drp-calendars">
          <div class="drp-month">${renderMonth(this.leftMonth)}</div>
          <div class="drp-divider-v"></div>
          <div class="drp-month">${renderMonth(this.rightMonth)}</div>
        </div>

        <div id="drp-times">
          <div class="drp-time-block">
            <span class="drp-time-label">Hora de salida</span>
            <input type="time" id="drp-t-dep" value="${this.departureTime}" data-action="time-dep"/>
          </div>
          <div class="drp-time-block">
            <span class="drp-time-label">Hora de llegada</span>
            <input type="time" id="drp-t-arr" value="${this.arrivalTime}" ${!this.endDate ? 'disabled' : ''} data-action="time-arr"/>
          </div>
        </div>

        <div id="drp-footer">
          <span id="drp-err"></span>
          <button class="drp-btn-sec" type="button" data-action="close">Cancelar</button>
          <button class="drp-btn-pri" type="button" data-action="confirm">Confirmar</button>
        </div>
      </div>
    `;

    this._bindEvents();
  }

  _bindEvents() {
    this.el.addEventListener('click', (e) => {
      const action = e.target.closest('[data-action]')?.dataset.action;
      const dateEl = e.target.closest('[data-date]');

      if (action === 'close')    { this.close(); return; }
      if (action === 'confirm')  { this._confirm(); return; }
      if (action === 'tab-dep')  { this.selecting = 'start'; this._render(); return; }
      if (action === 'tab-arr')  { this.selecting = 'end';   this._render(); return; }
      if (action === 'prev-left')  { this.leftMonth  = new Date(this.leftMonth.getFullYear(),  this.leftMonth.getMonth()  - 1, 1); this._render(); return; }
      if (action === 'next-left')  { this.leftMonth  = new Date(this.leftMonth.getFullYear(),  this.leftMonth.getMonth()  + 1, 1); this._render(); return; }
      if (action === 'prev-right') { this.rightMonth = new Date(this.rightMonth.getFullYear(), this.rightMonth.getMonth() - 1, 1); this._render(); return; }
      if (action === 'next-right') { this.rightMonth = new Date(this.rightMonth.getFullYear(), this.rightMonth.getMonth() + 1, 1); this._render(); return; }

      if (dateEl && dateEl.dataset.date) {
        const clicked = new Date(dateEl.dataset.date + 'T00:00:00');
        if (this.selecting === 'start' || (this.startDate && this.endDate)) {
          this.startDate = clicked;
          this.endDate   = null;
          this.selecting = 'end';
        } else {
          if (clicked <= this.startDate) {
            this.startDate = clicked;
            this.endDate   = null;
            this.selecting = 'end';
          } else {
            this.endDate   = clicked;
            this.selecting = 'start';
          }
        }
        this._render();
      }

      if (e.target === this.el) this.close();
    });

    this.el.addEventListener('mouseover', (e) => {
      const dateEl = e.target.closest('[data-date]');
      if (dateEl && this.startDate && !this.endDate) {
        const h = new Date(dateEl.dataset.date + 'T00:00:00');
        if (h.getTime() !== (this.hoverDate?.getTime())) {
          this.hoverDate = h;
          this._render();
        }
      }
    });

    this.el.addEventListener('change', (e) => {
      const action = e.target.dataset.action;
      if (action === 'time-dep') { this.departureTime = e.target.value; this._render(); }
      if (action === 'time-arr') { this.arrivalTime   = e.target.value; this._render(); }
    });
  }

  _confirm() {
    if (!this.startDate || !this.endDate) {
      document.getElementById('drp-err').textContent = 'Selecciona ambas fechas para continuar.';
      return;
    }
    const dep = `${this.startDate.toISOString().split('T')[0]} ${this.departureTime}`;
    const arr = `${this.endDate.toISOString().split('T')[0]} ${this.arrivalTime}`;
    if (this.startDate.getTime() === this.endDate.getTime() && this.departureTime >= this.arrivalTime) {
      document.getElementById('drp-err').textContent = 'La hora de llegada debe ser posterior.';
      return;
    }
    this.onConfirm(dep, arr);
    this.close();
  }

  _updateSummary() { this._render(); }
  _renderAll()     { this._render(); }

  open() {
    this.el.style.display = 'flex';
    requestAnimationFrame(() => this.el.classList.add('open'));
    document.body.style.overflow = 'hidden';
  }

  close() {
    this.el.classList.remove('open');
    setTimeout(() => { this.el.style.display = 'none'; }, 250);
    document.body.style.overflow = '';
  }
}