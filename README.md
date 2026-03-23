# Agent Monitor

OpenClaw Agent 实时监控工具，支持状态监控、告警通知、数据导出。

## 功能特性

| 功能 | 说明 |
|------|------|
| 实时监控 | Agent 状态、Token 消耗、任务进度 |
| 告警通知 | 飞书、邮件、Webhook |
| 数据导出 | CSV、JSON 格式 |
| 周报生成 | 自动汇总分析 |

## 快速开始

```bash
# 显示当前状态
python cli.py status

# 检查告警
python cli.py alerts

# 导出数据
python cli.py export --format json

# 生成报告
python cli.py report
```

## 告警配置

编辑 `config.json`:

```json
{
  "alerts": {
    "enabled": true,
    "channels": ["feishu"],
    "feishu_webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/xxx",
    "rules": {
      "agent_error": {"enabled": true, "severity": "high"},
      "cron_failed": {"enabled": true, "severity": "high"},
      "token_high": {"enabled": true, "threshold": 100000}
    }
  }
}
```

### 告警规则

| 规则 | 说明 | 默认阈值 |
|------|------|----------|
| agent_error | Agent 发生错误 | - |
| cron_failed | 定时任务失败 | - |
| token_high | Token 消耗过高 | 100,000 |
| agent_idle_long | Agent 长时间空闲 | 24小时 |

## 命令参考

### status - 显示状态

```bash
python cli.py status          # 文本输出
python cli.py status --json   # JSON 输出
```

### alerts - 告警管理

```bash
python cli.py alerts              # 检查告警
python cli.py alerts --send       # 检查并发送
python cli.py alerts --test-feishu  # 测试飞书
```

### export - 导出数据

```bash
python cli.py export              # JSON 格式，7天
python cli.py export --format csv # CSV 格式
python cli.py export --days 30    # 30天数据
```

### report - 生成报告

```bash
python cli.py report              # 7天报告
python cli.py report --days 30    # 30天报告
```

## 文件结构

```
agent-monitor/
├── cli.py           # 统一命令行入口
├── monitor.py       # 核心监控模块
├── alerts.py        # 告警通知模块
├── export.py        # 数据导出模块
├── config.json      # 配置文件
├── data/            # 数据存储
│   ├── monitor.db   # SQLite 数据库
│   └── exports/     # 导出文件
└── venv/            # Python 虚拟环境
```

## 版本历史

- v1.1.0 - 新增告警通知、数据导出功能
- v1.0.0 - 基础监控功能