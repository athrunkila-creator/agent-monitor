# Agent Monitor V1.0.1

🦞 OpenClaw Agent 实时监控工具

## 快速开始

### macOS 用户

1. 双击 `AgentMonitor.app` 即可启动
2. 首次运行会自动安装依赖
3. 自动打开浏览器访问 Dashboard

### 命令行启动

```bash
cd agent-monitor
python3 monitor.py    # 初始化数据
python3 server.py     # 启动服务
```

## 系统要求

- Python 3.10+
- macOS 10.13+

## 依赖安装

首次运行会自动安装，或手动执行：

```bash
pip3 install requests
```

## 访问地址

- 本地：http://localhost:9001
- 公网：需配置 Tailscale Funnel

## 功能

- ✅ 10个 Agent 状态监控
- ✅ Token 消耗统计
- ✅ 定时任务队列
- ✅ 任务展开/收起
- ✅ 响应式 Web Dashboard
- ✅ 赞助支持

## 停止服务

```bash
# macOS
pkill -f "python3 server.py"

# 或在终端按 Ctrl+C
```

## 许可证

MIT License - 自由使用，欢迎赞助支持！

---

🦞 Made with ❤️ by 小龙虾