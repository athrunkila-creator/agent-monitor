#!/usr/bin/env python3
"""
Agent Monitor - 统一命令行入口
"""

import argparse
import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from monitor import collect_metrics
from alerts import process_alerts, send_feishu_alert, send_email_alert
from export import export_all, generate_report

def main():
    parser = argparse.ArgumentParser(
        description="Agent Monitor - OpenClaw Agent 监控工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s status          显示当前状态
  %(prog)s alerts          检查告警
  %(prog)s export          导出数据
  %(prog)s report          生成报告
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # status 命令
    status_parser = subparsers.add_parser("status", help="显示当前状态")
    status_parser.add_argument("--json", action="store_true", help="JSON 输出")
    
    # alerts 命令
    alerts_parser = subparsers.add_parser("alerts", help="告警管理")
    alerts_parser.add_argument("--check", action="store_true", help="检查告警")
    alerts_parser.add_argument("--send", action="store_true", help="发送告警")
    alerts_parser.add_argument("--test-feishu", action="store_true", help="测试飞书通知")
    alerts_parser.add_argument("--test-email", action="store_true", help="测试邮件通知")
    
    # export 命令
    export_parser = subparsers.add_parser("export", help="导出数据")
    export_parser.add_argument("--format", choices=["json", "csv"], default="json", help="导出格式")
    export_parser.add_argument("--days", type=int, default=7, help="数据范围（天）")
    
    # report 命令
    report_parser = subparsers.add_parser("report", help="生成报告")
    report_parser.add_argument("--days", type=int, default=7, help="报告范围（天）")
    
    args = parser.parse_args()
    
    if args.command == "status":
        metrics = collect_metrics()
        if args.json:
            import json
            print(json.dumps(metrics, ensure_ascii=False, indent=2))
        else:
            print_status(metrics)
    
    elif args.command == "alerts":
        if args.test_feishu:
            send_feishu_alert("🧪 Agent Monitor 测试告警\n这是一条测试消息")
        elif args.test_email:
            send_email_alert("Agent Monitor 测试", "这是一条测试邮件")
        else:
            from alerts import check_alerts
            from monitor import analyze_agents, get_cron_jobs, get_sessions, get_subagents
            
            sessions = get_sessions()
            jobs = get_cron_jobs()
            subagents = get_subagents()
            agents_data = analyze_agents(sessions, jobs, subagents)
            agents = list(agents_data.values()) if isinstance(agents_data, dict) else []
            
            alerts = check_alerts(agents, jobs)
            
            if alerts:
                print(f"发现 {len(alerts)} 条告警:")
                for a in alerts:
                    severity_icon = "🔴" if a["severity"] == "high" else "🟡" if a["severity"] == "medium" else "🟢"
                    print(f"\n{severity_icon} [{a['type']}] {a['severity'].upper()}")
                    print(f"   {a['message'][:100]}...")
                
                if args.send:
                    print("\n发送告警...")
                    sent = process_alerts(agents, jobs, ["feishu"])
                    print(f"已发送 {len(sent)} 条")
            else:
                print("✅ 无告警")
    
    elif args.command == "export":
        print(f"导出最近 {args.days} 天数据...")
        files = export_all(args.format, args.days)
        print("\n导出完成:")
        for name, path in files.items():
            print(f"  {name}: {path}")
    
    elif args.command == "report":
        print(generate_report(args.days))
    
    else:
        parser.print_help()

def print_status(metrics):
    """打印状态摘要"""
    agents = metrics.get("agents", {})
    
    print("\n" + "=" * 50)
    print("Agent Monitor 状态")
    print("=" * 50)
    
    # 统计
    total = len(agents)
    active = sum(1 for a in agents.values() if a.get("status") == "active")
    busy = sum(1 for a in agents.values() if a.get("status") == "busy")
    idle = sum(1 for a in agents.values() if a.get("status") == "idle")
    
    print(f"\n📊 Agent: {total} 个 ({active} 活跃, {busy} 忙碌, {idle} 空闲)")
    
    # Token
    total_tokens = sum(a.get("tokens_today", 0) for a in agents.values())
    print(f"📈 今日 Token: {total_tokens:,}")
    
    # 显示前 5 个 Agent
    print("\nAgent 列表:")
    for agent_id, agent in list(agents.items())[:5]:
        status_icon = "🟢" if agent.get("status") == "active" else "🟡" if agent.get("status") == "busy" else "⚪"
        tokens = agent.get("tokens_today", 0)
        print(f"  {status_icon} {agent.get('name', agent_id)}: {tokens:,} tokens")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()