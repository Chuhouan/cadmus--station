#!/usr/bin/env python3
"""
Echo Maze Web Server v5.0 — Flask + Socket.IO + Canvas Pixel Renderer
CADMUS STATION — Industrial facility theme, dual-pulse mechanics.
"""
import sys, os, threading, queue, time, traceback, json

os.environ['ECHO_MAZE_WEB'] = '1'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cadmus-station-v5'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading',
                    max_http_buffer_size=10**7, ping_timeout=120)

# ── Per-session state ──
sessions = {}
sessions_lock = threading.Lock()

# ── Fragment distribution: 6 people × 3 fragments, spread across 10 levels ──
FRAGMENT_DATA = {
    'lin_xianhe': {
        'name_zh': '林先和', 'name_en': 'Lin Xianhe',
        'title_zh': '首席声学工程师', 'title_en': 'Chief Acoustics Engineer',
        'fragments': {
            1: {'level': 1, 'text_zh': '核心频率在自行爬升。我手动降了三次。每次三十秒内回到原值。我问是不是有人在远程操作。中央控制室没有回复。我不确定是通讯断了，还是他们不想回复。',
                'text_en': 'Core frequency climbing on its own. I manually lowered it three times. Back to the original value within thirty seconds each time. I asked if someone was operating remotely. No response from central control. Not sure if comms are down, or they chose not to reply.'},
            2: {'level': 3, 'text_zh': '我翻了两天的日志。不是算法。不是故障。有人从内部终端远程登录了核心控制系统。物理来源在设施内部。还有人在这里。我没有告诉任何人我在查——这里有第七个人。',
                'text_en': 'I went through two days of logs. Not an algorithm. Not a malfunction. Someone logged into the core control system from an internal terminal. The physical source is inside the facility. Someone is still here. I haven\'t told anyone I\'m investigating — there\'s a seventh person.'},
            3: {'level': 6, 'text_zh': '账户名：WU_AN。如果你是我没能等到的第八个人——带上这个。他还在里面。',
                'text_en': 'Account name: WU_AN. If you are the eighth person I couldn\'t wait for — take this. He is still inside.'},
        }
    },
    'su_wuying': {
        'name_zh': '苏无影', 'name_en': 'Su Wuying',
        'title_zh': '安保队长', 'title_en': 'Security Chief',
        'fragments': {
            1: {'level': 2, 'text_zh': 'B区清空了。三个实习生没来得及跑到集合点。我回头去找——通道塌了。我把他们带到C-7走廊。氧气还有四小时。我要去找另一条路。',
                'text_en': 'Sector B cleared. Three interns didn\'t reach the rally point in time. I went back for them — the corridor collapsed. I brought them to C-7. Four hours of oxygen left. I\'m going to find another way.'},
            2: {'level': 7, 'text_zh': '我找到第七个人了。他说他是来检查实验进度的。我不认识他。他有武器。他杀了小陈——就在我面前。我把他锁在了E-3仓库。他跑不出来。但我也出不去了。',
                'text_en': 'I found the seventh person. He said he was here to check on experiment progress. I don\'t know him. He has a weapon. He killed Xiao Chen — right in front of me. I locked him in E-3 storage. He can\'t get out. But neither can I.'},
            3: {'level': 10, 'text_zh': '我叫苏无影。安保队长。如果没人来开门——告诉我的家人，我没跑。三个实习生跟我在一起。他们需要笔和纸。我不需要。',
                'text_en': 'My name is Su Wuying. Security chief. If no one comes to open this door — tell my family I didn\'t run. The three interns are with me. They need pen and paper. I don\'t.'},
        }
    },
    'zhao_tieshan': {
        'name_zh': '赵铁山', 'name_en': 'Zhao Tieshan',
        'title_zh': '矿工技术员', 'title_en': 'Miner Technician',
        'fragments': {
            1: {'level': 2, 'text_zh': '下面有风。能闻到外面的味道。出口肯定在下面。',
                'text_en': 'There\'s wind below. I can smell the outside. The exit has to be below.'},
            2: {'level': 4, 'text_zh': '爬了六层。还没有到底。箭头我留墙上了——跟我走。或者别跟。我不知道。',
                'text_en': 'Climbed down six levels. Still no bottom. I left arrows on the walls — follow me. Or don\'t. I don\'t know.'},
            3: {'level': 4, 'text_zh': '别往下走。下面是核心。没有出口。箭头上被别的人覆盖了标记——他改了我留的方向。如果你之前走过死路，那是我走的路。不是你的错。',
                'text_en': 'Don\'t go down. The core is below. No exit. Someone covered my arrows with new marks — he changed the direction I left. If you walked into dead ends before, that was my path. Not your fault.'},
        }
    },
    'chen_ge': {
        'name_zh': '陈歌', 'name_en': 'Chen Ge',
        'title_zh': '通讯技术员', 'title_en': 'Communications Tech',
        'fragments': {
            1: {'level': 3, 'text_zh': '我在沿途放中继器。每五十米一个。不用自己ping——用我的。这可能是唯一不暴露你位置的方法。我在C-12通道。',
                'text_en': 'I\'m placing repeaters along the route. One every fifty meters. Don\'t use your own ping — use mine. It might be the only way that doesn\'t expose your position. I\'m heading to corridor C-12.'},
            2: {'level': 5, 'text_zh': '通道里有东西。对声波敏感。我不能再用脉冲了。关外骨骼。模黑走。只剩下触觉。祝我好运。',
                'text_en': 'There\'s something in the tunnel. Sensitive to sound waves. I can\'t use pulse anymore. Shutting down the exoskeleton. Walking blind. Nothing left but touch. Wish me luck.'},
            3: {'level': 8, 'text_zh': '最后一个中继器。如果有人收到——卡德摩斯站不是测绘项目。是个武器。不要相信任何从地面下来的人。他们早就知道。',
                'text_en': 'Last repeater. If anyone receives this — Cadmus Station is not a mapping project. It\'s a weapon. Don\'t trust anyone who comes down from the surface. They\'ve known all along.'},
        }
    },
    'wu_an': {
        'name_zh': '吴暗', 'name_en': 'Wu An',
        'title_zh': '设施监理', 'title_en': 'Facility Supervisor',
        'fragments': {
            1: {'level': 5, 'text_zh': '保安日志。今日已完成：按指示锁死所有撤离通道。确认无人离开。授权人：吴暗。',
                'text_en': 'Security log. Completed today: All evacuation routes locked per instruction. No personnel exit confirmed. Authorized by: Wu An.'},
            2: {'level': 7, 'text_zh': '实验授权书。编号：RES-117。目的：声场测试——战场上制造不可见区域。附带人员上限：六人。准许项：满功率运行。地面指挥部批准。',
                'text_en': 'Experiment authorization. Ref: RES-117. Purpose: acoustic field test — generate invisible zones in battlefield conditions. Personnel cap: six. Approved: full power operation. Authorized by surface command.'},
            3: {'level': 9, 'text_zh': '我锁了门。我删了文件。我也困在这里了。我需要第七个人——安全模式要两个活人。你不是我等的第七个人。你是他们派来的。',
                'text_en': 'I locked the doors. I deleted the files. I\'m trapped here too. I need a seventh person — safe mode requires two living people. You are not the seventh person I was waiting for. They sent you.'},
        }
    },
    'zheng_zhen': {
        'name_zh': '郑振', 'name_en': 'Zheng Zhen',
        'title_zh': '地质学家', 'title_en': 'Geologist',
        'fragments': {
            1: {'level': 4, 'text_zh': '核心过载前岩层应力出现异常。声场在定向聚焦——不是维持声场泡。是在做测试。这不是事故的前兆。这是实验的正常过程。有人等到实验完成了，然后关掉了监控。',
                'text_en': 'Pre-overload rock stress showed anomalies. The acoustic field was directionally focused — not maintaining a field bubble. This was a test. This was not the prelude to an accident. This was the normal course of the experiment. Someone waited until the experiment was complete, then shut off the monitors.'},
            2: {'level': 8, 'text_zh': '功率阈值是被人手动上调的。操作者权限：设施总监。吴暗只是代理——他没有这个权限。决策者在地面上。',
                'text_en': 'The power threshold was manually raised. Operator clearance: Facility Director. Wu An is only acting — he doesn\'t have that authority. The decision maker is on the surface.'},
            3: {'level': 9, 'text_zh': '实验还需要六个月才能拿到完整数据。事故后地面上没有救援——不是通讯断了。他们不会来。他们在等六个月后的数据。不要等。走。',
                'text_en': 'The experiment needs six more months for complete data. No rescue came after the accident — it\'s not that comms are down. They are not coming. They\'re waiting for six months of data. Don\'t wait. Go.'},
        }
    },
}

# ── 10-level palette themes ──
LEVEL_PALETTES = [
    {'name': 'EMERGENCY', 'wall': '#442211', 'floor': '#1a0f0a', 'glow': '#ff4433', 'accent': '#cc3322'},
    {'name': 'RUIN',      'wall': '#3a2211', 'floor': '#1a100a', 'glow': '#ff6633', 'accent': '#cc6622'},
    {'name': 'DATA',      'wall': '#112244', 'floor': '#0a0f1a', 'glow': '#4488ff', 'accent': '#2266cc'},
    {'name': 'DEPTHS',    'wall': '#112222', 'floor': '#0a1111', 'glow': '#44aaaa', 'accent': '#226666'},
    {'name': 'SIGNAL',    'wall': '#221144', 'floor': '#0f0a1a', 'glow': '#8844dd', 'accent': '#6622aa'},
    {'name': 'SECURITY',  'wall': '#331111', 'floor': '#0d0606', 'glow': '#ff3344', 'accent': '#cc2233'},
    {'name': 'ARCHIVE',   'wall': '#333333', 'floor': '#1a1a1a', 'glow': '#cccccc', 'accent': '#aaaaaa'},
    {'name': 'CAVERN',    'wall': '#112244', 'floor': '#0a0f1a', 'glow': '#4488cc', 'accent': '#224488'},
    {'name': 'CORE',      'wall': '#112233', 'floor': '#081018', 'glow': '#66aaff', 'accent': '#4488cc'},
    {'name': 'CONTROL',   'wall': '#1a1a22', 'floor': '#0a0c12', 'glow': '#667788', 'accent': '#445566'},
]

TOTAL_LEVELS = 10
BOSS_LEVELS = {3, 6, 9}
BOSS_NAMES = {3: 'echo_mother', 6: 'silent_hunter', 9: 'void_avatar'}


class GameSession:
    def __init__(self, sid):
        self.sid = sid
        self.key_queue = queue.Queue()
        self.buffer = ""
        self.game = None
        self.running = True
        self.config = None
        self.state_timer = 0
        self.thread = None

    def write(self, text: str):
        pass

    def flush(self):
        pass

    def get_key(self) -> str:
        try:
            key = self.key_queue.get(timeout=0.03)
            if key == '\x1b[A': return 'up'
            elif key == '\x1b[B': return 'down'
            elif key == '\x1b[C': return 'right'
            elif key == '\x1b[D': return 'left'
            elif key in ('\r','\n'): return '\r'
            elif key in ('\x7f','\x08','\x1b'): return ''
            return key
        except queue.Empty:
            return ''

    def push_key(self, key: str):
        self.key_queue.put(key)

    def broadcast_state(self):
        """Extract game state and send to client as JSON."""
        g = self.game
        if not g: return
        try:
            import echo_maze as game_mod
            state = {
                'energy': g.energy, 'maxEnergy': g.max_energy,
                'pings': g.pings, 'steps': g.moves,
                'score': g.total_score, 'level': g.level,
                'combo': g.combo, 'maxCombo': g.max_combo,
                'rating': g.rating() if g.won else '--',
                'damageFlash': g.damage_flash,
                'screenInvert': g.screen_invert,
                'themeName': g.theme.name if hasattr(g.theme, 'name') else 'EMERGENCY',
                'levelPalette': LEVEL_PALETTES[min(g.level - 1, len(LEVEL_PALETTES) - 1)],
            }
            # Exoskeleton character
            if g.walker_class:
                state['charName'] = game_mod.exo_name(g.walker_class)
                state['walkerClass'] = g.walker_class.value
            # Abilities
            if g.abilities:
                state['abilities'] = [game_mod.ab_name(a) for a in g.abilities]
            # Collectibles
            if g.collected_items:
                state['collectedItems'] = {}
                for it, count in g.collected_items.items():
                    key = it.name if hasattr(it, 'name') else str(it)
                    state['collectedItems'][key] = count
            # Modifiers (only SILENT / HUNTED in v5.0)
            if g.active_modifiers:
                state['modifiers'] = [m.value[0] for m in g.active_modifiers]
                mult = 1.0 + sum(m.value[2] for m in g.active_modifiers)
                state['modMultiplier'] = mult
            # Boss with shields
            if g.boss and not g.boss_defeated:
                state['bossName'] = game_mod.t(f'boss_{g.boss.boss_type.value}')
                state['bossShields'] = g.boss.shields
                state['bossHP'] = g.boss.shields  # backward compat for renderer
                state['bossMaxShields'] = g.boss.max_shields
                state['bossDistance'] = game_mod._boss_distance(g)
            elif g.boss_defeated:
                state['bossName'] = None
            # Fragment progress
            if hasattr(g, 'fragments_collected'):
                state['fragmentsCollected'] = g.fragments_collected
                state['fragmentsTotal'] = 18
                state['fragmentsAllCollected'] = g.fragments_all_collected
            # Recent message (strip ANSI)
            if g.msgs:
                import re
                raw_msg, _ = g.msgs[-1]
                state['lastMessage'] = re.sub(r'\x1b\[[0-9;]*m', '', raw_msg)
            # Special room
            room = g.room_at(g.px, g.py)
            if room is not None:
                state['specialRoom'] = room
            # Quest status
            state['exitLocked'] = g.exit_locked
            state['questComplete'] = g.quest_complete
            # Map grid for pixel renderer
            state['mapGrid'] = game_mod.build_map_grid(g)
            # Charging indicator
            state['charging'] = getattr(g, 'charging_focus', False)
            # Level opening text (send on level start)
            if getattr(g, '_level_intro_sent', False) is False:
                state['levelIntro'] = get_level_intro(g.level)
                g._level_intro_sent = True
            # Briefing (send once at game start)
            if getattr(g, '_briefing_sent', False) is False and g.level == 1:
                state['briefing'] = get_briefing_text()
                g._briefing_sent = True
            # Focus pulse energy check
            state['canFocus'] = g.energy >= 3
            socketio.emit('state', state, room=self.sid)
        except Exception as e:
            import traceback
            print(f'[BROADCAST ERROR] {e}', flush=True)
            traceback.print_exc()


def get_briefing_text() -> dict:
    """Pre-game mission briefing — first person narrative."""
    import echo_maze as game
    zh_text = game.LANG == 'zh'
    return {
        'zh': (
            '三天前，卡德摩斯地下声场研究站的主共振核心过载。\n'
            '事故原因：不明。\n'
            '后果：核心周围三百米半径内，所有光学设备失效。\n'
            '不是黑暗——是没有光可以接收。\n\n'
            '六名工作人员在疏散过程中失联。\n'
            '林先和，首席声学工程师。苏无影，安保队长。\n'
            '赵铁山，矿工出身的技术员。陈歌，通讯技术员。\n'
            '吴暗，设施监理。郑振，地质学家。\n'
            '至今没有收到任何信号。\n\n'
            '你是应急工程师。在地面上等了三天。\n'
            '今天早上，地面指挥部调了你的档案——\n'
            '你是方圆五百公里内唯一一个能操作旧型号声纳导航外骨骼的人。\n'
            '那套外骨骼是你十年前参与设计的。不依赖光线。只靠超声波回声测绘。\n\n'
            '他们给了你三个小时准备。没有问你是否愿意。\n\n'
            '你的任务：\n'
            '关闭主共振核心。找到幸存者。活着爬出来。\n\n'
            '电池剩余：10。\n'
            '声纳系统正常。\n'
            '外骨骼启动。\n\n'
            '我告诉我自己是来找人的。\n'
            '我没说实话。'
        ),
        'en': (
            'Three days ago, the main resonance core at Cadmus Subsonics Station overloaded.\n'
            'Cause: unknown.\n'
            'Effect: all optical equipment within a 300-meter radius — dead.\n'
            'Not darkness. There is simply no light left to receive.\n\n'
            'Six personnel went missing during evacuation.\n'
            'Lin Xianhe, Chief Acoustics Engineer. Su Wuying, Security Chief.\n'
            'Zhao Tieshan, Miner Technician. Chen Ge, Communications Tech.\n'
            'Wu An, Facility Supervisor. Zheng Zhen, Geologist.\n'
            'No signals received. Not one.\n\n'
            'You are an emergency engineer. You waited on the surface for three days.\n'
            'This morning, surface command pulled your file —\n'
            'you are the only person within 500 kilometers who can operate the old-model sonar navigation exoskeleton.\n'
            'You helped design it ten years ago. No optics. Ultrasonic echo mapping only.\n\n'
            'They gave you three hours to prepare. No one asked if you wanted to go.\n\n'
            'Your mission:\n'
            'Shut down the core. Find survivors. Climb back out alive.\n\n'
            'Battery: 10.\n'
            'Sonar system nominal.\n'
            'Exoskeleton online.\n\n'
            'I told myself I was here to find people.\n'
            'I wasn\'t telling the truth.'
        ),
    }


def get_level_intro(level: int) -> dict:
    """Return level intro — first person internal monologue."""
    intros = {
        1: {'zh': '我发射了第一次脉冲。墙壁在屏幕上亮了三秒，然后慢慢暗下去。像有人举着火柴走过一个没有窗的房间。声纳显示前方三十米处的闸门锁死了——控制面板需要一块备用电池。我记得这个设计。十年前我们加这个锁，是为了防止有人在声场测试期间误入。现在它锁住了六个人退出来的路。',
            'en': 'I fired the first pulse. The walls lit up on my screen for three seconds, then slowly faded. Like someone walking through a windowless room holding a match. Sonar shows the gate thirty meters ahead is locked — the control panel needs a spare battery. I remember this design. We added this lock ten years ago to keep people out during field tests. Now it has locked six people inside.'},
        2: {'zh': '控制室烧过。墙壁焦黑。空气里有股焦糊味，外骨骼过滤不掉。地上有水——不知道是管道破裂还是灭火留下的。水里飘着纸片。我捡起一张——林先和的手写日志。墙角有个人形的声纳残像。赵铁山在这里停过。他的最后一帧扫描数据刻在墙上："下面有风。出口在下面。"下面不是出口，老赵。下面是核心。',
            'en': 'The control room burned. Walls charred black. Air smells like smoke — the exoskeleton can\'t filter it out. Water on the floor — burst pipe or fire suppression, I can\'t tell. Paper floating in it. I picked one up — Lin Xianhe\'s handwritten log. There\'s a human-shaped sonar residue in the corner. Zhao Tieshan stopped here. His last scan data is scratched into the wall: "Wind below. Exit is below." Below is not the exit, old Zhao. Below is the core.'},
        3: {'zh': '声场模拟器还开着。它应该已经停了三天了。但它在自主运行——不断发射干扰脉冲，覆盖我的扫描范围。每次我ping它，它ping回来。比我快。比我大。这不是故障。故障会自己停下来。这东西在回答。',
            'en': 'The acoustic simulator is still running. It should have shut down three days ago. But it\'s running autonomously — firing interference pulses, drowning out my scan. Every time I ping it, it pings back. Faster than me. Bigger than me. This is not a malfunction. Malfunctions stop on their own. This thing is answering.'},
        4: {'zh': '竖井很深。平台上全是暗水——不是水，是声波冷却液。踩上去黏稠，外骨骼的液压系统在抗议。好消息是暗水里没法脉冲，捕食器听不到我。坏消息是我什么也看不见。赵铁山的箭头刻在墙上。越来越歪。他在往下爬的时候已经慌了。',
            'en': 'The shaft is deep. Platforms submerged in dark water — not water, acoustic coolant. Sticky underfoot, the exoskeleton\'s hydraulics complaining. Good news: you can\'t pulse in dark water, so the drones can\'t hear me. Bad news: I can\'t see a thing. Zhao Tieshan\'s arrows are carved into the walls. Getting crooked. He was already panicking as he climbed down.'},
        5: {'zh': '陈歌沿途放了很多中继器。每一个都是一次全屏扫描——她把自己的能量留着，用中继器的电池代替。她比我聪明。踩到第一个中继器时，她的声音自动播放："这里是陈歌。我把中继器放在沿途了。如果你听到这个，我在C-12通道。"她的声音很稳。不害怕。或者她把害怕藏得很好。',
            'en': 'Chen Ge placed repeaters all along the path. Each one is a full-screen scan — she saved her own energy and used the repeaters\' batteries instead. Smarter than me. When I stepped on the first one, her voice played automatically: "This is Chen Ge. I placed repeaters along the way. If you hear this, I\'m in corridor C-12." Her voice is steady. Not scared. Or she\'s hiding it well.'},
        6: {'zh': '安保通道全是无人机。它们不巡逻——它们在警戒。有什么东西把它们激活了。墙壁上有一面完好的安保面板。储存器还在运行。我趁无人机转身时靠近，外骨骼读出了一行指令："锁定所有撤离通道。阻止任何人员离开。授权人：吴暗。"锁定时间是事故前四小时。他提前四个小时就知道。',
            'en': 'The security corridor is crawling with drones. They\'re not patrolling — they\'re on alert. Something activated them. There\'s an intact security panel on the wall. The storage is still running. I got close while a drone turned away — the exoskeleton read one line: "Lock all evacuation routes. Prevent all personnel from leaving. Authorized by: Wu An." Lock time: four hours before the accident. He knew four hours in advance.'},
        7: {'zh': '档案室被涂了一层吸声材料。弹了一发脉冲——声波被吞得一干二净。这种涂层是实验品。他们把原型涂在了档案室，让它变成整个设施里最安静的地方。一个理想的——删除证据的地方。墙会吞噬所有声音。我只能靠撞墙来感知方向。房间中央有个东西在睡觉。比普通捕食器大三倍。它听到步数会醒。',
            'en': 'The archive is coated in sound-absorbing material. I fired a pulse — swallowed completely. This coating is experimental. They painted the prototype in the archive and made it the quietest place in the facility. An ideal place — to delete evidence. The walls eat all sound. I can only navigate by bumping into them. Something is sleeping in the center of the room. Three times bigger than a normal drone. It wakes up when it hears footsteps.'},
        8: {'zh': '到了最底层。天然岩洞，被改造成核心降温室。这里有水晶簇——天然的巨大晶体。声波碰到它们会折射，往四个方向散开。郑振的移动实验室在一个小舱室里。她的数据终端还插着电源——屏幕亮着。她的最后一封未发送邮件。"功率阈值是被人手动上调的。吴暗没有这个权限。地面上的人。"',
            'en': 'The deepest level. A natural cavern, converted into a core cooling chamber. Giant crystal clusters everywhere — natural formations. Sound waves refract when they hit them, scattering in four directions. Zheng Zhen\'s mobile lab is in a small pod. Her data terminal is still connected to power — the screen is on. Her last unsent message: "The power threshold was manually raised. Wu An doesn\'t have that clearance. The surface did this."'},
        9: {'zh': '核心就在前面。十二米直径的环形发生器，在黑暗里缓慢旋转。每次旋转地面就震一下——不是声音，是纯粹的振动，透过外骨骼的液压系统传到我的骨头里。房间里有个人形的东西。不是真人——是核心的声场投影。它在模仿六个人的外形。林先和的轮廓。苏无影的。然后模糊，变成另一个人。三个频率锚点。只有站在锚点上发射的聚焦脉冲才能穿透。',
            'en': 'The core is right there. Twelve meters across, a ring-shaped generator rotating slowly in the dark. The ground trembles with every rotation — not sound, pure vibration, traveling through the exoskeleton\'s hydraulics into my bones. There\'s a human-shaped thing in the room. Not a real person — a projection of the core\'s acoustic field. It imitates the six. Lin Xianhe\'s silhouette. Su Wuying\'s. Then it blurs, becoming someone else. Three frequency anchors. Only a focus pulse fired from an anchor point can penetrate.'},
        10: {'zh': '吴暗就站在刹车拉杆旁边。他的外骨骼比我旧两个型号，左腿的液压管在漏。他的脸在声纳扫描里只是一个轮廓——没有特征，没有表情。"你也走到这里了。两个人。帮我解锁。我关闭核心。我们一起出去。"他说"我的人会保证你没事"。他说的不是"地面"。不是"项目方"。是"我的人"。他早就选好了边。',
            'en': 'Wu An is standing right next to the brake lever. His exoskeleton is two models older than mine — the left leg\'s hydraulic line is leaking. His face is just an outline on my sonar — no features, no expression. "You made it here too. Two people. Help me unlock it. I\'ll shut down the core. We leave together." He says "my people will make sure you\'re taken care of." Not "the surface." Not "the project." "My people." He picked a side a long time ago.'},
    }
    return intros.get(level, {'zh': '', 'en': ''})


def get_act_break_text(act: int) -> dict:
    """Act break narrative — player's internal realization after boss levels."""
    breaks = {
        1: {'zh': '我叫______。三个小时前我以为我是来找人的。\n现在我明白了。我在找一个人——不是六个失踪者，是一个不在名单上的人。\n林先和发现了他的账户名。林先和现在在哪？',
            'en': 'My name is ______. Three hours ago I thought I was here to find people.\nNow I understand. I\'m looking for one person — not the six who are missing. Someone not on the list.\nLin Xianhe found his account name. Where is Lin Xianhe now?'},
        2: {'zh': '吴暗。设施监理。锁了门。删了文件。用了六个人的命做实验参数。\n但我刚才想起来——吴暗的权限级别是代理总监。他不是决策者。\n三天前地面上没有来救援。他们知道。他们签了字。\n我不是来救人的。我是来给吴暗当助手的。',
            'en': 'Wu An. Facility supervisor. Locked the doors. Deleted the files. Used six lives as experiment parameters.\nBut I just remembered — Wu An\'s clearance is Acting Director. He isn\'t the decision maker.\nThree days ago, no rescue came from the surface. They knew. They signed.\nI am not here to save anyone. I am here to be Wu An\'s assistant.'},
        3: {'zh': '我叫______。三个小时前我以为我是来找人的。\n现在我站在核心面前。六个人留下了碎片。吴暗留下了锁。地面的人留下了签名。\n如果我能出去——每一条证据都能用。\n但我不确定我想出去。',
            'en': 'My name is ______. Three hours ago I thought I was here to find people.\nNow I\'m standing in front of the core. Six people left fragments. Wu An left locks. The surface left signatures.\nIf I make it out — every piece of evidence can be used.\nBut I\'m not sure I want to leave.'},
    }
    return breaks.get(act, {'zh': '', 'en': ''})


def get_fragment_data(person_id: str, frag_num: int) -> dict:
    """Get a single fragment's data."""
    person = FRAGMENT_DATA.get(person_id, {})
    return person.get('fragments', {}).get(frag_num, {})


def get_all_fragments_for_level(level: int) -> list:
    """Get all fragments that appear on a given level."""
    result = []
    for person_id, person_data in FRAGMENT_DATA.items():
        for frag_num, frag_data in person_data['fragments'].items():
            if frag_data['level'] == level:
                result.append({
                    'person_id': person_id,
                    'frag_num': frag_num,
                    'name_zh': person_data['name_zh'],
                    'name_en': person_data['name_en'],
                    'text_zh': frag_data['text_zh'],
                    'text_en': frag_data['text_en'],
                })
    return result


def run_game_thread(sid: str, session: GameSession):
    """Run the game in a background thread."""
    try:
        import echo_maze as game

        sys.stdout = session
        game.get_key = session.get_key

        original_init = game.Game.__init__
        def patched_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            session.game = self
            self._level_intro_sent = False
        game.Game.__init__ = patched_init

        if session.config:
            _run_configured_game(game, session)
        else:
            game.main()

    except SystemExit: pass
    except Exception:
        traceback.print_exc()
    finally:
        session.flush()
        with sessions_lock:
            sessions.pop(sid, None)


def _run_configured_game(game, session: GameSession):
    """Run the game with pre-configured settings."""
    cfg = session.config
    diff = cfg.get('difficulty', 2)
    theme_idx = cfg.get('themeIdx', 0)
    map_scale = cfg.get('mapScale', 1)
    modifiers_raw = cfg.get('modifiers', [])
    walker_raw = cfg.get('walkerClass', None)

    modifiers = set()
    mod_map = {m.value[0]: m for m in game.ChallengeModifier}
    for mn in modifiers_raw:
        if mn in mod_map:
            modifiers.add(mod_map[mn])

    walker = None
    wc_map = {wc.value: wc for wc in game.WalkerClass}
    if walker_raw in wc_map:
        walker = wc_map[walker_raw]

    cfg_bonus = {1: 5, 2: 3, 3: 1}.get(diff, 3)
    lvl = 1; total_score = 0
    abilities = set(); prev_path = []

    cfg_debug = cfg.get('debug', False)
    debug_god = cfg.get('godMode', False)
    debug_level = cfg.get('startLevel', 1)

    lvl = debug_level if debug_level > 1 else 1

    g, _ = game.make_level(lvl, 0, theme_idx, abilities, prev_path, map_scale,
                           active_modifiers=modifiers, total_clears=0,
                           walker_class=walker)
    g.max_energy += cfg_bonus; g.energy = g.max_energy

    if debug_god:
        for wy in range(g.h):
            for wx in range(g.w):
                if g.maze[wy][wx] == game.Cell.WALL:
                    g.visible[(wx, wy)] = 20
        g.energy = 999; g.max_energy = 999

    session.game = g
    session.debug_god = debug_god

    last_tick = time.time()
    TICK = 1.0 / 10; acc = 0.0; first_frame = True  # 10 FPS for Render stability

    while session.running:
        now = time.time(); dt = now - last_tick; last_tick = now; acc += dt
        k = session.get_key()

        if k == 'q':
            break
        if k == 'l':
            game.LANG = 'en' if game.LANG == 'zh' else 'zh'
        if k == 'r' and g.won:
            lvl += 1; prev_path = list(g.path_this_run)
            if lvl > TOTAL_LEVELS:
                break  # Game complete
            # Auto-switch palette per level
            level_palette_idx = min(lvl - 1, len(LEVEL_PALETTES) - 1)
            theme_idx = level_palette_idx
            g, _ = game.make_level(lvl, g.total_score, theme_idx, abilities, prev_path, map_scale,
                                   active_modifiers=modifiers, walker_class=walker)
            g.max_energy += cfg_bonus; g.energy = g.max_energy
            g._level_intro_sent = False
            session.game = g
            first_frame = True

        # Debug hotkeys
        if cfg_debug:
            if k == 'g':
                session.debug_god = not session.debug_god
                if session.debug_god:
                    for wy in range(g.h):
                        for wx in range(g.w):
                            if g.maze[wy][wx] == game.Cell.WALL:
                                g.visible[(wx, wy)] = 20
                    g.energy = 999; g.max_energy = 999
                    g.msg('*** GOD MODE ON ***')
                else:
                    g.msg('*** GOD MODE OFF ***')
            elif k in tuple('1234567890'):
                target_lvl = int(k) if k != '0' else 10
                if target_lvl >= 1 and target_lvl <= 10:
                    lvl = target_lvl
                    abilities = set(); prev_path = list(g.path_this_run)
                    level_palette_idx = min(lvl - 1, len(LEVEL_PALETTES) - 1)
                    g, _ = game.make_level(lvl, g.total_score, level_palette_idx, abilities, prev_path, map_scale,
                                           active_modifiers=modifiers, total_clears=0, walker_class=walker)
                    g.max_energy += cfg_bonus; g.energy = g.max_energy
                    g._level_intro_sent = False
                    if session.debug_god:
                        for wy in range(g.h):
                            for wx in range(g.w):
                                if g.maze[wy][wx] == game.Cell.WALL:
                                    g.visible[(wx, wy)] = 20
                        g.energy = 999; g.max_energy = 999
                    session.game = g
                    g.msg(f'*** WARPED TO LEVEL {target_lvl} ***')
                    first_frame = True; continue

        # Level advancement when won
        if g.won and k in (' ', '\r', '\n'):
            lvl += 1; prev_path = list(g.path_this_run)
            if lvl > TOTAL_LEVELS:
                # Final ending — send gameover with special level 10 flag
                session._win_sent = True
                socketio.emit('gameover', {
                    'won': True, 'score': g.score, 'rating': g.rating(),
                    'maxCombo': g.max_combo, 'level': 10, 'isFinal': True,
                    'fragmentsAll': g.fragments_all_collected,
                }, room=session.sid)
                continue
            level_palette_idx = min(lvl - 1, len(LEVEL_PALETTES) - 1)
            g, _ = game.make_level(lvl, g.total_score, level_palette_idx, abilities, prev_path, map_scale,
                                   active_modifiers=modifiers, walker_class=walker)
            g.max_energy += cfg_bonus; g.energy = g.max_energy
            g._level_intro_sent = False
            session.game = g
            first_frame = True
            continue

        if not g.won and not g.is_dead:
            try:
                mm = {'w': (0, -1), 's': (0, 1), 'a': (-1, 0), 'd': (1, 0),
                      'up': (0, -1), 'down': (0, 1), 'left': (-1, 0), 'right': (1, 0)}
                if k in mm: g.move(*mm[k])
                # Dual pulse: action is now 'scan' or 'focus' from client
                if k == ' ': g.emit_ping()  # Legacy support
                if k == 'scan': g.scan_pulse()
                if k == 'focus': g.focus_pulse()

                ticks = min(int(acc / TICK), 4)
                for _ in range(ticks): g.tick()
                acc -= ticks * TICK
            except Exception as e:
                import traceback
                print(f'[GAME LOOP ERROR] lvl{g.level if g else "?"}: {e}', flush=True)
                traceback.print_exc()
        else:
            acc = 0
            if g.is_dead and not getattr(session, '_death_sent', False):
                session._death_sent = True
                socketio.emit('gameover', {'won': False, 'pings': g.pings, 'steps': g.moves, 'score': g.total_score}, room=session.sid)
            if g.won and not getattr(session, '_win_sent', False):
                session._win_sent = True
                is_final = g.level >= TOTAL_LEVELS
                evt = {
                    'won': True, 'score': g.score, 'rating': g.rating(),
                    'maxCombo': g.max_combo, 'level': g.level,
                    'isFinal': is_final,
                    'fragmentsAll': getattr(g, 'fragments_all_collected', False),
                }
                # Act break narrative after boss levels
                act_map = {3: 1, 6: 2, 9: 3}
                if g.level in act_map:
                    evt['actBreak'] = get_act_break_text(act_map[g.level])
                socketio.emit('gameover', evt, room=session.sid)

        session.broadcast_state()
        is_render = os.environ.get('RENDER', '') == 'true'
        time.sleep(0.06 if is_render else 0.04)


# ═══════════════════════════════════════════════════════════════════════
# FLASK ROUTES
# ═══════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/static/<path:filename>')
def static_files(filename):
    from flask import send_from_directory
    return send_from_directory('static', filename)


# ═══════════════════════════════════════════════════════════════════════
# SOCKET.IO EVENTS
# ═══════════════════════════════════════════════════════════════════════

@socketio.on('connect')
def handle_connect():
    sid = request.sid
    session = GameSession(sid)
    with sessions_lock:
        sessions[sid] = session
    emit('status', {'msg': 'CADMUS STATION v0.001 — CONNECTED'})


@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    with sessions_lock:
        session = sessions.pop(sid, None)
    if session:
        session.running = False
        session.push_key('q')


@socketio.on('key')
def handle_key(data):
    sid = request.sid
    with sessions_lock:
        session = sessions.get(sid)
    if session:
        session.push_key(data.get('key', ''))


@socketio.on('pulse')
def handle_pulse(data):
    """Handle dual-pulse action from client."""
    sid = request.sid
    with sessions_lock:
        session = sessions.get(sid)
    if session:
        action = data.get('action', 'scan')
        session.push_key(action)  # 'scan' or 'focus'


@socketio.on('start')
def handle_start(data):
    sid = request.sid
    with sessions_lock:
        session = sessions.get(sid)
    if not session: return
    session.config = data or {}
    session.debug_mode = data.get('debug', False) if data else False
    t = threading.Thread(target=run_game_thread, args=(sid, session), daemon=True)
    session.thread = t
    t.start()


@socketio.on('start_daily')
def handle_start_daily(data):
    sid = request.sid
    with sessions_lock:
        session = sessions.get(sid)
    if not session: return
    import echo_maze as game
    seed = game.daily_seed()
    import random; random.seed(seed)
    session.config = {
        'difficulty': 2, 'mapScale': 1,
        'themeIdx': seed % len(game.THEMES),
        'modifiers': [], 'walkerClass': None,
    }
    t = threading.Thread(target=run_game_thread, args=(sid, session), daemon=True)
    session.thread = t
    t.start()


@socketio.on('get_characters')
def handle_get_characters():
    import echo_maze as game
    unlocks = game.load_unlocks()
    # v5.0 unlock conditions
    unlock_hints = {
        'prophet': ('第3关击败Boss解锁' if game.LANG == 'zh' else 'Defeat boss at level 3'),
        'ghost': ('第7关完成后解锁' if game.LANG == 'zh' else 'Complete level 7'),
        'behemoth': ('第4关找到赵铁山的尸体解锁' if game.LANG == 'zh' else 'Find Zhao Tieshan\'s body at level 4'),
        'singer': ('第5关完成后解锁' if game.LANG == 'zh' else 'Complete level 5'),
        'shadow': ('结局A后解锁' if game.LANG == 'zh' else 'Unlocked after Ending A'),
        'resonator': ('结局B后解锁' if game.LANG == 'zh' else 'Unlocked after Ending B'),
    }
    chars = []
    for wc in game.WalkerClass:
        unlocked = game.is_char_unlocked(wc, unlocks)
        chars.append({
            'id': wc.value,
            'name': game.exo_name(wc),
            'desc': game.exo_desc(wc),
            'locked': not unlocked,
            'unlockHint': unlock_hints.get(wc.value, ''),
        })
    emit('characters', {'chars': chars})


@socketio.on('get_fragments')
def handle_get_fragments():
    """Return all fragment data for the fragment panel."""
    result = {}
    for person_id, person_data in FRAGMENT_DATA.items():
        result[person_id] = {
            'name_zh': person_data['name_zh'],
            'name_en': person_data['name_en'],
            'title_zh': person_data['title_zh'],
            'title_en': person_data['title_en'],
            'fragments': person_data['fragments'],
        }
    emit('fragments', result)


@socketio.on('get_leaderboard')
def handle_get_leaderboard():
    import echo_maze as game
    lb = game.load_leaderboard()
    emit('leaderboard', {
        'entries': lb[:10],
        'dailySeed': str(game.daily_seed()),
    })


@socketio.on('ending_choice')
def handle_ending_choice(data):
    """Handle player's ending choice at level 10."""
    sid = request.sid
    with sessions_lock:
        session = sessions.get(sid)
    if not session or not session.game: return
    choice = data.get('choice', 'A')
    # Unlock characters based on ending
    import echo_maze as game
    unlocks = game.load_unlocks()
    if choice == 'A':
        game.unlock_char(game.WalkerClass.SHADOW, unlocks)
    elif choice == 'B':
        game.unlock_char(game.WalkerClass.RESONATOR, unlocks)
    elif choice == 'C':
        game.unlock_char(game.WalkerClass.SINGER, unlocks)
    # Send ending text
    endings = get_ending_texts()
    emit('ending', {'choice': choice, 'text': endings.get(choice, {})}, room=sid)


def get_ending_texts():
    import echo_maze as game
    zh = game.LANG == 'zh'
    return {
        'A': {
            'title': '结局A：配合吴暗' if zh else 'Ending A: Cooperate',
            'text': '你抓住了拉杆。\n他犹豫了一秒，然后抓住了另一边。\n核心开始减速。低沉的嗡鸣，漫长。\n"你出去后什么都不会说。"他说。\n"对。"你说。"我什么都不会说。"\n\n你们往上爬。暗水。档案室。安保区。竖井。控制室废墟。应急通道。\n每一步他都在你前面半格。你没扶他。\n\n出口。天是亮的。\n媒体的闪光灯你提前看到了——声纳在四百米外就捕捉到了反射。\n他们安排好了。\n\n吴暗转身看你。他的脸在光线里了——四十多岁，颧骨高，左眼旁边有道没愈合的划伤。\n他的嘴张开了，想说什么。\n你从他身边走过去。\n\n你不会忘记。但你选好了——沉默，比说话重。\n\n报告是这么写的：不可预见的核心谐振事故。\n六个人被追授勋章。家属拿到了赔偿金。实验被正式中止。\n\n你偶尔回到那个入口。站在消光场的边界上。\n里面没有声音。但他还活着。他在等。\n也许有一天第八个人会听到他的脉冲。\n也许不会。'
                if zh else 'You grabbed the lever.\nHe hesitated one second, then grabbed the other side.\nThe core began to slow. A low hum, drawn out.\n"You won\'t say anything once you\'re out." He said.\n"Right." You said. "I won\'t say anything."\n\nYou climbed up. Dark water. Archive. Security zone. Shaft. Control room ruins. Emergency passage.\nHe stayed half a step ahead of you the whole way. You didn\'t help him.\n\nExit. The sky was bright.\nYou saw the media flashbulbs coming — sonar caught the reflections from 400 meters away.\nThey had arranged this.\n\nWu An turned to look at you. His face in the light now — mid-forties, high cheekbones, a fresh scratch next to his left eye.\nHis mouth opened to say something.\nYou walked past him.\n\nYou won\'t forget. But you made your choice — silence weighs more than words.\n\nThe report said: Unforeseen core resonance incident.\nSix people posthumously awarded medals. Families received compensation. The experiment was officially terminated.\n\nSometimes you return to that entrance. Standing at the edge of the null field.\nNo sound from inside. But he\'s alive. He\'s waiting.\nMaybe one day an eighth person will hear his pulse.\nMaybe not.',
            'unlock': '暗影' if zh else 'SHADOW',
        },
        'B': {
            'title': '结局B：揭露真相' if zh else 'Ending B: Expose',
            'text': '你没有动拉杆。\n吴暗等了五秒。"你在等什么？"\n"等你算错。"\n\n你转身就走。他喊了一声你的名字。不像命令。像在求。\n铁门在他和你之间落下了。\n\n控制室外面。十五秒。\n十秒把郑振的数据、林先和的日志、苏无影的录音打包发送。\n你的外骨骼广播模块能到地面。只要有人在听。\n最后五秒。你的手掌按在识别面板上。核心停止。\n\n往上爬的路很长。你走得很慢。\n每到一个地方，你都在那个人停留过的地方站一会儿。\n林先和控制室。苏无影的塌方通道。赵铁山的最后一面墙。\n陈歌的最后一个中继器。郑振的实验室。\n\n六个人。你在心里数——不是名单。是六种方式，你可以选择不坚持。\n但你没有。\n\n出口。天是暗的。早上四点。\n你坐在应急通道入口的台阶上，等日出。\n外骨骼的电池还剩三格。\n\n调查持续了两年。承包商破产。负责人被起诉。\n六个人的家属拿到了赔偿金。\n吴暗被判了——你的录音和碎片全部作为证据提交。\n\n你偶尔回到入口。你知道他还活着。他在等。\n但你不会再下去了。'
                if zh else 'You didn\'t move to the lever.\nWu An waited five seconds. "What are you waiting for?"\n"For your math to be wrong."\n\nYou turned and walked away. He shouted your name. Not a command. Like begging.\nThe iron door came down between you.\n\nOutside the control room. Fifteen seconds.\nTen to pack Zheng Zhen\'s data, Lin Xianhe\'s logs, Su Wuying\'s recording — broadcast to the surface. If anyone is listening.\nLast five seconds. Your palm on the recognition panel. The core stopped.\n\nThe climb up was long. You walked slowly.\nAt every place, you stopped where that person had stopped.\nLin Xianhe\'s control room. Su Wuying\'s collapsed corridor. Zhao Tieshan\'s last wall.\nChen Ge\'s last repeater. Zheng Zhen\'s lab.\n\nSix people. You counted in your head — not a roster. Six ways you could have chosen not to keep going.\nBut you didn\'t.\n\nExit. The sky was dark. Four in the morning.\nYou sat on the steps of the emergency entrance, waiting for sunrise.\nThree bars of battery left in the exoskeleton.\n\nThe investigation lasted two years. The contractor went bankrupt. The person in charge was prosecuted.\nThe six families received compensation.\nWu An was convicted — your recordings and fragments submitted as evidence.\n\nSometimes you return to the entrance. You know he\'s alive. He\'s waiting.\nBut you\'re not going back down.',
            'unlock': '共振者' if zh else 'RESONATOR',
        },
        'C': {
            'title': '结局C：炸毁设施' if zh else 'Ending C: Destroy',
            'text': '你站着没动。吴暗盯着你。\n"你不信任我？"\n"我在想郑振的数据。核心地基不稳定。主共振满功率运行会让岩层微观断裂。\n现在过了三天——应该快到临界了。"\n\n他愣住了。\n\n"赵铁山是矿工。他下来的时候带着矿用炸药。\n我在维护竖井里找到了。我没动它。"\n\n"你要干什么？"\n"我要让这个设施不存在。"\n\n你没有等他回答。往回走——不是出口。是竖井。\n赵铁山的炸药就在他尸体的手边。他没用——他不是放弃的人。\n他只是不知道往哪炸。你知道。\n\n十分钟。往上爬。每一步都在数——够不够。\n第九分钟的时候你还在管道里。最后三十秒——你看到了光。\n应急通道入口在二十米前。\n\n爆炸时你在地面十五米处。冲击波把你抛到草地上。\n你仰面朝天。看着黑色的烟从竖井上升起。\n核心沉默。设施坍塌。\n\n六个人的名字出现在你的外骨骼屏幕上。\n一个一个亮起。然后一个一个熄灭。\n\n三年后，地质探测队在废墟中记录到一个新的脉冲信号。\n它不像人。它像在学习。\n科学家说那只是地下的空洞回声。\n你知道不是。\n但你不会再下去了。'
                if zh else 'You stood still. Wu An stared at you.\n"You don\'t trust me?"\n"I\'m thinking about Zheng Zhen\'s data. The core foundation is unstable. Full-power resonance causes micro-fractures in the rock. It\'s been three days now — it should be close to critical."\n\nHe froze.\n\n"Zhao Tieshan was a miner. He came down with mining explosives. I found them in the maintenance shaft. I didn\'t touch them."\n\n"What are you going to do?"\n"I\'m going to make this facility not exist."\n\nYou didn\'t wait for an answer. You turned around — not toward the exit. Toward the shaft.\nZhao Tieshan\'s explosives were right next to his body. He didn\'t use them — he wasn\'t someone who gave up. He just didn\'t know where to blow. You know.\n\nTen minutes. Climbing up. Counting every step — is it enough.\nNinth minute, still in the pipe. Last thirty seconds — you saw light. The emergency entrance was twenty meters ahead.\n\nYou were fifteen meters above ground when it exploded. The shockwave threw you onto the grass.\nYou lay on your back, watching black smoke rise from the shaft opening.\nThe core fell silent. The facility collapsed.\n\nThe six names appeared on your exoskeleton screen.\nOne by one they lit up. One by one they went dark.\n\nThree years later, a survey team recorded a new pulse signal in the ruins.\nNot human. Like something learning.\nScientists said it was just empty echoes underground.\nYou know it isn\'t.\nBut you\'re not going back down.',
            'unlock': '歌者' if zh else 'SINGER',
        },
    }


@socketio.on('replay')
def handle_replay(data):
    sid = request.sid
    with sessions_lock:
        session = sessions.get(sid)
    if not session or not session.game: return
    action = data.get('action', '')
    if action == 'start':
        emit('state', {'replayMode': True}, room=sid)


if __name__ == '__main__':
    import echo_maze
    print(f"  CADMUS STATION v0.001 — Web Terminal Edition")
    print(f"  http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
