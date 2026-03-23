#!/usr/bin/env python3
"""
Agent Monitor - 数据导出模块
支持：CSV、JSON、Excel
"""

import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import os

# 数据目录
DATA_DIR = Path(__file__).parent / "data"
EXPORT_DIR = DATA_DIR / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================
# 数据收集
# ============================================

def collect_export_data(days: int = 7) -> Dict:
    """
    收集导出数据
    
    Args:
        days: 数据范围（天）
    
    Returns:
        {
            "agents": [...],
            "cron_jobs": [...],
            "token_history": [...],
            "alerts": [...]
        }
    """
    from monitor import analyze_agents, get_cron_jobs, get_sessions, get_subagents
    from alerts import load_config
    
    # 获取当前状态
    sessions = get_sessions()
    jobs = get_cron_jobs()
    subagents = get_subagents()
    agents_data = analyze_agents(sessions, jobs, subagents)
    agents = list(agents_data.values()) if isinstance(agents_data, dict) else []
    
    # 加载历史数据
    token_history = load_token_history(days)
    alerts_history = load_alerts_history(days)
    
    return {
        "export_time": datetime.now().isoformat(),
        "date_range": f"最近 {days} 天",
        "agents": agents,
        "cron_jobs": jobs,
        "token_history": token_history,
        "alerts": alerts_history
    }

def load_token_history(days: int = 7) -> List[Dict]:
    """加载 Token 历史数据"""
    history_file = DATA_DIR / "token_history.json"
    
    if not history_file.exists():
        return []
    
    with open(history_file, "r", encoding="utf-8") as f:
        all_data = json.load(f)
    
    # 过滤最近 N 天
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    
    return [
        d for d in all_data
        if d.get("timestamp", "") >= cutoff
    ]

def load_alerts_history(days: int = 7) -> List[Dict]:
    """加载告警历史"""
    alerts_file = DATA_DIR / "alerts_history.json"
    
    if not alerts_file.exists():
        return []
    
    with open(alerts_file, "r", encoding="utf-8") as f:
        all_data = json.load(f)
    
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    
    return [
        d for d in all_data
        if d.get("timestamp", "") >= cutoff
    ]

# ============================================
# CSV 导出
# ============================================

def export_agents_csv(agents: List[Dict], filepath: Optional[str] = None) -> str:
    """导出 Agent 状态为 CSV"""
    if filepath is None:
        filepath = EXPORT_DIR / f"agents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        
        # 表头
        writer.writerow([
            "Agent ID", "名称", "状态", "模型", 
            "今日Token", "会话数", "最后活动", "当前任务"
        ])
        
        # 数据
        for agent in agents:
            writer.writerow([
                agent.get("id", ""),
                agent.get("name", ""),
                agent.get("status", ""),
                agent.get("model", ""),
                agent.get("tokens_today", 0),
                agent.get("sessions", 0),
                agent.get("last_activity_text", ""),
                agent.get("current_task", "")[:50] if agent.get("current_task") else ""
            ])
    
    print(f"✅ Agent CSV 导出: {filepath}")
    return str(filepath)

def export_cron_csv(jobs: List[Dict], filepath: Optional[str] = None) -> str:
    """导出定时任务为 CSV"""
    if filepath is None:
        filepath = EXPORT_DIR / f"cron_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        
        writer.writerow([
            "任务ID", "名称", "调度", "状态", 
            "下次执行", "上次执行", "Agent"
        ])
        
        for job in jobs:
            state = job.get("state", {})
            writer.writerow([
                job.get("id", ""),
                job.get("name", ""),
                job.get("schedule", {}).get("expr", ""),
                state.get("lastStatus", ""),
                datetime.fromtimestamp(state.get("nextRunAtMs", 0) / 1000).strftime("%Y-%m-%d %H:%M") if state.get("nextRunAtMs") else "",
                datetime.fromtimestamp(state.get("lastRunAtMs", 0) / 1000).strftime("%Y-%m-%d %H:%M") if state.get("lastRunAtMs") else "",
                job.get("agentId", "")
            ])
    
    print(f"✅ Cron CSV 导出: {filepath}")
    return str(filepath)

def export_token_history_csv(history: List[Dict], filepath: Optional[str] = None) -> str:
    """导出 Token 历史为 CSV"""
    if filepath is None:
        filepath = EXPORT_DIR / f"tokens_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        
        writer.writerow([
            "时间", "Agent", "Token 消耗", "累计"
        ])
        
        for record in history:
            writer.writerow([
                record.get("timestamp", ""),
                record.get("agent_id", ""),
                record.get("tokens", 0),
                record.get("total", 0)
            ])
    
    print(f"✅ Token CSV 导出: {filepath}")
    return str(filepath)

# ============================================
# JSON 导出
# ============================================

def export_full_json(data: Dict, filepath: Optional[str] = None) -> str:
    """导出完整数据为 JSON"""
    if filepath is None:
        filepath = EXPORT_DIR / f"full_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 完整 JSON 导出: {filepath}")
    return str(filepath)

def export_agents_json(agents: List[Dict], filepath: Optional[str] = None) -> str:
    """导出 Agent 状态为 JSON"""
    if filepath is None:
        filepath = EXPORT_DIR / f"agents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(agents, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Agent JSON 导出: {filepath}")
    return str(filepath)

# ============================================
# 报告生成
# ============================================

def generate_report(days: int = 7) -> str:
    """
    生成摘要报告
    
    Returns:
        报告文本
    """
    data = collect_export_data(days)
    
    lines = []
    lines.append("=" * 60)
    lines.append(f"Agent Monitor 周报 ({days}天)")
    lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 60)
    
    # Agent 概览
    agents = data["agents"]
    lines.append("\n📊 Agent 概览:")
    lines.append(f"  总数: {len(agents)}")
    lines.append(f"  活跃: {sum(1 for a in agents if a.get('status') == 'active')}")
    lines.append(f"  空闲: {sum(1 for a in agents if a.get('status') == 'idle')}")
    lines.append(f"  忙碌: {sum(1 for a in agents if a.get('status') == 'busy')}")
    
    # Token 消耗
    total_tokens = sum(a.get("tokens_today", 0) for a in agents)
    lines.append(f"\n📈 Token 消耗:")
    lines.append(f"  今日总计: {total_tokens:,}")
    for a in sorted(agents, key=lambda x: x.get("tokens_today", 0), reverse=True)[:5]:
        if a.get("tokens_today", 0) > 0:
            lines.append(f"  - {a.get('name')}: {a.get('tokens_today'):,}")
    
    # 定时任务
    jobs = data["cron_jobs"]
    error_jobs = [j for j in jobs if j.get("state", {}).get("lastStatus") == "error"]
    lines.append(f"\n⏰ 定时任务:")
    lines.append(f"  总数: {len(jobs)}")
    lines.append(f"  错误: {len(error_jobs)}")
    if error_jobs:
        for j in error_jobs[:3]:
            lines.append(f"  - ⚠️ {j.get('name')}")
    
    # 告警
    alerts = data["alerts"]
    lines.append(f"\n🚨 告警:")
    lines.append(f"  总数: {len(alerts)}")
    high_alerts = [a for a in alerts if a.get("severity") == "high"]
    if high_alerts:
        lines.append(f"  高优先级: {len(high_alerts)}")
    
    lines.append("\n" + "=" * 60)
    
    return "\n".join(lines)

# ============================================
# 统一导出接口
# ============================================

def export_all(format: str = "json", days: int = 7) -> Dict[str, str]:
    """
    导出所有数据
    
    Args:
        format: json 或 csv
        days: 数据范围
    
    Returns:
        导出文件路径列表
    """
    data = collect_export_data(days)
    files = {}
    
    if format == "json":
        files["full"] = export_full_json(data)
        files["agents"] = export_agents_json(data["agents"])
    elif format == "csv":
        files["agents"] = export_agents_csv(data["agents"])
        files["cron"] = export_cron_csv(data["cron_jobs"])
        if data["token_history"]:
            files["tokens"] = export_token_history_csv(data["token_history"])
    
    # 生成报告
    report = generate_report(days)
    report_file = EXPORT_DIR / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    files["report"] = str(report_file)
    
    return files

# ============================================
# CLI 接口
# ============================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent Monitor 导出模块")
    parser.add_argument("--format", choices=["json", "csv", "all"], default="json", help="导出格式")
    parser.add_argument("--days", type=int, default=7, help="数据范围（天）")
    parser.add_argument("--report", action="store_true", help="只生成报告")
    
    args = parser.parse_args()
    
    if args.report:
        print(generate_report(args.days))
    else:
        files = export_all(args.format, args.days)
        print("\n导出完成:")
        for name, path in files.items():
            print(f"  {name}: {path}")