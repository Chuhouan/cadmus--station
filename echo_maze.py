#!/usr/bin/env python3
"""
################################################################
  ECHO MAZE v4.0 -- Echo Maze (Enhanced Edition)
  A game NO HUMAN has ever played before.

  You cannot see walls. You emit sonic pulses.
  Echoes reveal the maze. Memory guides you.

  ECHO MAZE v4.0 -- The Complete Echo Maze
  A game NO HUMAN has ever played before.

  NEW in v4.0 (Complete Edition):
  + Challenge Modifiers (6 types, stacking multipliers)
  + Boss Predators (Echo Mother / Silent Hunter / Void Avatar)
  + Environmental Interactions (Gas / Crystal / Dark Water / Echo Wall)
  + Daily Challenge + Local Leaderboard
  + Game Juice: fireworks, combo popups, damage flash, freeze frame
  + Secret Rooms with rare rewards
  + 6 Playable Echo Walkers (Prophet/Ghost/Behemoth/Singer/Shadow/Resonator)
  + Death Replay: god-view playback with speed control
################################################################
"""

import os, sys, random, math, time
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional, Set
from collections import deque
from enum import Enum

# ═══════════════════════════════════════════════════════════════════════
# PLATFORM SETUP (with web-mode fallback)
# ═══════════════════════════════════════════════════════════════════════

_WEB_MODE = os.environ.get('ECHO_MAZE_WEB', '0') == '1'

if not _WEB_MODE:
    try:
        if sys.platform == 'win32':
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            import msvcrt, ctypes
            k32 = ctypes.windll.kernel32
            k32.SetConsoleMode(k32.GetStdHandle(-11), 7)
            k32.SetConsoleMode(k32.GetStdHandle(-10), 7)
            k32.SetConsoleOutputCP(65001)
            k32.SetConsoleCP(65001)
        else:
            import termios, tty, select
    except Exception:
        pass  # Web mode: ignore platform setup errors

def get_key():
    # In web mode, this gets monkey-patched by server.py
    if _WEB_MODE:
        return ''
    if sys.platform == 'win32':
        if msvcrt.kbhit():
            k = msvcrt.getch()
            if k in (b'\xe0', b'\x00'):
                a = msvcrt.getch()
                return {b'H': 'up', b'P': 'down', b'K': 'left', b'M': 'right'}.get(a, '')
            try: return k.decode('utf-8', errors='ignore').lower()
            except: return ''
        return ''
    else:
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            if select.select([sys.stdin], [], [], 0)[0]:
                ch = sys.stdin.read(1)
                if ch == '\x1b' and select.select([sys.stdin], [], [], 0.01)[0]:
                    ch2 = sys.stdin.read(1)
                    if ch2 == '[' and select.select([sys.stdin], [], [], 0.01)[0]:
                        ch3 = sys.stdin.read(1)
                        return {'A': 'up', 'B': 'down', 'C': 'right', 'D': 'left'}.get(ch3, '')
                return ch.lower()
            return ''
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

def cls():  sys.stdout.write('__CLS__\n'); sys.stdout.flush()
def hide(): sys.stdout.write('\033[?25l'); sys.stdout.flush()
def show(): sys.stdout.write('\033[?25h'); sys.stdout.flush()

# ═══════════════════════════════════════════════════════════════════════
# THEME SYSTEM
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class Theme:
    name: str
    wave_outer: str; wave_mid: str; wave_inner: str; wave_core: str
    wall_fresh: str; wall_fade: str; wall_dim: str; wall_ghost: str
    player: str; ping_flash: str; exit_vis: str; exit_hint: str
    particle_a: str; particle_b: str
    title: str; accent: str; border: str
    crystal: str; rune: str; fragment: str
    echo_room: str; silent_room: str; memory_room: str
    trail: str; ghost: str

THEMES = [
    Theme("Ocean Deep",
        '\033[38;5;27m','\033[38;5;33m','\033[38;5;51m','\033[38;5;195m',
        '\033[38;5;226m\033[1m','\033[38;5;172m','\033[38;5;94m','\033[38;5;238m',
        '\033[38;5;82m\033[1m','\033[38;5;226m\033[1m',
        '\033[38;5;201m\033[1m\033[5m','\033[38;5;213m',
        '\033[38;5;51m','\033[38;5;195m',
        '\033[38;5;228m\033[1m','\033[38;5;213m\033[1m','\033[38;5;27m',
        '\033[38;5;51m\033[1m','\033[38;5;201m\033[1m','\033[38;5;226m\033[1m',
        '\033[38;5;213m','\033[38;5;240m','\033[38;5;33m',
        '\033[38;5;123m','\033[38;5;27m\033[2m',
    ),
    Theme("Volcanic Fury",
        '\033[38;5;124m','\033[38;5;160m','\033[38;5;202m','\033[38;5;226m',
        '\033[38;5;226m\033[1m','\033[38;5;208m','\033[38;5;130m','\033[38;5;52m',
        '\033[38;5;46m\033[1m','\033[38;5;220m\033[1m',
        '\033[38;5;201m\033[1m\033[5m','\033[38;5;208m',
        '\033[38;5;226m','\033[38;5;202m',
        '\033[38;5;226m\033[1m','\033[38;5;208m\033[1m','\033[38;5;160m',
        '\033[38;5;226m\033[1m','\033[38;5;196m\033[1m','\033[38;5;220m\033[1m',
        '\033[38;5;208m','\033[38;5;52m','\033[38;5;130m',
        '\033[38;5;202m','\033[38;5;94m\033[2m',
    ),
    Theme("Forest Spirit",
        '\033[38;5;22m','\033[38;5;28m','\033[38;5;40m','\033[38;5;118m',
        '\033[38;5;190m\033[1m','\033[38;5;142m','\033[38;5;64m','\033[38;5;235m',
        '\033[38;5;82m\033[1m','\033[38;5;190m\033[1m',
        '\033[38;5;201m\033[1m\033[5m','\033[38;5;213m',
        '\033[38;5;40m','\033[38;5;118m',
        '\033[38;5;190m\033[1m','\033[38;5;82m\033[1m','\033[38;5;28m',
        '\033[38;5;40m\033[1m','\033[38;5;201m\033[1m','\033[38;5;190m\033[1m',
        '\033[38;5;82m','\033[38;5;235m','\033[38;5;28m',
        '\033[38;5;118m','\033[38;5;22m\033[2m',
    ),
    Theme("Crystal Prism",
        '\033[38;5;55m','\033[38;5;91m','\033[38;5;129m','\033[38;5;201m',
        '\033[38;5;195m\033[1m','\033[38;5;153m','\033[38;5;97m','\033[38;5;53m',
        '\033[38;5;51m\033[1m','\033[38;5;195m\033[1m',
        '\033[38;5;226m\033[1m\033[5m','\033[38;5;225m',
        '\033[38;5;201m','\033[38;5;129m',
        '\033[38;5;225m\033[1m','\033[38;5;201m\033[1m','\033[38;5;91m',
        '\033[38;5;51m\033[1m','\033[38;5;201m\033[1m','\033[38;5;195m\033[1m',
        '\033[38;5;129m','\033[38;5;53m','\033[38;5;55m',
        '\033[38;5;153m','\033[38;5;55m\033[2m',
    ),
    Theme("Sunset Gold",
        '\033[38;5;94m','\033[38;5;136m','\033[38;5;178m','\033[38;5;226m',
        '\033[38;5;226m\033[1m','\033[38;5;214m','\033[38;5;172m','\033[38;5;58m',
        '\033[38;5;46m\033[1m','\033[38;5;226m\033[1m',
        '\033[38;5;201m\033[1m\033[5m','\033[38;5;208m',
        '\033[38;5;226m','\033[38;5;178m',
        '\033[38;5;226m\033[1m','\033[38;5;214m\033[1m','\033[38;5;136m',
        '\033[38;5;226m\033[1m','\033[38;5;196m\033[1m','\033[38;5;220m\033[1m',
        '\033[38;5;214m','\033[38;5;58m','\033[38;5;94m',
        '\033[38;5;178m','\033[38;5;136m\033[2m',
    ),
    Theme("Void Abyss",
        '\033[38;5;17m','\033[38;5;19m','\033[38;5;25m','\033[38;5;33m',
        '\033[38;5;250m\033[1m','\033[38;5;245m','\033[38;5;240m','\033[38;5;234m',
        '\033[38;5;51m\033[1m','\033[38;5;87m\033[1m',
        '\033[38;5;201m\033[1m\033[5m','\033[38;5;213m',
        '\033[38;5;33m','\033[38;5;87m',
        '\033[38;5;255m\033[1m','\033[38;5;201m\033[1m','\033[38;5;19m',
        '\033[38;5;87m\033[1m','\033[38;5;196m\033[1m','\033[38;5;255m\033[1m',
        '\033[38;5;25m','\033[38;5;234m','\033[38;5;17m',
        '\033[38;5;33m','\033[38;5;17m\033[2m',
    ),
]

R = '\033[0m'; B = '\033[1m'; D = '\033[2m'; I = '\033[3m'

# ═══════════════════════════════════════════════════════════════════════
# LOCALIZATION (中/EN 双语)
# ═══════════════════════════════════════════════════════════════════════

LOC = {
    # Title screen
    'title_see':  {'zh': '你看不到迷宫 —— 你只能"听"见它',     'en': 'You CANNOT see the maze -- you can only HEAR it.'},
    'title_fire': {'zh': '发射声波脉冲，从回声的涟漪中感知世界', 'en': 'Fire sonic pulses; walls revealed by their echo.'},
    'title_v2':   {'zh': 'v4.0: 粒子 | 特殊房间 | 收集品 | 连击 | 能力 | 词缀 | Boss', 'en': 'v4.0: Particles | Special Rooms | Items | Combos | Abilities | Mods | Boss'},
    'title_ctrl': {'zh': '[WASD] 移动  |  [空格] 脉冲  |  [Q] 退出  |  [L] 语言', 'en': '[WASD] Move  |  [SPACE] Ping  |  [Q] Quit  |  [L] Lang'},
    'title_diff': {'zh': 'DIFFICULTY_LEVEL', 'en': 'DIFFICULTY_LEVEL'},
    'title_easy': {'zh': 'EASY_MODE  -- 充裕能量，轻松漫步',    'en': 'EASY_MODE  -- Ample energy, relaxed pace'},
    'title_norm': {'zh': 'STD_MODE  -- 标准挑战，步步为营',    'en': 'STD_MODE -- Standard challenge'},
    'title_hard': {'zh': 'HARD_MODE -- 能量稀缺，真正考验',   'en': 'HARD_MODE -- Scarce energy, true test'},
    'title_pick': {'zh': '按 1-3 选择 | 4-7 地图 | a-f 主题 | L 语言',   'en': '1-3 difficulty | 4-7 map | a-f theme | L lang'},

    # Game UI — sci-fi terminal aesthetic
    'ui_energy':  {'zh': 'SIG_PWR', 'en': 'SIG_PWR'},
    'ui_combo':   {'zh': 'SLNT_', 'en': 'SLNT_'},
    'ui_level':   {'zh': 'LVL', 'en': 'LVL'},
    'ui_steps':   {'zh': 'POS', 'en': 'POS'},
    'ui_pings':   {'zh': 'PULSE', 'en': 'PULSE'},
    'ui_score':   {'zh': 'RES', 'en': 'RES'},
    'ui_maxcombo':{'zh': 'MAX_CHN', 'en': 'MAX_CHN'},
    'ui_items':   {'zh': 'MODS', 'en': 'MODS'},
    'ui_abilities':{'zh': 'AUG', 'en': 'AUG'},
    'ui_hint':    {'zh': 'WASD移动 | SPACE脉冲 | H帮助 | L语言 | Q退出', 'en': 'WASD move | SPACE ping | H help | L lang | Q quit'},
    'ui_footer1': {'zh': '>> ECHO_NAV: 你看不到墙——你看到的是声音的反射', 'en': '>> ECHO_NAV: You see NOT walls, but the ECHO of sound'},
    'ui_footer2': {'zh': '>> SLNT_CHAIN: 不发射脉冲持续移动积累暗行连击',   'en': '>> SLNT_CHAIN: Move without pinging to build silent chain'},

    # Messages
    'msg_energy0':  {'zh': '[!] 能量耗尽…静待恢复',           'en': '[!] Energy depleted... wait for recovery'},
    'msg_ping':     {'zh': '~ 脉冲！能量 [',                  'en': '~ PING! Energy ['},
    'msg_thud':     {'zh': '* 砰！撞墙 *',                    'en': '* THUD! *'},
    'msg_echo_ch':  {'zh': '*** 共鸣室！脉冲放大！***',        'en': '*** ECHO CHAMBER! Ping amplified! ***'},
    'msg_silent':   {'zh': '[寂静区] 脉冲被虚空吞噬…',         'en': '[Silent Zone] Your ping is swallowed by the void...'},
    'msg_mem_well': {'zh': '*** 记忆井！区域揭露！***',        'en': '*** MEMORY WELL! Area revealed! ***'},
    'msg_crystal':  {'zh': '*** 能量水晶！+3 能量 ***',        'en': '*** ENERGY CRYSTAL! +3 Energy ***'},
    'msg_rune':     {'zh': '*** 声呐符文！下次脉冲超级充能 ***', 'en': '*** SONAR RUNE! Next ping is supercharged ***'},
    'msg_fragment': {'zh': '*** 记忆碎片！出口方向已揭示 ***',  'en': '*** MEMORY FRAGMENT! Direction to exit revealed ***'},
    'msg_sonar_act':{'zh': '*** 声呐符文激活！***',            'en': '*** SONAR RUNE ACTIVATED! ***'},
    'msg_restart':  {'zh': '重新开始！',                      'en': 'Restarted!'},
    'msg_lvl_start':{'zh': '—— 在回声中找到出口！',            'en': '-- Find the exit through echoes!'},

    # Special room indicators
    'room_echo':   {'zh': '[共鸣室] 脉冲范围 x2！',           'en': '[Resonance Chamber] Ping range x2!'},
    'room_silent': {'zh': '[寂静区] 这里无法使用脉冲！',       'en': '[Silent Zone] Pings are useless here!'},

    # Memory fragment
    'frag_label':  {'zh': '碎片: 出口方向',                   'en': 'Fragment: Exit lies'},

    # Win screen
    'win_title':   {'zh': '>>> EXIT_UNLOCKED <<<',           'en': '>>> EXIT_UNLOCKED <<<'},
    'win_score':   {'zh': 'RESONANCE', 'en': 'RESONANCE'},
    'win_rating':  {'zh': 'GRADE', 'en': 'GRADE'},
    'win_combo':   {'zh': 'MAX_CHAIN', 'en': 'MAX_CHAIN'},
    'win_items':   {'zh': 'MODULES', 'en': 'MODULES'},
    'win_next':    {'zh': '[SPACE] 下一关',                   'en': '[SPACE] next level'},

    # Ratings
    'rat_S': {'zh': 'S  传说',   'en': 'S  LEGENDARY'},
    'rat_A': {'zh': 'A  大师',   'en': 'A  Master'},
    'rat_B': {'zh': 'B  熟练',   'en': 'B  Skilled'},
    'rat_C': {'zh': 'C  尚可',   'en': 'C  Adequate'},
    'rat_D': {'zh': 'D  迷失',   'en': 'D  Lost'},

    # Ability screen
    'ab_title':   {'zh': '*** 晋升 ***',           'en': '*** ASCENSION ***'},
    'ab_choose':  {'zh': '选择一个永久能力！',      'en': 'Choose a permanent ability!'},
    'ab_prompt':  {'zh': '按 1-{} 选择',           'en': 'Press 1-{} to choose'},

    # Ability descriptions
    'ab_bat_name': {'zh': '蝙蝠听觉', 'en': 'Bat Hearing'},
    'ab_bat_desc': {'zh': '能量恢复速度x2', 'en': 'Energy regen x2'},
    'ab_ele_name': {'zh': '大象步伐', 'en': 'Elephant Step'},
    'ab_ele_desc': {'zh': '脚步震动范围+1', 'en': 'Footstep reveal +1 range'},
    'ab_dol_name': {'zh': '海豚声呐', 'en': 'Dolphin Sonar'},
    'ab_dol_desc': {'zh': '脉冲范围+30%', 'en': 'Ping range +30%'},
    'ab_owl_name': {'zh': '猫头鹰之眼', 'en': 'Owl Eye'},
    'ab_owl_desc': {'zh': '墙壁记忆时间+50%', 'en': 'Wall memory +50% duration'},

    # Game over
    'bye_line1': {'zh': '感谢游玩 回声迷宫 v4.0！', 'en': 'Thank you for playing Echo Maze v4.0!'},
    'bye_line2': {'zh': '愿回声指引你',              'en': 'May the echoes guide you.'},

    # Language switch
    'lang_switch': {'zh': '语言切换', 'en': 'Language Switch'},
    'lang_prompt': {'zh': '当前: 中文 | [1]中文 [2]English', 'en': 'Current: English | [1]中文 [2]English'},

    # ── Story / Narrative ──
    'story_ch1_title':  {'zh': '第一章：回声行者',           'en': 'Chapter 1: The Echo Walker'},
    'story_ch1_body':   {'zh': '世界被"静默"吞噬。你是回声行者——\n'
                               '最后一个能用声音"看见"的人。\n'
                               '你必须穿越静默迷宫，\n'
                               '找到共鸣之心，唤醒失聪的世界。\n\n'
                               '但小心——静默中潜伏着回声捕食者，\n'
                               '它们被声音吸引，在暗处游荡...',
                          'en': 'The world is consumed by The Silence.\n'
                               'You are the last Echo Walker —\n'
                               'the only one who can "see" with sound.\n'
                               'Navigate the Silent Labyrinth,\n'
                               'find the Resonant Heart, and restore hearing to the world.\n\n'
                               'But beware — Echo Predators lurk in the quiet,\n'
                               'drawn to any sound you make...'},
    'story_ch2_title':  {'zh': '第二章：深渊低语',           'en': 'Chapter 2: Whispers of the Deep'},
    'story_ch2_body':   {'zh': '迷宫越来越暗，墙壁变得更厚。\n'
                               '回声捕食者越来越多——\n'
                               '它们曾是和你一样的回声行者，\n'
                               '被静默吞噬后变成了猎手。\n\n'
                               '你发现了特殊房间——\n'
                               '共鸣室、寂静区、记忆井。\n'
                               '它们是上古回声行者留下的遗迹。',
                          'en': 'The labyrinth grows darker, the walls thicker.\n'
                               'More Echo Predators roam —\n'
                               'they were once Echo Walkers like you,\n'
                               'consumed by The Silence, turned into hunters.\n\n'
                               'You discover special chambers —\n'
                               'Resonance Chambers, Silent Zones, Memory Wells.\n'
                               'Ruins left by ancient Echo Walkers.'},
    'story_ch3_title':  {'zh': '第三章：共鸣之心',           'en': 'Chapter 3: The Resonant Heart'},
    'story_ch3_body':   {'zh': '你能感觉到——共鸣之心就在附近。\n'
                               '每一次脉冲都带着希望的回响。\n'
                               '捕食者不敢靠近它。\n'
                               '你获得了上古的力量——\n'
                               '蝙蝠的听力、大象的脚步、\n'
                               '海豚的声呐、猫头鹰的夜眼。\n\n'
                               '终点就在前方。不要停。',
                          'en': 'You can feel it — the Resonant Heart is close.\n'
                               'Every ping carries an echo of hope.\n'
                               'The predators dare not approach it.\n'
                               'You have gained ancient powers —\n'
                               'hearing of the bat, step of the elephant,\n'
                               'sonar of the dolphin, eyes of the owl.\n\n'
                               'The end is near. Do not stop.'},
    'story_press':      {'zh': '按空格继续...',    'en': 'Press SPACE to continue...'},
    'story_skip':       {'zh': '按 Q 跳过剧情',   'en': 'Press Q to skip story'},

    # Map size
    'map_size':  {'zh': '地图大小', 'en': 'Map Size'},
    'map_small': {'zh': '小型',    'en': 'Small'},
    'map_medium':{'zh': '中型',    'en': 'Medium'},
    'map_large': {'zh': '大型',    'en': 'Large'},
    'map_huge':  {'zh': '巨型',    'en': 'Huge'},

    # Predator
    'pred_caught': {'zh': '回声捕食者抓住了你！-2能量', 'en': 'Echo Predator caught you! -2 Energy'},

    # Help / Knowledge Base
    'help_title': {'zh': '知识库', 'en': 'KNOWLEDGE BASE'},
    'help_nav':    {'zh': '迷宫导航', 'en': 'MAZE NAVIGATION'},
    'help_items':  {'zh': '收集品', 'en': 'COLLECTIBLES'},
    'help_rooms':  {'zh': '特殊房间', 'en': 'SPECIAL ROOMS'},
    'help_preds':  {'zh': '捕食者', 'en': 'PREDATORS'},
    'help_abils':  {'zh': '能力', 'en': 'ABILITIES'},
    'help_score':  {'zh': '计分', 'en': 'SCORING'},
    'help_press':  {'zh': '按任意键返回游戏...', 'en': 'Press any key to return to game...'},
    'help_you':    {'zh': '你的位置，所有回声的源头', 'en': 'Your position. Source of all echoes.'},
    'help_exit':   {'zh': '出口。被锁住，需找到钥匙', 'en': 'Exit. Locked until you find the quest key.'},
    'help_locked': {'zh': '出口被锁。先找到钥匙', 'en': 'Exit locked. Find the key first.'},
    'help_wall':   {'zh': '墙壁。回声脉冲短暂揭示', 'en': 'Wall. Revealed briefly by echo pulses.'},
    'help_path':   {'zh': '通道。安全可行走', 'en': 'Open passage. Safe to walk.'},
    'help_key':    {'zh': '任务钥匙。解锁出口。每关必找', 'en': 'Quest key. Unlocks exit. ONE per level. Must find!'},
    'help_crystal':{'zh': '能量水晶。拾取+3能量', 'en': 'Energy crystal. +3 energy on pickup.'},
    'help_rune':   {'zh': '声呐符文。下次脉冲2.5倍范围', 'en': 'Sonar rune. Next ping has 2.5x range.'},
    'help_frag':   {'zh': '记忆碎片。显示出口方向', 'en': 'Memory fragment. Shows direction to exit.'},
    'help_echo':   {'zh': '共鸣室。在里面脉冲范围x2', 'en': 'Echo chamber. Ping range x2 while inside.'},
    'help_silent': {'zh': '寂静区。脉冲无效，靠脚步导航', 'en': 'Silent zone. Pings do NOT work. Use footsteps.'},
    'help_well':   {'zh': '记忆井。进入时揭露大片区域', 'en': 'Memory well. Reveals large area on entry.'},
    'help_wander': {'zh': '游荡中。随机走动，没有在追你', 'en': 'Wandering. Not hunting... yet.'},
    'help_hunt':   {'zh': '狩猎中！听到了你的脉冲，冲过来了', 'en': 'HUNTING! Heard your ping. Coming for you.'},
    'help_stun':   {'zh': '晕眩中。刚攻击完，暂时无害', 'en': 'Stunned. Just attacked. Temporarily harmless.'},
    'help_bat':    {'zh': '蝙蝠听觉。能量恢复2倍速', 'en': 'Bat hearing. Energy regen 2x faster.'},
    'help_ele':    {'zh': '大象步伐。脚步揭示墙壁+1范围', 'en': 'Elephant step. Footsteps reveal walls +1 range.'},
    'help_dol':    {'zh': '海豚声呐。脉冲范围+30%', 'en': 'Dolphin sonar. Ping range +30%.'},
    'help_owl':    {'zh': '猫头鹰之眼。墙壁记忆时间+50%', 'en': 'Owl eye. Wall memory lasts 50% longer.'},
    'help_chain':  {'zh': '暗行连击。不发射脉冲连续移动=倍率', 'en': 'Silent chain. Move without pinging = combo multiplier.'},
    'help_grade':  {'zh': '评级。基于脉冲使用次数。S=<=3次', 'en': 'Grade. Based on pings used. S = <=3 pings!'},
    'help_achv':   {'zh': '成就。<=3脉冲+>=10步=暗行成就', 'en': 'Achievement. <=3 pings + >=10 moves = SILENT_RUN.'},

    # Quest
    'msg_exit_locked': {'zh': '出口被锁住了！必须先找到钥匙！', 'en': 'Exit is locked! Find the key first!'},
    'msg_quest': {'zh': '任务目标', 'en': 'Objective'},
    'quest_find_key': {'zh': '找到钥匙来解锁出口', 'en': 'Find the key to unlock the exit'},
    'quest_key_found': {'zh': '钥匙已找到！前往出口！', 'en': 'Key found! Head to the exit!'},
    'quest_stone': {'zh': '回声之石', 'en': 'Echo Stone'},
    'quest_ward': {'zh': '静默护符', 'en': 'Silence Ward'},
    'quest_key':  {'zh': '共鸣之钥', 'en': 'Resonant Key'},

    # Act story updates (for 3-act structure)
    'act1_title': {'zh': '第一幕：觉醒', 'en': 'Act I: Awakening'},
    'act1_body':  {'zh': '你从静默中醒来。\n'
                          '你是最后一个回声行者——\n'
                          '能用声音"看见"世界的人。\n\n'
                          '找到回声之石，它藏在迷宫深处，\n'
                          '是打开觉醒之门的唯一钥匙。\n\n'
                          '这片区域相对安全。\n'
                          '学会信任你的回声。',
                   'en': 'You awaken from The Silence.\n'
                         'You are the last Echo Walker —\n'
                         'one who can "see" the world through sound.\n\n'
                         'Find the Echo Stone, hidden deep in the maze.\n'
                         'It is the only key to the Gate of Awakening.\n\n'
                         'This region is relatively safe.\n'
                         'Learn to trust your echoes.'},
    'act2_title': {'zh': '第二幕：狩猎', 'en': 'Act II: The Hunt'},
    'act2_body':  {'zh': '迷宫变得更加黑暗扭曲。\n'
                          '回声捕食者出现了——\n'
                          '它们曾是和你一样的回声行者，\n'
                          '被静默吞噬后变成了猎手。\n\n'
                          '寻找静默护符来解锁出口，\n'
                          '但要小心——每次脉冲都会引来捕食者。\n\n'
                          '上古回声行者留下了特殊房间。\n'
                          '善用它们。',
                   'en': 'The labyrinth grows darker and more twisted.\n'
                         'Echo Predators have appeared —\n'
                         'they were once Echo Walkers like you,\n'
                         'consumed by Silence, turned into hunters.\n\n'
                         'Find the Silence Ward to unlock the exit,\n'
                         'but beware — every ping draws them closer.\n\n'
                         'Ancient Echo Walkers left special chambers.\n'
                         'Use them wisely.'},
    'act3_title': {'zh': '第三幕：共鸣', 'en': 'Act III: Resonance'},
    'act3_body':  {'zh': '你能感觉到——共鸣之心就在附近。\n'
                          '捕食者无处不在。\n'
                          '墙壁似乎在你耳边低语。\n\n'
                          '寻找最后的共鸣之钥。\n'
                          '只有它才能打开通往共鸣之心的门。\n\n'
                          '你不只是最后一个回声行者。\n'
                          '你是第一个共鸣者。\n'
                          '去吧。',
                   'en': 'You can feel it — the Resonant Heart is near.\n'
                         'Predators are everywhere.\n'
                         'The walls whisper in your ears.\n\n'
                         'Find the final Resonant Key.\n'
                         'Only it can open the door to the Heart.\n\n'
                         'You are not just the last Echo Walker.\n'
                         'You are the first Resonant.\n'
                         'Go.'},
    'act_final_title': {'zh': '终章', 'en': 'Finale'},
    'act_final_body':  {'zh': '共鸣之心在你面前跳动。\n'
                              '你把钥匙插入锁孔——\n'
                              '声音回来了。世界重新听见了自己。\n\n'
                              '静默结束了。\n'
                              '因为你。',
                        'en': 'The Resonant Heart pulses before you.\n'
                              'You turn the key —\n'
                              'Sound returns. The world hears itself again.\n\n'
                              'The Silence is over.\n'
                              'Because of you.'},

    # ── Challenge Modifiers ──
    'mod_title':      {'zh': '挑战词缀', 'en': 'CHALLENGE MODIFIERS'},
    'mod_subtitle':   {'zh': '可选难度加成（叠加生效，分数倍率叠加）', 'en': 'Optional difficulty modifiers (stack, score multipliers stack)'},
    'mod_prompt':     {'zh': '按 a-f 切换词缀 | 空格继续 | 不选跳过', 'en': 'a-f toggle | SPACE continue | skip'},
    'mod_none':       {'zh': '无词缀 (纯净通关)', 'en': 'NO MODIFIERS (Pure run)'},
    'mod_silent_name':{'zh': 'SILENT 静默 ─ 完全禁用脉冲', 'en': 'SILENT ─ Pings completely disabled'},
    'mod_silent_pings_disabled': {'zh': '脉冲已被禁用！', 'en': 'Pings disabled!'},
    'mod_silent_desc':{'zh': '无法发射任何脉冲。只能靠脚步和记忆。', 'en': 'Cannot fire any ping. Rely on footsteps and memory.'},
    'mod_hunted_name':{'zh': 'HUNTED 追猎 ─ 捕食者数量x3', 'en': 'HUNTED ─ Predator count x3'},
    'mod_hunted_desc':{'zh': '迷宫中的捕食者是正常的三倍。', 'en': 'Three times the normal number of predators.'},
    'mod_blind_name': {'zh': 'BLIND 盲目 ─ 出口标记隐藏', 'en': 'BLIND ─ Exit marker hidden'},
    'mod_blind_desc': {'zh': '出口位置不显示E标记。需凭记忆找到。', 'en': 'Exit location NOT shown. Find it from memory.'},
    'mod_fragile_name':{'zh': 'FRAGILE 脆弱 ─ 最大能量减半', 'en': 'FRAGILE ─ Max energy halved'},
    'mod_fragile_desc':{'zh': '能量上限只有正常的一半。', 'en': 'Energy capacity is only half of normal.'},
    'mod_amnesia_name':{'zh': 'AMNESIA 失忆 ─ 墙壁记忆-50%', 'en': 'AMNESIA ─ Wall memory -50%'},
    'mod_amnesia_desc':{'zh': '墙壁回声消逝速度加倍。', 'en': 'Wall echoes fade twice as fast.'},
    'mod_storm_name': {'zh': 'ECHO_STORM 回声风暴 ─ 自动脉冲', 'en': 'ECHO_STORM ─ Auto-ping'},
    'mod_storm_desc': {'zh': '每30步自动发射脉冲，暴露位置。', 'en': 'Auto-ping every 30 steps, revealing your position.'},
    'mod_bonus':      {'zh': '分数倍率', 'en': 'Score Multiplier'},
    'mod_unlocked':   {'zh': '已解锁！通关后可选择挑战词缀', 'en': 'UNLOCKED! Clear the game to unlock modifiers'},
    'mod_selected':   {'zh': '已选词缀', 'en': 'Active Modifiers'},
    'mod_multiplier': {'zh': '总倍率', 'en': 'Total Multiplier'},
    'mod_clears_label':{'zh': '通关次数', 'en': 'Total Clears'},

    # ── Boss ──
    'boss_alert':     {'zh': '*** 警告: {} 出现了！***', 'en': '*** WARNING: {} appears! ***'},
    'boss_defeated':  {'zh': '*** {} 已被击败！***', 'en': '*** {} has been DEFEATED! ***'},
    'boss_echo_mother':{'zh': '回响之母', 'en': 'Echo Mother'},
    'boss_silent_hunter':{'zh': '静默猎手', 'en': 'Silent Hunter'},
    'boss_void_avatar':{'zh': '虚空化身', 'en': 'Void Avatar'},
    'boss_echo_mother_ping':{'zh': '回响之母也发射了脉冲！墙壁显示陷入混乱…', 'en': 'The Echo Mother pings too! Wall display scrambles...'},
    'boss_echo_desc': {'zh': '每当玩家脉冲，她也脉冲——她的回声覆盖你的，墙壁显示混乱。', 'en': 'Every time you ping, she pings too — her echo overrides yours, scrambling wall display.'},
    'boss_silent_ate':{'zh': '静默猎手偷吃了能量水晶！', 'en': 'The Silent Hunter devoured an energy crystal!'},
    'boss_silent_desc':{'zh': '不攻击你，但会偷吃地图上的能量水晶。', 'en': "Doesn't attack you, but steals energy crystals from the map."},
    'boss_void_walls':{'zh': '虚空化身制造了幻象之墙！', 'en': 'The Void Avatar conjured illusory walls!'},
    'boss_void_desc': {'zh': '制造假墙壁——撞上去不疼但浪费时间。', 'en': 'Creates fake walls — harmless but time-wasting.'},
    'boss_drop_energy':{'zh': '*** Boss掉落: +5 能量！***', 'en': '*** Boss drop: +5 Energy! ***'},
    'boss_drop_perm':{'zh': '*** Boss掉落: 永久声呐（本关脉冲范围+50%）！***', 'en': '*** Boss drop: Permanent Sonar (ping range +50% this level)! ***'},
    'boss_drop_map':{'zh': '*** Boss掉落: 下一关全图揭示！***', 'en': '*** Boss drop: Full map revealed next level! ***'},

    # ── Environment Elements ──
    'env_gas':        {'zh': '瓦斯云', 'en': 'Gas Cloud'},
    'env_crystal':    {'zh': '水晶簇', 'en': 'Crystal Cluster'},
    'env_dark_water': {'zh': '暗水', 'en': 'Dark Water'},
    'env_echo_wall':  {'zh': '回音壁', 'en': 'Echo Wall'},
    'env_gas_desc':   {'zh': '脉冲经过时扩散到相邻格，扩大揭示范围', 'en': 'Ping waves spread gas to adjacent cells, expanding reveal'},
    'env_crystal_desc':{'zh': '脉冲碰撞时向4方向折射次级回声', 'en': 'Ping refracts into 4-directional secondary echoes'},
    'env_water_desc': {'zh': '踩上能量恢复x3，但移速减半（视觉反馈）', 'en': 'Energy regen x3 while standing, but slowed'},
    'env_echo_wall_desc':{'zh': '脉冲反弹显示背后地形', 'en': 'Ping bounces back, revealing terrain behind'},
    'env_gas_spread': {'zh': '瓦斯扩散了！', 'en': 'Gas cloud spreads!'},
    'env_gas_explode':{'zh': '*** 瓦斯爆炸！区域揭露！***', 'en': '*** GAS EXPLOSION! Area revealed! ***'},
    'env_crystal_refract':{'zh': '水晶折射了声波！', 'en': 'Crystal refracted the sound wave!'},
    'env_chain_flash':{'zh': '*** 连锁反应：全屏闪光！***', 'en': '*** CHAIN REACTION: Full screen flash! ***'},
    'env_water_step': {'zh': '踏入暗水…脚步沉重但能量涌动', 'en': 'Stepped into dark water... heavy steps but energy surges'},
    'env_echo_bounce':{'zh': '回音壁反弹了声波！', 'en': 'Echo Wall bounced the sound wave!'},

    # ── Daily Challenge ──
    'daily_title':   {'zh': '每日挑战', 'en': 'DAILY CHALLENGE'},
    'daily_desc':    {'zh': '全球同图，日更种子，本地排行', 'en': 'Global seed, daily refresh, local leaderboard'},
    'daily_seed':    {'zh': '今日种子', 'en': 'Daily Seed'},
    'daily_rank':    {'zh': '排行榜', 'en': 'LEADERBOARD'},
    'daily_enter':   {'zh': '今日挑战', 'en': 'Daily Run'},
    'daily_no_more': {'zh': '今日已完成！明天再来', 'en': 'Already completed today! Come back tomorrow'},
    'daily_result':  {'zh': '成绩已记录', 'en': 'Result Recorded'},
    'daily_score':   {'zh': '分数', 'en': 'Score'},
    'daily_pings':   {'zh': '脉冲', 'en': 'Pings'},
    'daily_steps':   {'zh': '步数', 'en': 'Steps'},
    'daily_grade':   {'zh': '评级', 'en': 'Grade'},
    'daily_rank_pos':{'zh': '排名', 'en': 'Rank'},
    'daily_empty':   {'zh': '暂无记录', 'en': 'No records yet'},
    'daily_press':   {'zh': '按任意键返回…', 'en': 'Press any key to return...'},

    # ── Game Juice ──
    'juice_combo':   {'zh': '暗行连击', 'en': 'SILENT CHAIN'},

    # ── Secret Rooms ──
    'secret_crack':   {'zh': '*** 墙壁出现裂缝！连续脉冲揭露了秘密入口！***', 'en': '*** A crack appears! Rapid pings revealed a secret entrance! ***'},
    'secret_enter':   {'zh': '*** 进入秘密房间！***', 'en': '*** Entered secret room! ***'},
    'secret_super_crystal': {'zh': '*** 超级能量水晶！+5 能量！***', 'en': '*** SUPER ENERGY CRYSTAL! +5 Energy! ***'},
    'secret_perm_sonar':    {'zh': '*** 永久声呐！本关脉冲范围+50%！***', 'en': '*** PERMANENT SONAR! Ping range +50% this level! ***'},
    'secret_repeller':      {'zh': '*** 捕食者驱散器！捕食者远离你！***', 'en': '*** PREDATOR REPELLER! Predators keep away! ***'},

    # ── Characters ──
    'char_title':     {'zh': '选择回声行者', 'en': 'CHOOSE ECHO WALKER'},
    'char_prompt':    {'zh': '按 1-6 选择角色 | 空格跳过', 'en': 'Press 1-6 to choose | SPACE to skip'},
    'char_prophet':   {'zh': '先知', 'en': 'Prophet'},
    'char_ghost':     {'zh': '幽灵', 'en': 'Ghost'},
    'char_behemoth':  {'zh': '巨兽', 'en': 'Behemoth'},
    'char_singer':    {'zh': '歌者', 'en': 'Singer'},
    'char_shadow':    {'zh': '暗影', 'en': 'Shadow'},
    'char_resonator': {'zh': '共振者', 'en': 'Resonator'},
    'char_prophet_desc':   {'zh': '初始可见范围+3 | 能量上限-2', 'en': 'Initial visibility +3 | Max energy -2'},
    'char_ghost_desc':     {'zh': '捕食者无视你 | 脉冲范围-40%', 'en': 'Predators ignore you | Ping range -40%'},
    'char_behemoth_desc':  {'zh': '撞墙直接摧毁变通道 | 每步-0.5能量', 'en': 'Destroy walls by walking | -0.5 energy/step'},
    'behemoth_wall_smash': {'zh': '墙壁粉碎！', 'en': 'Wall smashed!'},
    'char_singer_desc':    {'zh': '脉冲不消耗能量 | 脉冲范围极小', 'en': 'Pings cost 0 energy | Tiny ping range'},
    'char_shadow_desc':    {'zh': '移动不留下足迹 | 完全看不到自己位置', 'en': 'No footprints | Cannot see own position'},
    'char_resonator_desc': {'zh': '静止3秒自动揭露周围 | 不能发射脉冲', 'en': 'Still 3s = auto-reveal | Cannot ping'},
    'char_resonator_no_ping': {'zh': '共振者不能发射脉冲！靠静止感知…', 'en': 'Resonator cannot ping! Stand still to sense...'},
    'char_locked':    {'zh': '🔒 未解锁', 'en': '🔒 LOCKED'},
    'char_unlock_clear':   {'zh': '通关一次解锁', 'en': 'Clear game once'},
    'char_unlock_s':       {'zh': '获得S评级解锁', 'en': 'Get S rank'},
    'char_unlock_combo':   {'zh': '10连击解锁', 'en': '10 silent combo'},
    'char_unlock_boss':    {'zh': '击败3个Boss解锁', 'en': 'Defeat 3 bosses'},

    # ── Replay ──
    'replay_title':   {'zh': '回放', 'en': 'REPLAY'},
    'replay_prompt':  {'zh': '[R] 观看回放 | [SPACE] 继续', 'en': '[R] Watch replay | [SPACE] continue'},
    'replay_speed':   {'zh': '速度', 'en': 'Speed'},
    'replay_controls':{'zh': '[1]1x [2]2x [3]3x [Q]退出回放', 'en': '[1]1x [2]2x [3]3x [Q]exit replay'},
    'replay_event_ping':   {'zh': '声纳扫描', 'en': 'SCAN'},
    'replay_event_wall':   {'zh': '撞墙', 'en': 'WALL'},
    'replay_event_pred':   {'zh': '无人机撞击', 'en': 'DRONE HIT'},
    'replay_event_key':    {'zh': '找到权限卡', 'en': 'CARD FOUND'},
    'replay_event_boss':   {'zh': '异常清除', 'en': 'ANOMALY CLEARED'},
    'replay_event_exit':   {'zh': '闸门解锁', 'en': 'GATE UNLOCKED'},
    'replay_event_crystal':{'zh': '能量水晶', 'en': 'CRYSTAL'},
    'replay_event_dead':   {'zh': '能量耗尽', 'en': 'ENERGY DEPLETED'},
    'replay_stats':   {'zh': '统计', 'en': 'STATS'},
    'game_over':      {'zh': '能量耗尽…回声消散…', 'en': 'Energy depleted... echoes fade...'},
}

# Global language state
LANG = 'zh'

def t(key: str) -> str:
    """Translate a key to current language."""
    entry = LOC.get(key, {})
    return entry.get(LANG, key)

# Module-level alias to prevent shadowing by local loop variables named 't'
_tr = t

def ab_name(ab) -> str:
    """Get ability name in current language."""
    mapping = {
        'Bat Hearing': t('ab_bat_name'),
        'Elephant Step': t('ab_ele_name'),
        'Dolphin Sonar': t('ab_dol_name'),
        'Owl Eye': t('ab_owl_name'),
    }
    return mapping.get(ab.value[0], ab.value[0])

def ab_desc(ab) -> str:
    """Get ability description in current language."""
    mapping = {
        'Bat Hearing': t('ab_bat_desc'),
        'Elephant Step': t('ab_ele_desc'),
        'Dolphin Sonar': t('ab_dol_desc'),
        'Owl Eye': t('ab_owl_desc'),
    }
    return mapping.get(ab.value[0], ab.value[1])

def rating_text(pings: int) -> str:
    if pings <= 3: return t('rat_S')
    if pings <= 6: return t('rat_A')
    if pings <= 10: return t('rat_B')
    if pings <= 18: return t('rat_C')
    return t('rat_D')

# ═══════════════════════════════════════════════════════════════════════
# MAZE GENERATION
# ═══════════════════════════════════════════════════════════════════════

class Cell:
    WALL = 0; PATH = 1
    ECHO_CHAMBER = 2; SILENT_ZONE = 3; MEMORY_WELL = 4

def generate_maze(w: int, h: int) -> List[List[int]]:
    """Prim's algorithm maze. Returns grid of ints (Cell.WALL/PATH)."""
    grid = [[Cell.WALL] * w for _ in range(h)]
    sx = random.randrange(1, w - 1, 2)
    sy = random.randrange(1, h - 1, 2)
    grid[sy][sx] = Cell.PATH

    walls = []
    for dx, dy in [(2,0),(-2,0),(0,2),(0,-2)]:
        nx, ny = sx+dx, sy+dy
        if 0<nx<w-1 and 0<ny<h-1:
            walls.append((nx, ny, sx+dx//2, sy+dy//2))
    random.shuffle(walls)

    while walls:
        wx, wy, px, py = walls.pop()
        if grid[wy][wx] == Cell.WALL:
            grid[wy][wx] = Cell.PATH
            grid[py][px] = Cell.PATH
            batch = []
            for dx, dy in [(2,0),(-2,0),(0,2),(0,-2)]:
                nx, ny = wx+dx, wy+dy
                if 0<nx<w-1 and 0<ny<h-1 and grid[ny][nx]==Cell.WALL:
                    batch.append((nx, ny, wx+dx//2, wy+dy//2))
            random.shuffle(batch)
            walls.extend(batch)

    for x in range(w): grid[0][x]=grid[h-1][x]=Cell.WALL
    for y in range(h): grid[y][0]=grid[y][w-1]=Cell.WALL
    return grid

def find_farthest(grid, start):
    h, w = len(grid), len(grid[0])
    vis = [[False]*w for _ in range(h)]
    q = deque([(start[0], start[1], 0)])
    vis[start[1]][start[0]] = True
    far, md = start, 0
    while q:
        x, y, d = q.popleft()
        if d > md: md = d; far = (x, y)
        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nx, ny = x+dx, y+dy
            if 0<=nx<w and 0<=ny<h and not vis[ny][nx] and grid[ny][nx]!=Cell.WALL:
                vis[ny][nx] = True
                q.append((nx, ny, d+1))
    return far

def carve_special_rooms(grid, num_rooms=3):
    """Carve special rooms into the maze."""
    h, w = len(grid), len(grid[0])
    # Find open areas far from start
    open_cells = [(x,y) for y in range(1,h-1) for x in range(1,w-1)
                  if grid[y][x]==Cell.PATH]
    random.shuffle(open_cells)

    room_types = [Cell.ECHO_CHAMBER, Cell.SILENT_ZONE, Cell.MEMORY_WELL]
    rooms_placed = []

    for rt in room_types[:num_rooms]:
        for cx, cy in open_cells:
            # Check if we can carve a 3x3 room here
            if cx<2 or cy<2 or cx>w-4 or cy>h-4:
                continue
            # Check 3x3 area
            clear = True
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    if grid[cy+dy][cx+dx] == Cell.WALL and random.random()>0.5:
                        clear = False
            if clear:
                # Carve out
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        grid[cy+dy][cx+dx] = Cell.PATH
                grid[cy][cx] = rt  # Center marks the room type
                rooms_placed.append((cx, cy, rt))
                break

    return rooms_placed

# ═══════════════════════════════════════════════════════════════════════
# PARTICLES
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class Particle:
    x: float; y: float
    vx: float; vy: float
    life: float; max_life: float
    char: str; color: str

    def tick(self) -> bool:
        self.x += self.vx; self.y += self.vy
        self.vx *= 0.92; self.vy *= 0.92
        self.life -= 1
        return self.life > 0

def spawn_particles(x, y, count, colors) -> List[Particle]:
    ps = []
    for _ in range(count):
        angle = random.uniform(0, math.pi*2)
        speed = random.uniform(0.3, 1.5)
        ps.append(Particle(
            x=x, y=y,
            vx=math.cos(angle)*speed, vy=math.sin(angle)*speed,
            life=random.randint(6, 16), max_life=16,
            char=random.choice(['*', '+', '.', '\'']),
            color=random.choice(colors)
        ))
    return ps

# ═══════════════════════════════════════════════════════════════════════
# ECHO WAVE
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class Wave:
    ox: float; oy: float
    radius: float = 0.0; max_r: float = 8.0; speed: float = 0.5
    alive: bool = True

    def tick(self, maze, visible, particles, th: Theme):
        if not self.alive: return False
        self.radius += self.speed
        if self.radius >= self.max_r:
            self.alive = False
            return False
        h, w = len(maze), len(maze[0])
        ri = int(self.radius)+1
        for dy in range(-ri, ri+1):
            for dx in range(-ri, ri+1):
                d = math.sqrt(dx*dx+dy*dy)
                if d <= self.radius+0.5:
                    wx, wy = int(self.ox)+dx, int(self.oy)+dy
                    if 0<=wx<w and 0<=wy<h and maze[wy][wx]==Cell.WALL:
                        brightness = max(4, int(18-d*2.2))
                        cur = visible.get((wx, wy), 0)
                        if brightness > cur:
                            visible[(wx, wy)] = brightness
                            # Spawn spark particles on first hit
                            if cur == 0 and random.random()<0.3:
                                particles.extend(spawn_particles(
                                    wx+0.5, wy+0.5, random.randint(1,3),
                                    [th.particle_a, th.particle_b, th.wall_fresh]
                                ))
        return True

# ═══════════════════════════════════════════════════════════════════════
# COLLECTIBLES
# ═══════════════════════════════════════════════════════════════════════

class ItemType(Enum):
    ENERGY_CRYSTAL = 1
    SONAR_RUNE = 2
    MEMORY_FRAGMENT = 3
    QUEST_KEY = 4  # Quest item — unlocks the exit
    NARRATIVE_FRAGMENT = 5  # v5.0: narrative fragment (6 people × 3 = 18 total)

@dataclass
class Collectible:
    x: int; y: int
    item_type: ItemType
    glow: int = 8

# ═══════════════════════════════════════════════════════════════════════
# ECHO PREDATORS — blind creatures that hunt by sound
# ═══════════════════════════════════════════════════════════════════════

class PredatorType(Enum):
    """Types of drone enemies."""
    PATROL = "patrol"         # Standard patrol drone
    FAULT = "fault"           # Level 8: tracks footsteps, broken antenna
    SLEEPING_GIANT = "sleeping_giant"  # Level 7: dormant, wakes at step 50

@dataclass
class Predator:
    x: int; y: int
    dir_x: int = 0; dir_y: int = 0
    hunting: bool = False
    hunt_x: int = 0; hunt_y: int = 0
    stunned: int = 0
    wander_timer: int = 0
    hunt_timer: int = 0
    drone_type: PredatorType = PredatorType.PATROL
    patrol_path: List[Tuple[int,int]] = field(default_factory=list)  # Fixed patrol route
    patrol_idx: int = 0
    # Level 8: FAULT drone — tracks footsteps
    footstep_alert: int = 0  # Alerted by footstep, counts down
    # Invulnerable to focus pulse (all normal drones)
    invulnerable_to_focus: bool = True

# ═══════════════════════════════════════════════════════════════════════
# ABILITIES
# ═══════════════════════════════════════════════════════════════════════

class Ability(Enum):
    BAT_HEARING = ("Bat Hearing", "Energy regen x2", "bat")
    ELEPHANT_STEP = ("Elephant Step", "Footstep reveal +1 range", "elephant")
    DOLPHIN_SONAR = ("Dolphin Sonar", "Ping range +30%", "dolphin")
    OWL_EYE = ("Owl Eye", "Wall memory +50% duration", "owl")

# ═══════════════════════════════════════════════════════════════════════
# CHALLENGE MODIFIERS & BOSS TYPES
# ═══════════════════════════════════════════════════════════════════════

class ChallengeModifier(Enum):
    """Optional difficulty modifiers with score multipliers. v5.0: only SILENT and HUNTED."""
    SILENT = ("SILENT", "Pings disabled", 2.0)
    HUNTED = ("HUNTED", "Drones x3", 1.5)

class EnvElement(Enum):
    """Environmental elements that react with sound waves."""
    GAS_CLOUD = "gas_cloud"          # % — ping waves spread gas
    CRYSTAL_CLUSTER = "crystal_cluster"  # * — refracts waves
    DARK_WATER = "dark_water"        # ≈ — slows, energy regen
    ECHO_WALL = "echo_wall"          # ∥ — bounces waves back

class SecretReward(Enum):
    SUPER_CRYSTAL = "super_crystal"      # +5 energy
    PERMANENT_SONAR = "permanent_sonar"  # Ping range +50% rest of level
    PREDATOR_REPELLER = "predator_repeller"  # Predators stay 8+ cells away

class WalkerClass(Enum):
    """Playable exoskeleton models. v5.0: six peoples' exoskeletons."""
    PROPHET = "prophet"        # 林先和的遗物: scan range +3, max energy -2 (8)
    GHOST = "ghost"            # 苏无影的外骨骼: drones ignore scan pulse, scan range -40%
    BEHEMOTH = "behemoth"      # 赵铁山的改装: smash brittle walls, 0.3 energy per step
    SINGER = "singer"          # 陈歌的中继模式: scan pulse free, range 2, NO focus pulse
    SHADOW = "shadow"          # 吴暗的装备: no footstep sound, invisible self 3s after pulse
    RESONATOR = "resonator"    # 郑振的感应器: stationary 3s = auto-reveal 5 cells, NO active pulse

# ═══════════════════════════════════════════════════════════════════════
# PREDATORS & BOSS
# ═══════════════════════════════════════════════════════════════════════

class BossType(Enum):
    ECHO_MOTHER = "echo_mother"     # Level 3: acoustic field simulator
    SILENT_HUNTER = "silent_hunter"  # Level 6: security drone swarm core
    VOID_AVATAR = "void_avatar"     # Level 9: core acoustic projection

@dataclass
class Boss:
    """Boss with 3-layer shield system. Only focus pulse damages shields."""
    boss_type: BossType
    x: int; y: int
    shields: int = 3  # Shield layers (replaces HP)
    max_shields: int = 3
    stunned: int = 0
    # Echo Mother state
    counter_ping_timer: int = 0
    # Silent Hunter state
    target_crystal: Optional[Tuple[int,int]] = None
    extra_shields: int = 0  # Extra shields from eating crystals
    # Void Avatar state
    fake_walls: List[Tuple[int,int]] = field(default_factory=list)
    fake_wall_timer: int = 0
    anchors: List[Tuple[int,int]] = field(default_factory=list)  # Frequency anchors
    anchors_active: int = 0  # Number of anchors activated

# ═══════════════════════════════════════════════════════════════════════
# GAME STATE
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class Game:
    maze: List[List[int]]
    w: int; h: int
    px: int; py: int
    ex: int; ey: int
    theme: Theme
    energy: int = 8; max_energy: int = 8
    moves: int = 0; pings: int = 0
    level: int = 1; score: int = 0; total_score: int = 0
    won: bool = False
    visible: Dict = field(default_factory=dict)
    waves: List[Wave] = field(default_factory=list)
    particles: List[Particle] = field(default_factory=list)
    ping_flash: int = 0; exit_flash: int = 0
    exit_visible: bool = False
    footsteps: List[Tuple] = field(default_factory=list)
    msgs: List[Tuple] = field(default_factory=list)
    collectibles: List[Collectible] = field(default_factory=list)
    special_rooms: List[Tuple] = field(default_factory=list)  # (x,y,type)
    combo: int = 0; max_combo: int = 0
    sonar_charged: bool = False
    memory_direction: Optional[Tuple[float, float]] = None
    abilities: Set[Ability] = field(default_factory=set)
    previous_path: List[Tuple[int,int]] = field(default_factory=list)
    path_this_run: List[Tuple[int,int]] = field(default_factory=list)
    screen_shake: int = 0
    collected_items: Dict[ItemType, int] = field(default_factory=dict)
    predators: List[Predator] = field(default_factory=list)
    chapter: int = 1
    story_seen: bool = False
    exit_locked: bool = True  # Exit locked until quest key found
    quest_complete: bool = False
    explored: Dict[Tuple[int,int], int] = field(default_factory=dict)  # Permanent memory map
    wave_amp: float = 0.0  # Waveform amplitude
    wave_target: float = 0.0
    scanline: int = 0  # Ping scanline effect
    silent_steps: int = 0  # Steps without ping
    screen_invert: int = 0  # Full screen flash on key find
    active_modifiers: Set[ChallengeModifier] = field(default_factory=set)
    total_clears: int = 0  # Total number of game completions
    boss: Optional[Boss] = None  # Boss for this level
    boss_defeated: bool = False
    upcoming_map_reveal: bool = False  # Next level full map reward
    env_elements: Dict[Tuple[int,int], EnvElement] = field(default_factory=dict)
    env_cooldowns: Dict[Tuple[int,int], int] = field(default_factory=dict)  # Cooldown per element pos
    floating_texts: List[Tuple] = field(default_factory=list)  # (x,y,text,life)
    damage_flash: int = 0  # Red flash on damage
    freeze_frame: int = 0  # Freeze frame counter
    # Secret rooms
    secret_rooms: List[Dict] = field(default_factory=list)  # [{x,y,entrance_x,entrance_y,reward,revealed,entered}]
    last_ping_wall: Optional[Tuple[int,int]] = None  # Track consecutive pings on same wall
    last_ping_wall_frame: int = 0
    ping_frame_counter: int = 0  # Increments each ping
    # Character
    walker_class: Optional[WalkerClass] = None
    stationary_timer: int = 0  # For Resonator
    last_pos: Tuple[int,int] = (0,0)  # For Resonator stationary check
    # Replay system
    replay_log: List[Tuple] = field(default_factory=list)  # (frame, px, py, event_type, data)
    is_dead: bool = False
    dead_frame: int = 0  # Frame when energy hit 0
    # v5.0: Fragment system
    fragments_collected: int = 0  # Total fragments collected
    fragments_all_collected: bool = False  # All 18 collected
    fragments_person: Dict[str, set] = field(default_factory=dict)  # person_id -> {frag_nums}
    # v5.0: Dual pulse
    charging_focus: bool = False  # True when holding space for focus pulse
    focus_cooldown: int = 0  # Cooldown after focus pulse
    # v5.0: Level 7 step counter
    l7_step_counter: int = 0  # Steps taken in level 7
    l7_giant_awake: bool = False  # Whether the sleeping giant has awoken
    # v5.0: Boss narrative
    boss_narrative_sent: bool = False  # Whether boss defeat narrative was sent
    # v5.0: Direction tracking for focus pulse
    last_dx: int = 1  # Last movement direction x (-1, 0, 1)
    last_dy: int = 0  # Last movement direction y (-1, 0, 1)

    def msg(self, text: str):
        self.msgs.append((text, 40))

    def _record(self, event_type: str, data=None):
        """Record a replay event at current frame."""
        self.replay_log.append((self.moves + self.pings, self.px, self.py, event_type, data))

    def room_at(self, x, y):
        """Check if position is in a special room."""
        for rx, ry, rt in self.special_rooms:
            if abs(x-rx)<=1 and abs(y-ry)<=1:
                return rt
        return None

    def tick(self):
        # Use _tr (module-level alias) to avoid shadowing by loop variable 't'
        # Visible walls fade
        new_vis = {}
        for pos, tval in self.visible.items():
            # Owl Eye ability: 50% longer memory
            decay = 0.67 if Ability.OWL_EYE in self.abilities else 1.0
            if tval > decay:
                new_vis[pos] = tval - decay
        self.visible = new_vis

        # Waves tick
        new_waves = []
        for w in self.waves:
            if w.tick(self.maze, self.visible, self.particles, self.theme):
                new_waves.append(w)
        self.waves = new_waves

        # ── Environment: wave-element interaction ──
        env_to_trigger = []
        for (ex, ey), elem in list(self.env_elements.items()):
            cd = self.env_cooldowns.get((ex, ey), 0)
            if cd > 0:
                self.env_cooldowns[(ex, ey)] = cd - 1
                continue
            for w in self.waves:
                d = math.sqrt((ex - w.ox)**2 + (ey - w.oy)**2)
                if abs(d - w.radius) < 0.7:
                    env_to_trigger.append((ex, ey, elem, w))
                    break  # One trigger per element per tick

        triggered_gas = []
        triggered_crystal = []
        for ex, ey, elem, w in env_to_trigger:
            self.env_cooldowns[(ex, ey)] = 8  # Cooldown after trigger
            if elem == EnvElement.GAS_CLOUD:
                triggered_gas.append((ex, ey))
                # Reveal area around gas
                for dy in range(-3, 4):
                    for dx in range(-3, 4):
                        wx, wy = ex+dx, ey+dy
                        if 0<=wx<self.w and 0<=wy<self.h and self.maze[wy][wx]==Cell.WALL:
                            self.visible[(wx, wy)] = 15
                self.particles.extend(spawn_particles(ex+0.5, ey+0.5, 6,
                    ['\033[38;5;154m', '\033[38;5;190m\033[1m']))
                # Spread gas to adjacent cell
                for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                    nx, ny = ex+dx, ey+dy
                    if 0<=nx<self.w and 0<=ny<self.h and self.maze[ny][nx]==Cell.PATH \
                       and (nx, ny) not in self.env_elements:
                        self.env_elements[(nx, ny)] = EnvElement.GAS_CLOUD
                        self.env_cooldowns[(nx, ny)] = 15  # Longer cooldown for spread
                self.msg(_tr('env_gas_spread'))

            elif elem == EnvElement.CRYSTAL_CLUSTER:
                triggered_crystal.append((ex, ey))
                # Refract: emit secondary waves in 4 directions
                for a in [0, 90, 180, 270]:
                    rad = math.radians(a)
                    self.waves.append(Wave(
                        ox=ex+math.cos(rad)*0.3, oy=ey+math.sin(rad)*0.3,
                        radius=0.1, max_r=6.0+random.uniform(-0.5,2),
                        speed=0.3+random.uniform(-0.05,0.12),
                    ))
                self.particles.extend(spawn_particles(ex+0.5, ey+0.5, 8,
                    ['\033[38;5;225m\033[1m', '\033[38;5;201m']))
                self.msg(_tr('env_crystal_refract'))

            elif elem == EnvElement.ECHO_WALL:
                # Bounce: emit a reflected wave opposite direction
                bw = Wave(
                    ox=ex, oy=ey,
                    radius=0.1, max_r=w.max_r - w.radius,
                    speed=0.3,
                )
                self.waves.append(bw)
                self.particles.extend(spawn_particles(ex+0.5, ey+0.5, 4,
                    ['\033[38;5;255m\033[1m', '\033[38;5;250m']))
                # Reveal walls behind echo wall
                for dy in range(-2, 3):
                    for dx in range(-2, 3):
                        wx, wy = ex+dx, ey+dy
                        if 0<=wx<self.w and 0<=wy<self.h and self.maze[wy][wx]==Cell.WALL:
                            self.visible[(wx, wy)] = 14
                self.msg(_tr('env_echo_bounce'))

        # Chain reaction: gas + crystal in same tick = full screen flash
        if triggered_gas and triggered_crystal:
            # Reveal massive area
            for wy in range(self.h):
                for wx in range(self.w):
                    if self.maze[wy][wx] == Cell.WALL:
                        self.visible[(wx, wy)] = 25
            self.screen_invert = 6
            self.particles.extend(spawn_particles(
                self.px+0.5, self.py+0.5, 25,
                ['\033[38;5;226m\033[1m', '\033[38;5;255m\033[1m', '\033[38;5;201m\033[1m']
            ))
            self.msg(_tr('env_chain_flash'))
            # Stun all predators
            for p in self.predators:
                p.stunned = 25
                p.hunting = False
        # Gas explosion: gas + wave = stun nearby predators + reveal
        elif triggered_gas:
            for gx, gy in triggered_gas:
                for p in self.predators:
                    if abs(p.x-gx)+abs(p.y-gy) < 5:
                        p.stunned = 20
                        p.hunting = False

        # Particles tick
        self.particles = [p for p in self.particles if p.tick()]

        # Timers
        for attr in ['ping_flash', 'exit_flash', 'screen_shake', 'damage_flash', 'freeze_frame']:
            v = getattr(self, attr)
            if v > 0: setattr(self, attr, v-1)

        # Resonator: stationary auto-reveal
        if self.walker_class == WalkerClass.RESONATOR:
            if (self.px, self.py) == self.last_pos:
                self.stationary_timer += 1
            else:
                self.stationary_timer = 0
            if self.stationary_timer >= 45:  # ~3 seconds at 15 FPS
                # Reveal surrounding area
                for dy in range(-4, 5):
                    for dx in range(-4, 5):
                        wx, wy = self.px+dx, self.py+dy
                        if 0<=wx<self.w and 0<=wy<self.h and self.maze[wy][wx]==Cell.WALL:
                            self.visible[(wx, wy)] = 20
                self.stationary_timer = 0
                self.particles.extend(spawn_particles(self.px+0.5, self.py+0.5, 10,
                    ['\033[38;5;129m\033[1m', '\033[38;5;201m']))
        self.last_pos = (self.px, self.py)

        # Death check: energy at 0 for too long — with soft floor
        if self.energy <= 0 and not self.is_dead:
            self.dead_frame += 1
            # v5.0: auto-regen 0.5 energy/sec at zero (every 2 seconds = +1)
            if self.dead_frame % 30 == 0:
                self.energy = min(self.max_energy, self.energy + 1)
            if self.dead_frame >= 120:  # ~8 seconds at 15 FPS with auto-regen
                self.is_dead = True
                self._record('dead', (self.px, self.py))
        elif self.energy > 0:
            self.dead_frame = 0

        # Floating texts lifecycle
        self.floating_texts = [(x,y,txt,life-1) for x,y,txt,life in self.floating_texts if life>0]

        self.exit_visible = (self.ex, self.ey) in self.visible
        self.footsteps = [(x,y,t-1) for x,y,t in self.footsteps if t>1]
        self.msgs = [(txt,t-1) for txt,t in self.msgs if t>1]

        # Explored map — permanent memory of revealed walls
        for pos, t in self.visible.items():
            if t > 5: self.explored[pos] = max(self.explored.get(pos, 0), t)
        exp2 = {}
        for pos, t in self.explored.items():
            if t > 0.5: exp2[pos] = t - 0.3
        self.explored = exp2

        # Waveform decay
        if self.wave_amp > 0.01:
            self.wave_amp += (self.wave_target - self.wave_amp) * 0.3
            self.wave_target *= 0.85
        else:
            self.wave_amp = 0; self.wave_target = 0
        if self.scanline > 0: self.scanline -= 1
        if self.screen_invert > 0: self.screen_invert -= 1

        # Collectibles glow
        for c in self.collectibles:
            c.glow = max(2, c.glow + random.choice([-1, -1, 1]))

        # Energy regen
        regen_rate = 0.012 if Ability.BAT_HEARING in self.abilities else 0.006
        if random.random() < regen_rate and self.energy < self.max_energy:
            self.energy += 1

        # ── Predator AI ──
        ghost_mode = self.walker_class == WalkerClass.GHOST
        for p in self.predators:
            if p.stunned > 0:
                p.stunned -= 1
                continue

            # Hunting: move toward last known player position
            if p.hunting:
                p.hunt_timer -= 1
                if p.hunt_timer <= 0 or (p.x == p.hunt_x and p.y == p.hunt_y):
                    p.hunting = False
                else:
                    dx = 1 if p.hunt_x > p.x else (-1 if p.hunt_x < p.x else 0)
                    dy = 1 if p.hunt_y > p.y else (-1 if p.hunt_y < p.y else 0)
                    # Try to move toward target
                    nx, ny = p.x + dx, p.y + dy
                    if 0 <= nx < self.w and 0 <= ny < self.h and self.maze[ny][nx] != Cell.WALL:
                        p.x, p.y = nx, ny
                    elif dx != 0:
                        ny2 = p.y + dy if dy != 0 else p.y
                        nx2 = p.x + dx
                        if 0 <= nx2 < self.w and 0 <= ny2 < self.h and self.maze[ny2][nx2] != Cell.WALL:
                            p.x, p.y = nx2, ny2
                        elif dy != 0:
                            nx3, ny3 = p.x, p.y + dy
                            if 0 <= nx3 < self.w and 0 <= ny3 < self.h and self.maze[ny3][nx3] != Cell.WALL:
                                p.x, p.y = nx3, ny3
                    elif dy != 0:
                        nx2, ny2 = p.x, p.y + dy
                        if 0 <= nx2 < self.w and 0 <= ny2 < self.h and self.maze[ny2][nx2] != Cell.WALL:
                            p.x, p.y = nx2, ny2
            else:
                # Wandering
                p.wander_timer -= 1
                if p.wander_timer <= 0:
                    p.dir_x = random.choice([-1, 0, 1])
                    p.dir_y = random.choice([-1, 0, 1])
                    p.wander_timer = random.randint(8, 25)
                nx, ny = p.x + p.dir_x, p.y + p.dir_y
                if 0 <= nx < self.w and 0 <= ny < self.h and self.maze[ny][nx] != Cell.WALL:
                    p.x, p.y = nx, ny

            # Check if predator caught player (Ghost is ignored)
            if not ghost_mode and p.x == self.px and p.y == self.py and p.stunned == 0:
                self.energy = max(0, self.energy - 2)
                p.stunned = 20
                p.hunting = False
                self.damage_flash = 6  # Red flash on damage
                self._record('drone', (p.x, p.y))
                self.particles.extend(spawn_particles(
                    self.px+0.5, self.py+0.5, 8,
                    ['\033[38;5;203m\033[1m', '\033[38;5;196m']
                ))
                self.msg(f"[!] {t('pred_caught')}")

        # ── Boss AI (v5.0: shield system) ──
        if self.boss and not self.boss_defeated:
            b = self.boss
            if b.stunned > 0:
                b.stunned -= 1
            else:
                if b.boss_type == BossType.ECHO_MOTHER:
                    # Wanders slowly. Counter-pings periodically.
                    b.counter_ping_timer -= 1
                    if b.counter_ping_timer <= 0:
                        b.counter_ping_timer = random.randint(25, 45)
                        for a in range(0, 360, 30):
                            rad = math.radians(a)
                            self.waves.append(Wave(
                                ox=b.x+math.cos(rad)*0.3, oy=b.y+math.sin(rad)*0.3,
                                radius=0.1, max_r=5.0+random.uniform(-1,2),
                                speed=0.3+random.uniform(-0.05,0.1),
                            ))
                        # Scramble visible walls
                        for pos in list(self.visible.keys()):
                            if random.random() < 0.3:
                                self.visible[pos] = max(1, self.visible[pos] * 0.4)
                    if random.random() < 0.2:
                        for _ in range(3):
                            dx = random.choice([-1,0,1]); dy = random.choice([-1,0,1])
                            nx, ny = b.x+dx, b.y+dy
                            if 0<=nx<self.w and 0<=ny<self.h and self.maze[ny][nx]!=Cell.WALL:
                                b.x, b.y = nx, ny; break

                elif b.boss_type == BossType.SILENT_HUNTER:
                    # Moves toward crystals to eat them → gains extra shields
                    if b.target_crystal is None:
                        crystals = [c for c in self.collectibles if c.item_type==ItemType.ENERGY_CRYSTAL]
                        if crystals:
                            nearest = min(crystals, key=lambda c: abs(c.x-b.x)+abs(c.y-b.y))
                            b.target_crystal = (nearest.x, nearest.y)
                    if b.target_crystal:
                        tx, ty = b.target_crystal
                        dx = 1 if tx>b.x else (-1 if tx<b.x else 0)
                        dy = 1 if ty>b.y else (-1 if ty<b.y else 0)
                        nx, ny = b.x+dx, b.y+dy
                        if 0<=nx<self.w and 0<=ny<self.h and self.maze[ny][nx]!=Cell.WALL:
                            b.x, b.y = nx, ny
                        for c in self.collectibles[:]:
                            if c.x==b.x and c.y==b.y and c.item_type==ItemType.ENERGY_CRYSTAL:
                                self.collectibles.remove(c)
                                b.extra_shields = min(3, b.extra_shields + 1)
                                self.msg(_tr('boss_silent_ate'))
                                self.particles.extend(spawn_particles(b.x+0.5, b.y+0.5, 8,
                                    ['\033[38;5;203m\033[1m', '\033[38;5;196m']))
                                b.target_crystal = None
                                break

                elif b.boss_type == BossType.VOID_AVATAR:
                    # Creates fake walls + manages anchors
                    b.fake_wall_timer -= 1
                    if b.fake_wall_timer <= 0:
                        b.fake_wall_timer = random.randint(20, 40)
                        b.fake_walls.clear()
                        for _ in range(3):
                            for __ in range(10):
                                fx = self.px + random.randint(-5, 5)
                                fy = self.py + random.randint(-4, 4)
                                if 0<=fx<self.w and 0<=fy<self.h and self.maze[fy][fx]==Cell.PATH \
                                   and (fx,fy)!=(self.px,self.py) and (fx,fy)!=(self.ex,self.ey) \
                                   and (fx,fy) not in b.fake_walls:
                                    b.fake_walls.append((fx, fy))
                                    self.visible[(fx, fy)] = 20
                                    break
                    # Ensure 3 anchors exist
                    if not b.anchors:
                        for _ in range(3):
                            for __ in range(20):
                                ax = b.x + random.randint(-6, 6)
                                ay = b.y + random.randint(-5, 5)
                                if 0<=ax<self.w and 0<=ay<self.h and self.maze[ay][ax]==Cell.PATH \
                                   and (ax,ay)!=(self.px,self.py):
                                    b.anchors.append((ax, ay)); break
                    # Slow movement
                    if random.random() < 0.25:
                        for _ in range(3):
                            dx = random.choice([-1,0,1]); dy = random.choice([-1,0,1])
                            nx, ny = b.x+dx, b.y+dy
                            if 0<=nx<self.w and 0<=ny<self.h and self.maze[ny][nx]!=Cell.WALL:
                                b.x, b.y = nx, ny
                                # Shuffle anchors on move
                                if random.random() < 0.3:
                                    random.shuffle(b.anchors)
                                break

            # Boss collision with player
            if b.boss_type != BossType.SILENT_HUNTER:
                if b.x==self.px and b.y==self.py:
                    self.energy = max(0, self.energy - 3)
                    b.stunned = 15
                    self.damage_flash = 8
                    self.particles.extend(spawn_particles(
                        self.px+0.5, self.py+0.5, 12,
                        ['\033[38;5;203m\033[1m', '\033[38;5;196m\033[1m']
                    ))

    def emit_ping(self):
        """Legacy ping — now delegates to scan_pulse."""
        self.scan_pulse()

    def _pulse_blocked(self) -> bool:
        """Check if any pulse is blocked."""
        if ChallengeModifier.SILENT in self.active_modifiers:
            self.msg(t('mod_silent_name') + ': ' + t('mod_silent_pings_disabled'))
            return True
        room = self.room_at(self.px, self.py)
        if room == Cell.SILENT_ZONE:
            self.msg(t('msg_silent')); return True
        return False

    def _pulse_common(self, is_scan: bool = True):
        """Common pulse setup: particles, record, combo reset."""
        self.pings += 1
        self.ping_flash = 8
        self.combo = 0
        self.silent_steps = 0
        self.wave_target = 1.0
        self.scanline = 6
        self._record('scan' if is_scan else 'focus')
        self.particles.extend(spawn_particles(
            self.px+0.5, self.py+0.5, 12,
            [self.theme.wave_core, self.theme.wave_inner, self.theme.particle_a]
        ))

    def scan_pulse(self):
        """Scan pulse: 1 energy, 7-cell range, reveals walls. Does NOT damage bosses."""
        if self._pulse_blocked(): return
        # Resonator: cannot pulse
        if self.walker_class == WalkerClass.RESONATOR:
            self.msg(t('char_resonator_no_ping')); return
        if self.energy <= 0:
            self.msg(t('msg_energy0')); return

        # Singer: scan pulse costs 0 energy
        if self.walker_class != WalkerClass.SINGER:
            self.energy -= 1
        self._pulse_common(is_scan=True)

        range_bonus = self._calc_range_bonus(is_scan=True)
        base_r = 5.5 * range_bonus

        # Emit waves
        for a in range(0, 360, 20):
            rad = math.radians(a)
            self.waves.append(Wave(
                ox=self.px+math.cos(rad)*0.4, oy=self.py+math.sin(rad)*0.4,
                radius=0.2, max_r=base_r+random.uniform(-0.5, 2.5),
                speed=0.35+random.uniform(-0.08, 0.18),
            ))
        for i in range(3):
            self.waves.append(Wave(
                ox=self.px, oy=self.py,
                radius=float(i)*0.6, max_r=(7.0+i*2.5)*range_bonus,
                speed=0.32+i*0.1,
            ))
        self.msg(f"SCAN [{self.energy}/{self.max_energy}] ~")

        # Alert drones (unless GHOST)
        if self.walker_class != WalkerClass.GHOST:
            hunt_range = 12 * range_bonus
            if ChallengeModifier.HUNTED in self.active_modifiers:
                hunt_range *= 1.5
            for p in self.predators:
                if p.drone_type == PredatorType.SLEEPING_GIANT: continue  # Giant doesn't hear
                dist = math.sqrt((p.x - self.px)**2 + (p.y - self.py)**2)
                if dist < hunt_range:
                    p.hunting = True; p.hunt_x = int(self.px); p.hunt_y = int(self.py); p.hunt_timer = 25

        # Secret room detection
        self._check_secret_room(base_r)

    def focus_pulse(self):
        """Focus pulse: 3 energy, forward 3-cell cone, DAMAGES bosses. Knocks back drones."""
        if self._pulse_blocked(): return
        # Resonator and Singer cannot focus pulse
        if self.walker_class in (WalkerClass.RESONATOR, WalkerClass.SINGER):
            self.msg(t('char_resonator_no_ping')); return
        if self.energy < 3:
            self.msg('ENERGY LOW — need 3 for FOCUS' if LANG=='en' else '能量不足——聚焦脉冲需要3点能量')
            return

        self.energy -= 3
        self._pulse_common(is_scan=False)

        # Focus pulse: narrow cone in the direction the player last moved
        # Emit 3 powerful waves forward
        for i in range(3):
            self.waves.append(Wave(
                ox=self.px, oy=self.py,
                radius=float(i)*0.5, max_r=3.5 + i*1.0,
                speed=0.45 + i*0.08,
            ))
        # Visual distinction: bright white core
        self.particles.extend(spawn_particles(
            self.px+0.5, self.py+0.5, 18,
            ['\033[38;5;255m\033[1m', '\033[38;5;228m\033[1m', '\033[38;5;226m\033[1m']
        ))
        self.msg(f"FOCUS [{self.energy}/{self.max_energy}] !!" if LANG=='en' else f"聚焦脉冲 [{self.energy}/{self.max_energy}]！！")

        # Knock back nearby drones (within 2 cells)
        for p in self.predators:
            if p.drone_type == PredatorType.SLEEPING_GIANT: continue
            dist = math.sqrt((p.x - self.px)**2 + (p.y - self.py)**2)
            if dist < 3.0:
                # v5.0: Forward cone check — only affect drones in front of player
                if self.last_dx != 0 or self.last_dy != 0:
                    tx, ty = p.x - self.px, p.y - self.py
                    tdist = math.sqrt(tx*tx + ty*ty)
                    if tdist > 0:
                        dot = (tx/tdist)*self.last_dx + (ty/tdist)*self.last_dy
                        if dot < 0.707:  # ~45 degrees = half of 90° cone
                            continue
                # Knock back: push drone away from player
                dx = p.x - self.px; dy = p.y - self.py
                if dx != 0 or dy != 0:
                    nd = math.sqrt(dx*dx + dy*dy)
                    dx, dy = dx/nd, dy/nd
                else:
                    dx, dy = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
                for _ in range(4):
                    nx, ny = p.x + int(dx*2), p.y + int(dy*2)
                    if 0<=nx<self.w and 0<=ny<self.h and self.maze[ny][nx]==Cell.PATH:
                        p.x, p.y = nx, ny; break
                p.stunned = 25  # 5 second stun
                p.hunting = False
                self.particles.extend(spawn_particles(p.x+0.5, p.y+0.5, 8,
                    ['\033[38;5;226m\033[1m', '\033[38;5;196m']))

        # ── Boss interaction: focus pulse damages shields ──
        if self.boss and not self.boss_defeated:
            b = self.boss
            dist_to_boss = math.sqrt((b.x-self.px)**2 + (b.y-self.py)**2)
            can_damage = True
            # Echo Mother: must be within 3 cells
            if b.boss_type == BossType.ECHO_MOTHER and dist_to_boss > 3.0:
                can_damage = False
                self.msg('BOSS too far — must be within 3 cells!' if LANG=='en' else '距离Boss太远——必须在3格以内！')
            # Void Avatar: must be on a frequency anchor
            if b.boss_type == BossType.VOID_AVATAR:
                on_anchor = False
                for ax, ay in b.anchors:
                    if abs(self.px-ax) <= 1 and abs(self.py-ay) <= 1:
                        on_anchor = True; break
                if not on_anchor:
                    can_damage = False
                    self.msg('Must stand on a frequency anchor!' if LANG=='en' else '必须站在频率锚点上！')
            # v5.0: Forward cone check — only damage boss in front of player
            if can_damage and (self.last_dx != 0 or self.last_dy != 0):
                tx, ty = b.x - self.px, b.y - self.py
                tdist = math.sqrt(tx*tx + ty*ty)
                if tdist > 0:
                    dot = (tx/tdist)*self.last_dx + (ty/tdist)*self.last_dy
                    if dot < 0.707:
                        can_damage = False
            if can_damage and dist_to_boss < 4.0:
                # Silent Hunter: check extra shields from eaten crystals
                effective_shields = b.shields + b.extra_shields
                if b.boss_type == BossType.SILENT_HUNTER and effective_shields > b.shields:
                    b.extra_shields = max(0, b.extra_shields - 1)  # Strip extra shield first
                    self.msg('Extra shield stripped!' if LANG=='en' else '额外护盾被剥离！')
                else:
                    b.shields -= 1
                b.stunned = 12
                self.particles.extend(spawn_particles(
                    b.x+0.5, b.y+0.5, 20,
                    ['\033[38;5;226m\033[1m', '\033[38;5;196m\033[1m', self.theme.wave_core]
                ))
                if b.shields <= 0:
                    # Boss defeated!
                    self.boss_defeated = True
                    self._record('anomaly', (b.x, b.y))
                    boss_name = _tr(f'boss_{b.boss_type.value}')
                    self.msg(_tr('boss_defeated').format(boss_name))
                    # Drop energy crystals (1-2)
                    drop_count = random.randint(1, 2)
                    self.energy = min(self.max_energy, self.energy + drop_count * 3)
                    self.msg(f'BOSS DROP: +{drop_count*3} energy' if LANG=='en' else f'Boss掉落：+{drop_count*3} 能量')
                    self.particles.extend(spawn_particles(
                        b.x+0.5, b.y+0.5, 30,
                        [self.theme.exit_vis, self.theme.wave_core, self.theme.accent, self.theme.wall_fresh]
                    ))
                    self.screen_invert = 12
                    # v5.0: Boss-specific defeat narratives
                    if b.boss_type == BossType.ECHO_MOTHER:
                        self.msg('声场模拟器过载停机。残留数据读取中……林先和的记录：\'信号来自设施内部。有人还在里面。\'' if LANG=='zh' else 'Acoustic simulator offline. Residual data reading... Lin Xianhe\'s log: \'Signal comes from inside the facility. Someone is still inside.\'')
                    elif b.boss_type == BossType.SILENT_HUNTER:
                        self.msg('无人机核心损毁。储存器数据：\'锁定所有撤离通道。授权人：吴暗。\'不是事故。是封锁。' if LANG=='zh' else 'Drone core destroyed. Storage data: \'All evac routes locked. Authorized by: Wu An.\' Not an accident. A lockdown.')
                    elif b.boss_type == BossType.VOID_AVATAR:
                        self.msg('核心投影解体。安全模式启动。手动刹车需要两个活人。检测到另一个生物信号……' if LANG=='zh' else 'Core projection dissolved. Safe mode engaged. Manual brake requires two living persons. Another biosignal detected...')
                else:
                    shield_status = '▓'*b.shields + '░'*(b.max_shields - b.shields)
                    self.msg(f'[BOSS] Shields: [{shield_status}]')
            # Echo Mother: counter-pings
            if b.boss_type == BossType.ECHO_MOTHER and not self.boss_defeated:
                b.counter_ping_timer = max(1, b.counter_ping_timer - 15)

        # Crystal cluster: focus pulse destroys it + full screen flash
        for (ex, ey), elem in list(self.env_elements.items()):
            dist = math.sqrt((ex-self.px)**2 + (ey-self.py)**2)
            if dist < 3.0 and elem == EnvElement.CRYSTAL_CLUSTER:
                # v5.0: Forward cone check
                if self.last_dx != 0 or self.last_dy != 0:
                    tx, ty = ex - self.px, ey - self.py
                    tdist = math.sqrt(tx*tx + ty*ty)
                    if tdist > 0:
                        dot = (tx/tdist)*self.last_dx + (ty/tdist)*self.last_dy
                        if dot < 0.707: continue
                del self.env_elements[(ex, ey)]
                for wy in range(self.h):
                    for wx in range(self.w):
                        if self.maze[wy][wx] == Cell.WALL:
                            self.visible[(wx, wy)] = 20
                self.screen_invert = 8
                self.msg('CRYSTAL DESTROYED — Full scan!' if LANG=='en' else '水晶簇被摧毁——全屏扫描！')
                self.particles.extend(spawn_particles(ex+0.5, ey+0.5, 20,
                    ['\033[38;5;255m\033[1m', '\033[38;5;225m\033[1m']))
                break

        # Gas cloud: focus pulse ignites gas
        for (ex, ey), elem in list(self.env_elements.items()):
            dist = math.sqrt((ex-self.px)**2 + (ey-self.py)**2)
            if dist < 3.0 and elem == EnvElement.GAS_CLOUD:
                # v5.0: Forward cone check
                if self.last_dx != 0 or self.last_dy != 0:
                    tx, ty = ex - self.px, ey - self.py
                    tdist = math.sqrt(tx*tx + ty*ty)
                    if tdist > 0:
                        dot = (tx/tdist)*self.last_dx + (ty/tdist)*self.last_dy
                        if dot < 0.707: continue
                # Ignite: remove gas, stun all drones near gas
                del self.env_elements[(ex, ey)]
                for p in self.predators:
                    if abs(p.x-ex)+abs(p.y-ey) < 5:
                        p.stunned = 20; p.hunting = False
                self.particles.extend(spawn_particles(ex+0.5, ey+0.5, 15,
                    ['\033[38;5;226m\033[1m', '\033[38;5;202m\033[1m']))
                self.msg('GAS IGNITED!' if LANG=='en' else '瓦斯云被点燃！')
                break

    def _calc_range_bonus(self, is_scan: bool = True) -> float:
        """Calculate pulse range bonus based on character and room."""
        range_bonus = 1.0
        room = self.room_at(self.px, self.py)
        # Character-based
        if self.walker_class == WalkerClass.PROPHET:
            range_bonus += 0.4  # +3 cells effective
        elif self.walker_class == WalkerClass.SINGER:
            range_bonus = 0.28  # Tiny range (~2 cells)
        elif self.walker_class == WalkerClass.GHOST:
            range_bonus = 0.6  # Reduced range
        # Room
        if room == Cell.ECHO_CHAMBER:
            range_bonus = 2.0
            self.msg(t('msg_echo_ch'))
        # Abilities
        if Ability.DOLPHIN_SONAR in self.abilities:
            range_bonus += 0.3
        # Sonar rune: only affects scan pulse
        if is_scan and self.sonar_charged:
            range_bonus += 1.5
            self.sonar_charged = False
            self.msg(t('msg_sonar_act'))
        return range_bonus

    def _check_secret_room(self, base_r: float):
        """Check for secret room double-ping detection."""
        self.ping_frame_counter += 1
        for sr in self.secret_rooms:
            if sr['entered'] or sr['revealed']: continue
            ex, ey = sr['entrance_x'], sr['entrance_y']
            dist = math.sqrt((ex-self.px)**2 + (ey-self.py)**2)
            if dist < base_r * 1.2:
                if self.last_ping_wall == (ex, ey) and \
                   self.ping_frame_counter - self.last_ping_wall_frame < 5:
                    sr['revealed'] = True
                    self.msg(_tr('secret_crack'))
                    self.screen_invert = 4
                    self.particles.extend(spawn_particles(ex+0.5, ey+0.5, 15,
                        ['\033[38;5;226m\033[1m\033[5m', '\033[38;5;201m\033[1m']))
                self.last_ping_wall = (ex, ey)
                self.last_ping_wall_frame = self.ping_frame_counter
                break

    def move(self, dx, dy):
        nx, ny = self.px+dx, self.py+dy
        if not (0<=nx<self.w and 0<=ny<self.h):
            return False

        # v5.0: Level 7 — step counter + sleeping giant
        if self.level == 7 and not self.l7_giant_awake:
            self.l7_step_counter += 1
            if self.l7_step_counter >= 50:
                self.l7_giant_awake = True
                self.msg('THE GIANT AWAKES — RUN!' if LANG=='en' else '巨兽苏醒——快跑！')
                # Emit expanding red wave from giant position
                giant = next((p for p in self.predators if p.drone_type == PredatorType.SLEEPING_GIANT), None)
                if giant:
                    for i in range(8):
                        self.waves.append(Wave(
                            ox=giant.x, oy=giant.y,
                            radius=float(i)*1.5, max_r=12.0,
                            speed=0.15,
                        ))

        # v5.0: Level 8 — FAULT drone footstep tracking
        if self.level == 8:
            for p in self.predators:
                if p.drone_type == PredatorType.FAULT and p.stunned == 0 and not p.hunting:
                    if random.random() < 0.10:  # 10% chance per step
                        p.hunting = True
                        p.hunt_x = int(self.px); p.hunt_y = int(self.py)
                        p.hunt_timer = 8  # Only 2 seconds of attention

        # Secret room entrance: revealed entrance becomes passable
        for sr in self.secret_rooms:
            if sr['revealed'] and not sr['entered']:
                if nx == sr['entrance_x'] and ny == sr['entrance_y']:
                    # Enter the secret room! Teleport to center
                    self.px, self.py = sr['center_x'], sr['center_y']
                    sr['entered'] = True
                    self.msg(_tr('secret_enter'))
                    self.freeze_frame = 4
                    self.screen_invert = 4
                    # Give reward
                    reward = sr['reward']
                    if reward == SecretReward.SUPER_CRYSTAL:
                        self.energy = min(self.max_energy, self.energy + 5)
                        self.msg(_tr('secret_super_crystal'))
                        self.particles.extend(spawn_particles(self.px+0.5, self.py+0.5, 18,
                            ['\033[38;5;226m\033[1m', '\033[38;5;228m']))
                    elif reward == SecretReward.PERMANENT_SONAR:
                        self.sonar_charged = True
                        self.msg(_tr('secret_perm_sonar'))
                        self.particles.extend(spawn_particles(self.px+0.5, self.py+0.5, 18,
                            ['\033[38;5;51m\033[1m', '\033[38;5;195m']))
                    elif reward == SecretReward.PREDATOR_REPELLER:
                        # Make all predators flee far away
                        for p in self.predators:
                            p.hunting = False
                            p.stunned = 30
                            # Move predators far from player
                            for _ in range(10):
                                dx2 = random.choice([-1,0,1])
                                dy2 = random.choice([-1,0,1])
                                pnx, pny = p.x+dx2, p.y+dy2
                                if 0<=pnx<self.w and 0<=pny<self.h and self.maze[pny][pnx]==Cell.PATH:
                                    if abs(pnx-self.px)+abs(pny-self.py) > abs(p.x-self.px)+abs(p.y-self.py):
                                        p.x, p.y = pnx, pny
                        self.msg(_tr('secret_repeller'))
                        self.particles.extend(spawn_particles(self.px+0.5, self.py+0.5, 20,
                            ['\033[38;5;46m\033[1m', '\033[38;5;82m\033[1m']))
                    self.path_this_run.append((self.px, self.py))
                    return True

        # Void Avatar fake wall detection
        if self.boss and not self.boss_defeated and self.boss.boss_type==BossType.VOID_AVATAR:
            if (nx, ny) in self.boss.fake_walls:
                # Hit a fake wall — it dissipates
                self.boss.fake_walls.remove((nx, ny))
                if (nx, ny) in self.visible:
                    del self.visible[(nx, ny)]
                self.particles.extend(spawn_particles(nx+0.5, ny+0.5, 5,
                    ['\033[38;5;201m\033[1m', '\033[38;5;213m']))
                if LANG=='zh':
                    self.msg('* 幻象之墙消散了！*')
                else:
                    self.msg('* Illusory wall dissipated! *')
                return False

        if self.maze[ny][nx] == Cell.WALL:
            # Behemoth: destroy walls by walking through them
            if self.walker_class == WalkerClass.BEHEMOTH:
                self.maze[ny][nx] = Cell.PATH
                self.visible[(nx, ny)] = 20
                self.particles.extend(spawn_particles(nx+0.5, ny+0.5, 10,
                    ['\033[38;5;226m\033[1m', '\033[38;5;208m']))
                self.msg(t('behemoth_wall_smash'))
                # Cost 0.5 energy per wall destroyed (50% chance per step)
                if random.random() < 0.5:
                    self.energy = max(0, self.energy - 1)
                # Fall through to move
            else:
                self.visible[(nx, ny)] = 16
                self.particles.append(Particle(
                    nx+0.5, ny+0.5, 0, 0.3, 5, 5, '*', self.theme.wall_fresh
                ))
                self.msg(t('msg_thud'))
                self._record('wall', (nx, ny))
                return False

        # Shadow: no footprints
        if self.walker_class != WalkerClass.SHADOW:
            self.footsteps.append((self.px, self.py, 14))
        self.px, self.py = nx, ny
        self.last_dx, self.last_dy = dx, dy  # v5.0: Track facing direction for focus pulse
        self.moves += 1
        self.combo += 1
        self.silent_steps += 1
        if self.combo > self.max_combo:
            self.max_combo = self.combo
        self.path_this_run.append((nx, ny))

        # Behemoth: every step costs 0.5 energy (50% chance of -1 per step)
        if self.walker_class == WalkerClass.BEHEMOTH and random.random() < 0.5:
            self.energy = max(0, self.energy - 1)

        # Dark water step-on effect: energy regen x3 while standing
        if (nx, ny) in self.env_elements and self.env_elements[(nx, ny)] == EnvElement.DARK_WATER:
            if random.random() < 0.06:  # ~3x normal regen rate
                self.energy = min(self.max_energy, self.energy + 1)
            self.particles.append(Particle(
                nx+0.5, ny+0.5, 0, 0.2, 6, 6,
                '~', '\033[38;5;39m'
            ))

        # Combo popup: floating text on 5+ combo
        if self.combo >= 5 and self.combo % 5 == 0:
            combo_txt = f"x{self.combo} {t('juice_combo')}!"
            self.floating_texts.append((float(nx), float(ny), combo_txt, 25))

        # Footstep particles
        if random.random() < 0.5:
            self.particles.append(Particle(
                x=nx+0.5, y=ny+0.5,
                vx=random.uniform(-0.2,0.2), vy=random.uniform(-0.2,0.2),
                life=8, max_life=8,
                char='.', color=self.theme.trail
            ))

        # Elephant Step: reveal more walls
        step_range = 2 if Ability.ELEPHANT_STEP in self.abilities else 1
        for adx in range(-step_range, step_range+1):
            for ady in range(-step_range, step_range+1):
                ax, ay = nx+adx, ny+ady
                if 0<=ax<self.w and 0<=ay<self.h and self.maze[ay][ax]==Cell.WALL:
                    cur = self.visible.get((ax, ay), 0)
                    brightness = 6 if abs(adx)+abs(ady)<=1 else 3
                    if brightness > cur:
                        self.visible[(ax, ay)] = brightness

        # Check collectibles
        for c in self.collectibles[:]:
            if c.x==nx and c.y==ny:
                self._collect(c)

        # Check memory well
        room = self.room_at(nx, ny)
        if room == Cell.MEMORY_WELL:
            # Reveal large area
            for dy in range(-5, 6):
                for dx in range(-5, 6):
                    wx, wy = nx+dx, ny+dy
                    if 0<=wx<self.w and 0<=wy<self.h and self.maze[wy][wx]==Cell.WALL:
                        self.visible[(wx, wy)] = 20
            self.msg(t('msg_mem_well'))

        # Win check — exit must be unlocked
        if self.px==self.ex and self.py==self.ey:
            if self.exit_locked:
                self.msg(t('msg_exit_locked'))
                return True  # Can stand on exit but won't win
            self.won = True
            self._record('gate', (self.ex, self.ey))
            self._calc_score()
            # Victory fireworks!
            for _ in range(40):
                self.particles.append(Particle(
                    x=self.ex+0.5, y=self.ey+0.5,
                    vx=random.uniform(-1.5,1.5), vy=random.uniform(-1.5,1.5),
                    life=random.randint(12,30), max_life=30,
                    char=random.choice(['*','+','.','·','✦','✧']),
                    color=random.choice(['\033[38;5;226m\033[1m','\033[38;5;201m\033[1m',
                            '\033[38;5;51m\033[1m','\033[38;5;46m\033[1m','\033[38;5;213m\033[1m'])
                ))

        return True

    def _collect(self, c: Collectible):
        self.collectibles.remove(c)
        self.collected_items[c.item_type] = self.collected_items.get(c.item_type, 0) + 1

        if c.item_type == ItemType.QUEST_KEY:
            self.exit_locked = False
            self.quest_complete = True
            self._record('card', (c.x, c.y))
            self.screen_invert = 12
            self.freeze_frame = 5  # Brief freeze on key pickup
            self.particles.extend(spawn_particles(c.x+0.5, c.y+0.5, 20,
                [self.theme.exit_vis, self.theme.wave_core, self.theme.accent]))
            key_name = {'zh': {'echo_stone': '回声之石', 'silence_ward': '静默护符', 'resonant_key': '共鸣之钥'},
                        'en': {'echo_stone': 'Echo Stone', 'silence_ward': 'Silence Ward', 'resonant_key': 'Resonant Key'}}
            kn = 'echo_stone' if self.chapter==1 else ('silence_ward' if self.chapter==2 else 'resonant_key')
            self.msg(f"*** {key_name[LANG][kn]} {'已找到！出口已解锁！' if LANG=='zh' else 'found! Exit unlocked!'} ***")
        elif c.item_type == ItemType.ENERGY_CRYSTAL:
            self.energy = min(self.max_energy, self.energy + 3)
            self._record('crystal', (c.x, c.y))
            self.particles.extend(spawn_particles(c.x+0.5, c.y+0.5, 10,
                [self.theme.crystal, self.theme.wave_core]))
            self.msg(t('msg_crystal'))
        elif c.item_type == ItemType.SONAR_RUNE:
            self.sonar_charged = True
            self.particles.extend(spawn_particles(c.x+0.5, c.y+0.5, 14,
                [self.theme.rune, self.theme.exit_vis]))
            self.msg(t('msg_rune'))
        elif c.item_type == ItemType.MEMORY_FRAGMENT:
            dx = self.ex - self.px
            dy = self.ey - self.py
            dist = math.sqrt(dx*dx+dy*dy)
            if dist > 0:
                self.memory_direction = (dx/dist, dy/dist)
            self.particles.extend(spawn_particles(c.x+0.5, c.y+0.5, 12,
                [self.theme.fragment, self.theme.wall_fresh]))
            self.msg(t('msg_fragment'))
        elif c.item_type == ItemType.NARRATIVE_FRAGMENT:
            # v5.0: narrative fragment — track collection
            self.fragments_collected += 1
            if self.fragments_collected >= 18:
                self.fragments_all_collected = True
            self.particles.extend(spawn_particles(c.x+0.5, c.y+0.5, 15,
                [self.theme.exit_vis, self.theme.wave_core, self.theme.accent]))
            person = getattr(c, 'person_id', '???')
            frag_num = getattr(c, 'frag_num', 0)
            self.msg(f'[RECORD] Acoustic log acquired — {person}-{frag_num:02d}' if LANG=='en' else f'[记录] 声学记录获取——{person}-{frag_num:02d}')

    def _calc_score(self):
        efficiency = max(0, 120 - self.pings*6 - self.moves//2)
        combo_bonus = self.max_combo * 5
        item_bonus = sum(self.collected_items.values()) * 50
        boss_bonus = 500 if self.boss_defeated else 0
        self.score = 1000 + efficiency*15 + combo_bonus + item_bonus + boss_bonus
        # Challenge modifier score multiplier
        multiplier = 1.0 + sum(m.value[2] for m in self.active_modifiers)
        self.score = int(self.score * multiplier)
        self.total_score += self.score

    def rating(self) -> str:
        return rating_text(self.pings)

# ═══════════════════════════════════════════════════════════════════════
# RENDERER
# ═══════════════════════════════════════════════════════════════════════

def render(g: Game) -> str:
    th = g.theme
    out = []
    sx = random.randint(-g.screen_shake, g.screen_shake) if g.screen_shake else 0

    # Invert screen on quest key collect
    inv = '\033[7m' if g.screen_invert > 3 else ''
    inv_r = '\033[27m' if g.screen_invert > 3 else ''
    # Damage flash: red background tint
    dmg = '\033[41m' if g.damage_flash > 2 else ''
    dmg_r = '\033[49m' if g.damage_flash > 2 else ''

    # ── Header bar (compact, single line) ──
    chapter_tag = f'ACT_{g.chapter}' if LANG=='zh' else f'ACT_{g.chapter}'
    char_tag = f" [{t(f'char_{g.walker_class.value}')}]" if g.walker_class else ""
    header = f"ECHO_MAZE.sys v4.0  [{th.name}]  {chapter_tag}{char_tag}"
    out.append(f"{dmg}{inv}{th.border}{'='*58}{th.border}{inv_r}{dmg_r}{R}")
    out.append(f"{dmg}{inv}{th.border} {th.accent}{header}{R}"
               f"{' '*(58-len(header))}{th.border}{inv_r}{dmg_r}{R}")
    out.append(f"{dmg}{inv}{th.border}{'='*58}{th.border}{inv_r}{dmg_r}{R}")

    # ── Stats line (compact, single row, sci-fi labels) ──

    e_ok = g.energy > 2
    e_col = th.crystal if e_ok else '\033[38;5;203m\033[1m'
    energy_str = f"{t('ui_energy')}:{e_col}{g.energy}/{g.max_energy}{R}"
    pulse_str = f"{t('ui_pings')}:{g.pings}"
    pos_str = f"{t('ui_steps')}:{g.moves}"
    res_str = f"{t('ui_score')}:{g.total_score}"
    chain_str = f"{t('ui_combo')}{g.combo}" if g.combo > 2 else ""
    chain_tag = f" {chain_str}" if chain_str else ""
    silent_tag = f" QUIET:{g.silent_steps}" if g.silent_steps > 10 else ""
    stats = f"{energy_str}  {pulse_str}  {pos_str}  {res_str}{chain_tag}{silent_tag}"
    # Strip ANSI for length calc
    vis_len = len(stats.replace('\033[38;5;51m\033[1m','').replace('\033[0m','').replace('\033[38;5;203m\033[1m',''))
    pad = 58 - vis_len
    if pad < 0: stats = stats[:56]
    out.append(f"{inv}{th.border} {stats}{' '*max(0,pad-2)}{th.border}{inv_r}{R}")
    out.append(f"{inv}{th.border}{'='*58}{th.border}{inv_r}{R}")

    # ── Maze viewport (full width, no minimap embedded) ──
    mw = 54  # Full width maze
    mh = min(15, g.h)
    mx = max(0, min(g.w-mw, g.px - mw//2 + sx))
    my = max(0, min(g.h-mh, g.py - mh//2 + sx//2))

    out.append(f"{inv}{th.border} {'[ MAP ]':^56s} {th.border}{inv_r}{R}")
    for row_y in range(my, my+mh):
        line = f"{inv}{th.border} {R}"
        for col_x in range(mx, mx+mw):
            if 0<=col_x<g.w and 0<=row_y<g.h:
                line += cell_render(g, col_x, row_y, th)
            else:
                line += ' '
        line += f"{R}{inv}{th.border}{inv_r}{R}"
        out.append(line)
    out.append(f"{inv}{th.border}{'='*58}{th.border}{inv_r}{R}")

    # ── Quest & Status line ──
    if g.quest_complete:
        qtext = t('quest_key_found')
        qline = f">> {qtext} <<"
        out.append(f"{inv}{th.border} {'\033[38;5;46m\033[1m'}{qline}{R}"
                   f"{' '*(58-len(qline))}{th.border}{inv_r}{R}")
    elif g.exit_locked:
        kn = 'quest_stone' if g.chapter==1 else ('quest_ward' if g.chapter==2 else 'quest_key')
        qline = f">> {t('quest_find_key')} [{t(kn)}] <<"
        out.append(f"{inv}{th.border} {'\033[38;5;226m\033[1m'}{qline}{R}"
                   f"{' '*(58-len(qline))}{th.border}{inv_r}{R}")

    # ── Modifier & Boss status line ──
    if g.active_modifiers or (g.boss and not g.boss_defeated):
        mod_parts = []
        if g.active_modifiers:
            mod_names = {ChallengeModifier.SILENT: 'SLNT', ChallengeModifier.HUNTED: 'HUNT',
                         ChallengeModifier.BLIND: 'BLND', ChallengeModifier.FRAGILE: 'FRAG',
                         ChallengeModifier.AMNESIA: 'AMNS', ChallengeModifier.ECHO_STORM: 'STRM'}
            mult = 1.0 + sum(m.value[2] for m in g.active_modifiers)
            mod_parts.append(f"MODS: {','.join(mod_names[m] for m in g.active_modifiers)} x{mult:.1f}")
        if g.boss and not g.boss_defeated:
            boss_name = t(f'boss_{g.boss.boss_type.value}')
            mod_parts.append(f"BOSS: {boss_name} HP:{g.boss.hp}")
        status_line = ' | '.join(mod_parts)
        out.append(f"{inv}{th.border} {'\033[38;5;203m\033[1m'}{status_line}{R}"
                   f"{' '*(58-len(status_line))}{th.border}{inv_r}{R}")

    # ── Minimap + Waveform split row ──
    mini_size = 7; mini_half = mini_size // 2
    mmap_label = 'MINIMAP' if LANG != 'zh' else chr(23567)+chr(22320)+chr(22270)
    # Minimap rows (3 rows for the mini map)
    mmap_top = g.py - mini_half
    mmap_lines = []
    for mrow in range(mini_size):
        mline = ""
        mmap_y = mmap_top + mrow
        for mcol in range(g.px - mini_half, g.px + mini_half + 1):
            mline += minimap_cell(g, mcol, mmap_y, th)
        mmap_lines.append(mline)

    # Row 1: minimap header + short waveform
    wf_short = waveform_chars(g, 18)  # Shorter waveform
    wf_slabel = f"WAVE|{wf_short}|"
    out.append(f"{inv}{th.border} {th.accent}[{mmap_label}]{R}"
               f"     {th.wave_inner}{wf_slabel}{R}"
               f"{' '*(58-10-len(wf_slabel))}{th.border}{inv_r}{R}")
    # Row 2-4: minimap content + msg
    for i in range(mini_size):
        mmap_row = mmap_lines[i] if i < len(mmap_lines) else "       "
        if i == 0 and g.msgs:
            mtxt, _ = g.msgs[-1]
            while len(mtxt) > 36: mtxt = mtxt[:36]
        elif i == 1 and g.quest_complete:
            mtxt = '\033[38;5;46m\033[1m' + t('quest_key_found') + R
        elif i == 1 and g.exit_locked:
            kn = 'quest_stone' if g.chapter==1 else ('quest_ward' if g.chapter==2 else 'quest_key')
            mtxt = '\033[38;5;226m\033[1m' + f">> {t(kn)}" + R
        else:
            mtxt = ""
        out.append(f"{inv}{th.border} {th.border} {mmap_row} {R}{R}"
                   f"  {mtxt}"
                   f"{' '*(58-16-len(mtxt.replace(chr(27)+'[','')[:2]))}{th.border}{inv_r}{R}")

    # ── Legend line ──
    boss_legend = ''
    if g.boss and not g.boss_defeated:
        if g.boss.boss_type == BossType.ECHO_MOTHER:
            boss_legend = ' &:BOSS_EM'
        elif g.boss.boss_type == BossType.SILENT_HUNTER:
            boss_legend = ' %:BOSS_SH'
        else:
            boss_legend = ' ?:BOSS_VA'
    if LANG == 'zh':
        legend = f"{chr(9678)}:你 E:出口 #:墙 {chr(9830)}:钥匙 {chr(9670)}:水晶 ~:符文 ?:碎片 %:瓦斯 *:晶簇 ≈:暗水 ∥:回音{boss_legend}"
    else:
        legend = f"{chr(9678)}:You E:Exit #:Wall {chr(9830)}:Key {chr(9670)}:Cry ~:Rune ?:Frag %:Gas *:Xtal ≈:H2O ∥:Echo{boss_legend}"
    while len(legend) > 56: legend = legend[:56]
    out.append(f"{inv}{th.border} {'\033[38;5;245m'}{legend}{R}"
               f"{' '*(58-len(legend))}{th.border}{inv_r}{R}")

    # ── Special room indicator ──
    room = g.room_at(g.px, g.py)
    if room == Cell.ECHO_CHAMBER:
        out.append(f"{inv}{th.border} {th.echo_room}{t('room_echo')}{R}"
                   f"{' '*(58-len(t('room_echo')))}{th.border}{inv_r}{R}")
    elif room == Cell.SILENT_ZONE:
        out.append(f"{inv}{th.border} {th.silent_room}{t('room_silent')}{R}"
                   f"{' '*(58-len(t('room_silent')))}{th.border}{inv_r}{R}")

    # ── Message/properties line ──
    if g.msgs:
        txt, _ = g.msgs[-1]
    else:
        txt = t('ui_hint')
    ab_str = " | ".join(ab_name(a) for a in g.abilities) if g.abilities else ""
    if ab_str: txt = f"{txt}  [{ab_str}]"
    while len(txt) > 56: txt = txt[:56]
    out.append(f"{inv}{th.border} {'\033[38;5;243m'}{txt}{R}"
               f"{' '*(58-len(txt))}{th.border}{inv_r}{R}")

    # Scanline effect
    if g.scanline > 2:
        sline = g.scanline * 10
        scan_pos = (g.py - my)  # Position scanline at player row
        # Insert a bright line in the output
        scan_row = 4 + scan_pos  # Header + stats + border = ~4 lines above map
        if 0 <= scan_row < len(out):
            out[scan_row] = out[scan_row].replace(
                f'{inv}{th.border} ',
                f'\033[38;5;195m\033[1m{chr(9552)}{R}{inv}{th.border} '
            )

    out.append(f"{inv}{th.border}{'='*58}{th.border}{inv_r}{R}")

    # ── Win overlay ──
    if g.won:
        rat = g.rating()
        out.append("")
        out.append(f"  {'\033[38;5;46m\033[1m'}+{'='*54}+{R}")
        out.append(f"  {'\033[38;5;46m\033[1m'}|{R}  {th.accent}{t('win_title'):^50s}{R}  {'\033[38;5;46m\033[1m'}|{R}")
        inf = f"{t('win_score')}:{g.score}  {t('win_rating')}:{rat}  {t('win_combo')}:{g.max_combo}"
        out.append(f"  {'\033[38;5;46m\033[1m'}|{R}  {inf}{' '*(50-len(inf))}  {'\033[38;5;46m\033[1m'}|{R}")
        items_inf = f"{t('win_items')}: {sum(g.collected_items.values())}"
        out.append(f"  {'\033[38;5;46m\033[1m'}|{R}  {items_inf}{' '*(50-len(items_inf))}  {'\033[38;5;46m\033[1m'}|{R}")
        # Modifier multiplier
        if g.active_modifiers:
            mult = 1.0 + sum(m.value[2] for m in g.active_modifiers)
            mod_inf = f"MOD x{mult:.1f}: {','.join(m.value[0] for m in g.active_modifiers)}"
            out.append(f"  {'\033[38;5;46m\033[1m'}|{R}  {'\033[38;5;226m'}{mod_inf}{R}"
                       f"{' '*(50-len(mod_inf))}  {'\033[38;5;46m\033[1m'}|{R}")
        # Boss defeated
        if g.boss_defeated:
            boss_name = t(f'boss_{g.boss.boss_type.value}')
            boss_inf = f">>> {boss_name} {'已击败!' if LANG=='zh' else 'DEFEATED!'} <<<"
            out.append(f"  {'\033[38;5;46m\033[1m'}|{R}  {'\033[38;5;201m\033[1m'}{boss_inf}{R}"
                       f"{' '*(50-len(boss_inf))}  {'\033[38;5;46m\033[1m'}|{R}")
        out.append(f"  {'\033[38;5;46m\033[1m'}|{R}  {t('win_next'):^50s}{R}  {'\033[38;5;46m\033[1m'}|{R}")
        out.append(f"  {'\033[38;5;46m\033[1m'}+{'='*54}+{R}")
        # Silent run achievement
        if g.pings <= 3 and g.moves > 10:
            out.append(f"  {'\033[38;5;226m\033[1m\033[5m'}>>> ACHIEVEMENT: SILENT_RUN <<<{R}")

    # ── Death overlay ──
    if g.is_dead:
        out.append("")
        out.append(f"  {'\033[38;5;203m\033[1m'}+{'='*54}+{R}")
        out.append(f"  {'\033[38;5;203m\033[1m'}|{R}  {'\033[38;5;196m\033[1m\033[5m'}{t('game_over'):^50s}{R}  {'\033[38;5;203m\033[1m'}|{R}")
        stats_d = f"{t('ui_pings')}:{g.pings}  {t('ui_steps')}:{g.moves}  {t('ui_score')}:{g.total_score}"
        out.append(f"  {'\033[38;5;203m\033[1m'}|{R}  {stats_d}{' '*(50-len(stats_d))}  {'\033[38;5;203m\033[1m'}|{R}")
        out.append(f"  {'\033[38;5;203m\033[1m'}|{R}  {t('replay_prompt'):^50s}{R}  {'\033[38;5;203m\033[1m'}|{R}")
        out.append(f"  {'\033[38;5;203m\033[1m'}+{'='*54}+{R}")
    # ── Win screen replay prompt ──
    elif g.won:
        # Add replay hint to existing win overlay
        out.append(f"  {'\033[38;5;243m'}[R] {t('replay_title')} | [Q] {'退出' if LANG=='zh' else 'Quit'}{R}")

    # ── Footer ──
    out.append("")
    out.append(f"  {'\033[38;5;243m\033[3m'}{t('ui_footer1')}{R}")

    return '\n'.join(out)


def render_map_only(g: Game) -> str:
    """Render ONLY the maze viewport — no stats, minimap, waveform, or legend.
    All HUD data is shown in the HTML side panels."""
    CW = 58   # Character width (borderless area = 56)
    MH = 22   # Map height (rows) — fills CRT at large font
    th = g.theme

    # Default to first theme if th is string or None
    if not isinstance(th, Theme):
        th = THEMES[0]

    out = []
    inv = ''; inv_r = ''
    if g.screen_invert > 3:
        inv = '\033[7m'; inv_r = '\033[27m'
    dmg = ''; dmg_r = ''
    if g.damage_flash > 2:
        dmg = '\033[41m'; dmg_r = '\033[49m'

    # ── Minimal header ──
    chapter_tag = f'ACT_{g.chapter}'
    header = f"ECHO_MAZE v4.0  [{th.name}]  {chapter_tag}  LVL:{g.level}"
    out.append(f"{dmg}{inv}{th.border}{'='*CW}{th.border}{inv_r}{dmg_r}{R}")
    out.append(f"{dmg}{inv}{th.border} {th.accent}{header}{R}"
               f"{' '*(CW-len(header))}{th.border}{inv_r}{dmg_r}{R}")
    out.append(f"{dmg}{inv}{th.border}{'='*CW}{th.border}{inv_r}{dmg_r}{R}")

    # ── Maze viewport ──
    mw = 54
    mh = MH
    # Shake offset
    sx = g.screen_shake if g.screen_shake else 0
    mx = max(0, min(g.w-mw, g.px - mw//2 + (1 if sx > 2 else 0)))
    my = max(0, min(g.h-mh, g.py - mh//2))

    for row_y in range(my, my+mh):
        line = f"{inv}{th.border} {R}"
        for col_x in range(mx, mx+mw):
            if 0 <= col_x < g.w and 0 <= row_y < g.h:
                line += cell_render(g, col_x, row_y, th)
            else:
                line += ' '
        line += f"{R}{inv}{th.border}{inv_r}{R}"
        out.append(line)
    out.append(f"{inv}{th.border}{'='*CW}{th.border}{inv_r}{R}")

    # ── Quest status ──
    if g.quest_complete:
        qtext = t('quest_key_found')
        qline = f">> {qtext} <<"
        out.append(f"{inv}{th.border} {'\033[38;5;46m\033[1m'}{qline}{R}"
                   f"{' '*(CW-len(qline))}{th.border}{inv_r}{R}")
    elif g.exit_locked:
        kn = 'quest_stone' if g.chapter == 1 else ('quest_ward' if g.chapter == 2 else 'quest_key')
        qline = f">> {t('quest_find_key')} [{t(kn)}] <<"
        out.append(f"{inv}{th.border} {'\033[38;5;226m\033[1m'}{qline}{R}"
                   f"{' '*(CW-len(qline))}{th.border}{inv_r}{R}")
    else:
        out.append(f"{inv}{th.border}{' '*CW}{th.border}{inv_r}{R}")

    # ── Boss status (compact) ──
    if g.boss and not g.boss_defeated:
        boss_name = t(f'boss_{g.boss.boss_type.value}')
        hp_bar = chr(9608)*g.boss.hp + chr(9617)*(3-g.boss.hp)
        bline = f"BOSS: {boss_name} [{hp_bar}]"
        out.append(f"{inv}{th.border} {'\033[38;5;203m\033[1m'}{bline}{R}"
                   f"{' '*(CW-len(bline))}{th.border}{inv_r}{R}")
    else:
        out.append(f"{inv}{th.border}{' '*CW}{th.border}{inv_r}{R}")

    out.append(f"{inv}{th.border}{'='*CW}{th.border}{inv_r}{R}")

    # ── Win overlay ──
    if g.won:
        rat = g.rating()
        out.append("")
        out.append(f"  {'\033[38;5;46m\033[1m'}+{'='*(CW-4)}+{R}")
        out.append(f"  {'\033[38;5;46m\033[1m'}|{R}  {th.accent}{t('win_title'):^50s}{R}  {'\033[38;5;46m\033[1m'}|{R}")
        inf = f"{t('win_score')}:{g.score}  {t('win_rating')}:{rat}  {t('win_combo')}:{g.max_combo}"
        out.append(f"  {'\033[38;5;46m\033[1m'}|{R}  {inf}{' '*(50-len(inf))}  {'\033[38;5;46m\033[1m'}|{R}")
        if g.boss_defeated:
            bn = t(f'boss_{g.boss.boss_type.value}')
            out.append(f"  {'\033[38;5;46m\033[1m'}|{R}  {'\033[38;5;201m\033[1m'}>>> {bn} DEFEATED! <<<{R}{' '*(30-len(bn))}  {'\033[38;5;46m\033[1m'}|{R}")
        out.append(f"  {'\033[38;5;46m\033[1m'}|{R}  {t('win_next'):^50s}{R}  {'\033[38;5;46m\033[1m'}|{R}")
        out.append(f"  {'\033[38;5;46m\033[1m'}+{'='*(CW-4)}+{R}")
        # Silent run
        if g.pings <= 3 and g.moves > 10:
            out.append(f"  {'\033[38;5;226m\033[1m\033[5m'}>>> ACHIEVEMENT: SILENT_RUN <<<{R}")

    # ── Death overlay ──
    if g.is_dead:
        out.append("")
        out.append(f"  {'\033[38;5;203m\033[1m'}+{'='*(CW-4)}+{R}")
        out.append(f"  {'\033[38;5;203m\033[1m'}|{R}  {'\033[38;5;196m\033[1m\033[5m'}{t('game_over'):^50s}{R}  {'\033[38;5;203m\033[1m'}|{R}")
        stats_d = f"{t('ui_pings')}:{g.pings}  {t('ui_steps')}:{g.moves}  {t('ui_score')}:{g.total_score}"
        out.append(f"  {'\033[38;5;203m\033[1m'}|{R}  {stats_d}{' '*(50-len(stats_d))}  {'\033[38;5;203m\033[1m'}|{R}")
        out.append(f"  {'\033[38;5;203m\033[1m'}|{R}  {t('replay_prompt'):^50s}{R}  {'\033[38;5;203m\033[1m'}|{R}")
        out.append(f"  {'\033[38;5;203m\033[1m'}+{'='*(CW-4)}+{R}")
    elif g.won:
        out.append(f"  {'\033[38;5;243m'}[R] Replay | [Q] Quit{R}")

    return '\n'.join(out)


def help_screen(g: Game):
    """Knowledge base — explains all game concepts. Bilingual."""
    cls()
    th = g.theme
    items = [
        (t('help_nav'), [
            (chr(9678), t('help_you')),
            ('E', t('help_exit')),
            (chr(216), t('help_locked')),
            ('#', t('help_wall')),
            (' ', t('help_path')),
        ]),
        (t('help_items'), [
            (chr(9830), t('help_key')),
            (chr(9670), t('help_crystal')),
            ('~', t('help_rune')),
            ('?', t('help_frag')),
        ]),
        (t('help_rooms'), [
            (chr(9830), t('help_echo')),
            ('x', t('help_silent')),
            (chr(9674), t('help_well')),
        ]),
        (t('help_preds'), [
            ('~', t('help_wander')),
            ('!', t('help_hunt')),
            ('.', t('help_stun')),
        ]),
        (t('help_abils'), [
            ('BAT', t('help_bat')),
            ('ELE', t('help_ele')),
            ('DOL', t('help_dol')),
            ('OWL', t('help_owl')),
        ]),
        (t('help_score'), [
            ('SLNT', t('help_chain')),
            ('S-D', t('help_grade')),
            ('ACHV', t('help_achv')),
        ]),
        (t('mod_title'), [
            ('SLNT', t('mod_silent_desc')),
            ('HUNT', t('mod_hunted_desc')),
            ('BLND', t('mod_blind_desc')),
            ('FRAG', t('mod_fragile_desc')),
            ('AMNS', t('mod_amnesia_desc')),
            ('STRM', t('mod_storm_desc')),
        ]),
        ('BOSS', [
            ('& EM', t('boss_echo_desc')),
            ('% SH', t('boss_silent_desc')),
            ('? VA', t('boss_void_desc')),
        ]),
        ('ENV', [
            ('%', t('env_gas_desc')),
            ('*', t('env_crystal_desc')),
            ('≈', t('env_water_desc')),
            ('∥', t('env_echo_wall_desc')),
        ]),
        ('SECRET', [
            ('≈', ('连续ping同一墙壁2次揭示入口' if LANG=='zh' else 'Ping same wall 2x rapidly to reveal')),
        ]),
        ('CHAR', [
            (t('char_prophet'), t('char_prophet_desc')),
            (t('char_ghost'), t('char_ghost_desc')),
            (t('char_behemoth'), t('char_behemoth_desc')),
            (t('char_singer'), t('char_singer_desc')),
            (t('char_shadow'), t('char_shadow_desc')),
            (t('char_resonator'), t('char_resonator_desc')),
        ]),
    ]

    print(f"{th.border}+{'='*58}+{R}")
    title_h = f"ECHO MAZE — {t('help_title')}"
    print(f"{th.border}|{R}  {th.title}{title_h:^54s}{R}  {th.border}|{R}")
    print(f"{th.border}+{'='*58}+{R}")
    for section, entries in items:
        print(f"{th.border}|{R}  {th.accent}[{section}]{R}")
        for icon, desc in entries:
            print(f"{th.border}|{R}    {th.wall_fresh}{icon}{R}  {D}{desc}{R}")
    print(f"{th.border}+{'='*58}+{R}")
    print(f"\n  {th.wave_inner}{t('help_press')}{R}")

    while True:
        k = get_key()
        if k: break
        time.sleep(0.05)
    cls()


def minimap_cell(g: Game, x: int, y: int, th: Theme) -> str:
    """Render one cell of the sonar minimap (7x7 around player)."""
    if not (0<=x<g.w and 0<=y<g.h):
        return ' '
    # Player — blinking cursor dot on minimap (Shadow: invisible on minimap too)
    if x==g.px and y==g.py:
        if g.walker_class == WalkerClass.SHADOW:
            return ' '  # Shadow can't see self on minimap either
        return '\033[38;5;255m\033[1m'+chr(9670)+R  # ◆ bright diamond (different from main view)
    # Exit (BLIND modifier hides exit on minimap too)
    if x==g.ex and y==g.ey:
        if ChallengeModifier.BLIND not in g.active_modifiers and g.exit_visible:
            return '\033[38;5;226m\033[1mE'+R if not g.exit_locked else '\033[38;5;203mX'+R
        return ' '
    # Boss on minimap
    if g.boss and not g.boss_defeated and g.boss.x==x and g.boss.y==y:
        return '\033[38;5;196m\033[1m!'+R
    # Quest key
    for c in g.collectibles:
        if c.x==x and c.y==y and c.item_type==ItemType.QUEST_KEY:
            return '\033[38;5;226m\033[1m!'+R
    # Currently visible walls
    if (x,y) in g.visible and g.visible[(x,y)] > 5:
        return th.wall_fresh+'#'+R
    # Explored walls (persistent memory)
    if (x,y) in g.explored and g.explored[(x,y)] > 1:
        return th.wall_ghost+'·'+R
    # Explored empty space
    if (x,y) in g.explored:
        return ' '
    return ' '  # Unexplored


def waveform_chars(g: Game, width: int = 36) -> str:
    """Generate an ASCII waveform visualization."""
    w = width
    chars = []
    amp = g.wave_amp
    for i in range(w):
        t = i / w * 4 * math.pi
        # Base noise + ping spike
        val = math.sin(t * 2.3 + time.time() * 2) * 0.15
        if amp > 0.05:
            # Add damped wave from ping
            val += amp * math.sin(t * 8 - time.time() * 12) * math.exp(-t*0.3)
        # Nearby wall detection adds micro-spikes
        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            wx, wy = g.px+dx, g.py+dy
            if 0<=wx<g.w and 0<=wy<g.h and g.maze[wy][wx]==Cell.WALL:
                val += 0.12 * math.sin(t * 5 + i*0.5)
                break
        val = max(-1, min(1, val))
        # Map to char
        if val > 0.6: c = chr(9608)  # █
        elif val > 0.3: c = chr(9619)  # ▓
        elif val > 0.1: c = chr(9618)  # ▒
        elif val > -0.1: c = chr(9617)  # ░
        elif val > -0.4: c = '_'
        else: c = ' '
        chars.append(c)
    return ''.join(chars)


def cell_render(g: Game, x: int, y: int, th: Theme) -> str:
    # Player — echo ring (thematic!)
    # Shadow: cannot see own position (only shows on ping flash)
    if x==g.px and y==g.py:
        if g.walker_class == WalkerClass.SHADOW:
            if g.ping_flash > 0:
                return th.ping_flash+'?'+R  # Only visible during ping flash
            return ' '  # Invisible otherwise!
        if g.ping_flash>0: return th.ping_flash+chr(9678)+R  # ◉
        return th.player+chr(9678)+R  # ◎

    # Exit — locked or unlocked (BLIND modifier hides exit marker)
    if x==g.ex and y==g.ey:
        if ChallengeModifier.BLIND in g.active_modifiers:
            return ' '  # BLIND: exit is completely hidden
        if g.exit_visible:
            if g.exit_locked:
                return '\033[38;5;203m\033[1m'+chr(216)+R  # Locked: red Ø
            return th.exit_vis+'E'+R  # Unlocked: glowing E
        return ' '

    # Collectibles
    for c in g.collectibles:
        if c.x==x and c.y==y:
            glow = '\033[5m' if c.glow>5 else ''
            if c.item_type==ItemType.QUEST_KEY:       return '\033[38;5;226m\033[1m'+glow+chr(9830)+R  # ♪ quest key
            if c.item_type==ItemType.ENERGY_CRYSTAL: return th.crystal+glow+chr(9670)+R  # ◆
            if c.item_type==ItemType.SONAR_RUNE: return th.rune+glow+'~'+R      # wave
            if c.item_type==ItemType.MEMORY_FRAGMENT: return th.fragment+glow+'?'+R

    # Secret room entrance (revealed crack)
    for sr in g.secret_rooms:
        if sr['revealed'] and not sr['entered']:
            if x==sr['entrance_x'] and y==sr['entrance_y']:
                return '\033[38;5;226m\033[1m\033[5m≈\033[0m' + R  # Glowing crack
        if sr['entered'] and (x,y) in sr.get('room_cells', []):
            # Show reward in the center of the room
            if x==sr['center_x'] and y==sr['center_y']:
                if sr['reward'] == SecretReward.SUPER_CRYSTAL:
                    return '\033[38;5;226m\033[1m◆' + R
                elif sr['reward'] == SecretReward.PERMANENT_SONAR:
                    return '\033[38;5;51m\033[1m~' + R
                else:
                    return '\033[38;5;46m\033[1m●' + R

    # Environment elements
    if (x,y) in g.env_elements:
        elem = g.env_elements[(x,y)]
        if elem == EnvElement.GAS_CLOUD:
            return '\033[38;5;154m%' + R  # Pale green %
        elif elem == EnvElement.CRYSTAL_CLUSTER:
            return '\033[38;5;225m\033[1m*' + R  # Bright sparkle
        elif elem == EnvElement.DARK_WATER:
            return '\033[38;5;39m≈' + R  # Blue ≈
        elif elem == EnvElement.ECHO_WALL:
            return '\033[38;5;255m\033[1m∥' + R  # Bright ∥

    # Special room markers
    for rx, ry, rt in g.special_rooms:
        if x==rx and y==ry:
            if rt==Cell.ECHO_CHAMBER: return th.echo_room+chr(9830)+R    # ♪
            if rt==Cell.SILENT_ZONE: return th.silent_room+chr(215)+R    # ×
            if rt==Cell.MEMORY_WELL: return th.memory_room+chr(9674)+R   # ◊

    # Footprints + ghost trail
    for fx, fy, t in g.footsteps:
        if fx==x and fy==y: return th.trail+'.'+R

    # Echo ghost (previous run path)
    for gx, gy in g.previous_path:
        if gx==x and gy==y:
            return th.ghost+'.'+R

    # Boss (rendered before regular predators, takes priority)
    if g.boss and not g.boss_defeated:
        b = g.boss
        if b.x==x and b.y==y:
            if b.stunned > 0:
                return '\033[38;5;226m\033[5m' + ('&' if b.boss_type==BossType.ECHO_MOTHER else
                       '%' if b.boss_type==BossType.SILENT_HUNTER else '?') + R
            if b.boss_type == BossType.ECHO_MOTHER:
                return '\033[38;5;201m\033[1m&' + R  # Echo Mother
            elif b.boss_type == BossType.SILENT_HUNTER:
                return '\033[38;5;130m\033[1m%' + R  # Silent Hunter
            else:
                return '\033[38;5;55m\033[1m?' + R  # Void Avatar

    # Predators
    for p in g.predators:
        if p.x==x and p.y==y:
            if p.hunting:
                return '\033[38;5;196m\033[1m\033[5m!\033[0m' + R  # Red flashing ! when hunting
            elif p.stunned>0:
                return '\033[38;5;240m·' + R  # Dim when stunned
            else:
                return '\033[38;5;203m~' + R  # Wandering: subtle red wave

    # Particles
    for p in g.particles:
        if int(p.x)==x and int(p.y)==y and p.life>3:
            alpha = int(p.life/p.max_life*255)
            return p.color+p.char+R

    # Floating texts (combo popups etc.)
    for fx, fy, txt, life in g.floating_texts:
        if int(fx)==x and int(fy)==y and life > 10:
            return '\033[38;5;226m\033[1m' + txt[:3] + R

    # Waves
    for w in g.waves:
        d = math.sqrt((x-w.ox)**2+(y-w.oy)**2)
        if abs(d-w.radius)<0.55:
            r = w.radius/max(w.max_r,0.1)
            if r<0.2: return th.wave_core+'O'+R
            elif r<0.45: return th.wave_inner+'o'+R
            elif r<0.7: return th.wave_mid+'.'+R
            else: return th.wave_outer+'·'+R

    # Visible walls
    v = g.visible.get((x,y), 0)
    if v>0:
        if v>13: return th.wall_fresh+'#'+R
        elif v>7: return th.wall_fade+'#'+R
        elif v>3: return th.wall_dim+':'+R
        else: return th.wall_ghost+'·'+R

    # Hidden wall
    if g.maze[y][x]==Cell.WALL: return ' '

    # Open path
    return ' '

# ═══════════════════════════════════════════════════════════════════════
# LEVEL FACTORY
# ═══════════════════════════════════════════════════════════════════════

def show_story(lvl: int) -> bool:
    """Show story screen between acts. Returns False if skipped."""
    act = None
    if lvl == 1: act = 'act1'
    elif lvl == 4: act = 'act2'
    elif lvl == 7: act = 'act3'
    elif lvl >= 10: act = 'act_final'
    else: return True

    th = THEMES[0]
    cls()
    title_key = f'{act}_title'
    body_key = f'{act}_body'

    print(f"""
{th.border}+{'='*58}+{R}
{th.border}|{R}  {th.title}{t(title_key):^54s}{R}  {th.border}|{R}
{th.border}+{'='*58}+{R}
""")
    for line in t(body_key).split('\n'):
        print(f"{th.border} |{R}  {line:<52s}  {th.border} |{R}")
    print(f"{th.border}+{'='*58}+{R}")
    print(f"\n  {th.wave_inner}{t('story_press')}     {D}{t('story_skip')}{R}")

    while True:
        k = get_key()
        if k in (' ', '\r', '\n'): return True
        if k == 'q': return True
        time.sleep(0.04)


def make_level(lvl, total_score, theme_idx, abilities, prev_path, map_scale=0,
               active_modifiers=None, total_clears=0, upcoming_map_reveal=False,
               walker_class=None):
    # Map sizes — 4 tiers + bonus from level
    size_tiers = [
        [(21,13),(25,15),(29,17),(33,19),(37,21),(41,23),(45,25)],  # Small
        [(27,17),(31,19),(35,21),(39,23),(43,25),(47,27),(51,29)],  # Medium
        [(33,21),(37,23),(41,25),(45,27),(49,29),(53,31),(57,33)],  # Large
        [(39,25),(43,27),(47,29),(51,31),(55,33),(59,35),(63,37)],  # Huge
    ]
    sizes = size_tiers[min(map_scale, len(size_tiers)-1)]
    w, h = sizes[min(lvl-1, len(sizes)-1)]

    maze = generate_maze(w, h)
    rooms = carve_special_rooms(maze, min(3, 1+lvl//2))

    px=py=1
    while maze[py][px]!=Cell.PATH:
        px+=2
        if px>=w-1: px=1; py+=2

    ex, ey = find_farthest(maze, (px, py))

    energy = 6+lvl*2
    # Character trait: Prophet has -2 max energy
    if walker_class == WalkerClass.PROPHET:
        energy = max(3, energy - 2)
    th = THEMES[theme_idx % len(THEMES)]

    vis = {}
    vis_range = 4 if walker_class == WalkerClass.PROPHET else 2  # Prophet: +3 range
    for dy in range(-vis_range, vis_range+1):
        for dx in range(-vis_range, vis_range+1):
            wx, wy = px+dx, py+dy
            if 0<=wx<w and 0<=wy<h and maze[wy][wx]==Cell.WALL:
                vis[(wx, wy)] = 8

    # Determine chapter/act
    chapter = 1
    if lvl >= 7: chapter = 3
    elif lvl >= 4: chapter = 2

    # ── Place QUEST KEY (one per level) ──
    # Put the quest key somewhere between start and exit, but not too close
    quest_key = None
    open_cells = [(x,y) for y in range(1,h-1) for x in range(1,w-1)
                  if maze[y][x]==Cell.PATH and (x,y)!=(px,py) and (x,y)!=(ex,ey)]
    random.shuffle(open_cells)
    # Pick a cell roughly halfway between start and exit
    mid_dist = math.sqrt((ex-px)**2 + (ey-py)**2) / 2
    for cx, cy in open_cells:
        d_start = math.sqrt((cx-px)**2 + (cy-py)**2)
        if abs(d_start - mid_dist) < mid_dist * 0.6:
            quest_key = Collectible(x=cx, y=cy, item_type=ItemType.QUEST_KEY, glow=10)
            break
    if not quest_key and open_cells:
        quest_key = Collectible(x=open_cells[0][0], y=open_cells[0][1],
                                item_type=ItemType.QUEST_KEY, glow=10)

    # Place regular collectibles
    collectibles = [quest_key] if quest_key else []
    dead_ends = find_dead_ends(maze)
    random.shuffle(dead_ends)
    item_types = [ItemType.ENERGY_CRYSTAL, ItemType.SONAR_RUNE, ItemType.MEMORY_FRAGMENT]
    for i, (dex, dey) in enumerate(dead_ends[:min(6, len(dead_ends))]):
        if (dex, dey)!=(px, py) and (dex, dey)!=(ex, ey):
            if quest_key and dex==quest_key.x and dey==quest_key.y: continue
            collectibles.append(Collectible(
                x=dex, y=dey,
                item_type=random.choice(item_types)
            ))

    # ── Place secret rooms (0-2 per level) ──
    secret_rooms = []
    num_secret = random.choices([0, 1, 2], weights=[3, 4, 3])[0]  # 30%/40%/30%
    if num_secret > 0:
        # Find dead-end walls (walls with exactly 1 adjacent path)
        dead_walls = []
        for y in range(2, h-2):
            for x in range(2, w-2):
                if maze[y][x] == Cell.WALL:
                    path_neighbors = sum(1 for dx,dy in [(0,1),(0,-1),(1,0),(-1,0)]
                                        if 0<=x+dx<w and 0<=y+dy<h and maze[y+dy][x+dx]==Cell.PATH)
                    if path_neighbors == 1:
                        # Check there's space behind to carve
                        behind_x, behind_y = x, y
                        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                            nx, ny = x+dx, y+dy
                            if 0<=nx<w and 0<=ny<h and maze[ny][nx]==Cell.PATH:
                                behind_x, behind_y = x-dx, y-dy  # Opposite direction
                                break
                        if 3<=behind_x<w-3 and 3<=behind_y<h-3:
                            dead_walls.append((x, y, behind_x, behind_y))
        random.shuffle(dead_walls)
        rewards = [SecretReward.SUPER_CRYSTAL, SecretReward.PERMANENT_SONAR, SecretReward.PREDATOR_REPELLER]
        for i in range(min(num_secret, len(dead_walls))):
            wx, wy, bx, by = dead_walls[i]
            # Carve a 3x3 room behind the wall
            room_cells = []
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    cx, cy = bx+dx, by+dy
                    if 2<=cx<w-2 and 2<=cy<h-2:
                        maze[cy][cx] = Cell.PATH
                        room_cells.append((cx, cy))
            # Mark the entrance in maze (use a special marker)
            # We'll track it via secret_rooms data
            reward = rewards[i % len(rewards)]
            secret_rooms.append({
                'entrance_x': wx, 'entrance_y': wy,
                'center_x': bx, 'center_y': by,
                'reward': reward,
                'revealed': False,
                'entered': False,
                'room_cells': room_cells,
            })

    # ── Place environmental elements ──
    env_elements = {}
    env_cells = [(x,y) for y in range(2,h-2) for x in range(2,w-2)
                 if maze[y][x]==Cell.PATH and (x,y)!=(px,py) and (x,y)!=(ex,ey)
                 and not (quest_key and x==quest_key.x and y==quest_key.y)]
    random.shuffle(env_cells)
    num_env = min(2 + lvl//2 + map_scale, len(env_cells))
    env_types = [EnvElement.GAS_CLOUD, EnvElement.CRYSTAL_CLUSTER,
                 EnvElement.DARK_WATER, EnvElement.ECHO_WALL]
    for i in range(num_env):
        if i >= len(env_cells): break
        ex, ey = env_cells[i]
        elem = env_types[i % len(env_types)] if i < 4 else random.choice(env_types)
        env_elements[(ex, ey)] = elem

    # v5.0: Predator spawning per level design
    # Level 1: no drones (tutorial)
    # Level 2: 1 patrol drone
    # Level 3: 2 patrol drones + boss
    # Level 4: 2 patrol drones
    # Level 5: 1 patrol drone (minimal — focus on relay mechanic)
    # Level 6: 4 patrol drones + boss
    # Level 7: 0 normal drones, 1 SLEEPING_GIANT
    # Level 8: 3 FAULT drones
    # Level 9: 0 normal drones + boss
    # Level 10: no enemies (ending)
    predator_counts = {1:0, 2:1, 3:2, 4:2, 5:1, 6:4, 7:0, 8:0, 9:0, 10:0}
    num_predators = predator_counts.get(lvl, 0)
    # Level 8: FAULT drones
    fault_count = 3 if lvl == 8 else 0
    # Level 7: sleeping giant
    has_giant = (lvl == 7)

    if active_modifiers and ChallengeModifier.HUNTED in active_modifiers:
        num_predators = max(num_predators, 1) * 3
        fault_count = fault_count * 3

    predators = []
    pred_cells = [(x,y) for y in range(1,h-1) for x in range(1,w-1)
                  if maze[y][x]==Cell.PATH and (x,y)!=(px,py) and (x,y)!=(ex,ey)
                  and not (quest_key and x==quest_key.x and y==quest_key.y)]
    random.shuffle(pred_cells)

    for i in range(min(num_predators, len(pred_cells))):
        pred_x, pred_y = pred_cells[i]
        predators.append(Predator(
            x=pred_x, y=pred_y,
            wander_timer=random.randint(10, 30),
            drone_type=PredatorType.PATROL,
        ))

    # Level 8: FAULT drones
    for i in range(min(fault_count, len(pred_cells) - num_predators)):
        idx = num_predators + i
        if idx < len(pred_cells):
            pred_x, pred_y = pred_cells[idx]
            predators.append(Predator(
                x=pred_x, y=pred_y,
                wander_timer=random.randint(8, 20),
                drone_type=PredatorType.FAULT,
            ))

    # Level 7: Sleeping giant in room center
    if has_giant:
        center_x, center_y = w // 2, h // 2
        # Find nearest path cell to center
        best = None
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                cx, cy = center_x+dx, center_y+dy
                if 0<=cx<w and 0<=cy<h and maze[cy][cx]==Cell.PATH:
                    if best is None or abs(cx-center_x)+abs(cy-center_y) < abs(best[0]-center_x)+abs(best[1]-center_y):
                        best = (cx, cy)
        if best:
            gx, gy = best
            # Carve a small room for the giant
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    cx2, cy2 = gx+dx, gy+dy
                    if 0<=cx2<w and 0<=cy2<h:
                        maze[cy2][cx2] = Cell.PATH
            predators.append(Predator(
                x=gx, y=gy,
                drone_type=PredatorType.SLEEPING_GIANT,
                invulnerable_to_focus=True,
            ))

    # ── Boss spawning (v5.0: only at levels 3, 6, 9) ──
    boss = None
    if lvl in (3, 6, 9):
        boss_map = {3: BossType.ECHO_MOTHER, 6: BossType.SILENT_HUNTER, 9: BossType.VOID_AVATAR}
        boss_type = boss_map[lvl]
        boss_cells = [(x,y) for y in range(1,h-1) for x in range(1,w-1)
                      if maze[y][x]==Cell.PATH and (x,y)!=(px,py) and (x,y)!=(ex,ey)
                      and abs(x-px)+abs(y-py) > w//3]
        if boss_cells:
            bx, by = random.choice(boss_cells)
            boss = Boss(boss_type=boss_type, x=bx, y=by, shields=3, max_shields=3)
            # Initialize Void Avatar anchors
            if boss_type == BossType.VOID_AVATAR:
                for _ in range(3):
                    for __ in range(20):
                        ax = bx + random.randint(-6, 6)
                        ay = by + random.randint(-5, 5)
                        if 0<=ax<w and 0<=ay<h and maze[ay][ax]==Cell.PATH \
                           and (ax,ay)!=(px,py) and (ax,ay) not in boss.anchors:
                            boss.anchors.append((ax, ay)); break

    g = Game(
        maze=maze, w=w, h=h,
        px=px, py=py, ex=ex, ey=ey,
        theme=th,
        energy=energy, max_energy=energy,
        level=lvl, total_score=total_score,
        visible=vis, special_rooms=rooms,
        collectibles=collectibles,
        abilities=abilities,
        previous_path=prev_path,
        predators=predators,
        chapter=chapter,
        exit_locked=True,
        active_modifiers=active_modifiers or set(),
        total_clears=total_clears,
        boss=boss,
        env_elements=env_elements,
        secret_rooms=secret_rooms,
        walker_class=walker_class,
        last_pos=(px, py),
    )
    # Apply upcoming_map_reveal from previous boss kill
    if upcoming_map_reveal:
        # Reveal entire map
        for wy in range(g.h):
            for wx in range(g.w):
                if g.maze[wy][wx] == Cell.WALL:
                    g.visible[(wx, wy)] = 20
        g.upcoming_map_reveal = False
        g.msg(t('boss_drop_map'))

    g.msg(f"{t('ui_level')}{lvl} {th.name} {t('msg_lvl_start')}")
    g.msg(t('quest_find_key') if not g.quest_complete else t('quest_key_found'))
    # Boss alert message
    if boss:
        boss_name = t(f'boss_{boss.boss_type.value}')
        g.msg(t('boss_alert').format(boss_name))
    return g, theme_idx

def find_dead_ends(maze):
    h, w = len(maze), len(maze[0])
    dead = []
    for y in range(1, h-1):
        for x in range(1, w-1):
            if maze[y][x]==Cell.PATH:
                walls_around = sum(1 for dx,dy in [(0,1),(0,-1),(1,0),(-1,0)]
                                   if maze[y+dy][x+dx]==Cell.WALL)
                if walls_around >= 3:
                    dead.append((x, y))
    return dead

# ═══════════════════════════════════════════════════════════════════════
# ABILITY SELECT SCREEN
# ═══════════════════════════════════════════════════════════════════════

def ability_select(g: Game) -> Optional[Ability]:
    """Show ability selection. Returns chosen ability."""
    available = [a for a in Ability if a not in g.abilities]
    if not available:
        return None

    th = g.theme
    cls()
    title_ab = t('ab_title')
    choose_ab = t('ab_choose')
    print(f"""
{th.accent}  +{'='*58}+
  |                                                          |
  |                  {title_ab}                       |
  |            {choose_ab}                   |
  |                                                          |
  +{'='*58}+{R}
""")
    for i, ab in enumerate(available):
        name = ab_name(ab)
        desc = ab_desc(ab)
        print(f"  [{i+1}] {th.crystal}{name:20s}{R} -- {desc}")

    prompt = t('ab_prompt').format(len(available))
    print(f"\n  {th.accent}{prompt}...{R}")

    while True:
        k = get_key()
        if k.isdigit():
            idx = int(k)-1
            if 0 <= idx < len(available):
                return available[idx]
        if k == 'q':
            return None
        time.sleep(0.04)

# ═══════════════════════════════════════════════════════════════════════
# TITLE SCREEN
# ═══════════════════════════════════════════════════════════════════════

def title_screen(total_clears=0):
    """Returns (difficulty, theme_idx, map_scale, modifiers, walker_class)
    or (0,0,0,set(),None) for quit, (-1,0,0,set(),None) for lang."""
    global LANG
    th = THEMES[0]
    cls()

    if LANG == 'zh':
        print(f"""
{th.accent}  +{'='*58}+
  |                                                          |
  |   {th.wave_core}{chr(9679)}{th.wave_inner}   ▄▄▄▄▄▄▄▄   ▄▄▄▄▄▄▄▄   ▄▄▄▄▄▄▄▄   ▄▄▄▄▄▄▄▄   {th.wave_core}{chr(9679)}{th.accent}    |
  |   {th.wave_core}{chr(9675)}{th.wave_inner}   █  ▄▄  █   █ ▄▄█ █   █ █▄█ █   █    █   {th.wave_core}{chr(9675)}{th.accent}    |
  |   {th.wave_core}{chr(9678)}{th.wave_inner}   █ █  █ █   █ █▄▄█▄█   █ █▄▄█   █ ▄▄ █   {th.wave_core}{chr(9678)}{th.accent}    |
  |   {th.wave_core}{chr(9675)}{th.wave_inner}   █ █▄▄█ █   █ █  █▄█   █  ▄ █   █ █ ██   {th.wave_core}{chr(9675)}{th.accent}    |
  |   {th.wave_core}{chr(9679)}{th.wave_inner}   █  ▀▀  █   █▄▄▄▄▄▄█   █▄▄▄▄█   █▄█  █   {th.wave_core}{chr(9679)}{th.accent}    |
  |   {th.wave_core}{chr(9678)}{th.wave_inner}   ▀▀▀▀▀▀▀▀   ▀▀▀▀▀▀▀▀   ▀▀▀▀▀▀▀▀   ▀▀▀▀▀▀▀▀   {th.wave_core}{chr(9678)}{th.accent}    |
  |                                                          |
  |          {th.wall_fresh}回 声 迷 宫{th.accent}     {th.wave_inner}ECHO MAZE{th.accent}                    |
  |                                                          |
  |    {R}{t('title_see'):^54s}{th.accent}  |
  |    {D}{t('title_fire'):^54s}{th.accent}  |
  |                                                          |
  +{'='*58}+{R}
""")
    else:
        print(f"""
{th.accent}  +{'='*58}+
  |                                                          |
  |     {th.title}______  _____  _   _  _____                  {th.accent}        |
  |     {th.title}|  ___|/  __ \\| | | ||  __ \\                 {th.accent}       |
  |     {th.crystal}| |__  | /  \\/| |_| || |  \\/  ______  ______ {th.accent}      |
  |     {th.crystal}|  __| | |    |  _  || | __  |______||______|{th.accent}      |
  |     {th.wave_inner}| |___ | \\__/\\| | | || |_\\ \\                 {th.accent}       |
  |     {th.wave_inner}|____/  \\____/\\_| |_/ \\____/                 {th.accent}       |
  |                                                          |
  |     {th.wall_fresh}__  __  ___ ______  ___ _____ ______ ______{th.accent}         |
  |     {th.wall_fresh}|  \\/  |/ _ \\| ___ \\|_  /|  ___||___  /{th.accent}          |
  |     {th.wall_fade}| .  . |/ /_\\ \\ |_/ / / / | |__     / /{th.accent}           |
  |     {th.wall_fade}| |\\/| ||  _  ||    / / /  |  __|   / /{th.accent}            |
  |     {th.wall_dim}| |  | || | | || |\\ \\/ /___| |____./ /___ {th.accent}        |
  |     {th.wall_dim}\\_|  |_/\\_| |_/\\_| \\_\\____/\\____/\\_____/{th.accent}       |
  |                                                          |
  |    {R}{t('title_see'):58s}{th.accent}  |
  |  {D}{t('title_fire'):58s}{th.accent}    |
  |                                                          |
  +{'='*58}+{R}
""")

    theme_labels_zh = ["ocean.sys", "volcano.sys", "forest.sys", "crystal.sys", "sunset.sys", "void.sys"]
    theme_labels_en = ["ocean.sys", "volcano.sys", "forest.sys", "crystal.sys", "sunset.sys", "void.sys"]
    map_labels_zh = ["小型", "中型", "大型", "巨型"]
    map_labels_en = ["Small", "Medium", "Large", "Huge"]

    print(f"  {th.accent}+--- {t('title_diff')} ---+{R}")
    print(f"  {th.accent}|{R} [1] {t('title_easy'):44s}{th.accent}|{R}")
    print(f"  {th.accent}|{R} [2] {t('title_norm'):44s}{th.accent}|{R}")
    print(f"  {th.accent}|{R} [3] {t('title_hard'):44s}{th.accent}|{R}")
    print(f"  {th.accent}+{'-'*49}+{R}")
    print()
    print(f"  {th.accent}+--- {t('map_size')} ---+{R}")
    for i in range(4):
        ml = map_labels_zh[i] if LANG=='zh' else map_labels_en[i]
        sz = ['21x13','27x17','33x21','39x25'][i]
        print(f"  {th.accent}|{R} [{i+6}] {ml:8s} ({sz}){' '*(49-18)}{th.accent}|{R}")
    print(f"  {th.accent}+{'-'*49}+{R}")
    print()
    print(f"  {th.accent}+--- {'主题 Theme' if LANG=='zh' else 'Theme'} ---+{R}")
    for i, thm in enumerate(THEMES):
        label = theme_labels_zh[i] if LANG=='zh' else theme_labels_en[i]
        swatch = f"{thm.wave_core}███{thm.wave_inner}███{thm.accent}███{R}"
        name_colored = f"{thm.accent}{label}{R}"
        print(f"  {th.accent}|{R} [{chr(ord('a')+i)}] {swatch} {name_colored}"
              f"{' '*(49-22-len(label))}{th.accent}|{R}")
    print(f"  {th.accent}+{'-'*49}+{R}")

    # Daily challenge option
    if LANG == 'zh':
        daily_line = f"  {th.accent}|{R} [D] {'每日挑战':16s} -- 日期种子 | 固定难度 | 本地排行{' '*(49-44)}{th.accent}|{R}"
    else:
        daily_line = f"  {th.accent}|{R} [D] {'Daily Challenge':16s} -- Date seed | Fixed diff | Local LB{' '*(49-47)}{th.accent}|{R}"
    print(f"\n  {th.accent}+--- {'DAILY' if LANG != 'zh' else '每日'} ---+{R}")
    print(daily_line)
    print(f"  {th.accent}+{'-'*49}+{R}")

    print(f"\n  {D}{t('title_pick')}{R}")

    difficulty = 1; theme_idx = 0; map_scale = 1
    diff_names_zh = ['EASY_MODE', 'STD_MODE', 'HARD_MODE']
    diff_names_en = ['EASY_MODE', 'STD_MODE', 'HARD_MODE']
    need_redraw = False

    while True:
        if need_redraw:
            # Show current selections
            dn = diff_names_zh[difficulty-1] if LANG=='zh' else diff_names_en[difficulty-1]
            ml = map_labels_zh[map_scale] if LANG=='zh' else map_labels_en[map_scale]
            tl = theme_labels_zh[theme_idx]
            status_line = f"  >>> DIFF:{dn}  MAP:{ml}  THEME:{tl}  [ENTER to start] <<<"
            sys.stdout.write(f"\033[2K\r{th.accent}{status_line}{R}")
            sys.stdout.flush()
            need_redraw = False

        k = get_key()
        if k in ('1','2','3'):
            difficulty = int(k); need_redraw = True
        elif k in ('4','5','6','7'):
            map_scale = int(k) - 4; need_redraw = True
        elif k in ('a','b','c','d','e','f'):
            idx = ord(k) - ord('a')
            if idx < len(THEMES): theme_idx = idx; need_redraw = True
        elif k in ('\r','\n',' '):
            # Show character selection
            walker = _character_select_screen()
            if walker is None:  # User skipped
                walker = None
            # Show modifier selection if unlocked
            modifiers = set()
            if total_clears > 0:
                modifiers = _modifier_select_screen(total_clears)
                if modifiers is None:  # User backed out
                    need_redraw = True
                    continue
            return (difficulty, theme_idx, map_scale, modifiers, walker)
        elif k == 'l':
            LANG = 'en' if LANG == 'zh' else 'zh'
            return (-1, 0, 0, set(), None)
        elif k == 'd':
            # Daily challenge mode
            return (-2, 0, 0, set(), None)
        elif k == 'q':
            return (0, 0, 0, set(), None)
        time.sleep(0.04)

def _character_select_screen() -> Optional[WalkerClass]:
    """Show character selection screen. Returns chosen character or None for default."""
    global LANG
    th = THEMES[0]
    unlocks = load_unlocks()
    chars = list(WalkerClass)
    selected = None
    need_redraw = True

    while True:
        if need_redraw:
            cls()
            print(f"""
{th.accent}  +{'='*58}+
  |                                                          |
  |     {th.wall_fresh}{t('char_title'):^54s}{th.accent}                        |
  +{'='*58}+{R}
""")
            for i, char in enumerate(chars):
                unlocked = is_char_unlocked(char, unlocks)
                letter = str(i+1)
                name = t(f'char_{char.value}')
                desc = t(f'char_{char.value}_desc')
                if unlocked:
                    mark = ' '
                    colored_name = f"{th.wave_core}{name}{R}"
                    colored_desc = f"{D}{desc}{R}"
                else:
                    mark = '\033[38;5;203m🔒\033[0m'
                    colored_name = f"\033[38;5;240m{name}{R}"
                    colored_desc = f"\033[38;5;240m{desc}{R}"
                selected_marker = ' \033[38;5;46m◀\033[0m' if selected == char else '  '
                print(f"  {th.accent}|{R} [{letter}] {mark} {colored_name}{selected_marker}"
                      f"{' '*(40-len(name))}{th.accent}|{R}")
                print(f"  {th.accent}|{R}     {colored_desc}"
                      f"{' '*(50-len(desc))}{th.accent}|{R}")

            # Show current selection
            if selected:
                sel_name = t(f'char_{selected.value}')
                print(f"\n  {th.accent}>>> {t('char_title')}: {th.crystal}{sel_name}{R} {th.accent}<<<{R}")
            print(f"\n  {D}{t('char_prompt')}{R}")
            need_redraw = False

        k = get_key()
        if k in ('\r', '\n', ' '):
            return selected  # None = default (Prophet)
        elif k in ('1','2','3','4','5','6'):
            idx = int(k)-1
            if idx < len(chars):
                char = chars[idx]
                if is_char_unlocked(char, unlocks):
                    selected = char if selected != char else None
                    need_redraw = True
        elif k == 'q':
            return None
        time.sleep(0.04)


def _modifier_select_screen(total_clears: int) -> Optional[Set[ChallengeModifier]]:
    """Show modifier selection screen. Returns set of selected modifiers, or None to go back."""
    global LANG
    th = THEMES[0]
    modifiers = list(ChallengeModifier)
    selected = set()
    need_redraw = True

    while True:
        if need_redraw:
            cls()
            print(f"""
{th.accent}  +{'='*58}+
  |                                                          |
  |     {th.wall_fresh}{t('mod_title'):^54s}{th.accent}                        |
  |     {D}{t('mod_subtitle'):^54s}{th.accent}                        |
  |                                                          |
  +{'='*58}+{R}
""")
            print(f"  {th.accent}+--- {t('mod_title')} ---+{R}")
            for i, mod in enumerate(modifiers):
                letter = chr(ord('a')+i)
                selected_mark = '\033[38;5;46m\033[1m[✓]\033[0m' if mod in selected else '[ ]'
                bonus_pct = int(mod.value[2] * 100)
                name_zh = mod.value[0]
                bonus_str = f"+{bonus_pct}%"
                print(f"  {th.accent}|{R} [{letter}] {selected_mark} {th.wave_core}{name_zh}{R}"
                      f"  {th.accent}{bonus_str}{R}"
                      f"{' '*(49-22-len(name_zh))}{th.accent}|{R}")
            # Show none option
            none_mark = '\033[38;5;46m\033[1m[✓]\033[0m' if not selected else '[ ]'
            print(f"  {th.accent}|{R} [0] {none_mark} {th.wave_inner}{t('mod_none')}{R}"
                  f"{' '*(49-22-len(t('mod_none')))}{th.accent}|{R}")
            print(f"  {th.accent}+{'-'*49}+{R}")

            # Show total multiplier
            mult = 1.0 + sum(m.value[2] for m in selected)
            mult_str = f"{t('mod_multiplier')}: x{mult:.1f}"
            selected_names = ', '.join(m.value[0] for m in selected) if selected else t('mod_none')
            sel_str = f"{t('mod_selected')}: {selected_names}"
            print(f"  {th.accent}{mult_str} | {sel_str}{R}")
            print(f"\n  {D}{t('mod_prompt')}{R}")
            print(f"  {D}{t('mod_clears_label')}: {total_clears}{R}")

            need_redraw = False

        k = get_key()
        if k in ('\r', '\n', ' '):
            return selected
        elif k == '0':
            selected.clear()
            need_redraw = True
        elif k in ('a','b','c','d','e','f'):
            idx = ord(k)-ord('a')
            if idx < len(modifiers):
                mod = modifiers[idx]
                if mod in selected:
                    selected.discard(mod)
                else:
                    selected.add(mod)
                need_redraw = True
        elif k == 'q':
            return None  # Back to main title
        time.sleep(0.04)


# ═══════════════════════════════════════════════════════════════════════
# DAILY CHALLENGE
# ═══════════════════════════════════════════════════════════════════════

def daily_seed():
    """Generate a deterministic seed from today's date."""
    import hashlib
    today = time.strftime('%Y-%m-%d')
    h = hashlib.md5(today.encode()).hexdigest()
    return int(h[:8], 16)

def leaderboard_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'leaderboard.json')

def load_leaderboard() -> List[dict]:
    """Load leaderboard. Returns list of {date, score, pings, steps, grade}."""
    try:
        with open(leaderboard_path(), 'r', encoding='utf-8') as f:
            return __import__('json').load(f)
    except: return []

def save_leaderboard(data: List[dict]):
    try:
        with open(leaderboard_path(), 'w', encoding='utf-8') as f:
            __import__('json').dump(data, f, ensure_ascii=False, indent=2)
    except: pass

def add_daily_result(score: int, pings: int, steps: int, grade: str):
    """Add today's result to leaderboard. Keeps top 10 per day."""
    today = time.strftime('%Y-%m-%d')
    lb = load_leaderboard()
    # Remove old entry for today if exists (keep best run)
    lb = [e for e in lb if not (e.get('date')==today and e.get('score',0) >= score)]
    lb.append({'date': today, 'score': score, 'pings': pings, 'steps': steps, 'grade': grade})
    lb.sort(key=lambda x: x['score'], reverse=True)
    save_leaderboard(lb[:10])

# ═══════════════════════════════════════════════════════════════════════
# UNLOCK SYSTEM
# ═══════════════════════════════════════════════════════════════════════

def unlocks_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'unlocks.json')

def load_unlocks() -> dict:
    try:
        with open(unlocks_path(), 'r', encoding='utf-8') as f:
            return __import__('json').load(f)
    except: return {}

def save_unlocks(data: dict):
    try:
        with open(unlocks_path(), 'w', encoding='utf-8') as f:
            __import__('json').dump(data, f, ensure_ascii=False, indent=2)
    except: pass

def is_char_unlocked(char: WalkerClass, unlocks: dict) -> bool:
    """Check if a character is unlocked. v5.0: only PROPHET always unlocked."""
    if char == WalkerClass.PROPHET:
        return True  # Always unlocked (standard exoskeleton is default)
    if char == WalkerClass.GHOST:
        return True  # Always unlocked (standard exoskeleton)
    return unlocks.get(char.value, False)

def exo_name(wc: WalkerClass) -> str:
    """Get exoskeleton display name."""
    names = {
        WalkerClass.PROPHET: {'zh': '先知的遗物', 'en': "Prophet's Relic"},
        WalkerClass.GHOST: {'zh': '苏无影的外骨骼', 'en': "Su Wuying's Exoskeleton"},
        WalkerClass.BEHEMOTH: {'zh': '赵铁山的改装', 'en': "Zhao Tieshan's Mod"},
        WalkerClass.SINGER: {'zh': '陈歌的中继模式', 'en': "Chen Ge's Relay Mode"},
        WalkerClass.SHADOW: {'zh': '吴暗的装备', 'en': "Wu An's Equipment"},
        WalkerClass.RESONATOR: {'zh': '郑振的感应器', 'en': "Zheng Zhen's Sensor"},
    }
    return names.get(wc, {}).get(LANG, wc.value)

def exo_desc(wc: WalkerClass) -> str:
    """Get exoskeleton description."""
    descs = {
        WalkerClass.PROPHET: {'zh': '脉冲范围+3格 | 能量上限-2(8)', 'en': 'Scan range +3 | Max energy -2 (8)'},
        WalkerClass.GHOST: {'zh': '无人机不追踪探测脉冲 | 脉冲范围-40%', 'en': 'Drones ignore scan pulse | Range -40%'},
        WalkerClass.BEHEMOTH: {'zh': '撞碎脆墙 | 每步耗0.3能量', 'en': 'Smash brittle walls | 0.3 energy/step'},
        WalkerClass.SINGER: {'zh': '探测脉冲免费 | 范围2格 | 不能聚焦', 'en': 'Free scan pulse | Range 2 | No focus'},
        WalkerClass.SHADOW: {'zh': '移动无声 | 脉冲后自标消失3秒', 'en': 'Silent movement | Self-marker fades 3s after pulse'},
        WalkerClass.RESONATOR: {'zh': '静止3秒自动揭示5格 | 不能主动脉冲', 'en': 'Still 3s = auto-reveal 5 cells | No active pulse'},
    }
    return descs.get(wc, {}).get(LANG, '')

def _boss_distance(g: 'Game') -> int:
    """Get distance from player to boss."""
    if not g.boss or g.boss_defeated: return -1
    return int(math.sqrt((g.boss.x-g.px)**2 + (g.boss.y-g.py)**2))

def unlock_char(char: WalkerClass, unlocks: dict):
    """Unlock a character and save."""
    if char.value not in unlocks:
        unlocks[char.value] = True
        save_unlocks(unlocks)

def update_unlocks_from_game(g: 'Game', total_clears: int, bosses_defeated: int):
    """Check and unlock characters based on game achievements."""
    unlocks = load_unlocks()
    if total_clears >= 1:
        unlock_char(WalkerClass.BEHEMOTH, unlocks)
    if g.max_combo >= 10:
        unlock_char(WalkerClass.SHADOW, unlocks)
    if g.pings <= 3 and g.moves >= 10:  # S rank condition
        unlock_char(WalkerClass.SINGER, unlocks)
    if bosses_defeated >= 3:
        unlock_char(WalkerClass.RESONATOR, unlocks)

def play_replay(g: 'Game'):
    """Play back the recorded game with god-view and event annotations.
    Speed: 1=normal, 2=double, 3=triple."""
    global LANG
    if not g.replay_log:
        return

    th = g.theme
    speed = 1
    idx = 0
    last_tick = time.time()
    TICK = 1.0/15

    # Build position timeline from replay log
    # Interpolate player position between events
    events_by_frame = {}
    for frame, px, py, etype, edata in g.replay_log:
        if frame not in events_by_frame:
            events_by_frame[frame] = []
        events_by_frame[frame].append((px, py, etype, edata))

    max_frame = max(events_by_frame.keys()) if events_by_frame else 0
    last_px, last_py = g.replay_log[0][1], g.replay_log[0][2] if g.replay_log else (1,1)

    frame = 0
    event_markers = []  # (x, y, text, life)

    while True:
        # Handle input
        k = get_key()
        if k == 'q':
            break
        elif k == '1':
            speed = 1
        elif k == '2':
            speed = 2
        elif k == '3':
            speed = 3

        # Advance frame
        if time.time() - last_tick > TICK / speed:
            last_tick = time.time()
            frame += 1
            if frame > max_frame + 30:
                break  # End of replay

            # Update position from events
            if frame in events_by_frame:
                for px, py, etype, edata in events_by_frame[frame]:
                    last_px, last_py = px, py
                    # Add event marker
                    if etype == 'scan':
                        event_markers.append((px, py, t('replay_event_ping'), 20, '\033[38;5;51m\033[1m'))
                    elif etype == 'wall':
                        event_markers.append((edata[0], edata[1], t('replay_event_wall'), 18, '\033[38;5;203m'))
                    elif etype == 'drone':
                        event_markers.append((px, py, t('replay_event_pred'), 22, '\033[38;5;196m\033[1m'))
                    elif etype == 'card':
                        event_markers.append((edata[0], edata[1], t('replay_event_key'), 25, '\033[38;5;226m\033[1m'))
                    elif etype == 'crystal':
                        event_markers.append((edata[0], edata[1], t('replay_event_crystal'), 20, '\033[38;5;46m\033[1m'))
                    elif etype == 'anomaly':
                        event_markers.append((edata[0], edata[1], t('replay_event_boss'), 25, '\033[38;5;201m\033[1m'))
                    elif etype == 'gate':
                        event_markers.append((px, py, t('replay_event_exit'), 30, '\033[38;5;226m\033[1m\033[5m'))
                    elif etype == 'dead':
                        event_markers.append((px, py, t('replay_event_dead'), 35, '\033[38;5;196m\033[1m\033[5m'))

            # Age event markers
            event_markers = [(ex, ey, txt, life-1, col) for ex, ey, txt, life, col in event_markers if life > 0]

        # Render replay frame
        cls()
        sys.stdout.write('__CLS__\n')

        # Header
        speed_label = f'{speed}x'
        header = f"ECHO_MAZE.sys v4.0  REPLAY [{speed_label}]  {t('replay_controls')}"
        out = []
        out.append(f"{th.border}{'='*58}{th.border}{R}")
        out.append(f"{th.border} {th.accent}{header}{R}{' '*(58-len(header))}{th.border}{R}")
        out.append(f"{th.border}{'='*58}{th.border}{R}")

        # God-view map: show all walls
        mw = 54; mh = min(15, g.h)
        mx = max(0, min(g.w-mw, last_px - mw//2))
        my = max(0, min(g.h-mh, last_py - mh//2))

        out.append(f"{th.border} {'[ GOD VIEW ]':^56s} {th.border}{R}")
        for row_y in range(my, my+mh):
            line = f"{th.border} {R}"
            for col_x in range(mx, mx+mw):
                if not (0<=col_x<g.w and 0<=row_y<g.h):
                    line += ' '
                elif col_x==last_px and row_y==last_py:
                    line += th.player + chr(9678) + R  # Player
                elif col_x==g.ex and row_y==g.ey:
                    line += '\033[38;5;226mE' + R  # Exit
                elif g.maze[row_y][col_x] == Cell.WALL:
                    line += th.wall_fresh + '#' + R  # God view: all walls visible
                else:
                    # Check for event markers
                    marker_shown = False
                    for ex, ey, txt, life, col in event_markers:
                        if ex==col_x and ey==row_y and life > 10:
                            line += col + txt[0] + R
                            marker_shown = True
                            break
                    if not marker_shown:
                        line += ' '
            line += f"{R}{th.border}{R}"
            out.append(line)

        out.append(f"{th.border}{'='*58}{th.border}{R}")

        # Stats line
        stats = f"{t('ui_pings')}:{g.pings}  {t('ui_steps')}:{g.moves}  {t('ui_score')}:{g.total_score}  {t('win_rating')}:{g.rating()}"
        out.append(f"{th.border} {stats}{' '*(58-len(stats))}{th.border}{R}")
        out.append(f"{th.border}{'='*58}{th.border}{R}")

        # Event timeline at bottom
        recent_events = [txt for _,_,txt,life,_ in event_markers if life > 15]
        if recent_events:
            event_line = ' > '.join(recent_events[:3])
            out.append(f"  {'\033[38;5;243m'}{event_line}{R}")

        out.append(f"\n  {'\033[38;5;243m\033[3m'}{t('replay_controls')}{R}")

        sys.stdout.write('\n'.join(out))
        sys.stdout.flush()
        time.sleep(0.02)

    return  # End of play_replay


def show_leaderboard():
    """Display leaderboard screen."""
    global LANG
    th = THEMES[0]
    lb = load_leaderboard()
    cls()
    print(f"""
{th.accent}  +{'='*58}+
  |                                                          |
  |     {th.wall_fresh}{t('daily_rank'):^54s}{th.accent}                        |
  +{'='*58}+{R}
""")
    if not lb:
        print(f"  {th.accent}|{R}  {t('daily_empty'):^54s}  {th.accent}|{R}")
    else:
        header = f"  {'#':<3s} {t('daily_score'):>8s} {t('daily_pings'):>5s} {t('daily_steps'):>5s} {t('daily_grade'):>5s}  {t('daily_seed'):>12s}"
        print(f"  {th.accent}|{R} {header} {th.accent}|{R}")
        print(f"  {th.accent}|{R}{'-'*56}{th.accent}|{R}")
        for i, e in enumerate(lb[:10]):
            row = f"  {i+1:<3d} {e['score']:>8d} {e['pings']:>5d} {e['steps']:>5d} {e['grade']:>5s}  {e['date']:>12s}"
            if i == 0:
                row = '\033[38;5;226m\033[1m' + row + R
            print(f"  {th.accent}|{R} {row} {th.accent}|{R}")
    print(f"{th.accent}  +{'='*58}+{R}")
    print(f"\n  {D}{t('daily_press')}{R}")
    while True:
        k = get_key()
        if k: break
        time.sleep(0.05)


def build_map_grid(g: Game, vw: int = 30, vh: int = 20) -> dict:
    """Build viewport-sized game state grid for pixel rendering."""
    sx = max(0, min(g.w - vw, g.px - vw // 2))
    sy = max(0, min(g.h - vh, g.py - vh // 2))
    grid = []
    for row_y in range(sy, sy + vh):
        row = []
        for col_x in range(sx, sx + vw):
            cell = {'t': -1, 'v': 0, 'e': 0}
            if 0 <= col_x < g.w and 0 <= row_y < g.h:
                cell['t'] = g.maze[row_y][col_x]
                cell['v'] = g.visible.get((col_x, row_y), 0)
                cell['e'] = g.explored.get((col_x, row_y), 0)
                # Player
                if col_x == g.px and row_y == g.py:
                    cell['p'] = 1
                # Exit (show if visible or explored)
                if col_x == g.ex and row_y == g.ey and (g.exit_visible or g.quest_complete or (col_x, row_y) in g.visible):
                    cell['x'] = 1
                # Collectibles
                for c in g.collectibles:
                    if c.x == col_x and c.y == row_y:
                        cell['i'] = c.item_type.value
                # Predators
                for pr in g.predators:
                    if pr.x == col_x and pr.y == row_y:
                        cell['r'] = 1 if pr.hunting else (2 if pr.stunned > 0 else 0)
                # Boss
                if g.boss and not g.boss_defeated and g.boss.x == col_x and g.boss.y == row_y:
                    cell['b'] = g.boss.boss_type.value
                    cell['bs'] = g.boss.shields  # Current shields
                    cell['bms'] = g.boss.max_shields  # Max shields
                # Boss anchors (Void Avatar)
                if g.boss and not g.boss_defeated and g.boss.boss_type == BossType.VOID_AVATAR:
                    for ax, ay in g.boss.anchors:
                        if ax == col_x and ay == row_y:
                            cell['a'] = 1  # Frequency anchor
                # Environment elements
                if (col_x, row_y) in g.env_elements:
                    cell['n'] = g.env_elements[(col_x, row_y)].value
                # Footsteps
                for fx, fy, _ in g.footsteps:
                    if fx == col_x and fy == row_y:
                        cell['f'] = 1
                # Predator drone type
                for pr in g.predators:
                    if pr.x == col_x and pr.y == row_y:
                        cell['dt'] = pr.drone_type.value  # Drone type string
            row.append(cell)
        grid.append(row)
    return {
        'grid': grid, 'vw': vw, 'vh': vh,
        'px': g.px - sx, 'py': g.py - sy,
    }


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

def main():
    hide()
    try:
        theme_idx = 0; map_scale = 1; total_clears = 0; daily_mode = False
        walker_class = None
        while True:
            result = title_screen(total_clears)
            if result[0] == -1: continue
            if result[0] == -2:  # Daily mode
                daily_mode = True
                diff = 2; theme_idx = daily_seed() % len(THEMES); map_scale = 1
                modifiers = set(); walker_class = None
                random.seed(daily_seed())
                break
            diff, theme_idx, map_scale, modifiers, walker_class = result
            break
        if diff==0: cls(); print("Farewell."); return

        cfg = {1: dict(bonus=5), 2: dict(bonus=3), 3: dict(bonus=1)}[diff]

        lvl = 1; total_score = 0; chosen_theme = theme_idx
        abilities: Set[Ability] = set()
        prev_path: List[Tuple[int,int]] = []
        next_map_reveal = False
        bosses_defeated = 0  # Track boss kills for unlocks

        # Show story intro
        show_story(lvl)

        g, _ = make_level(lvl, 0, theme_idx, abilities, prev_path, map_scale,
                          active_modifiers=modifiers, total_clears=total_clears,
                          upcoming_map_reveal=next_map_reveal,
                          walker_class=walker_class)
        g.max_energy += cfg['bonus']; g.energy = g.max_energy
        g.story_seen = False

        last_tick = time.time()
        TICK = 1.0/15; acc = 0.0; first_frame = True

        running = True
        while running:
            now = time.time(); dt = now-last_tick; last_tick = now; acc += dt
            k = get_key()

            # Freeze frame: skip input during freeze
            if g.freeze_frame > 0:
                k = ''

            if k=='q':
                if daily_mode and not g.won:
                    add_daily_result(g.total_score, g.pings, g.moves, g.rating())
                    show_leaderboard()
                    first_frame = True
                running = False; continue
            if g.is_dead and k=='r':
                play_replay(g)
                first_frame = True; continue

            if k=='l':
                global LANG
                LANG = 'en' if LANG == 'zh' else 'zh'
                g.msg(f"[{t('lang_switch')}: {'中文' if LANG=='zh' else 'English'}]")
                first_frame = True

            if k=='h':
                help_screen(g)
                first_frame = True

            if k=='r':
                lvl=1; total_score=0; theme_idx=chosen_theme; abilities.clear(); prev_path.clear()
                next_map_reveal = False; bosses_defeated = 0
                show_story(lvl)
                g, theme_idx = make_level(lvl, 0, theme_idx, abilities, prev_path, map_scale,
                                          active_modifiers=modifiers, total_clears=total_clears,
                                          walker_class=walker_class)
                g.max_energy+=cfg['bonus']; g.energy=g.max_energy
                g.msg(t('msg_restart'))
                first_frame=True; continue

            if g.won:
                if k == 'r':
                    play_replay(g)
                    first_frame = True
                    continue
                if k in (' ', '\r', '\n'):
                    # Daily mode: save result and show leaderboard
                    if daily_mode:
                        add_daily_result(g.total_score, g.pings, g.moves, g.rating())
                        show_leaderboard()
                        first_frame = True
                    # Track clear
                    if g.pings > 0 or g.moves > 5:  # Actually played
                        total_clears += 1
                    # Track boss defeat
                    if g.boss_defeated:
                        bosses_defeated += 1
                    # Check for character unlocks
                    update_unlocks_from_game(g, total_clears, bosses_defeated)
                    prev_path = list(g.path_this_run)
                    next_map_reveal = g.upcoming_map_reveal
                    lvl += 1
                    # Story at act transitions (levels 4, 7, 10+)
                    if lvl in (4, 7, 10):
                        show_story(lvl)
                    if lvl>1 and (lvl-1)%3==0:
                        new_ab = ability_select(g)
                        if new_ab: abilities.add(new_ab)
                    theme_idx = chosen_theme + lvl - 1
                    g, theme_idx = make_level(lvl, g.total_score, theme_idx, abilities, prev_path, map_scale,
                                              active_modifiers=modifiers, total_clears=total_clears,
                                              upcoming_map_reveal=next_map_reveal,
                                              walker_class=walker_class)
                    g.max_energy+=cfg['bonus']; g.energy=g.max_energy
                    first_frame=True
                continue

            mm = {'w':(0,-1),'s':(0,1),'a':(-1,0),'d':(1,0),
                  'up':(0,-1),'down':(0,1),'left':(-1,0),'right':(1,0)}
            if k in mm: g.move(*mm[k])
            if k==' ': g.emit_ping()

            ticks = min(int(acc/TICK), 4)
            for _ in range(ticks): g.tick()
            acc -= ticks*TICK

            if first_frame: cls(); first_frame=False
            else: sys.stdout.write('__CLS__\n')
            sys.stdout.write(render(g))
            sys.stdout.flush()
            time.sleep(0.025)

    except KeyboardInterrupt: pass
    finally:
        show(); cls()
        line1 = t('bye_line1'); line2 = t('bye_line2')
        print(f"{THEMES[0].accent}+{'='*50}+{R}")
        print(f"{THEMES[0].accent}|  {line1}{' '*(50-len(line1))}|{R}")
        print(f"{THEMES[0].accent}|  {line2}{' '*(50-len(line2))}|{R}")
        print(f"{THEMES[0].accent}+{'='*50}+{R}")

if __name__=='__main__':
    main()
