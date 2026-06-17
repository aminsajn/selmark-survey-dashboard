/* ============================================================
   SELMARK SURVEY ENGINE
   Shared rendering & navigation engine for both surveys.
   Requires: config.js loaded before this script.
   Usage:
     window.SURVEY_ID  = 'lingerie-swim';   (set in each survey HTML)
     window.SCREENS    = [...];              (set in survey questions file)
     SurveyEngine.init();
   ============================================================ */

const SurveyEngine = (() => {

  // ── State ────────────────────────────────────────────────
  const state = {
    answers: {},
    currentIdx: 0,       // index into visibleScreens
    visibleScreens: [],
    respondentId: null,
    sessionId: null,
    productShown: {},
    startTime: null,
    dbRowId: null,
    submitted: false,
  };

  // ── Utility ──────────────────────────────────────────────
  function uuid() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
      const r = Math.random() * 16 | 0;
      return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
  }
  function shuffle(arr) {
    const a = [...arr];
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }
  function getParam(name) {
    return new URLSearchParams(window.location.search).get(name);
  }
  function setAnswer(id, val) {
    state.answers[id] = val;
    saveLocal();
  }
  function getAnswer(id) { return state.answers[id]; }

  // ── Product randomization ─────────────────────────────────
  // Each category has 3 triads. One triad is randomly selected per respondent.
  // A triad contains exactly 1 Selmark + 1 aspirational + 1 low competitor image.
  // The 3 images of the chosen triad are shown in random order.
  function assignProducts() {
    const sid = window.SURVEY_ID;
    if (!CONFIG.products[sid]) return;
    const cats = Object.keys(CONFIG.products[sid]);
    cats.forEach(cat => {
      const data = CONFIG.products[sid][cat];
      if (data.triads && data.triads.length) {
        // Pick one random triad, then shuffle its 3 images
        const triadIdx = Math.floor(Math.random() * data.triads.length);
        const triad = data.triads[triadIdx];
        state.productShown[cat] = shuffle([...triad]);
        // Record which triad was shown (for analysis)
        state.productShown[cat + '_triad'] = triadIdx + 1;
      }
    });
  }

  // ── Visible screens computation ───────────────────────────
  function computeVisible() {
    state.visibleScreens = (window.SCREENS || []).filter(s => {
      if (typeof s.condition === 'function') return s.condition(state.answers);
      return true;
    });
  }
  function totalScreens() { return state.visibleScreens.length; }
  function currentScreen() { return state.visibleScreens[state.currentIdx]; }

  // ── Local storage ─────────────────────────────────────────
  function saveLocal() {
    try {
      localStorage.setItem('selmark_' + window.SURVEY_ID, JSON.stringify({
        answers: state.answers,
        currentIdx: state.currentIdx,
        productShown: state.productShown,
        sessionId: state.sessionId,
        dbRowId: state.dbRowId,
      }));
    } catch(e) {}
  }
  function loadLocal() {
    try {
      const d = JSON.parse(localStorage.getItem('selmark_' + window.SURVEY_ID) || 'null');
      if (d && d.sessionId) {
        state.answers     = d.answers || {};
        state.currentIdx  = d.currentIdx || 0;
        state.productShown= d.productShown || {};
        state.sessionId   = d.sessionId;
        state.dbRowId     = d.dbRowId || null;
        return true;
      }
    } catch(e) {}
    return false;
  }

  // ── Supabase helpers ──────────────────────────────────────
  let _sb = null;
  function getSB() {
    if (!_sb && window.supabase && CONFIG.supabase.url !== 'TU_SUPABASE_URL') {
      _sb = window.supabase.createClient(CONFIG.supabase.url, CONFIG.supabase.anonKey);
    }
    return _sb;
  }
  async function dbUpsert(extra = {}) {
    const sb = getSB();
    if (!sb) return;
    try {
      const payload = {
        id: state.dbRowId,           // UUID generado en cliente — permite upsert sin SELECT
        survey_id: window.SURVEY_ID,
        respondent_id: state.respondentId,
        session_id: state.sessionId,
        answers: state.answers,
        product_shown: state.productShown,
        ...extra,
      };
      await sb.from('survey_responses').upsert(payload, { onConflict: 'id' });
    } catch(e) { console.warn('DB error', e); }
  }

  // ── Progress bar ──────────────────────────────────────────
  function updateProgress() {
    const pct = totalScreens() > 1
      ? Math.round((state.currentIdx / (totalScreens() - 1)) * 100)
      : 100;
    const bar = document.getElementById('progress-bar');
    const lbl = document.getElementById('progress-label');
    if (bar) bar.style.width = pct + '%';
    if (lbl) lbl.textContent = pct + '%';
  }

  // ── Render ────────────────────────────────────────────────
  function render(direction) {
    computeVisible();
    updateProgress();
    const sc = currentScreen();
    if (!sc) return;

    const container = document.getElementById('screen-container');
    const oldEl = container.querySelector('.screen');

    const newEl = document.createElement('div');
    newEl.className = 'screen';
    newEl.innerHTML = buildScreenHTML(sc);

    if (oldEl) {
      const outClass = direction === 'back' ? 'slide-out-right' : 'slide-out-left';
      const inClass  = direction === 'back' ? 'slide-in-left'  : 'slide-in-right';
      oldEl.classList.add(outClass);
      newEl.classList.add(inClass);
      setTimeout(() => { if (container.contains(oldEl)) container.removeChild(oldEl); }, 230);
    }
    container.appendChild(newEl);
    bindInteractions(sc, newEl);

    // footer visibility
    const footer = document.getElementById('nav-footer');
    if (footer) footer.style.display = (sc.type === 'intro' || sc.type === 'thanks') ? 'none' : '';

    const prevBtn = document.getElementById('btn-prev');
    if (prevBtn) prevBtn.disabled = state.currentIdx === 0;

    const nextBtn = document.getElementById('btn-next');
    if (nextBtn) {
      // Show "Enviar" on the last question screen (penultimate screen, before thanks)
      const vis = state.visibleScreens;
      let lastQScreen = vis.length - 1;
      for (let i = vis.length - 1; i >= 0; i--) {
        if (vis[i].type !== 'thanks' && vis[i].type !== 'intro') { lastQScreen = i; break; }
      }
      nextBtn.textContent = state.currentIdx === lastQScreen ? 'Enviar' : 'Siguiente';
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
    saveLocal();
  }

  // ── Screen HTML builder ───────────────────────────────────
  function buildScreenHTML(sc) {
    if (sc.type === 'intro')  return buildIntro(sc);
    if (sc.type === 'thanks') return buildThanks(sc);

    let html = '';
    if (sc.section) html += `<div class="section-label">${sc.section}</div>`;

    (sc.questions || []).forEach(q => {
      html += `<div class="question-block" id="qblock_${q.id}">`;
      if (q.num) html += `<div class="question-num">Pregunta ${q.num}</div>`;
      html += `<div class="question-text">${q.text}</div>`;
      if (q.sub) html += `<div class="question-sub">${q.sub}</div>`;
      html += buildQuestionInput(q);
      html += '</div>';
    });
    return html;
  }

  function buildIntro(sc) {
    return `<div class="intro-screen">
      <h1>${sc.title}</h1>
      ${sc.definition ? `<div class="definition-box"><strong>Definición</strong>${sc.definition}</div>` : ''}
      ${(sc.paragraphs || []).map(p => `<p>${p}</p>`).join('')}
      <button class="btn-start" onclick="SurveyEngine.next()">Comenzar</button>
    </div>`;
  }

  function buildThanks(sc) {
    return `<div class="thanks-screen">
      <div class="thanks-icon">✓</div>
      <h1>${sc.title || '¡Gracias por participar!'}</h1>
      ${(sc.paragraphs || []).map(p => `<p>${p}</p>`).join('')}
    </div>`;
  }

  function buildQuestionInput(q) {
    const saved = getAnswer(q.id);
    switch (q.type) {
      case 'text':    return buildText(q, saved);
      case 'number':  return buildNumber(q, saved);
      case 'open':    return buildOpen(q, saved);
      case 'single':  return buildSingle(q, saved);
      case 'multi':   return buildMulti(q, saved);
      case 'scale_block': return buildScaleBlock(q, saved);
      case 'dichotomy':   return buildDichotomy(q, saved);
      case 'ranking':     return buildRanking(q, saved);
      case 'color_pick':  return buildColorPick(q, saved);
      case 'color_combos':return buildColorCombos(q, saved);
      case 'product_select': return buildProductSelect(q, saved);
      default: return '';
    }
  }

  function buildText(q, saved) {
    return `<input class="input-text" type="text" id="inp_${q.id}"
      value="${saved || ''}"
      placeholder="${q.placeholder || ''}"
      oninput="SurveyEngine.setAns('${q.id}', this.value)">`;
  }
  function buildNumber(q, saved) {
    return `<input class="input-text" type="number" id="inp_${q.id}"
      value="${saved || ''}"
      min="${q.min || ''}" max="${q.max || ''}"
      placeholder="${q.placeholder || ''}"
      oninput="SurveyEngine.setAns('${q.id}', this.value)">`;
  }
  function buildOpen(q, saved) {
    return `<textarea class="input-textarea" id="inp_${q.id}"
      placeholder="${q.placeholder || ''}"
      oninput="SurveyEngine.setAns('${q.id}', this.value)">${saved || ''}</textarea>`;
  }

  // HTML-safe attribute encoding
  function ea(s) { return String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;'); }

  function buildSingle(q, saved) {
    return `<div class="choices" id="choices_${q.id}">
      ${(q.options || []).map((opt, idx) => {
        const val = typeof opt === 'object' ? opt.value : opt;
        const lbl = typeof opt === 'object' ? opt.label : opt;
        const sel = saved === val;
        const hasOpen = typeof opt === 'object' && opt.open;
        return `<div class="choice-card ${sel ? 'selected' : ''}" data-val="${ea(val)}" data-qid="${q.id}"
            onclick="SurveyEngine.selectSingle(this.dataset.qid, this.dataset.val, this)">
            <span class="radio-dot"></span>
            <span>${lbl}</span>
          </div>
          ${hasOpen ? `<input class="inline-open" type="text"
            placeholder="Especifica..." style="${sel ? '' : 'display:none'}"
            value="${ea(getAnswer(q.id + '_open') || '')}"
            oninput="SurveyEngine.setAns('${q.id}_open', this.value)">` : ''}`;
      }).join('')}
    </div>`;
  }

  function buildMulti(q, saved) {
    const sel = Array.isArray(saved) ? saved : [];
    return `<div class="choices" id="choices_${q.id}">
      ${(q.options || []).map(opt => {
        const val = typeof opt === 'object' ? opt.value : opt;
        const lbl = typeof opt === 'object' ? opt.label : opt;
        const isSelected = sel.includes(val);
        const hasOpen = typeof opt === 'object' && opt.open;
        const openVal = getAnswer(q.id + '_open_' + val) || '';
        return `<div class="choice-card ${isSelected ? 'selected' : ''}" data-val="${ea(val)}" data-qid="${q.id}"
            onclick="SurveyEngine.toggleMulti(this.dataset.qid, this.dataset.val, this)">
            <span class="check-box"></span>
            <span>${lbl}</span>
          </div>
          ${hasOpen ? `<input class="inline-open" type="text"
            placeholder="Especifica..." style="${isSelected ? '' : 'display:none'}"
            value="${ea(openVal)}"
            oninput="SurveyEngine.setAns('${q.id}_open_${ea(val)}', this.value)">` : ''}`;
      }).join('')}
    </div>`;
  }

  function buildScaleBlock(q, saved) {
    // q.rows = [{id, text}]
    const labels = ['', '1\nTotal.\nen des.', '2', '3', '4', '5\nTotal.\nde ac.'];
    return `<div class="scale-block" id="scaleblock_${q.id}">
      <div class="scale-block-header">
        <div class="label-left">Afirmación</div>
        ${[1,2,3,4,5].map(n => `<div>${n}</div>`).join('')}
      </div>
      ${(q.rows || []).map(row => {
        const rowSaved = getAnswer(row.id);
        return `<div class="scale-block-row ${rowSaved ? 'scale-row-answered' : ''}" id="sbrow_${row.id}">
          <div class="row-text">${row.text}</div>
          ${[1,2,3,4,5].map(n =>
            `<button class="scale-btn ${rowSaved == n ? 'selected' : ''}"
              onclick="SurveyEngine.setScale('${row.id}', ${n}, this)">${n}</button>`
          ).join('')}
        </div>`;
      }).join('')}
    </div>`;
  }

  function buildDichotomy(q, saved) {
    // q.pairs = [{id, a, b}]
    const answers = saved || {};
    return `<div class="dichotomy-list" id="dichot_${q.id}">
      ${(q.pairs || []).map(pair => {
        const v = answers[pair.id];
        return `<div class="dichotomy-row">
          <div class="dichotomy-btn ${v === 'a' ? 'selected' : ''}"
            onclick="SurveyEngine.setDichotomy('${q.id}', '${pair.id}', 'a', this.parentElement)">${pair.a}</div>
          <div class="dichotomy-vs">vs</div>
          <div class="dichotomy-btn ${v === 'b' ? 'selected' : ''}"
            onclick="SurveyEngine.setDichotomy('${q.id}', '${pair.id}', 'b', this.parentElement)">${pair.b}</div>
        </div>`;
      }).join('')}
    </div>`;
  }

  function buildRanking(q, saved) {
    // saved = { channel: rank } object
    const ranks = saved || {};
    const items = [...(q.options || [])];
    // Sort by saved rank for display
    const sorted = [...items].sort((a,b) => {
      const ra = ranks[a] || 999, rb = ranks[b] || 999;
      return ra - rb;
    });
    const maxRank = Object.values(ranks).filter(r => r > 0).length;
    return `<div>
      <div class="rank-instruction">Haz clic en los canales en orden de mayor a menor uso (el primero que hagas clic será el más utilizado).</div>
      <div class="rank-list" id="ranklist_${q.id}">
        ${sorted.map(item => {
          const r = ranks[item];
          return `<div class="rank-item ${r ? 'ranked' : ''}" data-item="${item}"
              data-qid="${q.id}" data-item="${ea(item)}"
              onclick="SurveyEngine.toggleRank(this.dataset.qid, this.dataset.item, this)">
              <div class="rank-badge">${r || ''}</div>
              <span>${item}</span>
            </div>`;
        }).join('')}
      </div>
    </div>`;
  }

  // Full 80-colour palette (8 rows × 10 cols), organized by hue family
  const COLOR_PALETTE = [
    // Row 1 – Blacks & Grays
    {hex:'#FFFFFF',name:'Blanco'},      {hex:'#F5F5F5',name:'Gris muy claro'}, {hex:'#E0E0E0',name:'Gris perla'},
    {hex:'#BDBDBD',name:'Gris claro'},  {hex:'#9E9E9E',name:'Gris medio'},     {hex:'#757575',name:'Gris'},
    {hex:'#616161',name:'Grafito'},     {hex:'#424242',name:'Antracita'},       {hex:'#212121',name:'Negro suave'}, {hex:'#000000',name:'Negro'},
    // Row 2 – Nudes & Browns
    {hex:'#FFF8F0',name:'Marfil'},      {hex:'#F5ECD7',name:'Crema'},          {hex:'#EDE0CF',name:'Beige claro'},
    {hex:'#D4BEA6',name:'Beige'},       {hex:'#C2A882',name:'Arena'},          {hex:'#A08060',name:'Camel'},
    {hex:'#8B6347',name:'Marrón'},      {hex:'#5C3A1E',name:'Marrón oscuro'},  {hex:'#3E2009',name:'Café'}, {hex:'#E8C4A0',name:'Nude'},
    // Row 3 – Pinks & Blush
    {hex:'#FFE4EE',name:'Rosa pálido'}, {hex:'#FFD1DC',name:'Blush'},          {hex:'#FFB3C6',name:'Rosa claro'},
    {hex:'#FF8FAB',name:'Rosa'},        {hex:'#FF69B4',name:'Rosa fuerte'},     {hex:'#FF1493',name:'Rosa intenso'},
    {hex:'#E91E8C',name:'Fucsia'},      {hex:'#C2185B',name:'Rosa oscuro'},     {hex:'#AD1457',name:'Rosa profundo'}, {hex:'#880E4F',name:'Rosa vino'},
    // Row 4 – Reds & Burgundy
    {hex:'#FFCDD2',name:'Rojo pálido'}, {hex:'#EF9A9A',name:'Rojo claro'},     {hex:'#E57373',name:'Coral'},
    {hex:'#EF5350',name:'Rojo vivo'},   {hex:'#F44336',name:'Rojo'},           {hex:'#CC2244',name:'Rojo oscuro'},
    {hex:'#B71C1C',name:'Rojo intenso'},{hex:'#7D1C4A',name:'Burdeos'},        {hex:'#5D1049',name:'Granate'}, {hex:'#4A0E2C',name:'Vino'},
    // Row 5 – Oranges, Salmon & Yellows
    {hex:'#FFF3E0',name:'Melocotón claro'},{hex:'#FFE0B2',name:'Melocotón'},   {hex:'#FFCC80',name:'Albaricoque'},
    {hex:'#FFA726',name:'Naranja claro'},{hex:'#FF8C42',name:'Naranja'},       {hex:'#FA8072',name:'Salmón'},
    {hex:'#FFD700',name:'Dorado'},      {hex:'#FFDB58',name:'Mostaza claro'},  {hex:'#F9A825',name:'Mostaza'}, {hex:'#E65100',name:'Naranja quemado'},
    // Row 6 – Greens
    {hex:'#F1F8E9',name:'Verde pálido'},{hex:'#DCEDC8',name:'Menta claro'},    {hex:'#C5E1A5',name:'Menta'},
    {hex:'#9CAF88',name:'Salvia'},      {hex:'#8BC34A',name:'Verde lima'},      {hex:'#4CAF50',name:'Verde'},
    {hex:'#388E3C',name:'Verde medio'}, {hex:'#2E7D32',name:'Verde oscuro'},   {hex:'#1B5E20',name:'Bosque'}, {hex:'#40B0A0',name:'Turquesa'},
    // Row 7 – Blues
    {hex:'#E3F2FD',name:'Azul pálido'}, {hex:'#B0C4DE',name:'Azul hielo'},     {hex:'#87CEEB',name:'Azul cielo'},
    {hex:'#64B5F6',name:'Azul claro'},  {hex:'#42A5F5',name:'Azul'},           {hex:'#2B7BB9',name:'Azul medio'},
    {hex:'#1565C0',name:'Azul intenso'},{hex:'#1B3A5C',name:'Azul marino'},    {hex:'#006994',name:'Azul petróleo'}, {hex:'#004D40',name:'Verde azulado'},
    // Row 8 – Purples & Lavender
    {hex:'#F3E5F5',name:'Lavanda pálida'},{hex:'#E8D5F0',name:'Lavanda'},      {hex:'#C8A2C8',name:'Lila'},
    {hex:'#CE93D8',name:'Malva'},       {hex:'#BA68C8',name:'Violeta claro'},  {hex:'#AB47BC',name:'Violeta'},
    {hex:'#8E24AA',name:'Morado'},      {hex:'#6A1B9A',name:'Ciruela'},        {hex:'#4A148C',name:'Morado oscuro'}, {hex:'#1A0030',name:'Morado noche'},
  ];

  // Alias used by color_combos (same palette)
  const FASHION_COLORS = COLOR_PALETTE;

  // ── HSV Colour Wheel helpers ──────────────────────────────
  function _hsvToRgb(h, s, v) {
    const c = v*s, x = c*(1-Math.abs((h/60)%2-1)), m = v-c;
    let r=0, g=0, b=0;
    if      (h<60)  {r=c;g=x;b=0;}
    else if (h<120) {r=x;g=c;b=0;}
    else if (h<180) {r=0;g=c;b=x;}
    else if (h<240) {r=0;g=x;b=c;}
    else if (h<300) {r=x;g=0;b=c;}
    else            {r=c;g=0;b=x;}
    return [Math.round((r+m)*255), Math.round((g+m)*255), Math.round((b+m)*255)];
  }
  function _rgbToHex(r,g,b) {
    return '#'+[r,g,b].map(v=>v.toString(16).padStart(2,'0')).join('');
  }

  function cpDrawWheel(qid) {
    const canvas = document.getElementById('cpw_canvas_'+qid);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const W = canvas.width, H = canvas.height;
    const cx = W/2, cy = H/2, r = Math.min(cx,cy)-3;
    const bright = parseInt(document.getElementById('cpw_bright_'+qid)?.value ?? 100)/100;

    const img = ctx.createImageData(W,H);
    const d = img.data;
    for (let y=0;y<H;y++) {
      for (let x=0;x<W;x++) {
        const dx=x-cx, dy=y-cy;
        const dist=Math.sqrt(dx*dx+dy*dy);
        const i=(y*W+x)*4;
        if (dist<=r) {
          const hue=((Math.atan2(dy,dx)*180/Math.PI)+360)%360;
          const sat=dist/r;
          const [rr,gg,bb]=_hsvToRgb(hue,sat,bright);
          d[i]=rr; d[i+1]=gg; d[i+2]=bb; d[i+3]=255;
        }
      }
    }
    ctx.putImageData(img,0,0);
    ctx.beginPath(); ctx.arc(cx,cy,r,0,2*Math.PI);
    ctx.strokeStyle='#C8DCF0'; ctx.lineWidth=2; ctx.stroke();

    // Draw markers for selected colors
    const sel = Array.isArray(getAnswer(qid)) ? getAnswer(qid) : [];
    sel.forEach((c,si) => {
      if (!c || c.h===undefined) return;
      const ang = c.h*Math.PI/180;
      const rad = (c.s/100)*r;
      const px=cx+Math.cos(ang)*rad, py=cy+Math.sin(ang)*rad;
      ctx.beginPath(); ctx.arc(px,py,9,0,2*Math.PI);
      ctx.fillStyle=c.hex; ctx.fill();
      ctx.strokeStyle='#fff'; ctx.lineWidth=2.5; ctx.stroke();
      ctx.beginPath(); ctx.arc(px,py,9,0,2*Math.PI);
      ctx.strokeStyle='rgba(0,0,0,.25)'; ctx.lineWidth=1; ctx.stroke();
      ctx.fillStyle='#fff'; ctx.font='bold 9px sans-serif';
      ctx.textAlign='center'; ctx.textBaseline='middle';
      ctx.fillText(si+1,px,py);
    });
  }

  function buildColorPick(q, saved) {
    const sel = Array.isArray(saved) ? saved.slice(0,3) : [];
    const slots = [0,1,2].map(i => {
      const c = sel[i]; const filled = c && c.hex;
      return `<div class="cpw-slot ${filled?'filled':''} ${i===0?'active':''}"
          id="cpwslot_${q.id}_${i}" style="${filled?'background:'+c.hex:''}"
          onclick="SurveyEngine.cpActivateSlot('${q.id}',${i})"
          title="${filled?(c.name||c.hex):'Color '+(i+1)}">
          <span class="cpw-slot-num">${i+1}</span>
          ${filled?`<button class="cpp-remove" onclick="event.stopPropagation();SurveyEngine.removeCPColor('${q.id}',${i})">×</button>`:''}
        </div>`;
    }).join('');

    return `<div class="cpw-wrap" id="cpw_${q.id}" data-active-slot="0">
      <div class="cpw-instructions">Activa un slot tocándolo y luego elige el color en la rueda. Selecciona los 3 colores.</div>
      <div class="cpw-slots" id="cpwslots_${q.id}">${slots}</div>
      <div class="cpw-canvas-wrap">
        <canvas id="cpw_canvas_${q.id}" class="cpw-canvas" width="280" height="280"></canvas>
      </div>
      <div class="cpw-bright-row">
        <span class="cpw-bright-label">Brillo</span>
        <input type="range" id="cpw_bright_${q.id}" class="cpw-bright-slider"
          min="10" max="100" value="100"
          oninput="SurveyEngine.cpBrightnessChange('${q.id}')">
        <span id="cpw_bright_val_${q.id}" class="cpw-bright-val">100%</span>
      </div>
    </div>`;
  }

  function buildColorCombos(q, saved) {
    const combos = Array.isArray(saved) && saved.length >= 3 ? saved
      : [{colors:['','','']},{colors:['','','']},{colors:['','','']}];
    const grid = FASHION_COLORS.map(c =>
      `<div class="palette-swatch" style="background:${c.hex}" title="${c.name}"
        data-hex="${c.hex}"
        onclick="SurveyEngine.paletteClick('${q.id}', '${c.hex}', this)"></div>`
    ).join('');

    const comboRows = combos.map((combo, ci) =>
      buildComboRow(q.id, combo, ci)
    ).join('');

    return `<div id="ccombos_${q.id}" data-qid="${q.id}">
      <div class="combos-label">Haz clic en un color de la paleta para añadirlo a la combinación activa (resaltada). Necesitas crear al menos 3 combinaciones de 3 colores cada una.</div>
      <div class="palette-grid">${grid}</div>
      <div class="combo-list" id="combolist_${q.id}">${comboRows}</div>
      <button class="btn-add-combo" onclick="SurveyEngine.addCombo('${q.id}')">+ Añadir combinación</button>
    </div>`;
  }

  function buildComboRow(qid, combo, ci) {
    const dots = (combo.colors || ['','','']).map((col, di) =>
      `<div class="combo-dot ${col ? 'filled' : ''}" data-di="${di}"
        style="${col ? 'background:' + col : ''}"
        onclick="SurveyEngine.comboSlotClick('${qid}',${ci},${di})"></div>`
    ).join('');
    return `<div class="combo-row" id="comborow_${qid}_${ci}" data-ci="${ci}" data-active="false">
      <div class="combo-idx">${ci+1}</div>
      <div class="combo-swatches">${dots}</div>
      <button class="combo-remove" onclick="SurveyEngine.removeCombo('${qid}',${ci})" title="Eliminar">×</button>
    </div>`;
  }

  function buildProductSelect(q, saved) {
    const cats = Array.isArray(q.categories) ? q.categories : [q.category];
    let html = `<div class="product-intro">${q.intro || 'A continuación verás una selección de productos. Fíjate bien en cada uno antes de responder.'}</div>`;
    cats.forEach(cat => {
      const imgs = state.productShown[cat] || [];
      if (imgs.length) {
        html += `<div class="product-grid" id="pgrid_${q.id}_${cat}">
          ${imgs.map(img => {
            const isSelected = saved && saved[cat] === img.id;
            return `<div class="product-card ${isSelected ? 'selected' : ''}"
                data-imgid="${img.id}" data-cat="${cat}"
                onclick="SurveyEngine.selectProduct('${q.id}','${cat}','${img.id}',this)">
                <img class="product-img" src="${img.src}" alt="${img.label}"
                  onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">
                <div class="product-placeholder" style="display:none">${img.label}</div>
                <div class="product-letter">${String.fromCharCode(65 + imgs.indexOf(img))}</div>
              </div>`;
          }).join('')}
        </div>
        <p class="product-hint">Haz clic en el producto que más te guste</p>`;
      }
    });
    return html;
  }

  // ── Interaction handlers (exposed globally) ───────────────
  function selectSingle(qid, val, el) {
    const wrap = document.getElementById('choices_' + qid);
    if (!wrap) return;
    wrap.querySelectorAll('.choice-card').forEach(c => c.classList.remove('selected'));
    el.classList.add('selected');
    // hide all inline-open fields, then show the one after this element
    wrap.querySelectorAll('.inline-open').forEach(inp => inp.style.display = 'none');
    const sib = el.nextElementSibling;
    if (sib && sib.classList.contains('inline-open')) sib.style.display = '';
    setAnswer(qid, val);
  }

  function toggleMulti(qid, val, el) {
    let arr = Array.isArray(getAnswer(qid)) ? [...getAnswer(qid)] : [];
    if (arr.includes(val)) {
      arr = arr.filter(v => v !== val);
      el.classList.remove('selected');
      const openInp = document.getElementById('open_' + qid + '_' + val);
      if (openInp) openInp.style.display = 'none';
    } else {
      arr.push(val);
      el.classList.add('selected');
      const sib = el.nextElementSibling;
      if (sib && sib.classList.contains('inline-open')) sib.style.display = '';
    }
    setAnswer(qid, arr);
  }

  function setScale(rowId, val, btn) {
    const row = document.getElementById('sbrow_' + rowId);
    if (!row) return;
    row.querySelectorAll('.scale-btn').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
    row.classList.add('scale-row-answered');
    setAnswer(rowId, val);
  }

  function setDichotomy(qid, pairId, side, rowEl) {
    rowEl.querySelectorAll('.dichotomy-btn').forEach(b => b.classList.remove('selected'));
    rowEl.querySelectorAll('.dichotomy-btn')[side === 'a' ? 0 : 1].classList.add('selected');
    const cur = getAnswer(qid) || {};
    cur[pairId] = side;
    setAnswer(qid, cur);
  }

  function toggleRank(qid, item, el) {
    const cur = getAnswer(qid) || {};
    if (cur[item]) {
      const removedRank = cur[item];
      delete cur[item];
      // re-number remaining
      Object.keys(cur).forEach(k => { if (cur[k] > removedRank) cur[k]--; });
    } else {
      const nextRank = Object.keys(cur).length + 1;
      cur[item] = nextRank;
    }
    setAnswer(qid, cur);
    // re-render ranks
    const list = document.getElementById('ranklist_' + qid);
    if (!list) return;
    list.querySelectorAll('.rank-item').forEach(itemEl => {
      const it = itemEl.dataset.item;
      const badge = itemEl.querySelector('.rank-badge');
      const r = cur[it];
      badge.textContent = r || '';
      itemEl.classList.toggle('ranked', !!r);
    });
  }

  function updateColorPick(qid, slotIdx, hexVal) {
    const r = parseInt(hexVal.slice(1,3),16);
    const g = parseInt(hexVal.slice(3,5),16);
    const b = parseInt(hexVal.slice(5,7),16);
    _updateColorSlot(qid, slotIdx, hexVal, r, g, b);
  }

  function updateColorRGB(qid, slotIdx, channel, val) {
    const savedColors = Array.isArray(getAnswer(qid)) ? [...getAnswer(qid)] : [{},{},{}];
    while(savedColors.length < 3) savedColors.push({});
    const c = savedColors[slotIdx] || {};
    const r = channel === 'r' ? val : (c.r !== undefined ? c.r : 255);
    const g = channel === 'g' ? val : (c.g !== undefined ? c.g : 255);
    const b = channel === 'b' ? val : (c.b !== undefined ? c.b : 255);
    const hex = '#' + [r,g,b].map(v => v.toString(16).padStart(2,'0')).join('');
    // sync native color input
    const native = document.getElementById('cinput_' + qid + '_' + slotIdx);
    if (native) native.value = hex;
    _updateColorSlot(qid, slotIdx, hex, r, g, b);
  }

  function _updateColorSlot(qid, slotIdx, hex, r, g, b) {
    const swatch = document.getElementById('cswatch_' + qid + '_' + slotIdx);
    const hexDisp = document.getElementById('chex_' + qid + '_' + slotIdx);
    const rSlide = document.getElementById('rslide_' + qid + '_' + slotIdx);
    const gSlide = document.getElementById('gslide_' + qid + '_' + slotIdx);
    const bSlide = document.getElementById('bslide_' + qid + '_' + slotIdx);
    const rVal = document.getElementById('rval_' + qid + '_' + slotIdx);
    const gVal = document.getElementById('gval_' + qid + '_' + slotIdx);
    const bVal = document.getElementById('bval_' + qid + '_' + slotIdx);
    if (swatch)  swatch.style.background = hex;
    if (hexDisp) hexDisp.textContent = hex.toUpperCase();
    if (rSlide)  rSlide.value = r; if (rVal) rVal.textContent = r;
    if (gSlide)  gSlide.value = g; if (gVal) gVal.textContent = g;
    if (bSlide)  bSlide.value = b; if (bVal) bVal.textContent = b;
    const savedColors = Array.isArray(getAnswer(qid)) ? [...getAnswer(qid)] : [{},{},{}];
    while(savedColors.length < 3) savedColors.push({});
    savedColors[slotIdx] = {hex, r, g, b};
    setAnswer(qid, savedColors);
  }

  // Active combo tracking
  let _activeCombo = {};  // qid → { ci, di (next empty slot) }

  // ── HSV Wheel interaction handlers ───────────────────────
  function cpActivateSlot(qid, idx) {
    const wrap = document.getElementById('cpw_'+qid);
    if (wrap) wrap.dataset.activeSlot = idx;
    [0,1,2].forEach(i =>
      document.getElementById('cpwslot_'+qid+'_'+i)?.classList.toggle('active', i===idx)
    );
  }

  function cpBrightnessChange(qid) {
    const val = document.getElementById('cpw_bright_'+qid)?.value ?? 100;
    const disp = document.getElementById('cpw_bright_val_'+qid);
    if (disp) disp.textContent = val+'%';
    // Update hue/sat of already-selected colors with new brightness
    const bright = parseInt(val)/100;
    let sel = Array.isArray(getAnswer(qid)) ? [...getAnswer(qid)] : [];
    let changed = false;
    sel.forEach((c,i) => {
      if (c && c.h!==undefined) {
        const [rr,gg,bb] = _hsvToRgb(c.h, c.s/100, bright);
        sel[i] = {...c, hex:_rgbToHex(rr,gg,bb), v:Math.round(bright*100)};
        changed = true;
      }
    });
    if (changed) { setAnswer(qid, sel); _cpRefreshSlots(qid, sel); }
    cpDrawWheel(qid);
  }

  function _cpPickColor(qid, clientX, clientY) {
    const canvas = document.getElementById('cpw_canvas_'+qid);
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width/rect.width, scaleY = canvas.height/rect.height;
    const cx=canvas.width/2, cy=canvas.height/2, r=Math.min(cx,cy)-3;
    const rawX=(clientX-rect.left)*scaleX, rawY=(clientY-rect.top)*scaleY;
    const dx=rawX-cx, dy=rawY-cy;
    if (Math.sqrt(dx*dx+dy*dy)>r) return;

    const hue=((Math.atan2(dy,dx)*180/Math.PI)+360)%360;
    const sat=Math.sqrt(dx*dx+dy*dy)/r;
    const bright=parseInt(document.getElementById('cpw_bright_'+qid)?.value??100)/100;
    const [rr,gg,bb]=_hsvToRgb(hue,sat,bright);
    const hex=_rgbToHex(rr,gg,bb);

    const wrap=document.getElementById('cpw_'+qid);
    const activeSlot=parseInt(wrap?.dataset.activeSlot??0);

    let sel=Array.isArray(getAnswer(qid))?[...getAnswer(qid)]:[null,null,null];
    while(sel.length<3) sel.push(null);
    sel[activeSlot]={hex, name:hex.toUpperCase(), h:Math.round(hue), s:Math.round(sat*100), v:Math.round(bright*100)};
    setAnswer(qid,sel);
    _cpRefreshSlots(qid,sel);
    cpDrawWheel(qid);

    // Auto-advance to next empty slot
    const nextEmpty=sel.findIndex((c,i)=>i>activeSlot&&!c);
    if (nextEmpty!==-1) cpActivateSlot(qid,nextEmpty);
  }

  function _cpRefreshSlots(qid, sel) {
    [0,1,2].forEach(i => {
      const el=document.getElementById('cpwslot_'+qid+'_'+i);
      if (!el) return;
      const c=sel[i];
      if (c&&c.hex) {
        el.classList.add('filled');
        el.style.background=c.hex;
        el.title=c.name||c.hex;
        if (!el.querySelector('.cpp-remove')) {
          const btn=document.createElement('button');
          btn.className='cpp-remove'; btn.textContent='×';
          btn.onclick=(e)=>{e.stopPropagation();SurveyEngine.removeCPColor(qid,i);};
          el.appendChild(btn);
        }
      } else {
        el.classList.remove('filled');
        el.style.background='';
        el.title='Color '+(i+1);
        el.querySelector('.cpp-remove')?.remove();
      }
    });
  }

  function removeCPColor(qid, idx) {
    let sel=Array.isArray(getAnswer(qid))?[...getAnswer(qid)]:[null,null,null];
    while(sel.length<3) sel.push(null);
    sel[idx]=null;
    setAnswer(qid,sel);
    _cpRefreshSlots(qid,sel);
    cpDrawWheel(qid);
    cpActivateSlot(qid,idx);
  }

  function paletteClick(qid, hex, swatchEl) {
    if (!_activeCombo[qid] || _activeCombo[qid].ci === undefined) {
      // activate first combo
      _setActiveCombo(qid, 0);
    }
    const ac = _activeCombo[qid];
    _fillComboSlot(qid, ac.ci, ac.di, hex);
  }

  function comboSlotClick(qid, ci, di) {
    _setActiveCombo(qid, ci, di);
  }

  function _setActiveCombo(qid, ci, di) {
    // deactivate others
    document.querySelectorAll(`[id^="comborow_${qid}_"]`).forEach(row => {
      row.dataset.active = 'false';
      row.classList.remove('active-combo');
    });
    const row = document.getElementById(`comborow_${qid}_${ci}`);
    if (row) {
      row.dataset.active = 'true';
      row.classList.add('active-combo');
      // find next empty slot starting from di or first empty
      const dots = row.querySelectorAll('.combo-dot');
      const saved = _getCombos(qid);
      const combo = saved[ci] || {colors:['','','']};
      let nextDi = di !== undefined ? di : 0;
      if (di === undefined) {
        nextDi = combo.colors.findIndex(c => !c);
        if (nextDi === -1) nextDi = 0;
      }
      _activeCombo[qid] = {ci, di: nextDi};
      dots.forEach((d,i) => d.classList.toggle('selected-dot', i === nextDi));
    }
  }

  function _fillComboSlot(qid, ci, di, hex) {
    const combos = _getCombos(qid);
    while(combos.length <= ci) combos.push({colors:['','','']});
    if (!combos[ci].colors) combos[ci].colors = ['','',''];
    combos[ci].colors[di] = hex;
    setAnswer(qid, combos);
    // update DOM
    const dot = document.querySelector(`#comborow_${qid}_${ci} .combo-dot:nth-child(${di+1})`);
    if (dot) {
      dot.style.background = hex;
      dot.classList.add('filled');
    }
    // advance to next empty slot
    const nextEmpty = combos[ci].colors.findIndex((c, i) => i > di && !c);
    const nextDi = nextEmpty !== -1 ? nextEmpty : di; // stay on last if full
    _activeCombo[qid] = {ci, di: nextDi};
    const row = document.getElementById(`comborow_${qid}_${ci}`);
    if (row) {
      row.querySelectorAll('.combo-dot').forEach((d,i) =>
        d.classList.toggle('selected-dot', i === nextDi));
    }
  }

  function _getCombos(qid) {
    const saved = getAnswer(qid);
    return Array.isArray(saved) ? saved.map(c => ({colors: c.colors ? [...c.colors] : ['','','']}))
      : [{colors:['','','']},{colors:['','','']},{colors:['','','']}];
  }

  function addCombo(qid) {
    const combos = _getCombos(qid);
    combos.push({colors:['','','']});
    setAnswer(qid, combos);
    const list = document.getElementById('combolist_' + qid);
    if (list) {
      const div = document.createElement('div');
      div.innerHTML = buildComboRow(qid, {colors:['','','']}, combos.length - 1);
      list.appendChild(div.firstElementChild);
    }
    _setActiveCombo(qid, combos.length - 1);
  }

  function removeCombo(qid, ci) {
    let combos = _getCombos(qid);
    if (combos.length <= 3) return; // keep minimum 3
    combos.splice(ci, 1);
    setAnswer(qid, combos);
    const list = document.getElementById('combolist_' + qid);
    if (!list) return;
    // re-render all combo rows
    list.innerHTML = combos.map((c, i) => buildComboRow(qid, c, i)).join('');
    _activeCombo[qid] = undefined;
  }

  function selectProduct(qid, cat, imgId, cardEl) {
    const grid = document.getElementById('pgrid_' + qid + '_' + cat);
    if (grid) grid.querySelectorAll('.product-card').forEach(c => c.classList.remove('selected'));
    cardEl.classList.add('selected');
    const cur = getAnswer(qid) || {};
    cur[cat] = imgId;
    setAnswer(qid, cur);
  }

  // ── Validation ────────────────────────────────────────────
  function validate() {
    const sc = currentScreen();
    if (!sc || sc.type === 'intro' || sc.type === 'thanks') return true;
    let errMsg = '';

    for (const q of (sc.questions || [])) {
      if (q.required === false) continue; // solo se salta si explícitamente required:false
      const val = getAnswer(q.id);
      let ok = false;
      if (q.type === 'text' || q.type === 'number' || q.type === 'open') {
        ok = !!(val && String(val).trim().length > 0);
      } else if (q.type === 'single') {
        ok = !!val;
        // Si la opción seleccionada tiene campo abierto ("Otras"), es obligatorio rellenarlo
        if (ok && val) {
          const selectedOpt = (q.options || []).find(opt =>
            (typeof opt === 'object' ? opt.value : opt) === val
          );
          if (selectedOpt && typeof selectedOpt === 'object' && selectedOpt.open) {
            const openVal = getAnswer(q.id + '_open');
            if (!openVal || !String(openVal).trim()) {
              ok = false;
              errMsg = 'Por favor, especifica tu respuesta en el campo de texto.';
            }
          }
        }
      } else if (q.type === 'multi') {
        ok = Array.isArray(val) && val.length > 0;
        // Si alguna opción seleccionada tiene campo abierto ("Otras"), es obligatorio rellenarlo
        if (ok && Array.isArray(val)) {
          for (const selectedVal of val) {
            const selectedOpt = (q.options || []).find(opt =>
              (typeof opt === 'object' ? opt.value : opt) === selectedVal
            );
            if (selectedOpt && typeof selectedOpt === 'object' && selectedOpt.open) {
              const openVal = getAnswer(q.id + '_open_' + selectedVal);
              if (!openVal || !String(openVal).trim()) {
                ok = false;
                errMsg = 'Por favor, especifica tu respuesta en el campo de texto.';
                break;
              }
            }
          }
        }
      } else if (q.type === 'scale_block') {
        ok = (q.rows || []).every(row => getAnswer(row.id));
      } else if (q.type === 'dichotomy') {
        ok = (q.pairs || []).every(pair => {
          const cur = getAnswer(q.id) || {};
          return !!cur[pair.id];
        });
      } else if (q.type === 'color_pick') {
        const colors = Array.isArray(val) ? val.filter(c => c && c.hex) : [];
        ok = colors.length >= 3;
      } else if (q.type === 'color_combos') {
        const combos = Array.isArray(val) ? val : [];
        ok = combos.length >= 3 && combos.every(c =>
          (c.colors || []).every(col => col));
      } else if (q.type === 'product_select') {
        const ans = val || {};
        const cats = Array.isArray(q.categories) ? q.categories : [q.category];
        ok = cats.every(cat => !!ans[cat]);
      } else {
        ok = true;
      }
      if (!ok) {
        errMsg = 'Por favor, responde esta pregunta antes de continuar.';
        // highlight
        const qblock = document.getElementById('qblock_' + q.id);
        if (qblock) {
          qblock.querySelectorAll('.input-text, .input-textarea').forEach(el => el.classList.add('error'));
          qblock.scrollIntoView({behavior:'smooth', block:'center'});
        }
        break;
      }
    }
    const errEl = document.getElementById('nav-error');
    if (errEl) errEl.textContent = errMsg;
    return !errMsg;
  }

  // ── Navigation ────────────────────────────────────────────
  function next() {
    if (state.submitted) return;
    if (!validate()) return;
    computeVisible();
    // Llamar a submitSurvey cuando el usuario está en la última pantalla de preguntas
    // (la siguiente sería la pantalla de "thanks", que no tiene botón de navegación)
    const vis = state.visibleScreens;
    let lastQIdx = vis.length - 1;
    for (let i = vis.length - 1; i >= 0; i--) {
      if (vis[i].type !== 'thanks') { lastQIdx = i; break; }
    }
    if (state.currentIdx >= lastQIdx) {
      submitSurvey();
      return;
    }
    state.currentIdx++;
    render('forward');
    dbUpsert(); // save progress
  }

  function prev() {
    if (state.currentIdx > 0) {
      state.currentIdx--;
      render('back');
    }
  }

  // ── Submit ────────────────────────────────────────────────
  async function submitSurvey() {
    state.submitted = true;
    const overlay = document.getElementById('submitting-overlay');
    if (overlay) overlay.classList.add('visible');

    const completedAt = new Date().toISOString();
    const rid = state.respondentId || '';

    // clear local storage
    try { localStorage.removeItem('selmark_' + window.SURVEY_ID); } catch(e) {}

    if (overlay) overlay.classList.remove('visible');

    // show thanks screen
    state.currentIdx = totalScreens() - 1;
    render('forward');

    // Guardar en BD y redirigir a Cint en paralelo.
    // El redirect ocurre a los 3s pase lo que pase con la BD.
    const redirectTimer = setTimeout(() => {
      window.location.href = CONFIG.cint.complete + rid;
    }, 3000);

    // Guardar como 'complete' (sin bloquear el redirect)
    try {
      const sb = getSB();
      if (sb) {
        const payload = {
          id: state.dbRowId,
          survey_id: window.SURVEY_ID,
          respondent_id: state.respondentId,
          session_id: state.sessionId,
          answers: state.answers,
          product_shown: state.productShown,
          status: 'complete',
          completed_at: completedAt,
        };
        const { error } = await sb.from('survey_responses').upsert(payload, { onConflict: 'id' });
        if (error) console.warn('submitSurvey save error:', error.message);
        else console.log('submitSurvey: guardado como complete OK');
      }
    } catch(e) {
      console.warn('submitSurvey save failed:', e.message);
    }
  }

  // ── Duplicate check ───────────────────────────────────────
  async function checkDuplicate(rid) {
    if (!rid || rid.startsWith('test_')) return false;
    const sb = getSB();
    if (!sb) return false;
    try {
      const { data } = await sb
        .from('survey_responses')
        .select('id')
        .eq('survey_id', window.SURVEY_ID)
        .eq('respondent_id', rid)
        .eq('status', 'complete')
        .limit(1);
      return data && data.length > 0;
    } catch(e) { return false; }
  }

  // ── Init ──────────────────────────────────────────────────
  async function init() {
    state.respondentId = getParam('respondent_id') || getParam('RID') || 'test_' + Date.now();

    // Redirect duplicates before showing anything
    const isDuplicate = await checkDuplicate(state.respondentId);
    if (isDuplicate) {
      window.location.href = CONFIG.cint.duplicate + state.respondentId;
      return;
    }

    const resumed = loadLocal();
    if (!resumed) {
      state.sessionId = uuid();
      state.dbRowId   = uuid();  // ID fijo generado en cliente para upsert
      assignProducts();
    } else {
      if (!state.dbRowId)   state.dbRowId   = uuid();
      if (!Object.keys(state.productShown).length) assignProducts();
    }
    state.startTime = Date.now();
    computeVisible();
    // clamp index
    if (state.currentIdx >= totalScreens()) state.currentIdx = 0;
    render('forward');
    // insert to DB (create row)
    dbUpsert({ status: 'in_progress' });
  }

  // ── Bind interactions after render ────────────────────────
  function bindInteractions(sc, el) {
    (sc.questions || []).forEach(q => {
      if (q.type === 'color_combos') {
        setTimeout(() => _setActiveCombo(q.id, 0), 50);
      }
      if (q.type === 'color_pick') {
        setTimeout(() => {
          cpDrawWheel(q.id);
          const canvas = document.getElementById('cpw_canvas_'+q.id);
          if (!canvas) return;
          let dragging = false;
          canvas.addEventListener('mousedown', e => { dragging=true; _cpPickColor(q.id,e.clientX,e.clientY); });
          canvas.addEventListener('mousemove', e => { if(dragging) _cpPickColor(q.id,e.clientX,e.clientY); });
          window.addEventListener('mouseup', () => { dragging=false; }, {once:false});
          canvas.addEventListener('touchstart', e => { e.preventDefault(); _cpPickColor(q.id,e.touches[0].clientX,e.touches[0].clientY); }, {passive:false});
          canvas.addEventListener('touchmove',  e => { e.preventDefault(); _cpPickColor(q.id,e.touches[0].clientX,e.touches[0].clientY); }, {passive:false});
        }, 60);
      }
    });
  }

  // expose
  return {
    init,
    next,
    prev,
    setAns: setAnswer,
    selectSingle,
    toggleMulti,
    setScale,
    setDichotomy,
    toggleRank,
    // HSV wheel
    cpActivateSlot,
    cpBrightnessChange,
    removeCPColor,
    // Color combos (unchanged)
    paletteClick,
    comboSlotClick,
    addCombo,
    removeCombo,
    // Products
    selectProduct,
    getState: () => state,
    FASHION_COLORS,
  };

})();
