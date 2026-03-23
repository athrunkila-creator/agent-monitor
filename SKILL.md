# Agent Monitor

实时监控 OpenClaw Agent 状态、Token 消耗、定时任务。

## 功能

| 功能 | 说明 |
|------|------|
| 📊 实时监控 | Agent 状态、当前任务、进度追踪 |
| 📈 Token 统计 | 每日消耗、趋势分析 |
| ⏰ 定时任务 | Cron 任务状态监控 |
| 🚨 告警通知 | 飞书/邮件/Webhook 多渠道告警 |
| 📤 数据导出 | CSV/JSON 格式导出 |
| 📋 周报生成 | 自动汇总分析报告 |

## 使用方式

```bash
# 显示当前状态
agent-monitor status

# 检查告警
agent-monitor alerts

# 导出数据
agent-monitor export --format json

# 生成报告
agent-monitor report
```

## 告警规则

| 规则 | 说明 | 严重级别 |
|------|------|----------|
| `agent_error` | Agent 发生错误 | 🔴 High |
| `cron_failed` | 定时任务失败 | 🔴 High |
| `token_high` | Token 消耗过高 | 🟡 Medium |
| `agent_idle_long` | Agent 长时间空闲 | 🟢 Low |

## 配置

编辑 `config.json` 配置告警渠道：

```json
{
  "alerts": {
    "enabled": true,
    "channels": ["feishu"],
    "feishu_webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/xxx",
    "rules": {
      "agent_error": {"enabled": true},
      "cron_failed": {"enabled": true},
      "token_high": {"enabled": true, "threshold": 100000}
    }
  }
}
```

## 定价

**赞助制**：全部功能免费使用，欢迎赞助支持开发。

- 赞助方式：微信/支付宝赞赏码
- 你的支持是我持续更新的动力 ☕

## 触发词

- `/monitor` - 显示 Agent 状态
- `/alerts` - 检查告警
- `/report` - 生成报告

## 版本

- v1.1.0 - 新增告警通知、数据导出
- v1.0.0 - 基础监控功能
