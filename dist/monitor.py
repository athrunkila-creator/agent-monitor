#!/usr/bin/env python3
"""
Agent Monitor - 实时监控 OpenClaw agents 状态
支持：实时状态、当前任务、任务进度、Token 消耗统计
"""
import json
import subprocess
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# 配置文件路径
CONFIG_FILE = Path(__file__).parent / "config.json"

def load_config():
    """加载配置文件"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}

# 加载配置
CONFIG = load_config()

# Agent 配置（从配置文件读取，提供默认值）
AGENTS_CONFIG = CONFIG.get("agents", {
    "main": {"name": "小龙虾", "emoji": "🦞"},
    "trading-shrimp": {"name": "交易虾", "emoji": "📈"},
    "news-shrimp": {"name": "新闻虾", "emoji": "📰"},
    "research-shrimp": {"name": "行研虾", "emoji": "📊"},
    "learning-shrimp": {"name": "学习虾", "emoji": "📚"},
    "business-shrimp": {"name": "商业虾", "emoji": "💼"},
    "coding-shrimp": {"name": "编程虾", "emoji": "💻"},
})

# Skill 到 Agent 的映射（从配置文件读取）
SKILL_AGENTS = CONFIG.get("skill_agents", {
    "trading-agents": "trading-shrimp",
    "skill-creator": "main",
    "super-websearch": "main",
    "openviking-memory": "main",
    "a-stock-trading": "trading-shrimp",
    "performance": "main",
})

def run_cmd(cmd, timeout=30):
    """执行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout, result.returncode
    except subprocess.TimeoutExpired:
        return "", 1
    except Exception as e:
        return f"Error: {e}", 1

def parse_json_output(output):
    """从输出中解析 JSON"""
    try:
        json_start = output.find('{')
        if json_start >= 0:
            depth = 0
            for i, c in enumerate(output[json_start:]):
                if c == '{':
                    depth += 1
                elif c == '}':
                    depth -= 1
                    if depth == 0:
                        return json.loads(output[json_start:json_start + i + 1])
        return None
    except:
        return None

def get_sessions():
    """获取所有活跃 sessions"""
    output, code = run_cmd("openclaw sessions --all-agents --active 1440 --json 2>/dev/null")
    data = parse_json_output(output)
    return data.get("sessions", []) if data else []

def get_cron_jobs():
    """获取定时任务列表"""
    output, code = run_cmd("openclaw cron list --json 2>/dev/null")
    data = parse_json_output(output)
    return data.get("jobs", []) if data else []

def get_subagents():
    """获取子 agent 列表"""
    output, code = run_cmd("openclaw subagents list --recent-minutes 60 --json 2>/dev/null")
    data = parse_json_output(output)
    return data.get("subagents", []) if data else []

def extract_user_message(content):
    """从消息内容提取用户说的话或任务描述"""
    if not content:
        return None, None  # (消息类型, 消息内容)
    
    # 如果是列表，提取文本
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text = item.get("text", "")
                if not text:
                    continue
                
                # 检查是否是定时任务消息
                if text.startswith('[cron:'):
                    # 格式: [cron:job-id job-name] 任务描述
                    match = re.match(r'\[cron:[^\]]+\s+([^\]]+)\]\s*(.*)', text)
                    if match:
                        job_name = match.group(1)
                        task_desc = match.group(2)[:100]
                        return "⏰ 定时任务", f"{job_name}: {task_desc}" if task_desc else job_name
                
                # 检查是否是系统消息（包含用户实际消息）
                if text.startswith('System:') or text.startswith('[Queued'):
                    # 提取用户实际消息
                    lines = text.split('\n\n')
                    user_msg = None
                    
                    for part in reversed(lines):
                        part = part.strip()
                        # 跳过系统和元数据行
                        if not part or part.startswith('System:') or part.startswith('Conversation') or part.startswith('Sender') or part.startswith('Replied') or part.startswith('```'):
                            continue
                        # 跳过纯元数据块
                        if part.startswith('{') and part.endswith('}'):
                            continue
                        # 跳过只有 [xxx] 的行
                        if re.match(r'^\[[^\]]+\]$', part):
                            continue
                        # 这是用户消息
                        user_msg = part
                        break
                    
                    if user_msg:
                        # 清理消息内容
                        # 1. 移除 markdown 代码块
                        user_msg = re.sub(r'```[\s\S]*?```', '[代码块]', user_msg)
                        # 2. 移除多余的换行
                        user_msg = re.sub(r'\n+', ' ', user_msg)
                        # 3. 截取前 150 个字符
                        if len(user_msg) > 150:
                            user_msg = user_msg[:150] + "..."
                        return "💬 用户对话", user_msg
                
                # 普通用户消息
                if len(text) > 5:
                    # 清理消息
                    clean_text = re.sub(r'```[\s\S]*?```', '[代码块]', text)
                    clean_text = re.sub(r'\n+', ' ', clean_text)
                    if len(clean_text) > 150:
                        clean_text = clean_text[:150] + "..."
                    return "💬 用户对话", clean_text
    
    return None, None

def get_current_task_from_session(session):
    """从 session transcript 中获取当前任务信息"""
    session_id = session.get("sessionId")
    agent_id = session.get("agentId", "main")
    
    # 构建 transcript 路径
    transcript_path = os.path.expanduser(f"~/.openclaw/agents/{agent_id}/sessions/{session_id}.jsonl")
    
    if not os.path.exists(transcript_path):
        return None
    
    try:
        with open(transcript_path, 'r') as f:
            lines = f.readlines()
            
        if not lines:
            return None
            
        task_type = None
        task_content = None
        tool_calls = 0
        last_tools = []
        
        # 从最后往前分析
        for line in reversed(lines[-300:]):
            try:
                event = json.loads(line)
                
                # 处理消息事件
                if event.get("type") == "message":
                    msg = event.get("message", {})
                    role = msg.get("role", "")
                    content = msg.get("content", [])
                    
                    # 用户消息
                    if role == "user" and not task_content:
                        task_type, task_content = extract_user_message(content)
                    
                    # 助手消息 - 统计工具调用
                    if role == "assistant" and isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict):
                                # 支持两种格式: tool_use 和 toolCall
                                item_type = item.get("type", "")
                                if item_type in ("tool_use", "toolCall"):
                                    tool_calls += 1
                                    tool_name = item.get("name", item.get("toolName", "unknown"))
                                    # 简化工具名称
                                    tool_short = tool_name.split('.')[-1] if '.' in tool_name else tool_name
                                    if tool_short not in last_tools and len(last_tools) < 5:
                                        last_tools.append(tool_short)
                                        
            except:
                pass
        
        # 构建任务描述
        if task_content:
            parts = []
            # 添加任务类型和内容
            parts.append(task_content)
            
            # 添加工具调用信息
            if last_tools:
                tools_str = " → ".join(last_tools[:4])
                parts.append(f"🔧 {tools_str}")
            
            # 计算进度
            progress = min(90, 10 + tool_calls * 8)
            
            return {
                "description": "\n".join(parts),
                "progress": progress,
                "progress_text": f"已调用 {tool_calls} 个工具"
            }
            
    except Exception as e:
        print(f"  读取错误: {e}")
    
    return None

def get_day_start_end_timestamps(target_date: str = None):
    """
    获取指定日期的开始和结束时间戳（秒）
    
    Args:
        target_date: 日期字符串 YYYY-MM-DD，None 表示今天
    
    Returns:
        (start_ts, end_ts): 当天 00:00:00 和 23:59:59 的时间戳
    """
    from datetime import datetime, timezone, timedelta
    tz_sh = timezone(timedelta(hours=8))
    
    if target_date:
        target = datetime.strptime(target_date, "%Y-%m-%d").replace(tzinfo=tz_sh)
    else:
        target = datetime.now(tz_sh)
    
    start = target.replace(hour=0, minute=0, second=0, microsecond=0)
    end = target.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    return int(start.timestamp()), int(end.timestamp())


def count_tokens_from_transcripts(target_date: str = None):
    """
    直接从 transcript 文件统计 token（最可靠的方式）
    
    扫描所有 agent 的 transcript 文件，按时间戳过滤指定日期的事件。
    这是比依赖 session.totalTokens 更可靠的方法。
    
    Returns:
        dict: {agent_id: token_count}
    """
    day_start, day_end = get_day_start_end_timestamps(target_date)
    agents_dir = Path.home() / '.openclaw' / 'agents'
    agent_tokens = {}
    
    if not agents_dir.exists():
        return agent_tokens
    
    for agent_dir in agents_dir.iterdir():
        if not agent_dir.is_dir():
            continue
        agent_id = agent_dir.name
        sessions_dir = agent_dir / 'sessions'
        
        if not sessions_dir.exists():
            continue
        
        total_chars_today = 0
        
        for transcript in sessions_dir.glob('*.jsonl'):
            try:
                with open(transcript, 'r') as f:
                    for line in f:
                        try:
                            event = json.loads(line)
                            ts_str = event.get('timestamp', '')
                            if ts_str:
                                ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                                ts_unix = int(ts.timestamp())
                                if day_start <= ts_unix <= day_end:
                                    total_chars_today += len(line)
                        except:
                            pass
            except:
                pass
        
        # 估算：1 token ≈ 4 字符
        if total_chars_today > 0:
            agent_tokens[agent_id] = total_chars_today // 4
    
    return agent_tokens


def get_token_usage_from_session(session, target_date: str = None):
    """
    从 session 中提取 token 使用量（统计指定日期的数据）
    
    Args:
        session: session 对象
        target_date: 日期字符串 YYYY-MM-DD，None 表示今天
    
    Returns:
        token 数量
    """
    # 直接从 session 对象获取 totalTokens
    total = session.get("totalTokens", 0)
    if total:
        return total
    
    # 后备：尝试从 totalTokensFresh 获取
    total_fresh = session.get("totalTokensFresh", 0)
    if total_fresh:
        return total_fresh
    
    # 最后后备：从 transcript 文件估算（仅统计指定日期的事件）
    session_id = session.get("sessionId")
    agent_id = session.get("agentId", "main")
    transcript_path = os.path.expanduser(f"~/.openclaw/agents/{agent_id}/sessions/{session_id}.jsonl")
    
    if os.path.exists(transcript_path):
        try:
            day_start, day_end = get_day_start_end_timestamps(target_date)
            total_chars = 0
            
            with open(transcript_path, 'r') as f:
                for line in f:
                    try:
                        event = json.loads(line)
                        timestamp = event.get("timestamp", "")
                        if timestamp:
                            # 解析 ISO 8601 时间戳
                            ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                            ts_unix = int(ts.timestamp())
                            # 只统计指定日期范围内的事件
                            if day_start <= ts_unix <= day_end:
                                total_chars += len(line)
                    except:
                        continue
            
            # 估算：1 token ≈ 4 字符（中文）
            return total_chars // 4
        except:
            pass
    
    return 0

def analyze_agents(sessions, cron_jobs, subagents, target_date: str = None):
    """分析所有 agent 状态"""
    agents = {}
    now = datetime.now()
    
    # 【关键改进】直接从 transcript 文件统计 token（最可靠）
    # 不再依赖 session.totalTokens（GLM-5 返回 0）
    token_counts = count_tokens_from_transcripts(target_date)
    
    # 初始化所有已配置的 agent
    for agent_id, config in AGENTS_CONFIG.items():
        agents[agent_id] = {
            "id": agent_id,
            "name": config["name"],
            "emoji": config["emoji"],
            "model": config["model"],
            "status": "idle",
            "sessions": 0,
            "last_activity": None,
            "last_activity_text": "-",
            "tasks": [],
            "current_task": None,
            "current_task_progress": 0,
            "current_task_text": "",
            "tokens_today": token_counts.get(agent_id, 0),  # 使用 transcript 统计的 token
            "active_run": None,
        }
    
    # 分析 sessions
    for session in sessions:
        agent_id = session.get("agentId", "main")
        if agent_id not in agents:
            agents[agent_id] = {
                "id": agent_id,
                "name": agent_id,
                "emoji": "🤖",
                "model": "unknown",
                "status": "idle",
                "sessions": 0,
                "last_activity": None,
                "last_activity_text": "-",
                "tasks": [],
                "current_task": None,
                "current_task_progress": 0,
                "current_task_text": "",
                "tokens_today": token_counts.get(agent_id, 0),  # 使用 transcript 统计的 token
                "active_run": None,
            }
        
        agents[agent_id]["sessions"] += 1
        
        # 更新最后活动时间
        updated_at = session.get("updatedAt", 0)
        if updated_at:
            if not agents[agent_id]["last_activity"] or updated_at > agents[agent_id]["last_activity"]:
                agents[agent_id]["last_activity"] = updated_at
                activity_time = datetime.fromtimestamp(updated_at / 1000)
                age = now - activity_time
                if age.total_seconds() < 60:
                    agents[agent_id]["last_activity_text"] = "刚刚"
                elif age.total_seconds() < 3600:
                    agents[agent_id]["last_activity_text"] = f"{int(age.total_seconds() / 60)}分钟前"
                else:
                    agents[agent_id]["last_activity_text"] = f"{int(age.total_seconds() / 3600)}小时前"
        
        # 检查是否活跃（10分钟内）
        age_ms = session.get("ageMs", 999999999)
        if age_ms < 600000:  # 10分钟内
            agents[agent_id]["status"] = "active"
        
        # 获取当前任务（10分钟内的 session）
        if age_ms < 600000:
            current_task = get_current_task_from_session(session)
            if current_task:
                if not agents[agent_id]["current_task"] or session.get("updatedAt", 0) > agents[agent_id].get("_last_task_time", 0):
                    agents[agent_id]["current_task"] = current_task["description"]
                    agents[agent_id]["current_task_progress"] = current_task["progress"]
                    agents[agent_id]["current_task_text"] = current_task["progress_text"]
                    agents[agent_id]["_last_task_time"] = session.get("updatedAt", 0)
                    if current_task["progress"] > 10:  # 有工具调用的才算busy
                        agents[agent_id]["status"] = "busy"
        
        # 分析定时任务
    for job in cron_jobs:
        agent_id = job.get("agentId", "main")
        job_name = job.get("name", "unknown")
        job_state = job.get("state", {})
        
        target_agent = agent_id if agent_id in agents else "main"
        
        task = {
            "type": "cron",
            "name": job_name,
            "schedule": job.get("schedule", {}).get("expr", job.get("schedule", {}).get("kind", "-")),
            "next_run": None,
            "status": job_state.get("lastStatus", "unknown"),
        }
        
        next_run_ms = job_state.get("nextRunAtMs", 0)
        if next_run_ms:
            next_run = datetime.fromtimestamp(next_run_ms / 1000)
            task["next_run"] = next_run.strftime("%H:%M")
        
        if job_state.get("runningAtMs"):
            agents[target_agent]["status"] = "busy"
            agents[target_agent]["active_run"] = f"⏳ {job_name}"
            agents[target_agent]["current_task"] = f"⏰ 定时任务\n📝 {job_name}"
            agents[target_agent]["current_task_progress"] = 50
            agents[target_agent]["current_task_text"] = "执行中..."
        
        agents[target_agent]["tasks"].append(task)
    
    # 分析子 agent
    for sub in subagents:
        skill_id = sub.get("skillId", "")
        status = sub.get("status", "unknown")
        
        target_agent = SKILL_AGENTS.get(skill_id, "main")
        
        if status in ["running", "pending"]:
            agents[target_agent]["status"] = "busy"
            agents[target_agent]["active_run"] = f"🔄 {skill_id}"
            agents[target_agent]["current_task"] = f"🔄 子任务\n📝 {skill_id}"
            agents[target_agent]["current_task_progress"] = 30
            agents[target_agent]["current_task_text"] = status
        
        task = {
            "type": "skill",
            "name": skill_id,
            "status": status,
            "started": sub.get("startedAt", "-"),
        }
        agents[target_agent]["tasks"].append(task)
    
    # 清理临时字段
    for agent_id in agents:
        if "_last_task_time" in agents[agent_id]:
            del agents[agent_id]["_last_task_time"]
    
    return agents

def collect_metrics(target_date: str = None):
    """
    收集所有指标
    
    Args:
        target_date: 日期字符串 YYYY-MM-DD，None 表示今天
    """
    if target_date:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 开始收集数据（日期：{target_date}）...")
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 开始收集数据（今天）...")
    
    sessions = get_sessions()
    print(f"  - Sessions: {len(sessions)}")
    
    cron_jobs = get_cron_jobs()
    print(f"  - Cron jobs: {len(cron_jobs)}")
    
    subagents = get_subagents()
    print(f"  - Subagents: {len(subagents)}")
    
    agents = analyze_agents(sessions, cron_jobs, subagents, target_date)
    
    # 统计主 Agent 和子 Agent
    primary_agents = [a for a in agents.values() if AGENTS_CONFIG.get(a["id"], {}).get("is_primary", True)]
    subagent_list = [a for a in agents.values() if not AGENTS_CONFIG.get(a["id"], {}).get("is_primary", True)]
    
    output = {
        "timestamp": datetime.now().isoformat(),
        "agents": agents,
        "summary": {
            "total_agents": len(agents),
            "active_agents": sum(1 for a in agents.values() if a["status"] == "active"),
            "busy_agents": sum(1 for a in agents.values() if a["status"] == "busy"),
            "primary_agents": len(primary_agents),
            "primary_active": sum(1 for a in primary_agents if a["status"] in ["active", "busy"]),
            "subagents": len(subagent_list),
            "subagents_active": sum(1 for a in subagent_list if a["status"] in ["active", "busy"]),
            "total_sessions": len(sessions),
            "total_tokens": sum(a["tokens_today"] for a in agents.values()),
            "cron_jobs": len(cron_jobs),
        }
    }
    
    with open(DATA_DIR / "realtime.json", "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 数据已保存")
    
    return output

def main():
    import sys
    # 支持命令行指定日期：python monitor.py [YYYY-MM-DD]
    target_date = sys.argv[1] if len(sys.argv) > 1 else None
    collect_metrics(target_date)

if __name__ == "__main__":
    main()