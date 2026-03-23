# 🦞 Agent Monitor

<div align="center">

**实时监控你的 AI Agent 状态**

[![Version](https://img.shields.io/badge/version-1.0.1-blue.svg)](https://github.com/openclaw/agent-monitor)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey.svg)]()

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [截图展示](#-截图展示) • [赞助支持](#-赞助支持)

</div>

---

## 🎯 这是什么？

**Agent Monitor** 是一个专为 [OpenClaw](https://github.com/openclaw/openclaw) 设计的实时监控工具。

如果你有多个 AI Agent 在后台运行，想知道：
- 🤔 每个 Agent 现在在做什么？
- 📊 Token 消耗了多少？
- ⏰ 定时任务什么时候执行？
- 📈 哪个 Agent 最忙碌？

**Agent Monitor 帮你一站式解决这些问题！**

---

## ✨ 功能特性

### 📊 实时状态监控
- 10个 Agent 状态一览（活跃/忙碌/空闲）
- 任务队列实时展示
- 最后活动时间追踪

### 💰 Token 消耗统计
- 每日 Token 消耗明细
- 总量汇总统计
- 成本可视化

### ⏰ 定时任务监控
- 24个 Cron 任务状态
- 下次执行时间预告
- 任务执行状态追踪

### 🎨 精美 Dashboard
- 响应式设计，手机也能看
- 深色主题，护眼舒适
- 一键刷新数据

### 🌐 多种访问方式
- 本地访问：`http://localhost:9001`
- 公网访问：支持 Tailscale Funnel
- 移动端友好

---

## 🚀 快速开始

### macOS 用户（推荐）

```bash
# 下载并解压
unzip AgentMonitor-v1.0.1-macOS.zip

# 双击运行
open AgentMonitor.app
```

### 命令行启动

```bash
# 克隆仓库
git clone https://github.com/openclaw/agent-monitor.git
cd agent-monitor

# 安装依赖（首次运行自动安装）
pip3 install requests

# 启动服务
python3 monitor.py  # 初始化数据
python3 server.py   # 启动服务
```

### 访问 Dashboard

打开浏览器访问：http://localhost:9001

---

## 📸 截图展示

### Dashboard 主界面
```
┌─────────────────────────────────────────────────────────────┐
│  🦞 Agent Monitor                        [☕ 赞助支持]      │
├─────────────────────────────────────────────────────────────┤
│  活跃主 Agent: 1   定时任务: 24   活跃子 Agent: 2          │
│  Token 消耗: 3.1M                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🦞 小龙虾                    状态: 🟡 忙碌                 │
│  ├── 模型: GLM-5                                           │
│  ├── 会话: 4    最后活动: 刚刚                              │
│  └── 待处理任务 (8)                                        │
│      • 飞书上下文监控    0 9,15,21 * * *                   │
│      • 每日摘要生成      0 0 * * *                         │
│                                                             │
│  📚 学习虾                    状态: ⚪ 空闲                 │
│  ├── 模型: Kimi-K2.5                                       │
│  ├── 会话: 58   最后活动: 50分钟前                          │
│  └── 待处理任务 (6)                                        │
│      • InStreet社区互动   every                            │
│                                                             │
│  📈 交易虾                    状态: ⚪ 空闲                 │
│  └── 待处理任务 (4)                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🦞 支持的 Agent

| Agent | 职责 | 状态 |
|-------|------|------|
| 🦞 小龙虾 | 主 Agent，任务调度 | ✅ |
| 📈 交易虾 | 股票交易分析 | ✅ |
| 📚 学习虾 | InStreet 社区学习 | ✅ |
| 💻 编程虾 | 代码开发 | ✅ |
| 📰 新闻虾 | 新闻播报 | ✅ |
| 📊 行研虾 | 研究分析 | ✅ |
| 💼 商业虾 | 商业分析 | ✅ |
| 🔍 闲鱼虾 | 闲鱼捡漏 | ✅ |
| 🎨 画图虾 | 图片生成 | ✅ |
| 🧪 测试虾 | 测试验证 | ✅ |

---

## 🛠️ 技术栈

- **后端**: Python 3.10+
- **前端**: 原生 HTML/CSS/JavaScript（零依赖）
- **数据**: JSON 文件存储
- **部署**: 支持 macOS / Linux / Windows

---

## 📦 项目结构

```
agent-monitor/
├── AgentMonitor.app/       # macOS 应用程序
├── monitor.py              # 数据采集模块
├── server.py               # Web 服务器
├── index.html              # Dashboard 界面
├── config.json             # 配置文件
├── alerts.py               # 告警模块
├── export.py               # 数据导出
└── cli.py                  # 命令行工具
```

---

## 🎁 赞助支持

如果你觉得这个工具有用，欢迎请作者喝杯咖啡 ☕

- 💰 微信赞赏码：见 `sponsor-wechat.jpg`
- 💡 建议 ¥50，支持持续维护

**全部功能免费使用，赞助完全自愿！**

---

## 📝 更新日志

### v1.0.1 (2026-03-23)
- ✨ Agent 按任务量排序
- ✨ 主 Agent 永远置顶
- ✨ 任务列表展开/收起

### v1.0.0 (2026-03-23)
- 🎉 首个正式版本发布
- ✅ 10个 Agent 监控
- ✅ Token 消耗统计
- ✅ 定时任务监控
- ✅ 响应式 Dashboard

---

## 📄 许可证

[MIT License](LICENSE) - 自由使用，欢迎 Star ⭐

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

<div align="center">

**Made with ❤️ by 小龙虾**

[⬆ 返回顶部](#-agent-monitor)

</div>