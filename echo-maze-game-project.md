---
name: echo-maze-game-project
description: "Echo Maze web game — echolocation pixel-art maze (Flask+Socket.IO+Canvas)"
type: project
---

# Echo Maze (回声迷宫) — v4.1

## 位置
`C:\Users\63259\Desktop\echo_maze\`

## 核心玩法
你看不到墙壁——只能发射声波脉冲，从回声反射中短暂"看见"迷宫。墙壁渐隐，凭记忆导航。找钥匙解锁出口，躲避回声捕食者，击败Boss进入下一关。

## 技术栈
- **后端**: Python + Flask + Socket.IO（`server.py` + `echo_maze.py`）
- **前端**: Canvas 2D 像素渲染（`pixel_renderer.js`）、HTML/CSS双面板HUD
- **音效**: Web Audio API 程序化合成（`audio.js`）
- **像素图标**: Canvas离屏绘制→data URL（`pixel_icons.js`）

## 架构
```
Python游戏逻辑 → 状态JSON → Socket.IO → 浏览器Canvas像素渲染
              → 无ANSI文本、无emoji、无外部图片
```

## 已实现
1. 回声脉冲 + 墙壁渐隐
2. Prim算法迷宫，关卡递增
3. 6种视觉主题（Ocean/Volcano/Forest/Crystal/Sunset/Void）— 像素调色板
4. 3种特殊房间、3种收集品、任务钥匙
5. 回声捕食者 AI（游荡/狩猎/晕眩）
6. 3种Boss（回响之母/静默猎手/虚空化身）每3关
7. 4种环境交互（瓦斯/水晶/暗水/回音壁）
8. 连击计分 S~D评级
9. 4种永久能力，每3关选一个
10. 6种挑战词缀，叠加分数倍率
11. 6个可玩角色（先知/幽灵默认解锁）
12. 秘密房间、每日挑战+排行榜、死亡回放
13. 双语系统（中/英）
14. 像素角色动画（待机/行走/脉冲/受伤）
15. 8-bit音效+背景音乐
16. 开发者模式（`键或?debug）
17. 叙事世界观文档

## 文件结构
```
echo_maze/
├── echo_maze.py              # 游戏引擎
├── server.py                 # Flask+Socket.IO
├── start.bat                 # 启动脚本
├── requirements.txt
├── LORE.md                   # 世界观
├── echo-maze-*.md            # 项目记忆文件
├── static/
│   ├── app.js                # 前端主逻辑
│   ├── pixel_renderer.js     # 像素渲染引擎
│   ├── pixel_icons.js        # 像素图标库
│   ├── audio.js              # 音效引擎
│   └── style.css             # 样式
├── templates/
│   └── index.html            # 主页面
├── unlocks.json              # 解锁数据
└── leaderboard.json          # 排行榜
```

## 用户偏好
- 中文母语，完整双语
- 零emoji——全部手绘像素图案
- 像素画面而非字符符号
- 有动感、科技感、不呆板
- 撞墙=墙体形变弹回，不震屏
- 特效集中在墙体，不在玩家身上喷粒子

## 当前迭代重点
- 🔜 叙事写入游戏
- 🔜 其余4角色像素精灵
- 🔜 物品/捕食者/Boss像素精灵细化
- 🔜 帮助系统像素图标接入
