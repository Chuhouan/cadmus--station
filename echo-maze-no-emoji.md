---
name: echo-maze-no-emoji
description: "Echo Maze: zero emoji — all visuals are hand-drawn pixel art"
type: feedback
---

# 禁止Emoji规则

此游戏**严禁**使用任何emoji字符。

## 替代方案
- Canvas 2D 像素绘制（角色/物品/墙壁/特效）
- 离屏Canvas→data URL 像素图标（面板/按钮/帮助系统）
- CSS纯文本标签（面板标题等）
- Web Audio API 合成音效（无外部音频文件）

## 检查清单
- HTML: `<img>` 用像素图标 data URL，不用emoji
- JS: 所有字符串不含emoji字符
- CSS: 所有装饰用纯CSS/Canvas实现
- Python: 不发送含emoji的状态数据

## 像素图标系统
`pixel_icons.js` — 所有UI图标均为12×12 Canvas手绘→data URL
