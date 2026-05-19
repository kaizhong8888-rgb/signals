#!/usr/bin/env python3
"""
量化信号服务 - 轻量HTTP服务器

提供：
1. 落地页展示（index.html）
2. /api/signal 接口返回最新信号数据
3. /api/history 接口返回历史信号记录

用法: python3 server.py [--port 8080]
"""

import json
import os
import sys
import argparse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from datetime import datetime

BUSINESS_DIR = Path.home() / 'Business'
WEB_DIR = BUSINESS_DIR / 'quant_signal_service' / 'web'
REPORTS_DIR = BUSINESS_DIR / 'quant_signal_service' / 'reports'


class SignalHandler(SimpleHTTPRequestHandler):
    """自定义HTTP请求处理器"""

    def __init__(self, *args, **kwargs):
        self.directory = str(WEB_DIR)
        super().__init__(*args, directory=self.directory, **kwargs)

    def do_GET(self):
        """处理GET请求"""
        if self.path == '/api/signal':
            self._serve_latest_signal()
        elif self.path == '/api/history':
            self._serve_history()
        elif self.path == '/':
            self._serve_landing()
        else:
            super().do_GET()

    def _serve_landing(self):
        """返回落地页HTML"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        html_path = WEB_DIR / 'index.html'
        if html_path.exists():
            with open(html_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.wfile.write(b'<h1>Quant Signal Service</h1><p>Landing page not found</p>')

    def _serve_latest_signal(self):
        """返回最新信号数据"""
        latest_path = REPORTS_DIR / 'latest_signal.json'
        if latest_path.exists():
            with open(latest_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self._json_response(data)
        else:
            self._json_response({'error': 'No signal data available'}, 404)

    def _serve_history(self):
        """返回历史信号列表"""
        history = []
        if REPORTS_DIR.exists():
            for f in sorted(REPORTS_DIR.glob('signal_*.json')):
                try:
                    with open(f, 'r', encoding='utf-8') as fh:
                        data = json.load(fh)
                        history.append({
                            'date': data.get('date'),
                            'total_signals': data.get('total_signals'),
                            'strong_signals': data.get('strong_signals'),
                            'top_pick': data['signals'][0]['name'] if data.get('signals') else None,
                        })
                except (json.JSONDecodeError, KeyError):
                    continue
        self._json_response({'history': history[-30:]})  # 最近30天

    def _json_response(self, data: dict, status: int = 200):
        """返回JSON响应"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def log_message(self, format, *args):
        """自定义日志格式"""
        sys.stderr.write(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}\n")


def main():
    parser = argparse.ArgumentParser(description='量化信号服务HTTP服务器')
    parser.add_argument('--port', type=int, default=8080, help='端口号 (默认8080)')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='绑定地址 (默认127.0.0.1)')
    args = parser.parse_args()

    server = HTTPServer((args.host, args.port), SignalHandler)

    print(f"=" * 60)
    print(f"  量化信号服务已启动")
    print(f"  落地页: http://{args.host}:{args.port}")
    print(f"  API:    http://{args.host}:{args.port}/api/signal")
    print(f"  历史:   http://{args.host}:{args.port}/api/history")
    print(f"  按 Ctrl+C 停止")
    print(f"=" * 60)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止")
        server.shutdown()


if __name__ == '__main__':
    main()
