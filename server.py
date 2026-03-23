#!/usr/bin/env python3
"""
Agent Monitor HTTP Server (纯标准库，无依赖)
网页请求时自动刷新数据
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import subprocess
import json
import threading
import time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "realtime.json"
MONITOR_SCRIPT = BASE_DIR / "monitor.py"

# 缓存控制
last_refresh = 0
refresh_interval = 30  # 最小刷新间隔（秒）- 避免频繁刷新导致超时
data_lock = threading.Lock()

def should_refresh():
    """检查是否需要刷新"""
    global last_refresh
    now = time.time()
    if now - last_refresh >= refresh_interval:
        return True
    return False

def run_monitor():
    """执行数据刷新"""
    global last_refresh
    try:
        subprocess.run(
            ["python3", str(MONITOR_SCRIPT)],
            cwd=str(BASE_DIR),
            capture_output=True,
            timeout=30
        )
        last_refresh = time.time()
        return True
    except Exception as e:
        print(f"刷新失败: {e}")
        return False

class MonitorHandler(SimpleHTTPRequestHandler):
    """自定义请求处理器"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)
    
    def end_headers(self):
        """添加 CORS 头"""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()
    
    def do_OPTIONS(self):
        """处理 OPTIONS 预检请求"""
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        """处理 GET 请求"""
        if self.path == "/":
            # 返回 index.html
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(BASE_DIR / "index.html", "rb") as f:
                self.wfile.write(f.read())
        elif self.path == "/data/realtime.json" or self.path.startswith("/data/realtime.json?"):
            # 获取数据（后台刷新，先返回缓存）
            if should_refresh():
                # 后台刷新，不阻塞请求
                threading.Thread(target=run_monitor, daemon=True).start()
            
            if DATA_FILE.exists():
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                with open(DATA_FILE, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'{"error": "no data"}')
        else:
            # 其他静态文件
            super().do_GET()
    
    def do_POST(self):
        """处理 POST 请求"""
        if self.path == "/api/refresh":
            # 强制刷新
            with data_lock:
                success = run_monitor()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            result = json.dumps({
                "success": success,
                "time": datetime.now().isoformat()
            })
            self.wfile.write(result.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """简化日志"""
        msg = args[0] if args else ""
        if isinstance(msg, str):
            if "/data/realtime.json" in msg:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 数据请求")
            elif msg.startswith('"GET / "') or msg.startswith('"POST'):
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg[:50]}")

def main():
    host = "0.0.0.0"
    port = 9001
    
    print(f"\n🦞 Agent Monitor Server 启动...")
    print(f"📍 访问地址: http://localhost:{port}")
    print(f"⚡ 网页请求时自动刷新数据（最小间隔 {refresh_interval}秒）")
    print(f"\n按 Ctrl+C 停止\n")
    
    server = HTTPServer((host, port), MonitorHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        server.shutdown()

if __name__ == "__main__":
    main()