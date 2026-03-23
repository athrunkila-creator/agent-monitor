#!/usr/bin/env python3
"""
Agent Monitor - 告警通知模块
支持：飞书、邮件、Webhook
"""

import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import requests

# 配置文件
CONFIG_FILE = Path(__file__).parent / "config.json"
ALERTS_FILE = Path(__file__).parent / "data" / "alerts_history.json"

def load_config():
    """加载配置"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_alert_history(alert: Dict):
    """保存告警历史"""
    alerts_dir = ALERTS_FILE.parent
    alerts_dir.mkdir(exist_ok=True)
    
    history = []
    if ALERTS_FILE.exists():
        with open(ALERTS_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
    
    history.append(alert)
    
    # 只保留最近 100 条
    if len(history) > 100:
        history = history[-100:]
    
    with open(ALERTS_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# ============================================
# 告警规则
# ============================================

ALERT_RULES = {
    "agent_error": {
        "name": "Agent 错误",
        "condition": lambda agent: agent.get("status") == "error",
        "severity": "high",
        "template": "🚨 Agent {name} 发生错误\n详情: {error_msg}"
    },
    "cron_failed": {
        "name": "定时任务失败",
        "condition": lambda job: job.get("state", {}).get("lastStatus") == "error",
        "severity": "high",
        "template": "⚠️ 定时任务失败\n任务: {job_name}\n时间: {last_run}"
    },
    "token_high": {
        "name": "Token 消耗过高",
        "condition": lambda agent: agent.get("tokens_today", 0) > 100000,
        "severity": "medium",
        "template": "📊 Token 消耗预警\nAgent: {name}\n今日消耗: {tokens_today:,}"
    },
    "agent_idle_long": {
        "name": "Agent 长时间空闲",
        "condition": lambda agent: agent.get("status") == "idle" and agent.get("idle_hours", 0) > 24,
        "severity": "low",
        "template": "💤 Agent 长时间空闲\nAgent: {name}\n空闲时长: {idle_hours}小时"
    }
}

def check_alerts(agents: List[Dict], cron_jobs: List[Dict]) -> List[Dict]:
    """检查告警条件"""
    alerts = []
    
    # 检查 Agent 告警
    for agent in agents:
        # 错误告警
        if ALERT_RULES["agent_error"]["condition"](agent):
            alerts.append({
                "type": "agent_error",
                "severity": "high",
                "agent_id": agent.get("id"),
                "message": ALERT_RULES["agent_error"]["template"].format(
                    name=agent.get("name", agent.get("id")),
                    error_msg=agent.get("error", "未知错误")
                ),
                "timestamp": datetime.now().isoformat()
            })
        
        # Token 告警
        if ALERT_RULES["token_high"]["condition"](agent):
            alerts.append({
                "type": "token_high",
                "severity": "medium",
                "agent_id": agent.get("id"),
                "message": ALERT_RULES["token_high"]["template"].format(
                    name=agent.get("name", agent.get("id")),
                    tokens_today=agent.get("tokens_today", 0)
                ),
                "timestamp": datetime.now().isoformat()
            })
    
    # 检查定时任务告警
    for job in cron_jobs:
        if ALERT_RULES["cron_failed"]["condition"](job):
            last_run = job.get("state", {}).get("lastRunAtMs", 0)
            last_run_str = datetime.fromtimestamp(last_run / 1000).strftime("%Y-%m-%d %H:%M") if last_run else "未知"
            
            alerts.append({
                "type": "cron_failed",
                "severity": "high",
                "job_id": job.get("id"),
                "message": ALERT_RULES["cron_failed"]["template"].format(
                    job_name=job.get("name", "未知"),
                    last_run=last_run_str
                ),
                "timestamp": datetime.now().isoformat()
            })
    
    return alerts

# ============================================
# 飞书通知
# ============================================

def send_feishu_alert(message: str, webhook_url: Optional[str] = None) -> bool:
    """发送飞书告警"""
    config = load_config()
    
    # 优先使用传入的 webhook，其次使用配置的
    webhook = webhook_url or config.get("alerts", {}).get("feishu_webhook")
    
    if not webhook:
        print("⚠️ 未配置飞书 Webhook")
        return False
    
    payload = {
        "msg_type": "text",
        "content": {
            "text": message
        }
    }
    
    try:
        response = requests.post(webhook, json=payload, timeout=10)
        if response.status_code == 200:
            print("✅ 飞书告警发送成功")
            return True
        else:
            print(f"❌ 飞书告警失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 飞书告警异常: {e}")
        return False

def send_feishu_card(title: str, content: str, webhook_url: Optional[str] = None) -> bool:
    """发送飞书卡片消息"""
    config = load_config()
    webhook = webhook_url or config.get("alerts", {}).get("feishu_webhook")
    
    if not webhook:
        return False
    
    payload = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": "red" if "错误" in title or "失败" in title else "blue"
            },
            "elements": [
                {"tag": "div", "text": {"tag": "plain_text", "content": content}}
            ]
        }
    }
    
    try:
        response = requests.post(webhook, json=payload, timeout=10)
        return response.status_code == 200
    except:
        return False

# ============================================
# 邮件通知
# ============================================

def send_email_alert(
    subject: str,
    body: str,
    to_email: Optional[str] = None,
    from_email: Optional[str] = None,
    smtp_server: Optional[str] = None,
    smtp_port: int = 587,
    smtp_password: Optional[str] = None
) -> bool:
    """发送邮件告警"""
    config = load_config()
    alert_config = config.get("alerts", {})
    
    # 使用配置或参数
    to_email = to_email or alert_config.get("email_to")
    from_email = from_email or alert_config.get("email_from")
    smtp_server = smtp_server or alert_config.get("smtp_server")
    smtp_password = smtp_password or alert_config.get("smtp_password")
    
    if not all([to_email, from_email, smtp_server, smtp_password]):
        print("⚠️ 邮件配置不完整")
        return False
    
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    
    msg.attach(MIMEText(body, "plain", "utf-8"))
    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(from_email, smtp_password)
            server.send_message(msg)
        print("✅ 邮件告警发送成功")
        return True
    except Exception as e:
        print(f"❌ 邮件告警失败: {e}")
        return False

# ============================================
# Webhook 通知
# ============================================

def send_webhook_alert(message: str, webhook_url: Optional[str] = None) -> bool:
    """发送 Webhook 告警"""
    config = load_config()
    webhook = webhook_url or config.get("alerts", {}).get("webhook_url")
    
    if not webhook:
        return False
    
    payload = {
        "text": message,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(webhook, json=payload, timeout=10)
        return response.status_code == 200
    except:
        return False

# ============================================
# 统一告警接口
# ============================================

def send_alert(alert: Dict, channels: List[str] = None) -> Dict[str, bool]:
    """
    发送告警到多个渠道
    
    Args:
        alert: 告警信息
        channels: 渠道列表 ["feishu", "email", "webhook"]
    
    Returns:
        各渠道发送结果
    """
    if channels is None:
        channels = ["feishu"]  # 默认只发飞书
    
    results = {}
    message = alert.get("message", "")
    title = f"Agent Monitor 告警 - {alert.get('type', 'unknown')}"
    
    for channel in channels:
        if channel == "feishu":
            results["feishu"] = send_feishu_card(title, message)
        elif channel == "email":
            results["email"] = send_email_alert(title, message)
        elif channel == "webhook":
            results["webhook"] = send_webhook_alert(message)
    
    # 保存历史
    alert["send_results"] = results
    save_alert_history(alert)
    
    return results

def process_alerts(agents: List[Dict], cron_jobs: List[Dict], channels: List[str] = None) -> List[Dict]:
    """
    检查并发送所有告警
    
    Returns:
        发送的告警列表
    """
    # 检查告警
    alerts = check_alerts(agents, cron_jobs)
    
    if not alerts:
        return []
    
    # 发送告警
    sent_alerts = []
    for alert in alerts:
        # 只发送高严重级别的告警
        if alert.get("severity") in ["high", "medium"]:
            results = send_alert(alert, channels)
            if any(results.values()):
                sent_alerts.append(alert)
    
    return sent_alerts

# ============================================
# CLI 接口
# ============================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent Monitor 告警模块")
    parser.add_argument("--test-feishu", action="store_true", help="测试飞书通知")
    parser.add_argument("--test-email", action="store_true", help="测试邮件通知")
    parser.add_argument("--check", action="store_true", help="检查当前告警")
    
    args = parser.parse_args()
    
    if args.test_feishu:
        send_feishu_alert("🧪 Agent Monitor 测试告警\n这是一条测试消息")
    
    elif args.test_email:
        send_email_alert("Agent Monitor 测试", "这是一条测试邮件")
    
    elif args.check:
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
                print(f"  [{a['severity']}] {a['message'][:50]}...")
        else:
            print("✅ 无告警")
    
    else:
        parser.print_help()