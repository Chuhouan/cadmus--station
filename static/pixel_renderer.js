/* ═══════════════════════════════════════════════════════════════════════
   ECHO MAZE v5.0 — Pixel Renderer
   Replaces text-mode <pre> with Canvas 2D pixel art.
   All sprites drawn programmatically — no external image files.
   ═══════════════════════════════════════════════════════════════════════ */

const TILE = 20;   // pixels per cell
const VW = 30;     // viewport width in cells
const VH = 20;     // viewport height in cells

let prCtx = null;
let prAnimFrame = 0;
let currentTheme = 0;

// Animation state tracking
let lastMoves = 0, lastPings = 0, lastDamage = 0;
let walkPhase = 0, pingPhase = 0, hurtPhase = 0, idlePhase = 0;
let playerDx = 0, playerDy = 0, lastPx = -1, lastPy = -1;

/* ── Theme Color Palettes ── */
const THEME_PALETTES = [
  { // 0: Ocean Deep — deep blue/cyan
    wall: [8,18,35], wallGlow: [0,200,220],
    floor: [4,8,12], floorDot: [6,14,20],
    playerGlow: [0,255,200], pingFlash: [0,200,180],
    exitUnlock: '#fd0',
  },
  { // 1: Volcanic Fury — dark red/orange
    wall: [35,12,8], wallGlow: [255,100,30],
    floor: [10,4,3], floorDot: [16,6,4],
    playerGlow: [255,130,50], pingFlash: [255,80,20],
    exitUnlock: '#fd0',
  },
  { // 2: Forest Spirit — dark green
    wall: [10,28,12], wallGlow: [50,220,60],
    floor: [3,8,4], floorDot: [5,14,6],
    playerGlow: [80,255,100], pingFlash: [60,220,80],
    exitUnlock: '#fd0',
  },
  { // 3: Crystal Prism — purple/magenta
    wall: [22,8,30], wallGlow: [220,60,255],
    floor: [8,3,10], floorDot: [14,4,16],
    playerGlow: [200,80,255], pingFlash: [180,40,220],
    exitUnlock: '#fd0',
  },
  { // 4: Sunset Gold — warm brown/gold
    wall: [30,18,8], wallGlow: [255,180,40],
    floor: [8,5,3], floorDot: [14,8,4],
    playerGlow: [255,200,80], pingFlash: [255,160,30],
    exitUnlock: '#fd0',
  },
  { // 5: Void Abyss — near-black, white glow
    wall: [16,16,20], wallGlow: [200,200,220],
    floor: [3,3,6], floorDot: [8,8,14],
    playerGlow: [220,220,255], pingFlash: [180,180,200],
    exitUnlock: '#fff',
  },
];

function setTheme(idx) { currentTheme = idx % THEME_PALETTES.length; }
function palette() { return THEME_PALETTES[currentTheme]; }

function initPixelRenderer() {
  const canvas = document.getElementById('gameCanvas');
  if (!canvas) return null;
  canvas.width = VW * TILE;
  canvas.height = VH * TILE;
  canvas.style.imageRendering = 'pixelated';
  canvas.style.width = '100%';
  canvas.style.height = '100%';
  prCtx = canvas.getContext('2d');
  prCtx.imageSmoothingEnabled = false;
  return prCtx;
}

/* ═══════════════════════════════════════════════════════════════════════
   SPRITE DRAWING FUNCTIONS
   ═══════════════════════════════════════════════════════════════════════ */

function drawFloor(ctx, x, y) {
  const p = palette();
  ctx.fillStyle = `rgb(${p.floor[0]},${p.floor[1]},${p.floor[2]})`;
  ctx.fillRect(x, y, TILE, TILE);
  ctx.fillStyle = `rgb(${p.floorDot[0]},${p.floorDot[1]},${p.floorDot[2]})`;
  ctx.fillRect(x + TILE/2, y + TILE/2, 1, 1);
}

function drawWall(ctx, x, y, brightness) {
  const b = Math.min(1, Math.max(0, brightness));
  const imp = getWallImpact(x, y);
  const squash = imp ? Math.max(0, imp.age / 14) : 0;

  ctx.save();

  // Deformation: squash toward impact direction (dramatic)
  if (squash > 0.01) {
    const cx = x + TILE/2, cy = y + TILE/2;
    const amount = squash * 0.6; // 60% compression — very visible
    const sx = (imp.dir === 'left' || imp.dir === 'right') ? 1 - amount : 1;
    const sy = (imp.dir === 'up' || imp.dir === 'down') ? 1 - amount : 1;
    ctx.translate(cx, cy);
    ctx.scale(sx, sy);
    ctx.translate(-cx, -cy);
  }

  const p = palette();
  const glow = b > 0.6 ? (b - 0.6) * 2.5 : 0;
  const w = p.wall, wg = p.wallGlow;
  const bodyL = Math.floor(b * 16 + 4 + glow * 18);
  const rr = Math.floor(w[0] * b + bodyL * 0.3 + wg[0] * glow * 0.15);
  const gg = Math.floor(w[1] * b + bodyL * 0.3 + wg[1] * glow * 0.15);
  const bb = Math.floor(w[2] * b + bodyL * 0.3 + wg[2] * glow * 0.15);
  ctx.fillStyle = `rgb(${rr},${gg},${bb})`;
  ctx.fillRect(x + 1, y + 1, TILE - 2, TILE - 2);
  ctx.fillStyle = `rgba(0,0,0,${0.3 - b * 0.1})`;
  ctx.fillRect(x + 3, y + 3, TILE - 6, TILE - 6);

  const edgeAlpha = 0.15 + b * 0.6 + glow * 0.5;
  ctx.fillStyle = `rgba(${wg[0]},${wg[1]},${wg[2]},${Math.min(1, edgeAlpha)})`;
  ctx.fillRect(x + 1, y + 1, TILE - 2, 1);
  ctx.fillRect(x + 1, y + 1, 1, TILE - 2);
  ctx.fillStyle = `rgba(${wg[0]},${wg[1]},${wg[2]},${edgeAlpha * 0.4})`;
  ctx.fillRect(x + 1, y + TILE - 2, TILE - 2, 1);
  ctx.fillRect(x + TILE - 2, y + 1, 1, TILE - 2);

  if (squash > 0.2) {
    ctx.fillStyle = `rgba(${wg[0]+50},${wg[1]+50},${wg[2]+50},${squash * 0.5})`;
    ctx.fillRect(x - 1, y - 1, TILE + 2, TILE + 2);
  }
  if (squash > 0.4) {
    ctx.strokeStyle = `rgba(${wg[0]+60},${wg[1]+60},${wg[2]+60},${squash})`;
    ctx.lineWidth = 1;
    const cx2 = x + TILE/2, cy2 = y + TILE/2;
    ctx.beginPath(); ctx.moveTo(x+3,y+2); ctx.lineTo(cx2+squash*4-2,cy2-1); ctx.lineTo(x+TILE-3,y+TILE-4); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(x+6,y+TILE-2); ctx.lineTo(cx2,cy2+2); ctx.lineTo(x+3,y+4); ctx.stroke();
  }

  ctx.restore();
}

function drawGhostWall(ctx, x, y, brightness) {
  const b = Math.min(1, Math.max(0, brightness));
  ctx.fillStyle = `rgba(20,40,20,${0.5 * b})`;
  ctx.fillRect(x + 2, y + 2, TILE - 4, TILE - 4);
}

function drawPlayer(ctx, x, y, amp, walkerClass) {
  const cx = x + TILE/2, cy = y + TILE/2;
  const glowR = 4 + (amp || 0) * 4;

  // Outer glow (differs per character)
  const pg = palette().playerGlow;
  let glowCol;
  if (walkerClass === 'ghost') glowCol = 'rgba(180,200,255,0.5)';
  else glowCol = `rgba(${pg[0]},${pg[1]},${pg[2]},0.7)`;

  const grad = ctx.createRadialGradient(cx, cy, 2, cx, cy, glowR + 6);
  grad.addColorStop(0, glowCol);
  grad.addColorStop(0.5, 'rgba(0,0,0,0)');
  grad.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = grad;
  ctx.fillRect(x - glowR - 4, y - glowR - 4, TILE + glowR*2 + 8, TILE + glowR*2 + 8);

  ctx.save();
  ctx.translate(cx, cy);

  if (walkerClass === 'ghost') {
    drawGhostSprite(ctx, amp);
  } else {
    drawProphetSprite(ctx, amp);  // Default / Prophet
  }

  ctx.restore();
}

// Animation update — called each frame before render
function updateAnimations(state) {
  const m = state.steps || 0;
  const p = state.pings || 0;
  const d = state.damageFlash || 0;

  // Walk detection
  if (m !== lastMoves) {
    walkPhase = 12; lastMoves = m;
    if (typeof sfxStep === 'function') sfxStep();
    if (state.mapGrid) {
      if (lastPx >= 0) { playerDx = state.mapGrid.px - lastPx; playerDy = state.mapGrid.py - lastPy; }
      lastPx = state.mapGrid.px; lastPy = state.mapGrid.py;
    }
  }
  // Ping detection
  if (p !== lastPings) { pingPhase = 10; lastPings = p; }
  // Hurt detection
  if (d > 0 && d !== lastDamage) { hurtPhase = 8; lastDamage = d; }
  if (d === 0) lastDamage = 0;

  // Decay
  if (walkPhase > 0) walkPhase--; else playerDx = playerDy = 0;
  if (pingPhase > 0) pingPhase--;
  if (hurtPhase > 0) hurtPhase--;
  idlePhase += 0.05;
}

// ── Prophet (先知) — detailed hooded mystic ──
function drawProphetSprite(ctx, amp) {
  const bob = Math.sin(idlePhase) * 0.4;
  const walkBob = walkPhase > 0 ? Math.sin(walkPhase * 0.8) * 1.5 : 0;
  const hurtShake = hurtPhase > 0 ? (Math.random() - 0.5) * hurtPhase * 0.6 : 0;
  const pingGlow = pingPhase > 0 ? pingPhase / 10 : 0;
  const robeSway = walkPhase > 0 ? Math.sin(walkPhase * 0.6) * 1 : 0;

  ctx.save();
  ctx.translate(hurtShake, bob + walkBob + hurtShake);

  // ── Ping radial glow ──
  if (pingGlow > 0.1) {
    const pg = palette().playerGlow;
    const grad = ctx.createRadialGradient(0, -1, 3, 0, -1, 14 + pingGlow * 10);
    grad.addColorStop(0, `rgba(${pg[0]},${pg[1]},${pg[2]},${pingGlow * 0.6})`);
    grad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = grad;
    ctx.fillRect(-16, -16, 32, 32);
  }

  // ── Shadow under feet ──
  ctx.fillStyle = 'rgba(0,0,0,0.3)';
  ctx.fillRect(-3, 7, 6, 2);

  // ── Staff (behind robe, left side) ──
  const staffSwing = walkPhase > 0 ? Math.sin(walkPhase * 0.5) * 2 : 0;
  const staffRaise = pingGlow * 5;
  ctx.save();
  ctx.translate(-5 + staffSwing * 0.3, -7 + staffRaise * 0.2);
  // Staff pole
  ctx.fillStyle = '#6b5040';
  ctx.fillRect(0, 3, 2, 11);
  ctx.fillStyle = '#8b7060';
  ctx.fillRect(0, 3, 1, 11);
  // Staff head — crystal housing
  ctx.fillStyle = '#444';
  ctx.fillRect(-1, 1, 4, 3);
  // Crystal
  const crystalCol = pingGlow > 0.3 ? '#fff' : '#0ff';
  ctx.fillStyle = crystalCol;
  ctx.fillRect(0, -1, 2, 3);
  ctx.fillStyle = 'rgba(255,255,255,0.5)';
  ctx.fillRect(0, -1, 1, 1);
  ctx.restore();

  // ── Robe body ──
  // Outer robe (dark purple)
  ctx.fillStyle = '#1e1638';
  ctx.beginPath();
  ctx.moveTo(-4 + robeSway * 0.3, 7);
  ctx.lineTo(-5, 2);
  ctx.lineTo(-5 - pingGlow * 1.5, -2);
  ctx.lineTo(-3, -5);
  ctx.lineTo(0, -8);
  ctx.lineTo(3, -5);
  ctx.lineTo(5 + pingGlow * 1.5, -2);
  ctx.lineTo(5, 2);
  ctx.lineTo(4 + robeSway * 0.3, 7);
  ctx.closePath();
  ctx.fill();

  // Robe inner layer (lighter purple, visible at front opening)
  ctx.fillStyle = '#2a1e4a';
  ctx.fillRect(-2, -4, 4, 11);

  // Robe folds (vertical lines)
  ctx.fillStyle = '#18102e';
  ctx.fillRect(-4, 2, 1, 5);
  ctx.fillRect(3, 2, 1, 5);
  ctx.fillStyle = 'rgba(255,255,255,0.04)';
  ctx.fillRect(-3, 1, 1, 6);
  ctx.fillRect(2, 1, 1, 6);

  // ── Hood face area ──
  ctx.fillStyle = '#0e0820';
  ctx.fillRect(-3, -7, 6, 4);

  // ── Eyes ──
  const eyeGlow = 2 + amp * 1.5 + pingGlow * 8;
  ctx.fillStyle = '#0ff';
  ctx.shadowColor = '#0ff';
  ctx.shadowBlur = eyeGlow;
  ctx.fillRect(-2, -5, 2, 2);
  ctx.fillRect(1, -5, 2, 2);
  // Eye centers (white hot)
  ctx.fillStyle = '#fff';
  ctx.fillRect(-1, -4, 1, 1);
  ctx.fillRect(2, -4, 1, 1);
  ctx.shadowBlur = 0;

  // ── Hood edge highlight ──
  ctx.fillStyle = '#3a2860';
  ctx.fillRect(-4, -6, 8, 1);
  ctx.fillStyle = 'rgba(255,255,255,0.06)';
  ctx.fillRect(-3, -7, 6, 1);

  // ── Belt / sash ──
  ctx.fillStyle = '#6b4080';
  ctx.fillRect(-5, 1, 10, 2);
  ctx.fillStyle = '#8a50a0';
  ctx.fillRect(-5, 1, 10, 1);
  // Belt pendant
  ctx.fillStyle = '#c0a030';
  ctx.fillRect(-1, 3, 2, 2);

  // ── Arms in sleeves (folded) ──
  ctx.fillStyle = '#1e1638';
  ctx.fillRect(-6 - pingGlow * 2, -2, 3, 5);
  ctx.fillRect(3 + pingGlow * 2, -2, 3, 5);
  // Hands (just visible at sleeve ends)
  ctx.fillStyle = '#8a7a90';
  ctx.fillRect(-4 - pingGlow * 2, 3, 2, 2);
  ctx.fillRect(3 + pingGlow * 2, 3, 2, 2);

  // ── Hurt flash overlay ──
  if (hurtPhase > 2) {
    ctx.fillStyle = `rgba(255,40,40,${hurtPhase / 14})`;
    ctx.fillRect(-7, -9, 14, 17);
  }

  // ── Footstep dust ──
  if (walkPhase > 3 && walkPhase < 11) {
    ctx.fillStyle = 'rgba(80,100,120,0.25)';
    ctx.fillRect(-3, 8, 2, 1);
    ctx.fillRect(2, 8, 2, 1);
  }

  ctx.restore();
}

// ── Ghost (幽灵) — detailed ethereal wraith ──
function drawGhostSprite(ctx, amp) {
  const floatY = Math.sin(idlePhase * 0.7) * 1.2;
  const wave1 = Math.sin(idlePhase * 0.4) * 0.5;
  const wave2 = Math.cos(idlePhase * 0.35) * 0.4;
  const pingGlow = pingPhase > 0 ? pingPhase / 10 : 0;
  const hurtShake = hurtPhase > 0 ? (Math.random() - 0.5) * hurtPhase * 0.5 : 0;
  const walkWiden = walkPhase > 0 ? Math.sin(walkPhase * 0.7) * 0.6 : 0;

  ctx.save();
  ctx.translate(hurtShake, floatY + hurtShake - 2);

  const bodyAlpha = 0.4 + pingGlow * 0.35;

  // ── Ping: bright aura ──
  if (pingGlow > 0.1) {
    const grad = ctx.createRadialGradient(0, -2, 3, 0, -2, 14 + pingGlow * 6);
    grad.addColorStop(0, `rgba(180,220,255,${pingGlow * 0.55})`);
    grad.addColorStop(0.5, `rgba(140,180,230,${pingGlow * 0.2})`);
    grad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = grad;
    ctx.fillRect(-16, -16, 32, 32);
  }

  // ── Shadow/ground connection ──
  ctx.fillStyle = 'rgba(100,150,200,0.08)';
  ctx.fillRect(-4, 7, 8, 2);

  // ── Trailing wisps (behind main body) ──
  for (let i = 0; i < 3; i++) {
    const wx = -2 + i * 2 + Math.sin(idlePhase * 0.5 + i) * 1.5;
    const wy = 5 + i * 2 + Math.cos(idlePhase * 0.4 + i) * 1;
    ctx.fillStyle = `rgba(140,190,240,${bodyAlpha * 0.3})`;
    ctx.fillRect(wx, wy, 3 - i * 0.5, 2 + i);
  }

  // ── Main ethereal body ──
  ctx.fillStyle = `rgba(160,210,250,${bodyAlpha})`;
  ctx.beginPath();
  ctx.moveTo(-4 + walkWiden, 6);
  ctx.lineTo(-4, 0);
  ctx.lineTo(-3, -3);
  ctx.lineTo(-1, -5 + wave1);
  ctx.lineTo(0, -7 + wave1);
  ctx.lineTo(1, -5 + wave2);
  ctx.lineTo(3, -3);
  ctx.lineTo(4, 0);
  ctx.lineTo(4 - walkWiden, 6);
  ctx.closePath();
  ctx.fill();

  // ── Inner body (denser core) ──
  ctx.fillStyle = `rgba(180,225,255,${bodyAlpha * 0.8})`;
  ctx.fillRect(-2, -3, 4, 8);

  // ── Head ──
  ctx.fillStyle = `rgba(190,235,255,${bodyAlpha * 1.1})`;
  ctx.beginPath();
  ctx.arc(0, -4, 3, 0, Math.PI * 2);
  ctx.fill();

  // ── Eyes — hollow bright ──
  const eyeAlpha = 0.7 + pingGlow * 0.3;
  ctx.fillStyle = `rgba(255,255,255,${eyeAlpha})`;
  ctx.shadowColor = 'rgba(200,230,255,0.6)';
  ctx.shadowBlur = 2 + pingGlow * 4;
  ctx.fillRect(-2, -5, 2, 2);
  ctx.fillRect(1, -5, 2, 2);
  ctx.shadowBlur = 0;

  // ── Skeletal rib hints ──
  ctx.fillStyle = `rgba(200,230,255,${bodyAlpha * 0.2})`;
  for (let r = 0; r < 3; r++) {
    ctx.fillRect(-3, r * 2, 6, 1);
  }

  // ── Body outline ──
  ctx.strokeStyle = `rgba(200,235,255,${0.2 + pingGlow * 0.25})`;
  ctx.lineWidth = 0.5;
  ctx.beginPath();
  ctx.moveTo(-4 + walkWiden, 6);
  ctx.lineTo(-4, 0); ctx.lineTo(-3, -3);
  ctx.lineTo(-1, -5 + wave1);
  ctx.lineTo(0, -7 + wave1);
  ctx.lineTo(1, -5 + wave2);
  ctx.lineTo(3, -3); ctx.lineTo(4, 0);
  ctx.lineTo(4 - walkWiden, 6);
  ctx.stroke();

  // ── Floating soul particles ──
  const pCount = pingGlow > 0.15 ? 5 : 3;
  for (let i = 0; i < pCount; i++) {
    const px = -5 + Math.sin(idlePhase * 0.25 + i * 1.2) * 4;
    const py = -6 + Math.cos(idlePhase * 0.3 + i * 1.1) * 4;
    const sz = (i === 0 ? 1.5 : 1);
    ctx.fillStyle = `rgba(200,230,255,${0.25 + pingGlow * 0.35})`;
    ctx.fillRect(px, py, sz, sz);
  }

  // ── Hurt flash ──
  if (hurtPhase > 2) {
    ctx.fillStyle = `rgba(255,60,60,${hurtPhase / 16})`;
    ctx.fillRect(-6, -9, 12, 16);
  }

  ctx.restore();
}

function drawExit(ctx, x, y, unlocked) {
  const cx = x + TILE/2, cy = y + TILE/2;
  const col = unlocked ? '#fd0' : '#440';
  const glowCol = unlocked ? 'rgba(255,200,0,0.5)' : 'rgba(60,40,0,0.3)';
  // Glow
  const grad = ctx.createRadialGradient(cx, cy, 3, cx, cy, 8);
  grad.addColorStop(0, glowCol);
  grad.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = grad;
  ctx.fillRect(x - 2, y - 2, TILE + 4, TILE + 4);
  // Arch shape
  ctx.fillStyle = col;
  ctx.fillRect(x + 3, y + 5, TILE - 6, TILE - 5);
  ctx.fillRect(x + 5, y + 3, TILE - 10, TILE - 3);
  // Pulse ring if unlocked
  if (unlocked && prAnimFrame % 20 < 10) {
    ctx.strokeStyle = col;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(cx, cy, 7 + Math.sin(prAnimFrame * 0.3) * 2, 0, Math.PI * 2);
    ctx.stroke();
  }
}

function drawItem(ctx, x, y, itemType) {
  const cx = x + TILE/2, cy = y + TILE/2;
  // Glow base
  const grad = ctx.createRadialGradient(cx, cy, 1, cx, cy, 6);
  let col, col2;
  if (itemType === 'QUEST_KEY') {
    col = 'rgba(255,220,0,0.6)'; col2 = 'rgba(255,180,0,0)';
  } else if (itemType === 'ENERGY_CRYSTAL') {
    col = 'rgba(0,200,255,0.6)'; col2 = 'rgba(0,100,200,0)';
  } else if (itemType === 'SONAR_RUNE') {
    col = 'rgba(0,220,200,0.6)'; col2 = 'rgba(0,150,150,0)';
  } else {  // MEMORY_FRAGMENT
    col = 'rgba(200,60,200,0.6)'; col2 = 'rgba(150,0,150,0)';
  }
  grad.addColorStop(0, col);
  grad.addColorStop(1, col2);
  ctx.fillStyle = grad;
  ctx.fillRect(x - 2, y - 2, TILE + 4, TILE + 4);

  if (itemType === 'QUEST_KEY') {
    // Key shape: circle + stem
    ctx.fillStyle = '#fd0';
    ctx.beginPath();
    ctx.arc(cx, cy - 3, 3, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillRect(cx + 2, cy - 3, 3, 2);
    ctx.fillRect(cx, cy, 2, 5);
  } else if (itemType === 'ENERGY_CRYSTAL') {
    // Diamond crystal
    ctx.fillStyle = '#0cf';
    ctx.beginPath();
    ctx.moveTo(cx, cy - 5);
    ctx.lineTo(cx + 4, cy);
    ctx.lineTo(cx, cy + 5);
    ctx.lineTo(cx - 4, cy);
    ctx.fill();
    ctx.fillStyle = '#fff';
    ctx.fillRect(cx - 1, cy - 1, 2, 2);
  } else if (itemType === 'SONAR_RUNE') {
    // Concentric arcs
    ctx.strokeStyle = '#0cc';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc(cx, cy, 4, 0, Math.PI * 2);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(cx, cy, 2, 0, Math.PI * 1.5);
    ctx.stroke();
  } else {
    // Memory fragment: ? shape
    ctx.fillStyle = '#c4c';
    ctx.font = 'bold 10px monospace';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('?', cx, cy);
  }
}

function drawPredator(ctx, x, y, state) {
  const cx = x + TILE/2, cy = y + TILE/2;
  let bodyCol, glowCol;
  if (state === 1) {  // Hunting
    bodyCol = '#f33';
    glowCol = 'rgba(255,50,50,0.4)';
  } else if (state === 2) {  // Stunned
    bodyCol = '#666';
    glowCol = 'rgba(0,0,0,0)';
  } else {  // Wandering
    bodyCol = '#c84';
    glowCol = 'rgba(200,130,50,0.2)';
  }
  // Glow for hunting
  if (state === 1) {
    const grad = ctx.createRadialGradient(cx, cy, 2, cx, cy, 8);
    grad.addColorStop(0, glowCol);
    grad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = grad;
    ctx.fillRect(x - 4, y - 4, TILE + 8, TILE + 8);
  }
  // Body (menacing triangle)
  ctx.fillStyle = bodyCol;
  ctx.beginPath();
  ctx.moveTo(cx, cy - 6);
  ctx.lineTo(cx + 5, cy + 4);
  ctx.lineTo(cx - 5, cy + 4);
  ctx.closePath();
  ctx.fill();
  // Eyes
  ctx.fillStyle = '#fff';
  ctx.fillRect(cx - 2, cy - 1, 2, 2);
  ctx.fillRect(cx + 1, cy - 1, 2, 2);
}

function drawBoss(ctx, x, y, bossType, shields) {
  const cx = x + TILE/2, cy = y + TILE/2;
  // Large glow
  const grad = ctx.createRadialGradient(cx, cy, 3, cx, cy, 12);
  let glowCol;
  if (bossType === 'echo_mother') glowCol = 'rgba(68,136,255,0.3)';       // blue for acoustic simulator
  else if (bossType === 'silent_hunter') glowCol = 'rgba(200,50,30,0.3)';  // red for security drone
  else glowCol = 'rgba(136,68,204,0.3)';                                     // purple for core projection
  grad.addColorStop(0, glowCol);
  grad.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = grad;
  ctx.fillRect(x - 8, y - 8, TILE + 16, TILE + 16);

  // Body color per boss type
  let bodyCol;
  if (bossType === 'echo_mother') bodyCol = '#4488ff';
  else if (bossType === 'silent_hunter') bodyCol = '#cc3322';
  else bodyCol = '#8844cc';
  ctx.fillStyle = bodyCol;
  ctx.beginPath();
  const r = 7;
  for (let i = 0; i < 8; i++) {
    const a = Math.PI * 2 * i / 8 - Math.PI / 8;
    const px = cx + Math.cos(a) * r;
    const py = cy + Math.sin(a) * r;
    if (i === 0) ctx.moveTo(px, py);
    else ctx.lineTo(px, py);
  }
  ctx.closePath();
  ctx.fill();

  // Shields indicator (3 segments)
  const sh = shields || 3;
  const segW = 6;
  for (let i = 0; i < 3; i++) {
    ctx.fillStyle = i < sh ? '#fff' : '#333';
    ctx.fillRect(cx - 9 + i * (segW + 1), cy - 4, segW, 3);
  }
}

/* ═══════════════════════════════════════════════════════════════════════
   EFFECTS
   ═══════════════════════════════════════════════════════════════════════ */

let screenShakeX = 0, screenShakeY = 0, shakeIntensity = 0;

// Wall deformation system — walls squash on impact then spring back
let wallImpacts = {};  // key: "x,y" → { age, dir }

function registerWallImpact(wx, wy, dir) {
  const key = wx + ',' + wy;
  wallImpacts[key] = { age: 20, dir: dir };  // 20 frames (~1 second)
}

function tickWallImpacts() {
  for (const k in wallImpacts) {
    wallImpacts[k].age--;
    if (wallImpacts[k].age <= 0) delete wallImpacts[k];
  }
}

function getWallImpact(x, y) {
  return wallImpacts[x + ',' + y] || null;
}

function triggerScreenShake(intensity) {
  shakeIntensity = Math.max(shakeIntensity || 0, intensity);
}

function drawScreenShake(ctx) {
  if (shakeIntensity > 0.1) {
    screenShakeX = (Math.random() - 0.5) * shakeIntensity * 6;
    screenShakeY = (Math.random() - 0.5) * shakeIntensity * 4;
    shakeIntensity *= 0.85;
    if (shakeIntensity < 0.1) { screenShakeX = 0; screenShakeY = 0; shakeIntensity = 0; }
  }
}

/* ═══════════════════════════════════════════════════════════════════════
   MAIN FRAME RENDER
   ═══════════════════════════════════════════════════════════════════════ */

const THEME_NAMES = ['Ocean Deep','Volcanic Fury','Forest Spirit','Crystal Prism','Sunset Gold','Void Abyss'];

function renderPixelFrame(state) {
  if (!prCtx || !state || !state.mapGrid) return;
  // Match theme
  if (state.themeName) {
    const ti = THEME_NAMES.indexOf(state.themeName);
    if (ti >= 0) currentTheme = ti;
  }
  const ctx = prCtx;
  const { grid } = state.mapGrid;
  const cw = ctx.canvas.width;
  const ch = ctx.canvas.height;

  // Update character animations
  updateAnimations(state);

  // Screen shake
  if (state.damageFlash > 0 || (state.waveAmp || 0) > 0.3) {
    triggerScreenShake(state.damageFlash > 0 ? 1 : 0.3);
  }
  drawScreenShake(ctx);

  ctx.save();
  ctx.translate(screenShakeX, screenShakeY);

  // Clear
  ctx.fillStyle = '#030508';
  ctx.fillRect(-4, -4, cw + 8, ch + 8);

  // Ping flash overlay
  if (state.waveAmp > 0.2) {
    const pf = palette().pingFlash;
    ctx.fillStyle = `rgba(${pf[0]},${pf[1]},${pf[2]},${state.waveAmp * 0.15})`;
    ctx.fillRect(-4, -4, cw + 8, ch + 8);
  }

  // Damage flash
  if (state.damageFlash > 0) {
    ctx.fillStyle = `rgba(255,30,30,${state.damageFlash * 0.12})`;
    ctx.fillRect(-4, -4, cw + 8, ch + 8);
  }

  // Wall impact detection — deform the wall the player is facing
  if (state.lastMessage) {
    const msg = state.lastMessage.toLowerCase();
    if (msg.includes('thud') || msg.includes('撞') || msg.includes('墙')) {
      if (state.mapGrid && state.mapGrid.px !== undefined) {
        const px = state.mapGrid.px, py = state.mapGrid.py;
        // Check 4 adjacent cells for walls — deform the first one found
        const dirs = [{dx:1,dy:0,d:'right'},{dx:-1,dy:0,d:'left'},{dx:0,dy:1,d:'down'},{dx:0,dy:-1,d:'up'}];
        for (const d of dirs) {
          const wx = px + d.dx, wy = py + d.dy;
          if (wx >= 0 && wy >= 0 && wx < VW && wy < VH) {
            const adj = state.mapGrid.grid[wy] && state.mapGrid.grid[wy][wx];
            if (adj && adj.t === 0) {
              registerWallImpact(wx, wy, d.d);
              break;
            }
          }
        }
      }
    }
    if (msg.includes('捕食者') || msg.includes('predator') || msg.includes('caught')) {
      triggerScreenShake(1.5);
    }
  }

  // Tick wall impacts
  tickWallImpacts();

  // Draw cells
  for (let r = 0; r < grid.length; r++) {
    const row = grid[r];
    for (let c = 0; c < row.length; c++) {
      const cell = row[c];
      if (!cell || cell.t === -1) continue;
      const gx = c * TILE, gy = r * TILE;

      // Floor
      if (cell.e > 0.5 || cell.v > 0) {
        drawFloor(ctx, gx, gy);
      }

      // Wall
      if (cell.t === 0 && cell.v > 0) {
        drawWall(ctx, gx, gy, cell.v / 20);
        // Flash on fresh reveal
        if (cell.v > 15) {
          ctx.fillStyle = `rgba(0,255,140,${(cell.v - 15) / 20 * 0.3})`;
          ctx.fillRect(gx - 1, gy - 1, TILE + 2, TILE + 2);
        }
      } else if (cell.t === 0 && cell.e > 1) {
        drawGhostWall(ctx, gx, gy, cell.e / 20);
      }

      // Player
      if (cell.p) drawPlayer(ctx, gx, gy, state.waveAmp || 0, state.walkerClass);
      // Exit
      if (cell.x) drawExit(ctx, gx, gy, state.questComplete);
      // Items
      if (cell.i) drawItem(ctx, gx, gy, cell.i);
      // Predators
      if (cell.r !== undefined) drawPredator(ctx, gx, gy, cell.r);
      // Boss
      if (cell.b) drawBoss(ctx, gx, gy, cell.b, state.bossHP);
    }
  }

  ctx.restore();

  // Scanlines
  ctx.fillStyle = 'rgba(0,0,0,0.05)';
  for (let sy = 0; sy < ch; sy += 3) {
    ctx.fillRect(0, sy, cw, 1);
  }

  // Chromatic fringe at edges
  ctx.fillStyle = 'rgba(255,0,170,0.02)';
  ctx.fillRect(cw - 3, 0, 3, ch);
  ctx.fillStyle = 'rgba(0,255,255,0.02)';
  ctx.fillRect(0, 0, 3, ch);

  // Vignette
  const vignette = ctx.createRadialGradient(cw/2, ch/2, cw*0.35, cw/2, ch/2, cw*0.8);
  vignette.addColorStop(0, 'rgba(0,0,0,0)');
  vignette.addColorStop(1, 'rgba(0,0,0,0.5)');
  ctx.fillStyle = vignette;
  ctx.fillRect(0, 0, cw, ch);

  prAnimFrame++;
}
