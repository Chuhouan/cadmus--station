/* ═══════════════════════════════════════════════════════════════════════
   ECHO MAZE — Web Audio API Sound Engine
   8-bit / retro synth sounds, zero external files.
   ═══════════════════════════════════════════════════════════════════════ */

let audioCtx = null;
let muted = false;
let musicGain = null, musicRunning = false;
let lastStepSound = 0;

function initAudio() {
  if (audioCtx) return;
  try { audioCtx = new (window.AudioContext || window.webkitAudioContext)(); } catch(e) {}
  if (audioCtx && audioCtx.state === 'suspended') audioCtx.resume();
}

function beep(freq, type, duration, vol, delay) {
  if (!audioCtx || muted) return;
  const t = audioCtx.currentTime + (delay || 0);
  const osc = audioCtx.createOscillator();
  const g = audioCtx.createGain();
  osc.type = type || 'sine';
  osc.frequency.setValueAtTime(freq, t);
  g.gain.setValueAtTime(vol || 0.15, t);
  g.gain.exponentialRampToValueAtTime(0.001, t + (duration || 0.15));
  osc.connect(g); g.connect(audioCtx.destination);
  osc.start(t); osc.stop(t + (duration || 0.15) + 0.01);
}

function noise(duration, vol, delay) {
  if (!audioCtx || muted) return;
  const t = audioCtx.currentTime + (delay || 0);
  const buf = audioCtx.createBuffer(1, audioCtx.sampleRate * duration, audioCtx.sampleRate);
  const data = buf.getChannelData(0);
  for (let i = 0; i < data.length; i++) data[i] = (Math.random() * 2 - 1);
  const src = audioCtx.createBufferSource();
  src.buffer = buf;
  const g = audioCtx.createGain();
  g.gain.setValueAtTime(vol || 0.1, t);
  g.gain.exponentialRampToValueAtTime(0.001, t + duration);
  const filter = audioCtx.createBiquadFilter();
  filter.type = 'bandpass'; filter.frequency.setValueAtTime(800, t); filter.Q.setValueAtTime(1, t);
  src.connect(filter); filter.connect(g); g.connect(audioCtx.destination);
  src.start(t); src.stop(t + duration + 0.01);
}

/* ═══════════════════════════════════════════════════════════════════════
   SOUND EFFECTS
   ═══════════════════════════════════════════════════════════════════════ */

function sfxPing() {
  if (!audioCtx || muted) return;
  const t = audioCtx.currentTime;
  // Ascending sweep
  const osc = audioCtx.createOscillator();
  const g = audioCtx.createGain();
  osc.type = 'sine';
  osc.frequency.setValueAtTime(200, t);
  osc.frequency.exponentialRampToValueAtTime(800, t + 0.12);
  g.gain.setValueAtTime(0.2, t);
  g.gain.exponentialRampToValueAtTime(0.001, t + 0.2);
  osc.connect(g); g.connect(audioCtx.destination);
  osc.start(t); osc.stop(t + 0.25);
  // Sub bass thump
  beep(60, 'sine', 0.15, 0.15, 0.02);
}

function sfxWallThud() {
  noise(0.08, 0.12);
  beep(50, 'triangle', 0.1, 0.18);
}

function sfxPickup() {
  beep(523, 'square', 0.08, 0.1);
  beep(659, 'square', 0.08, 0.1, 0.08);
  beep(784, 'square', 0.12, 0.12, 0.16);
}

function sfxKeyPickup() {
  beep(523, 'square', 0.1, 0.12);
  beep(659, 'square', 0.1, 0.12, 0.1);
  beep(784, 'square', 0.1, 0.12, 0.2);
  beep(1047, 'square', 0.2, 0.15, 0.3);
}

function sfxPredatorHit() {
  noise(0.15, 0.18);
  beep(40, 'sawtooth', 0.3, 0.2, 0.05);
  // Alarm burst
  for (let i = 0; i < 3; i++) {
    beep(800 - i * 100, 'square', 0.06, 0.08, 0.1 + i * 0.08);
  }
}

function sfxFootstep() {
  const now = audioCtx ? audioCtx.currentTime : 0;
  if (now - lastStepSound < 0.2) return;
  lastStepSound = now;
  noise(0.03, 0.03);
}

function sfxDeath() {
  beep(400, 'sawtooth', 0.5, 0.2);
  beep(300, 'sawtooth', 0.4, 0.15, 0.2);
  beep(200, 'sawtooth', 0.3, 0.1, 0.4);
  beep(80, 'triangle', 0.8, 0.12, 0.6);
}

function sfxWin() {
  const notes = [523, 659, 784, 1047, 784, 1047, 1319];
  notes.forEach((f, i) => {
    beep(f, 'square', i === notes.length - 1 ? 0.4 : 0.12, i === notes.length - 1 ? 0.15 : 0.1, i * 0.1);
  });
}

function sfxBossAppear() {
  beep(40, 'sawtooth', 0.6, 0.15);
  beep(60, 'sawtooth', 0.3, 0.1, 0.3);
  beep(80, 'square', 0.2, 0.12, 0.6);
  // Pulsing alarm
  for (let i = 0; i < 4; i++) {
    beep(120, 'sawtooth', 0.1, 0.1, 0.8 + i * 0.4);
  }
}

function sfxCombo() {
  beep(880, 'square', 0.1, 0.1);
  beep(1109, 'square', 0.1, 0.1, 0.1);
  beep(1319, 'square', 0.15, 0.12, 0.2);
}

/* ═══════════════════════════════════════════════════════════════════════
   TRIGGER SOUNDS FROM GAME MESSAGES
   ═══════════════════════════════════════════════════════════════════════ */

let playedHashes = {};  // msg fingerprint → timestamp
const AUDIO_COOLDOWN = 250;  // ms between any two sounds

function _msgHash(msg) {
  // Take first 20 chars as fingerprint — stable across minor text variations
  return (msg || '').slice(0, 20).replace(/[^a-zA-Z一-鿿]/g, '').toLowerCase();
}

function processAudioFromState(state) {
  if (!state || muted) return;
  const now = Date.now();

  const msg = state.lastMessage || '';
  if (!msg) return;

  const hash = _msgHash(msg);
  // Already played this message recently?
  if (playedHashes[hash] && now - playedHashes[hash] < 2000) return;
  // Global cooldown
  if (Object.keys(playedHashes).length > 0) {
    const lastPlay = Math.max(...Object.values(playedHashes));
    if (now - lastPlay < AUDIO_COOLDOWN) return;
  }

  const lo = msg.toLowerCase();
  let triggered = false;

  if ((lo.includes('ping') || lo.includes('脉冲') || lo.includes('pulse')) && !lo.includes('boss')) {
    sfxPing(); triggered = true;
  }
  if (lo.includes('thud') || lo.includes('撞墙') || lo.includes('撞')) {
    sfxWallThud(); triggered = true;
  }
  if (lo.includes('key') || lo.includes('钥匙') || lo.includes('quest')) {
    sfxKeyPickup(); triggered = true;
  }
  else if (lo.includes('crystal') || lo.includes('水晶') || lo.includes('能量') || lo.includes('rune') || lo.includes('符文') || lo.includes('fragment') || lo.includes('碎片')) {
    sfxPickup(); triggered = true;
  }
  if (lo.includes('predator') || lo.includes('捕食者') || lo.includes('caught') || lo.includes('抓住')) {
    sfxPredatorHit(); triggered = true;
  }
  if (lo.includes('boss') && (lo.includes('appear') || lo.includes('alert') || lo.includes('出现') || lo.includes('小心'))) {
    sfxBossAppear(); triggered = true;
  }
  if ((lo.includes('combo') || lo.includes('连击')) && !lo.includes('0')) {
    sfxCombo(); triggered = true;
  }

  if (triggered) {
    playedHashes[hash] = now;
    // Clean old entries (>5s)
    for (const h in playedHashes) { if (now - playedHashes[h] > 5000) delete playedHashes[h]; }
  }
}

// Footstep tracking — external trigger from renderer
function sfxStep() { sfxFootstep(); }

/* ═══════════════════════════════════════════════════════════════════════
   BACKGROUND MUSIC
   ═══════════════════════════════════════════════════════════════════════ */

let musicNodes = [];
let musicSeq = 0;

const MUSIC_SCALES = [
  [130.8, 164.8, 196.0, 220.0, 261.6, 329.6],  // Ocean — C minor ambient
  [110.0, 138.6, 164.8, 220.0, 277.2, 329.6],  // Volcano — D minor
  [146.8, 174.6, 220.0, 261.6, 293.7, 349.2],  // Forest — F# minor
  [130.8, 196.0, 246.9, 261.6, 329.6, 392.0],  // Crystal — C phrygian
  [164.8, 220.0, 261.6, 293.7, 349.2, 440.0],  // Sunset — E minor
  [138.6, 207.7, 277.2, 311.1, 415.3, 554.4],  // Void — C# diminished
];

function startMusic(themeIdx) {
  if (!audioCtx || musicRunning) return;
  musicRunning = true;
  musicGain = audioCtx.createGain();
  musicGain.gain.setValueAtTime(0.06, audioCtx.currentTime);
  musicGain.connect(audioCtx.destination);
  musicSeq = 0;
  const scale = MUSIC_SCALES[themeIdx % MUSIC_SCALES.length];

  function tick() {
    if (!musicRunning || muted) { setTimeout(tick, 1000); return; }
    const t = audioCtx.currentTime;
    const note = scale[Math.floor(Math.random() * scale.length)];

    // Soft pad note
    const osc = audioCtx.createOscillator();
    const g = audioCtx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(note / 2, t);  // Sub octave
    g.gain.setValueAtTime(0.04, t);
    g.gain.exponentialRampToValueAtTime(0.001, t + 2.0);
    osc.connect(g); g.connect(musicGain);
    osc.start(t); osc.stop(t + 2.1);

    // Subtle high ping (every 4th note)
    if (musicSeq % 4 === 0) {
      const osc2 = audioCtx.createOscillator();
      const g2 = audioCtx.createGain();
      osc2.type = 'triangle';
      osc2.frequency.setValueAtTime(note * 2, t);
      g2.gain.setValueAtTime(0.02, t);
      g2.gain.exponentialRampToValueAtTime(0.001, t + 0.6);
      osc2.connect(g2); g2.connect(musicGain);
      osc2.start(t); osc2.stop(t + 0.7);
    }

    musicSeq++;
    const next = 1.5 + Math.random() * 2.5;
    musicNodes = musicNodes.filter(n => n.g.gain.value > 0.001 || n.osc.playbackState !== 3);  // Keep alive ones
    setTimeout(tick, next * 1000);
  }
  tick();
}

function stopMusic() {
  musicRunning = false;
  if (musicGain) {
    musicGain.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 0.5);
  }
}

function toggleMute() {
  muted = !muted;
  if (muted && musicRunning) stopMusic();
  if (!muted && !musicRunning && audioCtx) startMusic(currentTheme);
  return muted;
}

/* ═══════════════════════════════════════════════════════════════════════
   INIT — call once on first user interaction
   ═══════════════════════════════════════════════════════════════════════ */

document.addEventListener('click', initAudio, { once: true });
document.addEventListener('keydown', initAudio, { once: true });
