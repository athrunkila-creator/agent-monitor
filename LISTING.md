# Agent Monitor - OpenClaw Agent 实时监控工具

> 一键监控你的 Agent 状态、Token 消耗、定时任务，支持告警通知和数据导出。

---

## 🎯 产品简介

Agent Monitor 是专为 OpenClaw 用户打造的 Agent 监控工具。实时追踪所有 Agent 的运行状态、Token 消耗、任务进度，支持多渠道告警通知和数据导出，让你的 Agent 运行状态一目了然。

---

## ✨ 核心功能

### 📊 实时状态监控

- **Agent 状态**：实时显示活跃/忙碌/空闲状态
- **Token 消耗**：精确统计每日/每周 Token 使用量
- **任务进度**：追踪当前执行任务的进度和详情
- **定时任务**：监控所有 Cron 任务执行状态

### 🚨 智能告警通知

| 告警类型 | 说明 | 级别 |
|---------|------|------|
| Agent 错误 | Agent 执行出错 | 🔴 高 |
| 任务失败 | 定时任务执行失败 | 🔴 高 |
| Token 预警 | 消耗超过阈值 | 🟡 中 |
| 长时间空闲 | Agent 超过 24h 未活动 | 🟢 低 |

**支持渠道**：飞书、邮件、自定义 Webhook

### 📤 数据导出

- **CSV 格式**：Excel 友好，适合数据分析
- **JSON 格式**：完整数据，适合系统集成
- **周报生成**：自动汇总关键指标

### 🌐 Web Dashboard

可视化仪表盘，实时刷新，一目了然。

---

## 💰 定价策略：赞助制

**全部功能免费使用**，如果你觉得有用，欢迎赞助支持开发者持续维护。

| 功能 | 赞助版 |
|------|--------|
| 实时监控 | ✅ |
| Agent 数量 | 无限 |
| 告警通知 | ✅ |
| 数据导出 | ✅ |
| 历史数据 | 30 天 |
| API 接口 | ✅ |
| 技术支持 | 社区支持 |

**赞助方式**：
- 💰 微信赞赏：扫码支持（见 `sponsor-wechat.jpg`）
- ☕ 请作者喝杯咖啡：¥50（建议金额）

> 你的支持是我持续更新的动力！感谢每一位赞助者 🙏

---

## 🚀 快速开始

### 安装

```bash
# 从 ClawHub 安装
openclaw skill install agent-monitor

# 或本地安装
cd agent-monitor && ./install.sh
```

### 使用

```bash
# 显示状态
agent-monitor status

# 检查告警
agent-monitor alerts

# 导出数据
agent-monitor export --format json

# 生成报告
agent-monitor report
```

### 配置告警

编辑 `config.json`：

```json
{
  "alerts": {
    "enabled": true,
    "channels": ["feishu"],
    "feishu_webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/your-webhook",
    "rules": {
      "agent_error": {"enabled": true},
      "cron_failed": {"enabled": true},
      "token_high": {"enabled": true, "threshold": 100000}
    }
  }
}
```

---

## 📸 截图

### Dashboard 界面

```
┌─────────────────────────────────────────────────────┐
│  🦞 Agent Monitor                        🟢 运行中   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  📊 Agent 状态          📈 今日 Token: 1,234,567    │
│  ┌─────────────┐                                   │
│  │ 🦞 小龙虾    │ 🟢 活跃  │ 127,169 tokens        │
│  │ 📈 交易虾    │ 🟢 活跃  │  54,123 tokens        │
│  │ 📰 新闻虾    │ ⚪ 空闲  │  31,828 tokens        │
│  │ 📚 学习虾    │ ⚪ 空闲  │ 493,857 tokens        │
│  └─────────────┘                                   │
│                                                     │
│  ⏰ 定时任务: 22 个  │  ⚠️ 错误: 1                  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 💬 用户评价

> "终于不用手动检查 Agent 状态了，告警功能太实用了！" —— 某开发者

> "Token 统计很精确，帮我节省了不少 API 成本。" —— 某用户

---

## ❓ 常见问题

**Q: 支持 OpenClaw 以外的平台吗？**  
A: 目前仅支持 OpenClaw，未来计划支持更多平台。

**Q: 买断后大版本升级需要付费吗？**  
A: 大版本升级享受 50% 折扣。

**Q: 数据存储在哪里？**  
A: 所有数据存储在本地 SQLite，不上传云端，保护隐私。

**Q: 可以自定义告警规则吗？**  
A: Team 版本支持自定义告警规则和阈值。

---

## 📞 支持

- 📧 邮箱：support@openclaw.ai
- 💬 社区：https://discord.gg/clawd
- 📚 文档：https://docs.openclaw.ai/skills/agent-monitor

---

## 📜 更新日志

### v1.1.0 (2026-03-23)
- ✨ 新增告警通知功能（飞书/邮件/Webhook）
- ✨ 新增数据导出功能（CSV/JSON）
- ✨ 新增周报生成功能
- 🐛 修复 Token 统计不准确问题
- 📝 优化文档和 CLI

### v1.0.0 (2026-03-18)
- 🎉 首次发布
- ✨ 基础监控功能
- ✨ Web Dashboard
- ✨ 定时任务监控

---

**立即安装，让 Agent 状态尽在掌握！** 🦞