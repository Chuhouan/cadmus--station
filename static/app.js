/* ═══════════════════════════════════════════════════════════════════════
   CADMUS STATION v0.001 — Client (Canvas pixel renderer)
   Dual-pulse system: SCAN (tap) / FOCUS (hold 0.5s)
   ═══════════════════════════════════════════════════════════════════════ */

console.log('CADMUS STATION v0.001 init');

// ── State ──
const S = { difficulty:2, mapScale:1, themeIdx:0, walkerClass:null, modifiers:[], gameActive:false, debugGod:false, debugLevel:1 };
let IS_DEBUG = location.search.includes('debug');
let spaceDownTime = 0;
let focusCharging = false;
let holdTimer = null;
let fragmentData = null;
let _lastMsgSent = '';
let _briefingShown = false;

// ── Socket ──
const socket = io({ transports:['websocket','polling'], reconnection:true });

socket.on('state', (data) => {
  try {
    if (!data) return;
    // Briefing on first state (game start)
    if (data.briefing && !_briefingShown) {
      _briefingShown = true;
      showNarrativeOverlay(data.briefing, () => {});
    }
    // Handle level intro
    if (data.levelIntro) showLevelIntro(data.levelIntro);
    updatePanels(data);
    renderPixelFrame(data);
    processAudioFromState(data);
    // Charging ring — purely client-side, no server dependency
    if (focusCharging) {
      drawChargeRing((Date.now() - spaceDownTime) / 1000);
    }
  } catch(e) { console.warn('state:', e.message); }
});
socket.on('event', (data) => { if (data) addEvent(data.type, data.label); });
socket.on('gameover', (data) => {
  S.gameActive = false;
  focusCharging = false;
  spaceDownTime = 0;
  if (data && data.won) {
    if (data.isFinal) showEndingChoice(data);
    else if (data.actBreak) {
      // Show act break narrative, then proceed
      showNarrativeOverlay(data.actBreak, () => {
        showOverlay('win', data);
      });
    } else showOverlay('win', data);
  } else showOverlay('death', data);
});
socket.on('ending', (data) => {
  showEndingText(data);
});
socket.on('fragments', (data) => {
  fragmentData = data;
});

// ── Keyboard with dual-pulse timing ──
document.addEventListener('keydown', (e) => {
  if (e.key === 'm' || e.key === 'M') {
    e.preventDefault();
    const isMuted = toggleMute();
    const mb = document.getElementById('muteBtn');
    if (mb) mb.textContent = isMuted ? 'MUTED' : 'SND:ON';
    return;
  }
  if (e.key === '`' || e.key === '~') {
    e.preventDefault();
    IS_DEBUG = !IS_DEBUG;
    const dp = document.getElementById('debugPanel');
    if (dp) dp.style.display = IS_DEBUG ? 'flex' : 'none';
    return;
  }
  // TAB: open fragment panel
  if (e.key === 'Tab' && S.gameActive) {
    e.preventDefault();
    showFragmentPanel();
    return;
  }
  // Space: dual-pulse — record press time
  if (e.key === ' ' && spaceDownTime === 0 && S.gameActive) {
    e.preventDefault();
    spaceDownTime = Date.now();
    focusCharging = false;
    // After 0.2s, start showing charging ring
    holdTimer = setTimeout(() => { if (spaceDownTime > 0) focusCharging = true; }, 200);
    // Update focus indicator text
    const fi = $id('focusIndicator');
    if (fi) fi.classList.add('focus-charging');
    return;
  }
  const map = { 'ArrowUp':'up','ArrowDown':'down','ArrowLeft':'left','ArrowRight':'right','Enter':'\r','Escape':'\x1b','Backspace':'\x7f' };
  const k = map[e.key] || (e.key.length === 1 ? e.key.toLowerCase() : null);
  if (k) { e.preventDefault(); socket.emit('key', { key: k }); }
});

document.addEventListener('keyup', (e) => {
  if (e.key === ' ' && spaceDownTime > 0) {
    e.preventDefault();
    clearTimeout(holdTimer);
    const duration = (Date.now() - spaceDownTime) / 1000;
    spaceDownTime = 0;
    focusCharging = false;
    // Reset focus indicator text
    const fi = $id('focusIndicator');
    if (fi) fi.classList.remove('focus-charging');
    if (duration >= 0.5) {
      socket.emit('pulse', { action: 'focus' });
    } else {
      socket.emit('pulse', { action: 'scan' });
    }
  }
});

// ── Touch ──
let ts = null, touchHoldTimer = null;
document.addEventListener('touchstart', e => {
  ts = { x: e.touches[0].clientX, y: e.touches[0].clientY };
  spaceDownTime = Date.now();
  touchHoldTimer = setTimeout(() => { focusCharging = true; }, 200);
});
document.addEventListener('touchend', e => {
  if (touchHoldTimer) clearTimeout(touchHoldTimer);
  const duration = spaceDownTime > 0 ? (Date.now() - spaceDownTime) / 1000 : 0;
  spaceDownTime = 0;
  focusCharging = false;
  if (!ts) return;
  const dx = e.changedTouches[0].clientX - ts.x, dy = e.changedTouches[0].clientY - ts.y;
  if (Math.abs(dx) < 15 && Math.abs(dy) < 15) {
    if (duration >= 0.5) socket.emit('pulse', { action: 'focus' });
    else socket.emit('pulse', { action: 'scan' });
  } else if (Math.abs(dx) > Math.abs(dy)) socket.emit('key', { key: dx > 0 ? 'right' : 'left' });
  else socket.emit('key', { key: dy > 0 ? 'down' : 'up' });
  ts = null; clearChargeRing();
});

/* ═══════════════════════════════════════════════════════════════════════
   SPLASH
   ═══════════════════════════════════════════════════════════════════════ */

const COLORS = ['#cc3322','#cc6622','#2266cc','#226666','#6622aa','#cc2233','#aaaaaa','#224488','#4488cc','#445566'];
function initSplash() {
  if (IS_DEBUG) {
    const dp = document.getElementById('debugPanel');
    if (dp) dp.style.display = 'flex';
  }
  const sw = document.getElementById('themeSwatches');
  if (!sw) return;
  COLORS.forEach((c, i) => {
    const d = document.createElement('div');
    d.className = 'theme-swatch' + (i === 0 ? ' selected' : '');
    d.style.background = c;
    d.onclick = () => { S.themeIdx = i; sw.querySelectorAll('.theme-swatch').forEach((s, j) => s.classList.toggle('selected', j === i)); };
    sw.appendChild(d);
  });
  document.querySelectorAll('#diffBtns .opt-btn').forEach(b => {
    b.onclick = () => { S.difficulty = parseInt(b.dataset.val); document.querySelectorAll('#diffBtns .opt-btn').forEach(bb => bb.classList.remove('selected')); b.classList.add('selected'); };
  });
  document.querySelectorAll('#mapBtns .opt-btn').forEach(b => {
    b.onclick = () => { S.mapScale = parseInt(b.dataset.val); document.querySelectorAll('#mapBtns .opt-btn').forEach(bb => bb.classList.remove('selected')); b.classList.add('selected'); };
  });
}

function startGame() {
  document.getElementById('splash').style.display = 'none';
  document.getElementById('mainContainer').style.display = 'flex';
  document.getElementById('bottomBar').style.display = 'flex';
  initPixelRenderer();
  initPanelIcons();
  initAudio();
  startMusic(S.themeIdx);
  socket.emit('start', { difficulty:S.difficulty, mapScale:S.mapScale, themeIdx:S.themeIdx, walkerClass:S.walkerClass, modifiers:S.modifiers, debug:IS_DEBUG, godMode:S.debugGod, startLevel:S.debugLevel });
  S.gameActive = true;
}
function startDaily() {
  document.getElementById('splash').style.display = 'none';
  document.getElementById('mainContainer').style.display = 'flex';
  document.getElementById('bottomBar').style.display = 'flex';
  initPixelRenderer();
  initPanelIcons();
  initAudio();
  startMusic(0);
  socket.emit('start_daily', {});
  S.gameActive = true;
}

/* ═══════════════════════════════════════════════════════════════════════
   PANELS
   ═══════════════════════════════════════════════════════════════════════ */

function $id(id) { return document.getElementById(id); }

function updatePanels(s) {
  try {
  // Energy bar
  if (s.energy !== undefined) {
    const pct = s.maxEnergy > 0 ? (s.energy / s.maxEnergy * 100) : 0;
    const bar = $id('energyBar'); if (bar) { bar.style.width = pct + '%'; bar.classList.toggle('low', pct < 30); }
    const num = $id('energyNum'); if (num) num.textContent = s.energy + '/' + (s.maxEnergy || 10);
    // Focus indicator
    const fi = $id('focusIndicator');
    if (fi) {
      fi.classList.toggle('focus-low', s.energy < 3);
      if (s.energy >= 3) fi.style.opacity = '1';
    }
  }
  // Stats
  const ids = { statPings:s.pings, statSteps:s.steps, statScore:s.score, statLevel:s.level };
  Object.keys(ids).forEach(id => { if (ids[id] !== undefined) { const el = $id(id); if (el) el.textContent = ids[id]; } });
  // Combo
  if (s.combo !== undefined) { const cd = $id('comboDisplay'); if (cd) { cd.textContent = s.combo; cd.classList.toggle('active', s.combo >= 5); } }
  // Abilities
  if (s.abilities) { const ap = $id('abilitiesPanel'); const al = $id('abilitiesList'); if (ap) ap.style.display = s.abilities.length ? 'block' : 'none'; if (al) al.innerHTML = (s.abilities||[]).map(a => `<span class="ability-tag">${a}</span>`).join(''); }
  // Collected items
  if (s.collectedItems) { const keys = Object.keys(s.collectedItems); const ip = $id('itemsPanel'); const il = $id('itemsList'); if (ip) ip.style.display = keys.length ? 'block' : 'none'; if (il) il.textContent = keys.map(k => `${k}: ${s.collectedItems[k]}`).join(' | '); }
  // Modifiers
  if (s.modifiers && s.modifiers.length) { const mp = $id('modsPanel'); const ml = $id('modsList'); const mm = $id('modMultiplier'); if (mp) mp.style.display = 'block'; if (ml) ml.textContent = s.modifiers.join(', '); if (mm && s.modMultiplier) mm.textContent = 'x' + s.modMultiplier.toFixed(1); }
  else { const mp = $id('modsPanel'); if (mp) mp.style.display = 'none'; }
  // Boss shields
  if (s.bossName) {
    const bp = $id('bossPanel'); const bi = $id('bossInfo');
    if (bp) bp.style.display = 'block';
    if (bi) {
      const sh = s.bossShields || 0; const mx = s.bossMaxShields || 3;
      const shields = '▓'.repeat(sh) + '░'.repeat(mx - sh);
      let status = '';
      if (sh === 3) status = 'ACOUSTIC_FIELD STABLE';
      else if (sh === 2) status = 'FREQUENCY FLUCTUATING';
      else if (sh === 1) status = 'STRUCTURE COLLAPSING';
      else status = 'CORE EXPOSED — FINAL STRIKE';
      bi.innerHTML = `<span style="color:#c34;">${s.bossName}</span><br>SHIELDS: ${shields}<br><span style="font-size:9px;color:#888;">${status}</span>`;
    }
  } else if (s.bossName === null) { const bp = $id('bossPanel'); if (bp) bp.style.display = 'none'; }
  // Level palette
  if (s.levelPalette && s.levelPalette.name) {
    const themeClass = 'theme-' + s.levelPalette.name.toLowerCase();
    document.body.className = document.body.className.replace(/theme-\w+/g, '') + ' ' + themeClass;
  }
  // Rating
  if (s.rating && $id('ratingDisplay')) $id('ratingDisplay').textContent = s.rating;
  // Character
  if (s.charName) { const cn = $id('charName'); if (cn) cn.textContent = s.charName; }
  if (s.walkerClass) { const ci = $id('charIconImg'); if (ci) ci.src = getCharIconURL(s.walkerClass); }
  // Game message
  if (s.lastMessage) { const mel = $id('gameMsg'); if (mel && mel.textContent !== s.lastMessage) { mel.textContent = s.lastMessage; mel.style.animation = 'none'; mel.offsetHeight; mel.style.animation = 'fadeInRight 0.3s ease'; } }
  // Special room
  if (s.specialRoom) {
    const rp = $id('roomPanel'); const ri = $id('roomInfo');
    if (rp) rp.style.display = 'block';
    const roomNames = {1:'ECHO CHAMBER',2:'SILENT ZONE',3:'ECHO RESIDUE'};
    if (ri) ri.textContent = roomNames[s.specialRoom] || '';
  } else { const rp = $id('roomPanel'); if (rp) rp.style.display = 'none'; }
  // Quest
  const qp = $id('questPanel');
  if (qp && s.exitLocked !== undefined) {
    if (s.questComplete) { qp.style.display = 'block'; const qi = $id('questInfo'); if (qi) qi.innerHTML = '<span style="color:#0f8;">[GATE UNLOCKED]</span>'; }
    else if (s.exitLocked) { qp.style.display = 'block'; const qi = $id('questInfo'); if (qi) qi.innerHTML = '<span style="color:#fd0;">[FIND ACCESS CARD]</span>'; }
  }
  // Fragment progress with dot grid
  if (s.fragmentsCollected !== undefined) {
    const fp = $id('fragmentProgress');
    if (fp) {
      fp.textContent = s.fragmentsCollected + '/18';
      if (s.fragmentsAllCollected) fp.style.color = '#ffd700';
      else fp.style.color = '#8899aa';
    }
    // Render fragment dot grid
    const fg = $id('fragmentGrid');
    if (fg) {
      let dots = '';
      for (let i = 0; i < 18; i++) {
        const cls = i < s.fragmentsCollected ? (s.fragmentsAllCollected ? 'all-done' : 'collected') : '';
        dots += `<span class="fragment-dot ${cls}"></span>`;
      }
      fg.innerHTML = dots;
    }
  }
  // Emit events from lastMessage
  if (s.lastMessage && s.lastMessage !== _lastMsgSent) {
    _lastMsgSent = s.lastMessage;
    let etype = 'scan', elabel = s.lastMessage;
    const l = s.lastMessage.toLowerCase();
    if (l.includes('wall') || l.includes('墙')) { etype = 'wall'; elabel = 'WALL'; }
    else if (l.includes('drone') || l.includes('无人机') || l.includes('dron')) { etype = 'drone'; elabel = 'DRONE'; }
    else if (l.includes('card') || l.includes('卡') || l.includes('key')) { etype = 'card'; elabel = 'CARD'; }
    else if (l.includes('anomaly') || l.includes('boss') || l.includes('异常') || l.includes('清除')) { etype = 'anomaly'; elabel = 'ANOMALY'; }
    else if (l.includes('gate') || l.includes('闸门') || l.includes('exit') || l.includes('出口')) { etype = 'gate'; elabel = 'GATE'; }
    else if (l.includes('focus') || l.includes('聚焦')) { etype = 'scan'; elabel = 'FOCUS'; }
    else if (l.includes('scan') || l.includes('扫描')) { etype = 'scan'; elabel = 'SCAN'; }
    addEvent(etype, elabel);
  }
  // Can focus indicator
  if (s.canFocus !== undefined) {
    const fi = $id('focusIndicator');
    if (fi) fi.style.opacity = s.canFocus ? '1' : '0.3';
  }
  } catch(e) { console.warn('updatePanels:', e.message); }
}

/* ═══════════════════════════════════════════════════════════════════════
   NARRATIVE OVERLAY & LEVEL INTRO
   ═══════════════════════════════════════════════════════════════════════ */

function showNarrativeOverlay(data, callback) {
  // Full-screen narrative display — multi-paragraph text, press space to continue
  if (!data) { if (callback) callback(); return; }
  const ov = document.createElement('div');
  ov.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:#050508;z-index:350;display:flex;flex-direction:column;align-items:center;justify-content:center;';
  const text = data.zh || data.en || '';
  const lines = text.split('\n');
  let idx = 0;
  const content = document.createElement('div');
  content.style.cssText = 'max-width:620px;padding:30px;font-family:var(--font-mono);font-size:17px;color:#c8ccd0;line-height:2;text-align:left;';
  ov.appendChild(content);
  // Lower-left hint
  const hint = document.createElement('div');
  hint.style.cssText = 'position:absolute;bottom:30px;left:50%;transform:translateX(-50%);font-family:var(--font-mono);font-size:11px;color:#445566;';
  hint.textContent = '[ SPACE ]';
  ov.appendChild(hint);

  function showNextLine() {
    if (idx < lines.length) {
      const line = lines[idx];
      const span = document.createElement('span');
      span.textContent = line;
      span.style.display = 'block';
      span.style.opacity = '0';
      span.style.animation = 'fadeInRight 0.4s ease forwards';
      content.appendChild(span);
      idx++;
      // If this is a blank line or short line, show next immediately
      if (!line.trim() || line.length < 15) {
        showNextLine();
      }
    }
  }
  // Show first batch of lines
  for (let i = 0; i < 5 && idx < lines.length; i++) {
    const line = lines[idx];
    const span = document.createElement('span');
    span.textContent = line;
    span.style.display = 'block';
    span.style.opacity = '0';
    span.style.animation = 'fadeInRight 0.4s ease forwards';
    span.style.animationDelay = (i * 0.3) + 's';
    content.appendChild(span);
    idx++;
  }

  function onKey(e) {
    if (e.key === ' ') {
      e.preventDefault();
      if (idx < lines.length) {
        // Show more lines
        const batch = Math.min(5, lines.length - idx);
        for (let i = 0; i < batch; i++) {
          const line = lines[idx];
          const span = document.createElement('span');
          span.textContent = line;
          span.style.display = 'block';
          span.style.opacity = '0';
          span.style.animation = 'fadeInRight 0.3s ease forwards';
          content.appendChild(span);
          idx++;
        }
      } else {
        document.removeEventListener('keydown', onKey);
        ov.style.transition = 'opacity 0.5s';
        ov.style.opacity = '0';
        setTimeout(() => { ov.remove(); if (callback) callback(); }, 500);
      }
    }
  }
  document.addEventListener('keydown', onKey);
  document.body.appendChild(ov);
}

function showLevelIntro(data) {
  if (!data) return;
  const ov = document.createElement('div');
  ov.className = 'level-intro-overlay';
  const text = data.zh || data.en || '';
  const lines = text.split('\n');
  const displayText = lines.length > 3 ? lines.slice(0, 3).join('\n') + '…' : text;
  ov.innerHTML = `<div class="level-intro-text">${displayText.replace(/\n/g, '<br>')}</div>`;
  document.body.appendChild(ov);
  setTimeout(() => { ov.style.opacity = '0'; setTimeout(() => ov.remove(), 500); }, 5000);
}

function drawChargeRing(progress) {
  const canvas = document.getElementById('gameCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const cx = canvas.width / 2, cy = canvas.height / 2;
  const maxR = 40, minR = 8;
  const t = Math.min(1, Math.max(0, (progress - 0.2) / 0.3)); // 0.2-0.5s
  const r = maxR - t * (maxR - minR);
  // Color based on energy
  let color = '#4488ff';
  if (progress >= 0.45) color = '#ffaa00';
  ctx.strokeStyle = color;
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.arc(cx, cy, r, 0, Math.PI * 2);
  ctx.stroke();
  // Inner glow
  ctx.strokeStyle = 'rgba(255,255,255,0.3)';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.arc(cx, cy, r + 2, 0, Math.PI * 2);
  ctx.stroke();
}

function clearChargeRing() {
  // Ring is drawn per-frame; when charging stops, it simply stops being drawn
}

/* ═══════════════════════════════════════════════════════════════════════
   FRAGMENT PANEL (TAB)
   ═══════════════════════════════════════════════════════════════════════ */

function showFragmentPanel() {
  if (!fragmentData) {
    socket.emit('get_fragments', {});
    socket.once('fragments', (data) => {
      fragmentData = data;
      _renderFragmentPanel();
    });
    return;
  }
  _renderFragmentPanel();
}

let _fragPanelOpen = false; let _fragSelectedPerson = 'lin_xianhe';

function _renderFragmentPanel() {
  // Remove existing
  const existing = document.getElementById('fragmentPanelOverlay');
  if (existing) { existing.remove(); _fragPanelOpen = false; return; }
  _fragPanelOpen = true;

  const ov = document.createElement('div');
  ov.id = 'fragmentPanelOverlay';
  ov.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(5,5,8,0.94);z-index:300;display:flex;justify-content:center;align-items:center;';
  const personIds = ['lin_xianhe','su_wuying','zhao_tieshan','chen_ge','wu_an','zheng_zhen'];
  const personTabs = personIds.map(id => {
    const p = fragmentData[id];
    const active = id === _fragSelectedPerson ? ' style="border-bottom:2px solid #4488ff;color:#fff;"' : '';
    return `<button class="frag-tab" data-person="${id}"${active}>${p ? p.name_zh : id}</button>`;
  }).join('');

  const sel = fragmentData[_fragSelectedPerson];
  let fragList = '';
  if (sel) {
    for (let i = 1; i <= 3; i++) {
      const f = sel.fragments[i];
      if (f) {
        fragList += `<div class="frag-item" style="padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);">
          <span style="color:#4488ff;">[${i.toString().padStart(2,'0')}]</span>
          <span style="color:#889;"> — ${'关卡 ' + f.level}</span>
          <div style="margin-top:4px;color:#ccc;font-size:12px;">${f.text_zh}</div>
        </div>`;
      } else {
        fragList += `<div class="frag-item" style="padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);color:#444;">
          [${i.toString().padStart(2,'0')}] — ??? (未收集)
        </div>`;
      }
    }
  }

  ov.innerHTML = `<div style="background:var(--bg-crt);border:1px solid var(--border);border-radius:8px;padding:24px;max-width:600px;width:90%;max-height:80vh;overflow-y:auto;">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
      <div style="font-size:20px;color:#4488ff;font-family:var(--font-mono);">RECORDED_AUDIO_LOGS</div>
      <button class="nav-btn" onclick="document.getElementById('fragmentPanelOverlay').remove();_fragPanelOpen=false;" style="font-size:12px;padding:6px 14px;">[X] CLOSE</button>
    </div>
    <div style="display:flex;gap:4px;margin-bottom:16px;flex-wrap:wrap;">${personTabs}</div>
    <div style="margin-bottom:8px;color:#aaa;font-size:11px;">当前选择: ${sel ? sel.name_zh + ' / ' + sel.title_zh : '???'}</div>
    <div>${fragList}</div>
    <div style="margin-top:12px;text-align:center;font-family:var(--font-mono);font-size:12px;color:#889;">
      全收集进度: ${S.gameActive ? '游戏中...' : '--'}
    </div>
  </div>`;
  document.body.appendChild(ov);

  // Tab switching
  ov.querySelectorAll('.frag-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      _fragSelectedPerson = tab.dataset.person;
      _renderFragmentPanel();
    });
  });

  // Close on ESC
  const escHandler = (e) => {
    if (e.key === 'Escape') {
      const el = document.getElementById('fragmentPanelOverlay');
      if (el) { el.remove(); _fragPanelOpen = false; }
      document.removeEventListener('keydown', escHandler);
    }
  };
  document.addEventListener('keydown', escHandler);
}

/* ═══════════════════════════════════════════════════════════════════════
   ENDING CHOICE (Level 10)
   ═══════════════════════════════════════════════════════════════════════ */

function showEndingChoice(data) {
  const ov = document.createElement('div');
  ov.id = 'endingOverlay';
  ov.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(5,5,8,0.95);z-index:400;display:flex;flex-direction:column;align-items:center;justify-content:center;';

  const hasAll = data.fragmentsAll || false;
  let html = `<div style="font-size:22px;color:#4488ff;margin-bottom:8px;font-family:var(--font-mono);">CONTROL ROOM — FINAL SEQUENCE</div>
    <div style="color:#aaa;margin-bottom:24px;font-size:12px;">核心安全模式已启动。手动刹车需要两个活人。</div>
    <div style="display:flex;gap:24px;flex-wrap:wrap;justify-content:center;">`;

  // Option A
  html += `<div class="ending-card" onclick="chooseEnding('A')" style="border:1px solid #4488ff;padding:20px;border-radius:8px;cursor:pointer;width:200px;text-align:center;">
    <div style="font-size:18px;color:#fff;margin-bottom:8px;">[A]</div>
    <div style="font-size:14px;color:#ccc;">配合吴暗</div>
    <div style="font-size:10px;color:#888;margin-top:4px;">关闭核心，一起出去</div>
    <div style="font-size:9px;color:#5588aa;margin-top:8px;">解锁：吴暗的装备</div>
  </div>`;

  // Option B
  html += `<div class="ending-card" onclick="chooseEnding('B')" style="border:1px solid #cc8844;padding:20px;border-radius:8px;cursor:pointer;width:200px;text-align:center;">
    <div style="font-size:18px;color:#fff;margin-bottom:8px;">[B]</div>
    <div style="font-size:14px;color:#ccc;">揭露真相</div>
    <div style="font-size:10px;color:#888;margin-top:4px;">独自关闭，把证据带出去</div>
    <div style="font-size:9px;color:#cc8844;margin-top:8px;">解锁：郑振的感应器</div>
  </div>`;

  // Option C (hidden unless all fragments)
  if (hasAll) {
    html += `<div class="ending-card" onclick="chooseEnding('C')" style="border:1px solid #ffd700;padding:20px;border-radius:8px;cursor:pointer;width:200px;text-align:center;animation:pulse 2s infinite;">
      <div style="font-size:18px;color:#ffd700;margin-bottom:8px;">[C]</div>
      <div style="font-size:14px;color:#ffd700;">炸毁设施</div>
      <div style="font-size:10px;color:#888;margin-top:4px;">一切结束</div>
      <div style="font-size:9px;color:#ffd700;margin-top:8px;">解锁：陈歌的中继模式</div>
    </div>`;
  } else {
    html += `<div style="border:1px solid #333;padding:20px;border-radius:8px;width:200px;text-align:center;opacity:0.4;">
      <div style="font-size:18px;color:#555;margin-bottom:8px;">[C]</div>
      <div style="font-size:12px;color:#555;">全18块碎片解锁</div>
    </div>`;
  }
  html += `</div>`;
  ov.innerHTML = html;
  document.body.appendChild(ov);
}

function chooseEnding(choice) {
  socket.emit('ending_choice', { choice: choice });
  document.getElementById('endingOverlay')?.remove();
}

function showEndingText(data) {
  const ov = document.createElement('div');
  ov.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(5,5,8,0.96);z-index:500;display:flex;flex-direction:column;align-items:center;justify-content:center;';
  const t = data.text || {};
  ov.innerHTML = `<div style="max-width:600px;text-align:center;padding:40px;">
    <div style="font-size:24px;color:#4488ff;margin-bottom:20px;font-family:var(--font-mono);">${t.title || ''}</div>
    <div style="font-size:16px;color:#ccc;line-height:2;margin-bottom:30px;">${t.text || ''}</div>
    <div style="font-size:12px;color:#889;">解锁角色: ${t.unlock || ''}</div>
    <button class="btn-primary" onclick="location.reload();" style="margin-top:24px;">返回标题 / RETURN</button>
  </div>`;
  document.body.appendChild(ov);
}

/* ═══════════════════════════════════════════════════════════════════════
   EVENTS & OVERLAYS
   ═══════════════════════════════════════════════════════════════════════ */

function addEvent(type, label) {
  const log = document.getElementById('eventLog'); if (!log) return;
  const el = document.createElement('span'); el.className = 'event-item ' + (type || ''); el.textContent = (label || type || '?');
  log.appendChild(el); while (log.children.length > 12) log.removeChild(log.firstChild);
}
function showOverlay(type, data) {
  const ov = document.createElement('div'); ov.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(5,5,8,0.92);display:flex;flex-direction:column;align-items:center;justify-content:center;z-index:300;';
  if (type === 'win') ov.innerHTML = `<div style="font-size:28px;color:#0c4;text-shadow:0 0 20px #0f5;margin-bottom:12px;">>>> GATE UNLOCKED <<<</div><div style="font-family:monospace;font-size:14px;">SCORE: ${data.score||0} | GRADE: ${data.rating||'?'}</div><div style="display:flex;gap:12px;margin-top:16px;"><button class="btn-primary" onclick="socket.emit('key',{key:' '});this.closest('div[style*=fixed]').remove();">NEXT >>></button><button class="btn-secondary" onclick="this.closest('div[style*=fixed]').remove();">CLOSE</button></div>`;
  else ov.innerHTML = `<div style="font-size:24px;color:#c34;text-shadow:0 0 16px #f45;margin-bottom:12px;">电池耗尽 / BATTERY DEPLETED</div><div style="font-family:monospace;font-size:13px;">SCANS: ${data.pings||0} | STEPS: ${data.steps||0} | SCORE: ${data.score||0}</div><div style="display:flex;gap:12px;margin-top:16px;"><button class="btn-primary" onclick="location.reload();">RETRY</button></div>`;
  document.body.appendChild(ov);
}

function toggleLang() { socket.emit('key', { key: 'l' }); }

/* ═══════════════════════════════════════════════════════════════════════
   MODAL: Character & Modifier (simplified for v5.0)
   ═══════════════════════════════════════════════════════════════════════ */

const MODIFIERS = [
  { id: 'SILENT', nameZh: '静默 SILENT', nameEn: 'SILENT', bonus: 2.0, color: '#fff', descZh: '完全禁用脉冲', descEn: 'Pings completely disabled' },
  { id: 'HUNTED', nameZh: '追猎 HUNTED', nameEn: 'HUNTED', bonus: 1.5, color: '#f33', descZh: '无人机数量×3', descEn: '3x drone count' },
];

function showCharModal() {
  const ov = document.createElement('div');
  ov.className = 'modal-overlay';
  ov.innerHTML = `<div class="modal-box">
    <div class="modal-title">EXOSKELETON MODEL</div>
    <div class="character-grid" id="charGrid">
      <div style="text-align:center;color:var(--text-dim);padding:20px;">加载中...</div>
    </div>
    <div style="text-align:center;margin-top:12px;font-family:var(--font-mono);font-size:11px;color:var(--text-dim);" id="charSelHint">当前: ${S.walkerClass ? '已选择' : '标准外骨骼 / Standard'}</div>
    <div class="modal-footer">
      <button class="btn-primary" onclick="closeCharModal(this, true)">确认 CONFIRM</button>
      <button class="btn-secondary" onclick="closeCharModal(this, false)">跳过 SKIP</button>
    </div>
  </div>`;
  document.body.appendChild(ov);

  ov.addEventListener('click', e => { if (e.target === ov) closeCharModal(null, false); });
  document.addEventListener('keydown', function escC(e) {
    if (e.key === 'Escape') { closeCharModal(null, false); document.removeEventListener('keydown', escC); }
  });

  let loaded = false;
  const timer = setTimeout(function() {
    if (!loaded) { loaded = true; renderCharGrid(buildFallbackChars()); }
  }, 3000);

  function onChars(data) {
    if (loaded) return;
    loaded = true;
    clearTimeout(timer);
    socket.off('characters', onChars);
    renderCharGrid(data && data.chars ? data.chars : buildFallbackChars());
  }
  socket.on('characters', onChars);
  socket.emit('get_characters', {});

  function renderCharGrid(chars) {
    const grid = document.getElementById('charGrid');
    if (!grid) return;
    grid.innerHTML = chars.map(c => {
      const sel = S.walkerClass === c.id ? ' selected' : '';
      const lock = c.locked ? ' locked' : '';
      const imgSrc = getCharIconURL(c.id);
      const lockHtml = c.locked ? `<div class="char-lock">[LOCKED] ${c.unlockHint||''}</div>` : '';
      return `<div class="char-card${sel}${lock}" data-id="${c.id}" onclick="pickChar(this)" style="position:relative;">
        <div class="char-icon"><img src="${imgSrc}" width="32" height="32" style="image-rendering:pixelated;"></div>
        <div class="char-name">${c.name}</div>
        <div class="char-desc">${c.desc}</div>
        ${lockHtml}
      </div>`;
    }).join('');
  }
}

function buildFallbackChars() {
  return [
    { id:'prophet', name:"Prophet's Relic", desc:'Scan +3 | Energy -2', locked:false, unlockHint:'' },
    { id:'ghost', name:"Su Wuying's Exo", desc:'Drones ignore scan | Range -40%', locked:false, unlockHint:'' },
    { id:'behemoth', name:"Zhao's Mod", desc:'Smash walls | Step costs', locked:true, unlockHint:'Find body at Lv4' },
    { id:'singer', name:"Chen Ge's Relay", desc:'Free scan | Tiny range | No focus', locked:true, unlockHint:'Complete Lv5' },
    { id:'shadow', name:"Wu An's Equipment", desc:'Silent steps | Hide self', locked:true, unlockHint:'Ending A' },
    { id:'resonator', name:"Zheng Zhen's Sensor", desc:'Auto-reveal 3s | No pulse', locked:true, unlockHint:'Ending B' },
  ];
}

function pickChar(el) {
  if (el.classList.contains('locked')) return;
  const id = el.dataset.id;
  document.querySelectorAll('.char-card').forEach(c => c.classList.remove('selected'));
  el.classList.add('selected');
  S.walkerClass = id;
  const hint = document.getElementById('charSelHint');
  if (hint) hint.textContent = '已选择 / Selected';
}

function closeCharModal(btn, confirmed) {
  const ov = btn ? btn.closest('.modal-overlay') : document.querySelector('.modal-overlay');
  if (ov) ov.remove();
  updateSplashLabels();
}

function showModModal() {
  const ov = document.createElement('div');
  ov.className = 'modal-overlay';
  const activeIds = new Set(S.modifiers);
  const renderMods = () => MODIFIERS.map(m => {
    const active = activeIds.has(m.id);
    return `<div class="modifier-item${active ? ' active' : ''}" data-id="${m.id}" onclick="toggleMod(this)" style="display:flex;align-items:center;gap:12px;padding:10px 14px;margin-bottom:4px;">
      <div class="mod-toggle${active ? ' on' : ''}"></div>
      <div style="flex:1;">
        <div style="font-family:var(--font-mono);font-size:12px;color:var(--text-bright);">
          <span style="color:${m.color};font-weight:bold;">${m.id}</span>
          <span style="color:var(--accent);margin-left:8px;">+${Math.round(m.bonus*100)}%</span>
        </div>
        <div style="font-size:10px;color:var(--text-dim);">${m.descZh} / ${m.descEn}</div>
      </div>
    </div>`;
  }).join('');

  const getMultiplier = () => {
    let mult = 1.0;
    activeIds.forEach(id => {
      const m = MODIFIERS.find(mm => mm.id === id);
      if (m) mult += m.bonus;
    });
    return mult;
  };

  ov.innerHTML = `<div class="modal-box">
    <div class="modal-title">CHALLENGE MODIFIERS</div>
    <div id="modList">${renderMods()}</div>
    <div style="text-align:center;margin-top:12px;font-family:var(--font-mono);font-size:11px;">
      <span style="color:var(--text-dim);">总倍率 Multiplier: </span>
      <span style="color:var(--accent);font-size:14px;font-weight:bold;" id="modMult">×${getMultiplier().toFixed(1)}</span>
    </div>
    <div class="modal-footer">
      <button class="btn-primary" onclick="closeModModal(this, true)">确认 CONFIRM</button>
      <button class="btn-secondary" onclick="closeModModal(this, false)">清除 CLEAR</button>
    </div>
  </div>`;
  document.body.appendChild(ov);
  ov._activeIds = activeIds;
  ov._getMultiplier = getMultiplier;
  ov.addEventListener('click', e => { if (e.target === ov) closeModModal(null, false); });
  document.addEventListener('keydown', function escM(e) {
    if (e.key === 'Escape') { closeModModal(null, false); document.removeEventListener('keydown', escM); }
  });
}

function toggleMod(el) {
  const id = el.dataset.id;
  const ov = el.closest('.modal-overlay');
  if (!ov || !ov._activeIds) return;
  if (ov._activeIds.has(id)) { ov._activeIds.delete(id); el.classList.remove('active'); el.querySelector('.mod-toggle').classList.remove('on'); }
  else { ov._activeIds.add(id); el.classList.add('active'); el.querySelector('.mod-toggle').classList.add('on'); }
  const multEl = document.getElementById('modMult');
  if (multEl && ov._getMultiplier) multEl.textContent = '×' + ov._getMultiplier().toFixed(1);
}

function closeModModal(btn, confirmed) {
  const ov = btn ? btn.closest('.modal-overlay') : document.querySelector('.modal-overlay');
  if (confirmed && ov && ov._activeIds) S.modifiers = Array.from(ov._activeIds);
  if (ov) ov.remove();
  updateSplashLabels();
}

function updateSplashLabels() {
  const cl = document.getElementById('charSelectLabel');
  if (cl) {
    const names = {prophet:"Prophet's Relic",ghost:"Su's Exoskeleton",behemoth:"Zhao's Mod",singer:"Chen's Relay",shadow:"Wu's Equipment",resonator:"Zheng's Sensor"};
    const id = S.walkerClass || 'prophet';
    cl.textContent = names[id] || id;
  }
  const ml = document.getElementById('modSelectLabel');
  if (ml) {
    if (S.modifiers.length > 0) {
      const total = 1.0 + S.modifiers.reduce((s,id) => { const m = MODIFIERS.find(mm => mm.id===id); return s + (m?m.bonus:0); }, 0);
      ml.textContent = S.modifiers.length + ' modifier(s) / ×' + total.toFixed(1);
    } else ml.textContent = 'None';
  }
}

/* ═══════════════════════════════════════════════════════════════════════
   SPLASH PARTICLE BACKGROUND
   ═══════════════════════════════════════════════════════════════════════ */

function initParticles() {
  const c = document.getElementById('splashParticles');
  if (!c) return;
  const ctx = c.getContext('2d');
  c.width = c.offsetWidth; c.height = c.offsetHeight;
  const particles = [];
  const count = 60;
  for (let i = 0; i < count; i++) {
    particles.push({
      x: Math.random() * c.width, y: Math.random() * c.height,
      r: Math.random() * 1.5 + 0.5,
      vx: (Math.random() - 0.5) * 0.3, vy: (Math.random() - 0.5) * 0.3,
      alpha: Math.random() * 0.6 + 0.2,
      pulse: Math.random() * Math.PI * 2,
    });
  }
  function draw() {
    ctx.clearRect(0, 0, c.width, c.height);
    particles.forEach(p => {
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0) p.x = c.width; if (p.x > c.width) p.x = 0;
      if (p.y < 0) p.y = c.height; if (p.y > c.height) p.y = 0;
      p.pulse += 0.02;
      const a = p.alpha + Math.sin(p.pulse) * 0.2;
      ctx.fillStyle = `rgba(68,136,255,${Math.max(0,Math.min(1,a))})`;
      ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2); ctx.fill();
    });
    requestAnimationFrame(draw);
  }
  draw();
  window.addEventListener('resize', () => { c.width = c.offsetWidth; c.height = c.offsetHeight; });
}

/* ═══════════════════════════════════════════════════════════════════════
   HELP SYSTEM (v5.0 simplified)
   ═══════════════════════════════════════════════════════════════════════ */

function showHelp() {
  const ov = document.createElement('div');
  ov.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(5,5,8,0.94);z-index:300;overflow-y:auto;';
  ov.innerHTML = `<div style="max-width:720px;margin:40px auto;padding:20px;">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
      <div style="font-size:24px;color:#4488ff;font-family:'Cascadia Code',monospace;">[SYS] FACILITY MANUAL</div>
      <button class="nav-btn" onclick="this.closest('div[style*=fixed]').remove();" style="font-size:14px;padding:6px 18px;">[X] CLOSE</button>
    </div>
    <div style="background:var(--bg-crt);border:1px solid var(--border);border-radius:8px;padding:20px;">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
        <div style="padding:12px;border:1px solid var(--border);border-radius:4px;">
          <div style="color:#4488ff;font-weight:bold;margin-bottom:8px;">SCAN PULSE [TAP SPACE]</div>
          <div style="font-size:11px;color:#889;">轻按空格(<0.2s): 消耗1能量, 7格范围, 揭示墙壁。不造成伤害。</div>
        </div>
        <div style="padding:12px;border:1px solid var(--border);border-radius:4px;">
          <div style="color:#ffaa00;font-weight:bold;margin-bottom:8px;">FOCUS PULSE [HOLD 0.5s]</div>
          <div style="font-size:11px;color:#889;">长按空格(≥0.5s): 消耗3能量, 前方3格扇形, 破Boss护盾/弹飞无人机。</div>
        </div>
        <div style="padding:12px;border:1px solid var(--border);border-radius:4px;">
          <div style="color:#ccc;font-weight:bold;margin-bottom:8px;">DRONES</div>
          <div style="font-size:11px;color:#889;">聚焦脉冲不能击杀普通无人机——只能弹飞+晕眩5秒。触碰损失3能量。</div>
        </div>
        <div style="padding:12px;border:1px solid var(--border);border-radius:4px;">
          <div style="color:#c34;font-weight:bold;margin-bottom:8px;">BOSSES</div>
          <div style="font-size:11px;color:#889;">3层护盾。仅聚焦脉冲击穿。回响之母(3关=3格内) / 静默猎手(6关) / 虚空化身(9关=锚点)。</div>
        </div>
        <div style="padding:12px;border:1px solid var(--border);border-radius:4px;">
          <div style="color:#ffd700;font-weight:bold;margin-bottom:8px;">FRAGMENTS [TAB]</div>
          <div style="font-size:11px;color:#889;">18块叙事碎片。6人×3块。全收集解锁终章隐藏选择。</div>
        </div>
        <div style="padding:12px;border:1px solid var(--border);border-radius:4px;">
          <div style="color:#aaa;font-weight:bold;margin-bottom:8px;">CONTROLS</div>
          <div style="font-size:11px;color:#889;">WASD:移动 | SPACE:脉冲 | TAB:碎片面板 | H:帮助 | L:语言 | Q:退出</div>
        </div>
      </div>
    </div>
  </div>`;
  document.body.appendChild(ov);
  ov.addEventListener('click', e => { if (e.target === ov) ov.remove(); });
  document.addEventListener('keydown', function esc(e) { if (e.key === 'Escape') { ov.remove(); document.removeEventListener('keydown', esc); } });
}

/* ═══════════════════════════════════════════════════════════════════════
   SIMPLIFIED LEADERBOARD
   ═══════════════════════════════════════════════════════════════════════ */

function showLeaderboard() {
  socket.emit('get_leaderboard', {});
  socket.once('leaderboard', (data) => {
    const ov = document.createElement('div'); ov.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(5,5,8,0.92);display:flex;flex-direction:column;align-items:center;justify-content:center;z-index:300;';
    ov.innerHTML = `<div style="font-size:20px;color:#4488ff;margin-bottom:16px;">LEADERBOARD</div>${(data.entries||[]).map((e,i) => `<div style="font-family:monospace;font-size:13px;padding:4px;">#${i+1} ${e.score}pts | ${e.pings}p | ${e.steps}s | ${e.grade} | ${e.date}</div>`).join('')||'No records yet'}<button class="btn-secondary" style="margin-top:14px;" onclick="this.closest('div[style*=fixed]').remove();">CLOSE</button>`;
    document.body.appendChild(ov);
  });
}

/* ═══════════════════════════════════════════════════════════════════════
   INIT
   ═══════════════════════════════════════════════════════════════════════ */

initSplash();
initParticles();
initNavIcons();
console.log('CADMUS STATION ready. Press DEPLOY.');
