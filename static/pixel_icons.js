/* ═══════════════════════════════════════════════════════════════════════
   CADMUS STATION v5.0 — Pixel Icon System
   Underground acoustic research facility accident theme.
   All hand-drawn pixel art (12×12 / 14×14 / 16×16). NO emoji.
   ═══════════════════════════════════════════════════════════════════════ */

const ICON_SIZE = 12;
const ICON_CACHE = {};

function _makeIconCanvas(size = ICON_SIZE) {
  const c = document.createElement('canvas');
  c.width = size; c.height = size;
  c.style.imageRendering = 'pixelated';
  return c;
}

function _iconToURL(c) {
  return c.toDataURL('image/png');
}

function _px(c, ctx, x, y, color) {
  const s = c.width;
  if (x < 0 || x >= s || y < 0 || y >= s) return;
  ctx.fillStyle = color;
  ctx.fillRect(x, y, 1, 1);
}

function _hline(c, ctx, y, x1, x2, color) {
  for (let x = x1; x <= x2; x++) _px(c, ctx, x, y, color);
}

function _vline(c, ctx, x, y1, y2, color) {
  for (let y = y1; y <= y2; y++) _px(c, ctx, x, y, color);
}

function _rect(c, ctx, x1, y1, x2, y2, color) {
  for (let y = y1; y <= y2; y++)
    for (let x = x1; x <= x2; x++)
      _px(c, ctx, x, y, color);
}

/* ═══════════════════════════════════════════════════════════════════════
   CHARACTER ICONS — 6 Exoskeleton Models (12×12)
   ═══════════════════════════════════════════════════════════════════════ */

// Standard MK-I / Prophet's Relic (Lin Xianhe) — blue helmet, industrial suit, damaged visor
function iconProphet() {
  if (ICON_CACHE.prophet) return ICON_CACHE.prophet;
  const c = _makeIconCanvas(), t = c.getContext('2d');
  // Helmet dome
  _hline(c,t,0,3,7,'#335577'); _px(c,t,2,1,'#335577'); _px(c,t,8,1,'#335577');
  _px(c,t,1,2,'#335577'); _px(c,t,9,2,'#335577');
  // Visor (blue glow)
  _hline(c,t,1,3,7,'#4488ff'); _px(c,t,4,2,'#66aaff'); _px(c,t,5,2,'#66aaff'); _px(c,t,6,2,'#66aaff');
  // Antenna
  _px(c,t,5,0,'#5599cc');
  // Body - industrial suit
  _rect(c,t,2,3,7,9,'#445566');
  // Chest plate (lighter)
  _rect(c,t,3,3,6,4,'#5577aa');
  // Belt
  _hline(c,t,6,2,7,'#997744');
  // Shoulder plates
  _px(c,t,1,3,'#556677'); _px(c,t,8,3,'#445566');
  _px(c,t,1,4,'#556677'); _px(c,t,8,4,'#445566');
  // Damaged corner (Lin Xianhe's broken visor)
  _px(c,t,7,1,'#ff6644');
  // Legs
  _hline(c,t,7,3,7,'#334455'); _hline(c,t,8,3,7,'#334455');
  _hline(c,t,9,3,7,'#334455'); _hline(c,t,10,4,6,'#334455');
  // Boots
  _hline(c,t,10,3,3,'#223344'); _hline(c,t,10,7,7,'#223344');
  _hline(c,t,11,3,4,'#223344'); _hline(c,t,11,6,7,'#223344');
  ICON_CACHE.prophet = _iconToURL(c);
  return ICON_CACHE.prophet;
}

// Ghost / Su Wuying's Exoskeleton — stealth black, slim, asymmetric antenna
function iconGhost() {
  if (ICON_CACHE.ghost) return ICON_CACHE.ghost;
  const c = _makeIconCanvas(), t = c.getContext('2d');
  // Sleek helmet
  _hline(c,t,0,3,6,'#1a1a2e'); _px(c,t,2,1,'#1a1a2e'); _px(c,t,7,1,'#1a1a2e');
  // Narrow visor (dim cyan)
  _hline(c,t,1,3,6,'#226688'); _px(c,t,4,2,'#338899'); _px(c,t,5,2,'#338899');
  // Asymmetric antenna (right side)
  _px(c,t,8,0,'#334455'); _px(c,t,8,1,'#334455');
  // Slim body
  _rect(c,t,2,3,7,8,'#1a1a2e');
  // Stealth mesh pattern
  _px(c,t,3,4,'#222238'); _px(c,t,5,4,'#222238'); _px(c,t,7,4,'#222238');
  _px(c,t,4,6,'#222238'); _px(c,t,6,6,'#222238');
  _px(c,t,3,8,'#222238'); _px(c,t,5,8,'#222238');
  // Utility belt
  _hline(c,t,6,2,7,'#334455');
  // Legs
  _hline(c,t,9,3,6,'#151525'); _hline(c,t,10,4,5,'#151525');
  // Light boots
  _hline(c,t,11,3,5,'#1a1a30');
  ICON_CACHE.ghost = _iconToURL(c);
  return ICON_CACHE.ghost;
}

// Behemoth / Zhao Tieshan's Mod — bulky orange, heavy plates, mining exo
function iconBehemoth() {
  if (ICON_CACHE.behemoth) return ICON_CACHE.behemoth;
  const c = _makeIconCanvas(), t = c.getContext('2d');
  // Heavy helmet
  _hline(c,t,0,2,8,'#664422'); _px(c,t,1,1,'#664422'); _px(c,t,9,1,'#664422');
  // Wide visor (orange glow)
  _hline(c,t,1,3,7,'#dd8800'); _px(c,t,3,2,'#ff9933'); _px(c,t,4,2,'#ff9933'); _px(c,t,5,2,'#ff9933'); _px(c,t,6,2,'#ff9933'); _px(c,t,7,2,'#ff9933');
  // Thick body
  _rect(c,t,1,3,9,7,'#664422');
  // Shoulder armor
  _rect(c,t,0,3,1,5,'#886633'); _rect(c,t,9,3,10,5,'#886633');
  // Chest reinforcement
  _hline(c,t,4,3,7,'#775533'); _hline(c,t,5,2,8,'#775533');
  // Heavy belt
  _hline(c,t,7,1,9,'#997755');
  // Thick legs
  _rect(c,t,2,8,8,10,'#553311');
  // Heavy boots
  _hline(c,t,10,1,9,'#442200'); _hline(c,t,11,2,8,'#331100');
  // Mining pick on back (diagonal)
  _px(c,t,0,3,'#aa8855'); _px(c,t,0,4,'#aa8855'); _px(c,t,0,5,'#aa8855');
  ICON_CACHE.behemoth = _iconToURL(c);
  return ICON_CACHE.behemoth;
}

// Singer / Chen Ge's Relay Mode — slim pink/magenta, relay antenna array
function iconSinger() {
  if (ICON_CACHE.singer) return ICON_CACHE.singer;
  const c = _makeIconCanvas(), t = c.getContext('2d');
  // Light helmet
  _hline(c,t,0,3,6,'#883366'); _px(c,t,2,1,'#883366'); _px(c,t,7,1,'#883366');
  // Visor (pink)
  _hline(c,t,1,3,6,'#ff44aa'); _px(c,t,4,2,'#ff66bb'); _px(c,t,5,2,'#ff66bb');
  // Twin antenna array (relay mode)
  _px(c,t,3,0,'#cc3388'); _px(c,t,6,0,'#cc3388');
  // Slim body
  _rect(c,t,2,3,7,8,'#772255');
  // Relay module on chest
  _rect(c,t,3,4,6,5,'#ff44aa');
  // Wire details
  _px(c,t,4,5,'#ff88cc'); _px(c,t,5,5,'#ff88cc');
  // Belt
  _hline(c,t,7,2,7,'#994477');
  // Slim legs
  _hline(c,t,9,3,6,'#662244'); _hline(c,t,10,4,5,'#662244');
  _hline(c,t,11,4,5,'#551133');
  // Signal wave (right side)
  _px(c,t,10,2,'#ff88cc'); _px(c,t,10,4,'#ff88cc'); _px(c,t,9,3,'#ff88cc');
  ICON_CACHE.singer = _iconToURL(c);
  return ICON_CACHE.singer;
}

// Shadow / Wu An's Equipment — dark grey, barely visible, erased appearance
function iconShadow() {
  if (ICON_CACHE.shadow) return ICON_CACHE.shadow;
  const c = _makeIconCanvas(), t = c.getContext('2d');
  // Faint outline — deliberately hard to see
  _hline(c,t,0,3,6,'rgba(40,40,50,0.6)'); _px(c,t,2,1,'rgba(50,50,60,0.4)'); _px(c,t,7,1,'rgba(50,50,60,0.4)');
  // Dark visor (barely visible)
  _hline(c,t,1,3,6,'rgba(60,60,80,0.3)');
  // Faint body outline
  _px(c,t,2,3,'rgba(40,40,50,0.5)'); _px(c,t,7,3,'rgba(40,40,50,0.5)');
  _px(c,t,2,4,'rgba(40,40,50,0.5)'); _px(c,t,7,4,'rgba(40,40,50,0.5)');
  _px(c,t,2,5,'rgba(40,40,50,0.5)'); _px(c,t,7,5,'rgba(40,40,50,0.5)');
  _px(c,t,2,6,'rgba(40,40,50,0.5)'); _px(c,t,7,6,'rgba(40,40,50,0.5)');
  _px(c,t,3,7,'rgba(40,40,50,0.4)'); _px(c,t,6,7,'rgba(40,40,50,0.4)');
  _px(c,t,3,8,'rgba(40,40,50,0.3)'); _px(c,t,6,8,'rgba(40,40,50,0.3)');
  // Erased streak effect
  _hline(c,t,4,3,6,'rgba(30,30,40,0.15)');
  // Single faint eye
  _px(c,t,4,2,'rgba(100,100,130,0.3)');
  // Legs (fading out)
  _px(c,t,4,9,'rgba(35,35,45,0.25)'); _px(c,t,5,9,'rgba(35,35,45,0.25)');
  _px(c,t,4,10,'rgba(30,30,40,0.15)'); _px(c,t,5,10,'rgba(30,30,40,0.15)');
  ICON_CACHE.shadow = _iconToURL(c);
  return ICON_CACHE.shadow;
}

// Resonator / Zheng Zhen's Sensor — tech green, sensor array, no weapon
function iconResonator() {
  if (ICON_CACHE.resonator) return ICON_CACHE.resonator;
  const c = _makeIconCanvas(), t = c.getContext('2d');
  // Tech helmet with sensor dome
  _hline(c,t,0,3,6,'#225544'); _px(c,t,2,1,'#225544'); _px(c,t,7,1,'#225544');
  // Green visor
  _hline(c,t,1,3,6,'#00dd88'); _px(c,t,4,2,'#00ffaa'); _px(c,t,5,2,'#00ffaa');
  // Sensor array on top
  _px(c,t,3,0,'#00cc77'); _px(c,t,5,0,'#00cc77'); _px(c,t,4,-1 > 0 ? -1 : 0,'#00cc77');
  // Body - tech suit
  _rect(c,t,2,3,7,8,'#224433');
  // Sensor equipment on chest
  _rect(c,t,3,4,6,5,'#00bb66');
  _px(c,t,4,4,'#00ff88'); _px(c,t,5,4,'#00ff88');
  // Data cable
  _px(c,t,8,4,'#00aa55'); _px(c,t,8,5,'#00aa55'); _px(c,t,8,6,'#00aa55');
  // Belt with instruments
  _hline(c,t,7,2,7,'#336644');
  // Legs
  _hline(c,t,9,3,6,'#1a3322'); _hline(c,t,10,4,5,'#1a3322');
  _hline(c,t,11,4,5,'#112211');
  // Sensor readings (right side)
  _px(c,t,9,2,'#00ff88'); _px(c,t,10,3,'#00cc66'); _px(c,t,10,5,'#00aa44');
  ICON_CACHE.resonator = _iconToURL(c);
  return ICON_CACHE.resonator;
}

/* ═══════════════════════════════════════════════════════════════════════
   ITEM ICONS — Industrial equipment
   ═══════════════════════════════════════════════════════════════════════ */

// Battery Module (was Energy Crystal)
function iconEnergy() {
  if (ICON_CACHE.energy) return ICON_CACHE.energy;
  const c = _makeIconCanvas(), t = c.getContext('2d');
  // Battery body (gray rectangle)
  _rect(c,t,2,3,8,8,'#667788');
  // Dark casing
  _rect(c,t,3,4,7,7,'#445566');
  // Positive terminal (top nub)
  _rect(c,t,4,1,6,2,'#8899aa');
  // Charge bars (green-yellow gradient)
  _hline(c,t,7,3,6,'#44cc44');
  _hline(c,t,6,3,6,'#88cc44');
  _hline(c,t,5,3,6,'#cccc44');
  _hline(c,t,4,3,6,'#ffcc00');
  // Terminal highlight
  _px(c,t,5,1,'#ccdddd');
  // Bottom contact
  _hline(c,t,9,3,6,'#8899aa');
  ICON_CACHE.energy = _iconToURL(c);
  return ICON_CACHE.energy;
}

// Access Card (was Key)
function iconKey() {
  if (ICON_CACHE.key) return ICON_CACHE.key;
  const c = _makeIconCanvas(), t = c.getContext('2d');
  // Card body
  _rect(c,t,2,3,8,8,'#4488aa');
  // Card edge highlight
  _hline(c,t,3,3,8,'#66aacc');
  // Magnetic stripe
  _hline(c,t,7,3,7,'#335566');
  // Chip (gold)
  _rect(c,t,4,4,6,5,'#ffcc44');
  _px(c,t,4,4,'#ffdd66'); _px(c,t,5,4,'#ffdd66');
  // Contact pads
  _px(c,t,3,5,'#ddbb33'); _px(c,t,6,5,'#ddbb33');
  // Card edge
  _hline(c,t,8,3,8,'#336677');
  // Glow
  _px(c,t,5,4,'#ffee88');
  ICON_CACHE.key = _iconToURL(c);
  return ICON_CACHE.key;
}

// Frequency Amplifier Module (was Sonar Rune icon)
function iconRune() {
  if (ICON_CACHE.rune) return ICON_CACHE.rune;
  const c = _makeIconCanvas(), t = c.getContext('2d');
  // Hexagonal circuit board
  _px(c,t,5,1,'#33cccc'); _px(c,t,4,2,'#33cccc'); _px(c,t,6,2,'#33cccc');
  _hline(c,t,3,3,7,'#2288aa');
  // Inner circuit traces
  _hline(c,t,5,3,7,'#33cccc');
  // Hex corners
  _px(c,t,3,3,'#33cccc'); _px(c,t,7,3,'#33cccc');
  _px(c,t,4,6,'#33cccc'); _px(c,t,6,6,'#33cccc');
  _hline(c,t,4,4,6,'#226677');
  _hline(c,t,5,5,5,'#33cccc');
  // Center chip
  _px(c,t,5,4,'#44ffdd');
  // Contact points
  _px(c,t,3,7,'#2288aa'); _px(c,t,7,7,'#2288aa');
  _px(c,t,5,7,'#33cccc');
  // Glow pulse
  _px(c,t,5,5,'#66ffff');
  ICON_CACHE.rune = _iconToURL(c);
  return ICON_CACHE.rune;
}

// Data Tablet / Narrative Fragment
function iconFragment() {
  if (ICON_CACHE.fragment) return ICON_CACHE.fragment;
  const c = _makeIconCanvas(), t = c.getContext('2d');
  // Rounded tablet
  _hline(c,t,2,3,7,'#775588'); _hline(c,t,8,3,7,'#775588');
  _px(c,t,2,3,'#9966aa'); _px(c,t,8,3,'#9966aa');
  _px(c,t,2,4,'#664477'); _px(c,t,8,4,'#664477');
  // Screen area
  _rect(c,t,3,4,7,6,'#221133');
  // Waveform lines on screen
  _px(c,t,4,5,'#cc44ff'); _px(c,t,5,4,'#cc44ff'); _px(c,t,6,5,'#cc44ff'); _px(c,t,7,4,'#cc44ff');
  // Data dots
  _px(c,t,4,6,'#aa33dd'); _px(c,t,6,6,'#aa33dd');
  // Edge
  _hline(c,t,3,3,7,'#9966aa'); _hline(c,t,9,3,7,'#553366');
  // Glow
  _px(c,t,5,5,'#ee88ff');
  ICON_CACHE.fragment = _iconToURL(c);
  return ICON_CACHE.fragment;
}

/* ═══════════════════════════════════════════════════════════════════════
   ENEMY ICONS — Drones & Bosses
   ═══════════════════════════════════════════════════════════════════════ */

// Patrol Drone (was Predator)
function iconDrone() {
  if (ICON_CACHE.drone) return ICON_CACHE.drone;
  const c = _makeIconCanvas(), t = c.getContext('2d');
  // Hexagonal body
  _px(c,t,4,3,'#889999'); _px(c,t,5,3,'#889999'); _px(c,t,6,3,'#889999');
  _hline(c,t,4,3,6,'#778888'); _hline(c,t,5,3,6,'#778888');
  _hline(c,t,6,3,6,'#667777');
  // Body fill
  _rect(c,t,3,5,7,7,'#889999');
  // Inner core
  _rect(c,t,4,5,6,6,'#667777');
  // Rotating antenna (top)
  _px(c,t,5,2,'#aabbbb');
  _px(c,t,5,1,'#cccccc');
  // Antenna rotation indicator
  _px(c,t,4,1,'#99aaaa');
  // Sensor lights
  _px(c,t,4,8,'#ff6644');  // Red sensor
  _px(c,t,6,8,'#ff6644');
  // Center light
  _px(c,t,5,6,'#44aacc');
  ICON_CACHE.drone = _iconToURL(c);
  return ICON_CACHE.drone;
}

// Hunting Drone (red alert)
function iconDroneHunt() {
  if (ICON_CACHE.droneh) return ICON_CACHE.droneh;
  const c = _makeIconCanvas(), t = c.getContext('2d');
  // Hex body (red-tinted)
  _hline(c,t,3,3,7,'#994444'); _hline(c,t,4,4,6,'#883333');
  _rect(c,t,3,5,7,7,'#994444');
  // Inner core (bright red)
  _rect(c,t,4,5,6,6,'#cc3333');
  // Alert antenna
  _px(c,t,5,2,'#ff4444');
  _px(c,t,5,1,'#ff6666');
  _px(c,t,4,1,'#ff2222');
  // Flashing sensors
  _px(c,t,4,8,'#ff0000'); _px(c,t,6,8,'#ff0000');
  // Alert core
  _px(c,t,5,6,'#ff0000');
  ICON_CACHE.droneh = _iconToURL(c);
  return ICON_CACHE.droneh;
}

// Stunned Drone (yellow flicker)
function iconDroneStun() {
  if (ICON_CACHE.drones) return ICON_CACHE.drones;
  const c = _makeIconCanvas(), t = c.getContext('2d');
  // Damaged body
  _hline(c,t,3,3,7,'#887744'); _hline(c,t,4,4,6,'#776633');
  _rect(c,t,3,5,7,7,'#887744');
  // Scrambled core
  _px(c,t,4,5,'#ffcc00'); _px(c,t,6,5,'#ffcc00');
  _px(c,t,5,6,'#ffaa00');
  // Broken antenna
  _px(c,t,5,2,'#997755');
  _px(c,t,6,1,'#997755');  // Bent
  // Yellow flicker
  _px(c,t,4,8,'#ffcc00'); _px(c,t,6,8,'#ffcc00');
  ICON_CACHE.drones = _iconToURL(c);
  return ICON_CACHE.drones;
}

// Fault Drone (broken, L8)
function iconDroneFault() {
  if (ICON_CACHE.dronef) return ICON_CACHE.dronef;
  const c = _makeIconCanvas(), t = c.getContext('2d');
  // Damaged casing
  _hline(c,t,3,3,7,'#667766'); _hline(c,t,4,4,6,'#556655');
  _rect(c,t,3,5,7,7,'#667766');
  // Cracked core
  _px(c,t,4,5,'#335533'); _px(c,t,6,5,'#335533');
  _px(c,t,5,6,'#224422');
  // Broken antenna (snapped)
  _px(c,t,5,2,'#778877');
  _px(c,t,7,1,'#778877');  // Snapped off
  // Intermittent spark
  _px(c,t,5,5,'#ffff44');
  // Crack marks
  _px(c,t,3,4,'#334433'); _px(c,t,7,6,'#334433');
  ICON_CACHE.dronef = _iconToURL(c);
  return ICON_CACHE.dronef;
}

// Sleeping Giant (L7, large)
function iconGiant() {
  if (ICON_CACHE.giant) return ICON_CACHE.giant;
  const c = _makeIconCanvas(), t = c.getContext('2d');
  // Massive body (takes most of canvas)
  _rect(c,t,1,2,9,9,'#553322');
  // Outer shell
  _hline(c,t,1,2,9,'#664433'); _hline(c,t,9,2,9,'#442211');
  _vline(c,t,1,3,8,'#664433'); _vline(c,t,9,3,8,'#442211');
  // Red pulse core (center)
  _rect(c,t,4,4,6,7,'#881111');
  _px(c,t,5,5,'#ff2222');
  // Pulse ring
  _px(c,t,3,4,'#661111'); _px(c,t,7,4,'#661111');
  _px(c,t,3,6,'#661111'); _px(c,t,7,6,'#661111');
  _px(c,t,4,3,'#661111'); _px(c,t,6,3,'#661111');
  _px(c,t,4,7,'#661111'); _px(c,t,6,7,'#661111');
  // Closed "eye" sensors
  _hline(c,t,3,4,6,'#331111');
  // Vent ports
  _px(c,t,2,5,'#442211'); _px(c,t,8,5,'#331100');
  _px(c,t,2,7,'#442211'); _px(c,t,8,7,'#331100');
  ICON_CACHE.giant = _iconToURL(c);
  return ICON_CACHE.giant;
}

// Boss Icons — larger presence

// Warning Triangle (Boss alert)
function iconBoss() {
  if (ICON_CACHE.boss) return ICON_CACHE.boss;
  const c = _makeIconCanvas(), t = c.getContext('2d');
  // Triangle outline
  _px(c,t,5,1,'#cc3344'); 
  _px(c,t,4,2,'#cc3344'); _px(c,t,6,2,'#cc3344');
  _px(c,t,3,3,'#cc3344'); _px(c,t,7,3,'#cc3344');
  _px(c,t,2,4,'#cc3344'); _px(c,t,8,4,'#cc3344');
  _px(c,t,1,5,'#cc3344'); _px(c,t,9,5,'#cc3344');
  _px(c,t,1,6,'#cc3344'); _px(c,t,9,6,'#cc3344');
  _px(c,t,1,7,'#cc3344'); _px(c,t,9,7,'#cc3344');
  _hline(c,t,8,2,8,'#cc3344');
  // Triangle fill
  _hline(c,t,3,3,7,'#66111a');
  _rect(c,t,2,4,8,7,'#77111a');
  // Inner glow
  _px(c,t,4,3,'#aa2233'); _px(c,t,5,3,'#aa2233'); _px(c,t,6,3,'#aa2233');
  _rect(c,t,3,4,7,6,'#881122');
  // Exclamation mark
  _vline(c,t,5,4,6,'#ffffff');
  _px(c,t,5,8,'#ffffff');
  ICON_CACHE.boss = _iconToURL(c); return ICON_CACHE.boss;
}

// Silent Hunter icon (Boss 2) — black hexagon drone
function iconBossHunter() {
  if (ICON_CACHE.bossh) return ICON_CACHE.bossh;
  const c = _makeIconCanvas(), t = c.getContext('2d');
  // Large hexagonal body
  _hline(c,t,2,4,6,'#111111'); _hline(c,t,8,4,6,'#111111');
  _rect(c,t,3,3,7,7,'#1a1a1a');
  _px(c,t,4,2,'#222222'); _px(c,t,6,2,'#222222');
  _px(c,t,4,8,'#222222'); _px(c,t,6,8,'#222222');
  // Red sensor arrays (6)
  _px(c,t,3,3,'#cc1111'); _px(c,t,7,3,'#cc1111');
  _px(c,t,3,5,'#ff0000'); _px(c,t,7,5,'#ff0000');
  _px(c,t,3,7,'#cc1111'); _px(c,t,7,7,'#cc1111');
  _px(c,t,5,2,'#ff0000');
  _px(c,t,5,8,'#cc1111');
  // Central core (dark red)
  _rect(c,t,4,4,6,6,'#330000');
  _px(c,t,5,5,'#ff1111');  // Glowing center
  // Armor plates
  _px(c,t,5,3,'#333333'); _px(c,t,5,7,'#333333');
  ICON_CACHE.bossh = _iconToURL(c);
  return ICON_CACHE.bossh;
}

// Void Avatar icon (Boss 3) — density ripple humanoid
function iconBossVoid() {
  if (ICON_CACHE.bossv) return ICON_CACHE.bossv;
  const c = _makeIconCanvas(), t = c.getContext('2d');
  // Humanoid ripple form
  // Head
  _hline(c,t,1,4,5,'rgba(100,140,200,0.5)');
  _px(c,t,3,0,'rgba(80,120,180,0.3)'); _px(c,t,6,0,'rgba(80,120,180,0.3)');
  // Shoulders
  _hline(c,t,2,3,6,'rgba(100,140,200,0.4)');
  // Body ripple
  _hline(c,t,3,3,6,'rgba(110,150,210,0.45)');
  _hline(c,t,4,3,6,'rgba(110,150,210,0.5)');
  _hline(c,t,5,3,6,'rgba(100,140,200,0.45)');
  _hline(c,t,6,3,6,'rgba(90,130,190,0.4)');
  // Arms (diffuse)
  _px(c,t,2,4,'rgba(80,120,180,0.3)'); _px(c,t,7,4,'rgba(80,120,180,0.3)');
  _px(c,t,1,5,'rgba(70,110,170,0.2)'); _px(c,t,8,5,'rgba(70,110,170,0.2)');
  // Legs (fading)
  _px(c,t,4,7,'rgba(90,130,190,0.35)'); _px(c,t,5,7,'rgba(90,130,190,0.35)');
  _px(c,t,4,8,'rgba(80,120,180,0.25)'); _px(c,t,5,8,'rgba(80,120,180,0.25)');
  // Eyes (bright spots in ripple)
  _px(c,t,4,1,'rgba(200,230,255,0.7)'); _px(c,t,5,1,'rgba(200,230,255,0.7)');
  // Phase shift lines
  _hline(c,t,2,4,5,'rgba(150,190,240,0.15)');
  _hline(c,t,7,3,6,'rgba(150,190,240,0.1)');
  ICON_CACHE.bossv = _iconToURL(c);
  return ICON_CACHE.bossv;
}

/* ═══════════════════════════════════════════════════════════════════════
   UI ICONS
   ═══════════════════════════════════════════════════════════════════════ */

// Exoskeleton helmet silhouette (walker selection)
function iconWalkerHelmet() {
  if (ICON_CACHE.walkerh) return ICON_CACHE.walkerh;
  const c = _makeIconCanvas(), t = c.getContext('2d');
  // Helmet dome
  _hline(c,t,1,4,5,'#3388aa'); _px(c,t,3,0,'#3388aa'); _px(c,t,6,0,'#3388aa');
  _px(c,t,2,1,'#3388aa'); _px(c,t,7,1,'#3388aa');
  // Visor slit (cyan glow)
  _hline(c,t,2,4,5,'#44cccc');
  _px(c,t,4,2,'#66eeee'); _px(c,t,5,2,'#66eeee');
  // Antenna
  _px(c,t,5,0,'#339999');
  // Chin/jaw
  _px(c,t,3,3,'#226677'); _px(c,t,6,3,'#226677');
  // Collar
  _hline(c,t,4,3,6,'#448899');
  // Neck seal
  _hline(c,t,5,3,6,'#336677');
  ICON_CACHE.walkerh = _iconToURL(c); return ICON_CACHE.walkerh;
}

function iconStats() {
  if (ICON_CACHE.stats) return ICON_CACHE.stats;
  const c = _makeIconCanvas(), t = c.getContext('2d');
  // Radar screen background
  _rect(c,t,1,1,9,9,'#0a1122');
  // Screen border
  _hline(c,t,0,1,10,'#44cccc'); _hline(c,t,10,1,10,'#44cccc');
  _vline(c,t,0,1,10,'#44cccc'); _vline(c,t,10,1,10,'#44cccc');
  // Sweep line (diagonal)
  _px(c,t,5,5,'#66eeee');
  _px(c,t,6,5,'#44cccc'); _px(c,t,5,6,'#44cccc');
  _px(c,t,7,5,'#339999'); _px(c,t,6,6,'#339999'); _px(c,t,5,7,'#339999');
  _px(c,t,8,5,'#226666'); _px(c,t,7,6,'#226666'); _px(c,t,6,7,'#226666'); _px(c,t,5,8,'#226666');
  // Blips/dots on radar
  _px(c,t,3,3,'#44ff88'); _px(c,t,8,3,'#ffaa00'); _px(c,t,3,7,'#88ccff');
  // Crosshairs
  _vline(c,t,5,2,9,'rgba(68,204,204,0.15)');
  _hline(c,t,5,2,9,'rgba(68,204,204,0.15)');
  ICON_CACHE.stats = _iconToURL(c); return ICON_CACHE.stats;
}

function iconCombo() {
  if (ICON_CACHE.combo) return ICON_CACHE.combo;
  const c = _makeIconCanvas(), t = c.getContext('2d');
  // Baseline
  _hline(c,t,7,1,10,'#886600');
  // Waveform signal
  _px(c,t,2,6,'#ffcc00'); _px(c,t,3,5,'#ffcc00');
  _px(c,t,4,4,'#ffdd33'); _px(c,t,5,3,'#ffdd33');
  _px(c,t,6,3,'#ffee66'); _px(c,t,7,5,'#ffee66');
  _px(c,t,8,6,'#ffcc00'); _px(c,t,9,6,'#ffcc00'); _px(c,t,10,7,'#ffcc00');
  // Amplitude peaks
  _px(c,t,5,2,'#ffff88'); _px(c,t,6,2,'#ffff88');
  // Small peaks
  _px(c,t,3,4,'#ffdd33'); _px(c,t,8,5,'#ffdd33');
  // Grid line
  _hline(c,t,5,2,9,'rgba(255,204,0,0.15)');
  ICON_CACHE.combo = _iconToURL(c); return ICON_CACHE.combo;
}

function iconAug() {
  if (ICON_CACHE.aug) return ICON_CACHE.aug;
  const c = _makeIconCanvas(), t = c.getContext('2d');
  // Enhancement module body
  _rect(c,t,2,2,8,8,'#221133');
  // Module border
  _hline(c,t,1,3,7,'#8844cc'); _hline(c,t,9,3,7,'#8844cc');
  _vline(c,t,2,2,8,'#8844cc'); _vline(c,t,8,2,8,'#8844cc');
  // Corner glows
  _px(c,t,2,2,'#aa55ee'); _px(c,t,8,2,'#aa55ee');
  _px(c,t,2,8,'#aa55ee'); _px(c,t,8,8,'#aa55ee');
  // Inner enhancement lines (diagonal)
  _px(c,t,3,3,'#cc66ff'); _px(c,t,4,4,'#cc66ff'); _px(c,t,5,5,'#cc66ff'); _px(c,t,6,6,'#cc66ff'); _px(c,t,7,7,'#cc66ff');
  _px(c,t,7,3,'#aa44dd'); _px(c,t,6,4,'#aa44dd'); _px(c,t,4,6,'#aa44dd'); _px(c,t,3,7,'#aa44dd');
  // Center core
  _px(c,t,5,5,'#ffffff');
  // Upgrade arrows (top and bottom)
  _px(c,t,5,0,'#dd88ff');
  _px(c,t,5,10,'#dd88ff');
  ICON_CACHE.aug = _iconToURL(c); return ICON_CACHE.aug;
}

function iconItems() {
  if (ICON_CACHE.items) return ICON_CACHE.items;
  const c = _makeIconCanvas(), t = c.getContext('2d');
  // Chip body
  _rect(c,t,2,2,8,8,'#1a3322');
  // Chip edges
  _hline(c,t,1,3,7,'#44cc44'); _hline(c,t,9,3,7,'#44cc44');
  _vline(c,t,2,2,8,'#44cc44'); _vline(c,t,8,2,8,'#44cc44');
  // Contact pins (left)
  _px(c,t,1,3,'#33aa33'); _px(c,t,1,5,'#33aa33'); _px(c,t,1,7,'#33aa33');
  // Contact pins (right)
  _px(c,t,9,3,'#33aa33'); _px(c,t,9,5,'#33aa33'); _px(c,t,9,7,'#33aa33');
  // Circuit traces
  _hline(c,t,4,3,7,'#33aa33');
  _hline(c,t,6,3,7,'#339933');
  // Center die
  _rect(c,t,3,4,7,6,'#228822');
  // Die pads
  _px(c,t,4,5,'#44ff88'); _px(c,t,5,5,'#44ff88'); _px(c,t,6,5,'#44ff88');
  _px(c,t,5,4,'#33cc66'); _px(c,t,5,6,'#33cc66');
  // Corner markers
  _px(c,t,2,2,'#66ff66');
  ICON_CACHE.items = _iconToURL(c); return ICON_CACHE.items;
}

function iconMsg() {
  if (ICON_CACHE.msg) return ICON_CACHE.msg;
  const c = _makeIconCanvas(), t = c.getContext('2d');
  // Terminal window body
  _rect(c,t,1,1,9,9,'#1a1a22');
  // Window border
  _hline(c,t,0,1,10,'#667788'); _hline(c,t,10,1,10,'#667788');
  _vline(c,t,0,1,10,'#667788'); _vline(c,t,10,1,10,'#667788');
  // Title bar
  _rect(c,t,1,1,9,2,'#445566');
  // Close/minimize dots
  _px(c,t,2,2,'#cc3344'); _px(c,t,4,2,'#ccaa44'); _px(c,t,6,2,'#44cc44');
  // Log text lines (grey)
  _hline(c,t,4,2,8,'#889999');
  _hline(c,t,6,2,7,'#778888');
  _hline(c,t,8,2,6,'#667777');
  // Blinking cursor
  _px(c,t,9,8,'#aabbbb');
  // Scan line effect
  _px(c,t,5,5,'rgba(68,204,204,0.1)');
  ICON_CACHE.msg = _iconToURL(c); return ICON_CACHE.msg;
}

function iconModsIcon() {
  if (ICON_CACHE.mods) return ICON_CACHE.mods;
  const c = _makeIconCanvas(), t = c.getContext('2d');
  // Wrench head (top left)
  _px(c,t,3,2,'#ffcc00'); _px(c,t,4,1,'#ffcc00'); _px(c,t,5,1,'#ffcc00');
  _px(c,t,2,3,'#ffcc00'); _px(c,t,2,4,'#ffcc00');
  _px(c,t,3,4,'#cc9900'); _px(c,t,4,4,'#ffcc00'); _px(c,t,5,4,'#ffcc00');
  _hline(c,t,3,3,4,'#ffcc00');
  // Wrench jaw gap
  _px(c,t,3,3,'#000000');
  // Wrench handle (diagonal shaft)
  _px(c,t,6,5,'#eedd44'); _px(c,t,7,5,'#eedd44');
  _px(c,t,7,6,'#eedd44'); _px(c,t,8,6,'#eedd44');
  _px(c,t,8,7,'#eedd44'); _px(c,t,9,7,'#eedd44');
  _px(c,t,9,8,'#eedd44');
  // Wrench head highlight
  _px(c,t,4,2,'#ffee66');
  ICON_CACHE.mods = _iconToURL(c); return ICON_CACHE.mods;
}

function iconQuest() {
  if (ICON_CACHE.quest) return ICON_CACHE.quest;
  const c = _makeIconCanvas(), t = c.getContext('2d');
  // Crosshair target
  _vline(c,t,5,0,10,'#4488ff');
  _hline(c,t,5,0,10,'#4488ff');
  // Outer ring
  _hline(c,t,2,4,6,'#6699ff'); _hline(c,t,8,4,6,'#6699ff');
  _vline(c,t,3,2,8,'#6699ff'); _vline(c,t,7,2,8,'#6699ff');
  // Inner ring
  _hline(c,t,3,4,6,'#88ccff'); _hline(c,t,7,4,6,'#88ccff');
  _vline(c,t,4,3,7,'#88ccff'); _vline(c,t,6,3,7,'#88ccff');
  // Center dot
  _px(c,t,5,5,'#ffffff');
  // Corners
  _px(c,t,2,2,'#aaddff'); _px(c,t,8,2,'#aaddff');
  _px(c,t,2,8,'#aaddff'); _px(c,t,8,8,'#aaddff');
  ICON_CACHE.quest = _iconToURL(c); return ICON_CACHE.quest;
}

function iconRoom() {
  if (ICON_CACHE.room) return ICON_CACHE.room;
  const c = _makeIconCanvas(), t = c.getContext('2d');
  // Compass rose background
  _rect(c,t,1,1,9,9,'#0a1111');
  // Compass ring
  _hline(c,t,0,2,8,'#44aaaa'); _hline(c,t,10,2,8,'#44aaaa');
  _vline(c,t,1,1,9,'#44aaaa'); _vline(c,t,9,1,9,'#44aaaa');
  // Cardinal directions
  _vline(c,t,5,0,10,'#44cccc');
  _hline(c,t,5,0,10,'#44cccc');
  // NE/NW/SE/SW
  _px(c,t,7,3,'#338888'); _px(c,t,3,3,'#338888');
  _px(c,t,7,7,'#338888'); _px(c,t,3,7,'#338888');
  // Center diamond
  _px(c,t,5,4,'#66eeee'); _px(c,t,4,5,'#66eeee'); _px(c,t,6,5,'#66eeee'); _px(c,t,5,6,'#66eeee');
  _px(c,t,5,5,'#ffffff');
  // N indicator
  _px(c,t,5,1,'#88ffff');
  ICON_CACHE.room = _iconToURL(c); return ICON_CACHE.room;
}

function iconRatingIcon() {
  if (ICON_CACHE.rating) return ICON_CACHE.rating;
  const c = _makeIconCanvas(), t = c.getContext('2d');
  // Star shape (gold)
  _px(c,t,5,1,'#ffcc00');
  _px(c,t,4,2,'#ffcc00'); _px(c,t,5,2,'#ffcc00'); _px(c,t,6,2,'#ffcc00');
  _px(c,t,3,3,'#ffcc00'); _px(c,t,4,3,'#ffdd33'); _px(c,t,5,3,'#ffdd33'); _px(c,t,6,3,'#ffdd33'); _px(c,t,7,3,'#ffcc00');
  _px(c,t,2,4,'#ffcc00'); _px(c,t,3,4,'#ffdd33'); _px(c,t,4,4,'#ffee66'); _px(c,t,5,4,'#ffee66'); _px(c,t,6,4,'#ffee66'); _px(c,t,7,4,'#ffdd33'); _px(c,t,8,4,'#ffcc00');
  _px(c,t,3,5,'#ffcc00'); _px(c,t,4,5,'#ffdd33'); _px(c,t,5,5,'#ffee66'); _px(c,t,6,5,'#ffdd33'); _px(c,t,7,5,'#ffcc00');
  _px(c,t,2,6,'#ffbb00'); _px(c,t,3,6,'#ffcc00'); _px(c,t,4,6,'#ffdd33'); _px(c,t,5,6,'#ffdd33'); _px(c,t,6,6,'#ffdd33'); _px(c,t,7,6,'#ffcc00'); _px(c,t,8,6,'#ffbb00');
  _px(c,t,3,7,'#ffbb00'); _px(c,t,4,7,'#ffcc00'); _px(c,t,5,7,'#ffcc00'); _px(c,t,6,7,'#ffcc00'); _px(c,t,7,7,'#ffbb00');
  _px(c,t,4,8,'#ffbb00'); _px(c,t,5,8,'#ffee66'); _px(c,t,6,8,'#ffbb00');
  _px(c,t,5,9,'#ffbb00');
  // Center glow
  _px(c,t,5,4,'#ffffff');
  ICON_CACHE.rating = _iconToURL(c); return ICON_CACHE.rating;
}

function iconLogo() {
  if (ICON_CACHE.logo) return ICON_CACHE.logo;
  const c = _makeIconCanvas(16), t = c.getContext('2d');
  // Gear outline (ring)
  _hline(c,t,4,6,9,'#4488ff'); _hline(c,t,11,6,9,'#4488ff');
  _vline(c,t,5,5,10,'#4488ff'); _vline(c,t,10,5,10,'#4488ff');
  // Gear teeth: top, bottom, left, right
  _px(c,t,6,3,'#4488ff'); _px(c,t,7,3,'#4488ff'); _px(c,t,8,3,'#4488ff'); _px(c,t,9,3,'#4488ff');
  _px(c,t,6,12,'#4488ff'); _px(c,t,7,12,'#4488ff'); _px(c,t,8,12,'#4488ff'); _px(c,t,9,12,'#4488ff');
  _px(c,t,3,6,'#4488ff'); _px(c,t,3,7,'#4488ff'); _px(c,t,3,8,'#4488ff'); _px(c,t,3,9,'#4488ff');
  _px(c,t,12,6,'#4488ff'); _px(c,t,12,7,'#4488ff'); _px(c,t,12,8,'#4488ff'); _px(c,t,12,9,'#4488ff');
  // Gear teeth: diagonals
  _px(c,t,4,4,'#4488ff'); _px(c,t,11,4,'#4488ff');
  _px(c,t,4,11,'#4488ff'); _px(c,t,11,11,'#4488ff');
  // Inner gear cross
  _vline(c,t,7,6,9,'#5599ff'); _hline(c,t,7,6,8,'#5599ff');
  // Sound wave arcs (right side)
  _px(c,t,13,6,'#66ccff'); _px(c,t,13,9,'#66ccff');
  _px(c,t,14,5,'#88ddff'); _px(c,t,14,6,'#88ddff'); _px(c,t,14,8,'#88ddff'); _px(c,t,14,9,'#88ddff'); _px(c,t,14,10,'#88ddff');
  _px(c,t,15,5,'#aaefff'); _px(c,t,15,7,'#aaefff'); _px(c,t,15,10,'#aaefff');
  // Center dot
  _px(c,t,7,8,'#ffffff');
  ICON_CACHE.logo = _iconToURL(c); return ICON_CACHE.logo;
}

function iconHelp() {
  if (ICON_CACHE.help) return ICON_CACHE.help;
  const c = _makeIconCanvas(14), t = c.getContext('2d');
  // Terminal bracket "[ ]" style
  _vline(c,t,2,3,10,'#44cccc'); _hline(c,t,2,2,4,'#44cccc'); _hline(c,t,10,2,4,'#44cccc');
  _vline(c,t,11,3,10,'#44cccc'); _hline(c,t,2,11,12,'#44cccc');
  // "?" character pixel art
  _hline(c,t,4,5,7,'#ffffff'); _hline(c,t,5,5,8,'#ffffff');
  _px(c,t,8,5,'#ffffff'); _px(c,t,8,6,'#ffffff');
  _px(c,t,7,6,'#ffffff'); _px(c,t,7,7,'#ffffff');
  _px(c,t,6,7,'#ffffff');
  _px(c,t,6,9,'#ffffff'); _px(c,t,6,10,'#ffffff');
  ICON_CACHE.help = _iconToURL(c); return ICON_CACHE.help;
}

function iconLang() {
  if (ICON_CACHE.lang) return ICON_CACHE.lang;
  const c = _makeIconCanvas(14), t = c.getContext('2d');
  // Pixel "中" character (left side, 5x5 area)
  _vline(c,t,2,3,8,'#44cccc'); _hline(c,t,3,1,6,'#44cccc'); _hline(c,t,8,1,6,'#44cccc');
  _px(c,t,1,4,'#44cccc'); _px(c,t,1,6,'#44cccc'); _px(c,t,1,7,'#44cccc');
  _px(c,t,6,4,'#44cccc'); _px(c,t,6,5,'#44cccc'); _px(c,t,6,6,'#44cccc'); _px(c,t,6,7,'#44cccc');
  _vline(c,t,4,2,7,'#44cccc');
  // Separator "/"
  _px(c,t,8,4,'#339999'); _px(c,t,9,5,'#339999'); _px(c,t,10,6,'#339999');
  // Pixel "A" character (right side)
  _px(c,t,12,3,'#44cccc');
  _px(c,t,11,4,'#44cccc'); _px(c,t,13,4,'#44cccc');
  _hline(c,t,5,10,12,'#44cccc');
  _vline(c,t,11,5,8,'#44cccc'); _vline(c,t,13,5,8,'#44cccc');
  _hline(c,t,7,10,12,'#44cccc');
  ICON_CACHE.lang = _iconToURL(c); return ICON_CACHE.lang;
}

function iconStart() {
  if (ICON_CACHE.start) return ICON_CACHE.start;
  const c = _makeIconCanvas(16), t = c.getContext('2d');
  // Downward deploy chevron (V-shaped arrow pointing down)
  _px(c,t,7,3,'#44cc44'); _px(c,t,8,3,'#44cc44');
  _px(c,t,6,4,'#44cc44'); _px(c,t,7,4,'#44cc44'); _px(c,t,8,4,'#44cc44'); _px(c,t,9,4,'#44cc44');
  _px(c,t,5,5,'#33aa33'); _px(c,t,6,5,'#44cc44'); _px(c,t,7,5,'#44cc44'); _px(c,t,8,5,'#44cc44'); _px(c,t,9,5,'#44cc44'); _px(c,t,10,5,'#33aa33');
  _px(c,t,4,6,'#33aa33'); _px(c,t,5,6,'#44cc44'); _px(c,t,6,6,'#44cc44'); _px(c,t,7,6,'#44cc44'); _px(c,t,8,6,'#44cc44'); _px(c,t,9,6,'#44cc44'); _px(c,t,10,6,'#44cc44'); _px(c,t,11,6,'#33aa33');
  _px(c,t,5,7,'#33aa33'); _px(c,t,6,7,'#44cc44'); _px(c,t,7,7,'#44cc44'); _px(c,t,8,7,'#44cc44'); _px(c,t,9,7,'#44cc44'); _px(c,t,10,7,'#33aa33');
  _px(c,t,6,8,'#33aa33'); _px(c,t,7,8,'#44cc44'); _px(c,t,8,8,'#44cc44'); _px(c,t,9,8,'#33aa33');
  _px(c,t,7,9,'#33aa33'); _px(c,t,8,9,'#33aa33');
  // Arrow shaft
  _px(c,t,7,10,'#228822'); _px(c,t,8,10,'#228822');
  _px(c,t,7,11,'#228822'); _px(c,t,8,11,'#228822');
  _px(c,t,7,12,'#228822'); _px(c,t,8,12,'#228822');
  ICON_CACHE.start = _iconToURL(c); return ICON_CACHE.start;
}

function iconDifficulty() {
  if (ICON_CACHE.difficulty) return ICON_CACHE.difficulty;
  const c = _makeIconCanvas(), t = c.getContext('2d');
  // Keycard badge body
  _rect(c,t,2,1,9,9,'#cc8844');
  // Edge highlight
  _hline(c,t,1,3,9,'#ddaa66');
  // Magnetic stripe
  _hline(c,t,8,3,8,'#885522');
  // Clearance level bars (top of card)
  _hline(c,t,3,2,4,'#ffeebb'); _hline(c,t,3,3,5,'#ffeebb'); _hline(c,t,3,4,6,'#ffeebb');
  // Card chip
  _rect(c,t,4,5,5,6,'#eedd99');
  _px(c,t,4,5,'#ffffff');
  // Corner notch
  _px(c,t,3,1,'transparent'); // implied by shape
  // Bottom edge
  _hline(c,t,10,2,8,'#996633');
  ICON_CACHE.difficulty = _iconToURL(c); return ICON_CACHE.difficulty;
}

function iconMapSize() {
  if (ICON_CACHE.mapsize) return ICON_CACHE.mapsize;
  const c = _makeIconCanvas(), t = c.getContext('2d');
  // Grid lines (3x3 sectors)
  _vline(c,t,4,1,10,'#44aaaa'); _vline(c,t,7,1,10,'#44aaaa');
  _hline(c,t,4,2,9,'#44aaaa'); _hline(c,t,7,2,9,'#44aaaa');
  // Grid border
  _hline(c,t,1,2,9,'#44cccc'); _hline(c,t,10,2,9,'#44cccc');
  _vline(c,t,1,2,9,'#44cccc'); _vline(c,t,10,2,9,'#44cccc');
  // Corner marks
  _px(c,t,2,2,'#66eeee'); _px(c,t,9,2,'#66eeee');
  _px(c,t,2,9,'#66eeee'); _px(c,t,9,9,'#66eeee');
  // Highlighted sector (center)
  _rect(c,t,4,4,7,7,'rgba(68,204,204,0.25)');
  // Center node
  _px(c,t,5,5,'#88ffff');
  ICON_CACHE.mapsize = _iconToURL(c); return ICON_CACHE.mapsize;
}

function iconTheme() {
  if (ICON_CACHE.theme) return ICON_CACHE.theme;
  const c = _makeIconCanvas(), t = c.getContext('2d');
  // Palette tray shape
  _hline(c,t,2,4,8,'#884488'); _hline(c,t,9,3,7,'#662266');
  _vline(c,t,3,3,8,'#994499'); _vline(c,t,8,3,8,'#662266');
  _hline(c,t,8,3,7,'#884488');
  // Thumb hole
  _px(c,t,7,4,'#110011'); _px(c,t,7,5,'#110011');
  // Color swatches
  _px(c,t,4,4,'#cc3344'); _px(c,t,5,4,'#44cc44'); _px(c,t,6,4,'#4488ff');
  _px(c,t,4,5,'#ffcc00'); _px(c,t,5,5,'#cc44ff'); _px(c,t,6,5,'#ff8844');
  _px(c,t,4,6,'#44cccc'); _px(c,t,5,6,'#ffffff'); _px(c,t,6,6,'#888888');
  // Highlight
  _px(c,t,4,3,'#bb66bb');
  ICON_CACHE.theme = _iconToURL(c); return ICON_CACHE.theme;
}

/* ═══════════════════════════════════════════════════════════════════════
   HELP CARD ICONS — Industrial facility theme
   ═══════════════════════════════════════════════════════════════════════ */

function iconHelpPlayer() {
  if(ICON_CACHE.hplayer) return ICON_CACHE.hplayer;
  const c=_makeIconCanvas(),t=c.getContext('2d');
  // Exoskeleton
  _hline(c,t,1,4,5,'#4488cc'); _px(c,t,3,0,'#4488cc'); _px(c,t,6,0,'#4488cc');
  _hline(c,t,2,3,6,'#335577'); _hline(c,t,3,3,6,'#445566');
  _hline(c,t,4,3,6,'#445566'); _hline(c,t,5,4,5,'#445566');
  _hline(c,t,7,3,6,'#334455'); _hline(c,t,8,4,5,'#334455');
  _hline(c,t,9,4,5,'#223344');
  ICON_CACHE.hplayer=_iconToURL(c);return ICON_CACHE.hplayer;
}

function iconHelpExit() {
  if(ICON_CACHE.hexit) return ICON_CACHE.hexit;
  const c=_makeIconCanvas(),t=c.getContext('2d');
  // Gate
  _vline(c,t,3,2,9,'#667788'); _vline(c,t,8,2,9,'#667788');
  _hline(c,t,1,4,7,'#889999'); _hline(c,t,9,4,7,'#556677');
  _rect(c,t,4,3,7,9,'#0a0c14');
  _px(c,t,5,5,'#4488cc'); _px(c,t,6,5,'#4488cc');
  ICON_CACHE.hexit=_iconToURL(c);return ICON_CACHE.hexit;
}

function iconHelpWall() {
  if(ICON_CACHE.hwall) return ICON_CACHE.hwall;
  const c=_makeIconCanvas(),t=c.getContext('2d');
  // Industrial wall panel
  for(let y=1;y<=9;y++)for(let x=2;x<=8;x++)_px(c,t,x,y,'#2a3040');
  _hline(c,t,3,2,8,'#3a4050'); _hline(c,t,6,2,8,'#3a4050');
  _vline(c,t,5,1,9,'#3a4050');
  _px(c,t,2,1,'#556677'); _px(c,t,8,1,'#556677');
  ICON_CACHE.hwall=_iconToURL(c);return ICON_CACHE.hwall;
}

function iconHelpKey() {
  if(ICON_CACHE.hkey) return ICON_CACHE.hkey;
  const c=_makeIconCanvas(),t=c.getContext('2d');
  // Access card
  _rect(c,t,2,3,7,7,'#4488aa');
  _hline(c,t,3,3,7,'#66aacc');
  _rect(c,t,3,4,6,5,'#ffcc44');
  _px(c,t,4,4,'#ffdd66');
  _hline(c,t,6,3,6,'#335566');
  ICON_CACHE.hkey=_iconToURL(c);return ICON_CACHE.hkey;
}

function iconHelpTrail() {
  if(ICON_CACHE.htrail) return ICON_CACHE.htrail;
  const c=_makeIconCanvas(),t=c.getContext('2d');
  // Footprints
  _px(c,t,2,6,'rgba(68,136,204,0.4)'); _px(c,t,4,5,'rgba(68,136,204,0.35)');
  _px(c,t,6,6,'rgba(68,136,204,0.3)'); _px(c,t,8,5,'rgba(68,136,204,0.2)');
  ICON_CACHE.htrail=_iconToURL(c);return ICON_CACHE.htrail;
}

function iconHelpCrystal() {
  if(ICON_CACHE.hcrystal) return ICON_CACHE.hcrystal;
  const c=_makeIconCanvas(),t=c.getContext('2d');
  // Battery module
  _rect(c,t,2,3,7,7,'#667788');
  _rect(c,t,3,4,6,6,'#445566');
  _rect(c,t,4,2,5,3,'#8899aa');
  _px(c,t,4,5,'#33cc66'); _px(c,t,5,5,'#33cc66');
  _hline(c,t,8,3,6,'#8899aa');
  ICON_CACHE.hcrystal=_iconToURL(c);return ICON_CACHE.hcrystal;
}

function iconHelpRune() {
  if(ICON_CACHE.hrune) return ICON_CACHE.hrune;
  const c=_makeIconCanvas(),t=c.getContext('2d');
  // Frequency amp hex
  _px(c,t,5,2,'#33cccc'); _px(c,t,4,3,'#33cccc'); _px(c,t,6,3,'#33cccc');
  _hline(c,t,4,3,6,'#2288aa'); _hline(c,t,5,4,5,'#33cccc');
  _hline(c,t,5,6,5,'#2288aa');
  _px(c,t,5,5,'#44ffdd');
  ICON_CACHE.hrune=_iconToURL(c);return ICON_CACHE.hrune;
}

function iconHelpFrag() {
  if(ICON_CACHE.hfrag) return ICON_CACHE.hfrag;
  const c=_makeIconCanvas(),t=c.getContext('2d');
  // Data tablet
  _hline(c,t,2,3,7,'#775588'); _hline(c,t,7,3,7,'#664477');
  _rect(c,t,3,3,6,7,'#221133');
  _px(c,t,4,4,'#cc44ff'); _px(c,t,5,5,'#cc44ff'); _px(c,t,6,4,'#cc44ff');
  ICON_CACHE.hfrag=_iconToURL(c);return ICON_CACHE.hfrag;
}

function iconHelpEcho() {
  if(ICON_CACHE.hecho) return ICON_CACHE.hecho;
  const c=_makeIconCanvas(),t=c.getContext('2d');
  // Echo chamber: amplifying rings
  _rect(c,t,3,3,7,7,'#1a3344');
  _px(c,t,5,5,'#66ccff');
  _hline(c,t,1,4,6,'#3388aa'); _hline(c,t,9,4,6,'#3388aa');
  _vline(c,t,4,1,9,'#3388aa'); _vline(c,t,6,1,9,'#3388aa');
  _px(c,t,5,0,'#3388aa'); _px(c,t,5,10,'#3388aa');
  ICON_CACHE.hecho=_iconToURL(c);return ICON_CACHE.hecho;
}

function iconHelpSilent() {
  if(ICON_CACHE.hsilent) return ICON_CACHE.hsilent;
  const c=_makeIconCanvas(),t=c.getContext('2d');
  // Silent zone: absorbed waves
  _rect(c,t,2,2,8,8,'#1a1a22');
  _px(c,t,5,5,'#334466');
  // X mark
  _px(c,t,3,3,'#cc3344'); _px(c,t,7,7,'#cc3344');
  _px(c,t,3,7,'#cc3344'); _px(c,t,7,3,'#cc3344');
  ICON_CACHE.hsilent=_iconToURL(c);return ICON_CACHE.hsilent;
}

function iconHelpWell() {
  if(ICON_CACHE.hwell) return ICON_CACHE.hwell;
  const c=_makeIconCanvas(),t=c.getContext('2d');
  // Echo residue: fading figure
  _hline(c,t,1,4,5,'rgba(100,140,200,0.3)');
  _hline(c,t,2,3,6,'rgba(100,140,200,0.3)');
  _hline(c,t,3,3,6,'rgba(80,120,180,0.2)');
  _hline(c,t,4,3,6,'rgba(80,120,180,0.15)');
  _px(c,t,4,6,'rgba(100,140,200,0.25)'); _px(c,t,5,6,'rgba(100,140,200,0.25)');
  _px(c,t,4,7,'rgba(80,120,180,0.15)'); _px(c,t,5,7,'rgba(80,120,180,0.15)');
  ICON_CACHE.hwell=_iconToURL(c);return ICON_CACHE.hwell;
}

function iconHelpPredW() {
  if(ICON_CACHE.hpredw) return ICON_CACHE.hpredw;
  const c=_makeIconCanvas(),t=c.getContext('2d');
  // Patrol drone
  _hline(c,t,3,3,7,'#889999'); _hline(c,t,4,4,6,'#778888');
  _rect(c,t,3,5,7,7,'#889999');
  _px(c,t,5,2,'#aabbbb'); _px(c,t,5,1,'#cccccc');
  _px(c,t,4,8,'#ff6644'); _px(c,t,6,8,'#ff6644');
  _px(c,t,5,6,'#44aacc');
  ICON_CACHE.hpredw=_iconToURL(c);return ICON_CACHE.hpredw;
}

function iconHelpPredH() {
  if(ICON_CACHE.hpredh) return ICON_CACHE.hpredh;
  const c=_makeIconCanvas(),t=c.getContext('2d');
  // Hunting drone (red)
  _hline(c,t,3,3,7,'#994444'); _hline(c,t,4,4,6,'#883333');
  _rect(c,t,3,5,7,7,'#994444');
  _px(c,t,5,2,'#ff4444'); _px(c,t,5,1,'#ff6666');
  _px(c,t,4,8,'#ff0000'); _px(c,t,6,8,'#ff0000');
  _px(c,t,5,6,'#ff0000');
  ICON_CACHE.hpredh=_iconToURL(c);return ICON_CACHE.hpredh;
}

function iconHelpPredS() {
  if(ICON_CACHE.hpreds) return ICON_CACHE.hpreds;
  const c=_makeIconCanvas(),t=c.getContext('2d');
  // Stunned drone (yellow)
  _hline(c,t,3,3,7,'#887744'); _hline(c,t,4,4,6,'#776633');
  _rect(c,t,3,5,7,7,'#887744');
  _px(c,t,5,2,'#997755'); _px(c,t,6,1,'#997755');
  _px(c,t,4,5,'#ffcc00'); _px(c,t,6,5,'#ffcc00');
  ICON_CACHE.hpreds=_iconToURL(c);return ICON_CACHE.hpreds;
}

function iconHelpGas() {
  if(ICON_CACHE.hgas) return ICON_CACHE.hgas;
  const c=_makeIconCanvas(),t=c.getContext('2d');
  // Gas cloud (scattered particles)
  for(let i=0;i<10;i++) {
    const x=3+Math.floor(Math.random()*6), y=3+Math.floor(Math.random()*6);
    _px(c,t,x,y,'rgba(150,200,100,0.5)');
  }
  _px(c,t,5,5,'rgba(180,220,120,0.7)');
  ICON_CACHE.hgas=_iconToURL(c);return ICON_CACHE.hgas;
}

function iconHelpXtal() {
  if(ICON_CACHE.hxtal) return ICON_CACHE.hxtal;
  const c=_makeIconCanvas(),t=c.getContext('2d');
  // Crystal cluster
  _px(c,t,5,2,'#dd88ff'); _px(c,t,4,3,'#dd88ff'); _px(c,t,6,3,'#dd88ff');
  _px(c,t,3,4,'#cc66ee'); _px(c,t,5,4,'#fff'); _px(c,t,7,4,'#cc66ee');
  _px(c,t,4,5,'#cc66ee'); _px(c,t,6,5,'#cc66ee');
  _px(c,t,4,6,'#bb55dd'); _px(c,t,6,6,'#bb55dd');
  _px(c,t,5,7,'#aa44cc');
  ICON_CACHE.hxtal=_iconToURL(c);return ICON_CACHE.hxtal;
}

function iconHelpWater() {
  if(ICON_CACHE.hwater) return ICON_CACHE.hwater;
  const c=_makeIconCanvas(),t=c.getContext('2d');
  // Dark water pool
  _rect(c,t,2,4,8,7,'rgba(30,60,100,0.6)');
  _px(c,t,3,5,'rgba(50,100,180,0.4)'); _px(c,t,6,5,'rgba(50,100,180,0.4)');
  _px(c,t,4,6,'rgba(40,80,160,0.3)'); _px(c,t,7,6,'rgba(40,80,160,0.3)');
  // Ripple
  _px(c,t,5,5,'rgba(100,160,220,0.5)');
  ICON_CACHE.hwater=_iconToURL(c);return ICON_CACHE.hwater;
}

function iconHelpEchoWall() {
  if(ICON_CACHE.hechow) return ICON_CACHE.hechow;
  const c=_makeIconCanvas(),t=c.getContext('2d');
  // Echo wall: reflective panel
  _rect(c,t,2,1,8,9,'#4a5060');
  _hline(c,t,1,3,7,'#667788'); _hline(c,t,9,3,7,'#3a4050');
  // Reflection waves
  _px(c,t,9,4,'#889999'); _px(c,t,10,5,'#aabbbb');
  _px(c,t,10,3,'#aabbbb');
  // Glossy highlight
  _px(c,t,3,2,'#7a8090'); _px(c,t,5,2,'#7a8090');
  ICON_CACHE.hechow=_iconToURL(c);return ICON_CACHE.hechow;
}

/* ═══════════════════════════════════════════════════════════════════════
   INIT & CHARACTER ICON MAPPING
   ═══════════════════════════════════════════════════════════════════════ */

function initPanelIcons() {
  const icons = {
    iconEnergy: iconEnergy, iconStats: iconStats, iconCombo: iconCombo,
    iconAug: iconAug, iconItems: iconItems, iconMsg: iconMsg,
    iconQuest: iconQuest, iconRoom: iconRoom, iconMods: iconModsIcon,
    iconBoss: iconBoss, iconRating: iconRatingIcon,
    iconWalkerHdr: iconWalkerHelmet,
  };
  for (const [id, fn] of Object.entries(icons)) {
    const el = document.getElementById(id);
    if (el) el.src = fn();
  }
  const ci = document.getElementById('charIconImg');
  if (ci) ci.src = iconProphet();

  const nh = document.getElementById('navHelpIcon');
  if (nh) nh.src = iconHelp();
  const nl = document.getElementById('navLangIcon');
  if (nl) nl.src = iconLang();

  const sd = document.getElementById('splashDiffIcon');
  if (sd) sd.src = iconDifficulty();
  const sm = document.getElementById('splashMapIcon');
  if (sm) sm.src = iconMapSize();
  const st = document.getElementById('splashThemeIcon');
  if (st) st.src = iconTheme();
  const sw = document.getElementById('splashWalkerIcon');
  if (sw) sw.src = iconWalkerHelmet();
  const smd = document.getElementById('splashModIcon');
  if (smd) smd.src = iconModsIcon();

  const sb = document.getElementById('splashStartIcon');
  if (sb) sb.src = iconStart();
  const lo = document.getElementById('navLogoIcon');
  if (lo) lo.src = iconLogo();
  const bl = document.getElementById('botLogIcon');
  if (bl) bl.src = iconMsg();
}

function initNavIcons() {
  const lo = document.getElementById('navLogoIcon');
  if (lo) lo.src = iconLogo();
  const nh = document.getElementById('navHelpIcon');
  if (nh) nh.src = iconHelp();
  const nl = document.getElementById('navLangIcon');
  if (nl) nl.src = iconLang();
  const sd = document.getElementById('splashDiffIcon');
  if (sd) sd.src = iconDifficulty();
  const sm = document.getElementById('splashMapIcon');
  if (sm) sm.src = iconMapSize();
  const st = document.getElementById('splashThemeIcon');
  if (st) st.src = iconTheme();
  const sw = document.getElementById('splashWalkerIcon');
  if (sw) sw.src = iconWalkerHelmet();
  const smd = document.getElementById('splashModIcon');
  if (smd) smd.src = iconModsIcon();
  const sb = document.getElementById('splashStartIcon');
  if (sb) sb.src = iconStart();
}

const CHAR_ICONS = {
  prophet: iconProphet, ghost: iconGhost, behemoth: iconBehemoth,
  singer: iconSinger, shadow: iconShadow, resonator: iconResonator,
};

function getCharIconURL(id) {
  const fn = CHAR_ICONS[id];
  return fn ? fn() : iconProphet();
}
