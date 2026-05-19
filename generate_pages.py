#!/usr/bin/env python3
"""
GitHub Pages HTML 生成器

读取 reports/latest_signal.json，生成 index.html 和 subscribe.html，
用于推送到 https://github.com/kaizhong8888-rgb/signals 的 GitHub Pages 站点。

用法:
    python3 generate_pages.py              # 输出到当前目录
    python3 generate_pages.py --output-dir /path/to/output
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


PROJECT_DIR = Path(__file__).resolve().parent
REPORTS_DIR = PROJECT_DIR / 'reports'


def load_latest_signal() -> Optional[dict]:
    """加载最新信号数据"""
    signal_path = REPORTS_DIR / 'latest_signal.json'
    if not signal_path.exists():
        print(f"[ERROR] 信号文件不存在: {signal_path}")
        return None
    with open(signal_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_index_html(data: dict) -> str:
    """生成 index.html"""
    today = data['date']
    total = data['total_signals']
    strong = data['strong_signals']
    moderate = data['moderate_signals']
    ai_positive = data['market_summary']['ai_positive_growth']
    signals = data['signals']

    # 信号卡片
    cards = ''
    for i, s in enumerate(signals, 1):
        is_strong = s['strength'] == 'STRONG'
        border_color = '#10b981' if is_strong else '#f59e0b'
        badge_bg = 'rgba(16,185,129,0.15)' if is_strong else 'rgba(245,158,11,0.15)'
        badge_color = '#10b981' if is_strong else '#f59e0b'
        badge_label = '★★★ 强烈' if is_strong else '★★ 关注'

        profit_growth = s.get('profit_growth', 0)
        profit_sign = '+' if profit_growth >= 0 else ''
        profit_color = '#10b981' if profit_growth >= 0 else '#ef4444'

        cards += f"""        <div class="signal-card" style="border-left-color: {border_color};">
            <div class="signal-top">
                <div>
                    <div class="signal-name">{i}. {s['name']}</div>
                    <div class="signal-code">{s['code']}</div>
                </div>
                <span class="signal-badge" style="background:{badge_bg};color:{badge_color};border-color:{badge_color};">{badge_label}</span>
            </div>
            <div class="signal-metrics">
                <div class="metric"><span class="metric-label">现价</span><span class="metric-value">¥{s['price']:.2f}</span></div>
                <div class="metric"><span class="metric-label">PE</span><span class="metric-value">{s['pe']:.1f}</span></div>
                <div class="metric"><span class="metric-label">ROE</span><span class="metric-value">{s['roe']:.1f}%</span></div>
                <div class="metric"><span class="metric-label">利润增速</span><span class="metric-value" style="color:{profit_color};">{profit_sign}{profit_growth:.1f}%</span></div>
            </div>
            <div class="signal-reason">\U0001f4a1 {s['reason']}</div>
        </div>
"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI量化信号 | {today}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif; background: #0a0e1a; color: #f1f5f9; line-height: 1.6; }}
.container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
header {{ padding: 40px 0 32px; border-bottom: 1px solid #1e293b; margin-bottom: 32px; }}
.logo-row {{ display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }}
.logo-icon {{ width: 40px; height: 40px; background: linear-gradient(135deg, #6366f1, #818cf8); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; }}
h1 {{ font-size: 28px; font-weight: 700; }}
.subtitle {{ color: #94a3b8; font-size: 15px; }}
.date-badge {{ display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px; background: rgba(99,102,241,0.15); border: 1px solid rgba(99,102,241,0.3); border-radius: 20px; font-size: 13px; color: #a5b4fc; margin-top: 16px; }}
.date-badge::before {{ content: ""; width: 6px; height: 6px; background: #10b981; border-radius: 50%; }}
.stats-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 32px; }}
.stat-card {{ background: #111827; border: 1px solid #1e293b; border-radius: 12px; padding: 20px; text-align: center; }}
.stat-value {{ font-size: 32px; font-weight: 700; }}
.stat-label {{ font-size: 13px; color: #64748b; margin-top: 4px; }}
.signal-card {{ background: #111827; border: 1px solid #1e293b; border-radius: 12px; border-left: 3px solid; padding: 20px; margin-bottom: 12px; }}
.signal-top {{ display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 12px; }}
.signal-name {{ font-size: 17px; font-weight: 600; }}
.signal-code {{ font-size: 13px; color: #64748b; font-family: monospace; }}
.signal-badge {{ padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; border: 1px solid; }}
.signal-metrics {{ display: flex; gap: 24px; margin-bottom: 12px; flex-wrap: wrap; }}
.metric {{ display: flex; flex-direction: column; }}
.metric-label {{ font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }}
.metric-value {{ font-size: 15px; font-weight: 600; font-family: monospace; }}
.signal-reason {{ padding: 10px 14px; background: rgba(99,102,241,0.06); border-radius: 8px; font-size: 14px; color: #94a3b8; border-left: 2px solid #6366f1; }}
.cta-section {{ background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(16,185,129,0.08)); border: 1px solid rgba(99,102,241,0.2); border-radius: 12px; padding: 32px; text-align: center; margin: 40px 0; }}
.cta-price {{ display: flex; align-items: baseline; justify-content: center; gap: 4px; margin-bottom: 20px; }}
.cta-price .amount {{ font-size: 40px; font-weight: 800; color: #10b981; }}
.cta-price .period {{ font-size: 15px; color: #64748b; }}
.cta-features {{ display: flex; justify-content: center; gap: 24px; margin-bottom: 24px; flex-wrap: wrap; color: #94a3b8; font-size: 14px; }}
.cta-button {{ display: inline-flex; align-items: center; padding: 14px 32px; background: linear-gradient(135deg, #6366f1, #818cf8); color: #fff; font-size: 16px; font-weight: 600; border-radius: 10px; text-decoration: none; border: none; cursor: pointer; }}
.disclaimer {{ padding: 16px; background: rgba(245,158,11,0.08); border: 1px solid rgba(245,158,11,0.2); border-radius: 8px; font-size: 13px; color: #64748b; margin-bottom: 32px; }}
footer {{ padding: 24px 0; border-top: 1px solid #1e293b; text-align: center; font-size: 13px; color: #64748b; }}
@media (max-width: 640px) {{ .stats-grid {{ grid-template-columns: repeat(2, 1fr); }} }}
</style>
</head>
<body>
<div class="container">
    <header>
        <div class="logo-row"><div class="logo-icon">\U0001f4ca</div><h1>AI量化信号</h1></div>
        <p class="subtitle">AI选股 + 高股息策略 · 双重验证</p>
        <div class="date-badge">{today}</div>
    </header>
    <div class="stats-grid">
        <div class="stat-card"><div class="stat-value">{total}</div><div class="stat-label">信号总数</div></div>
        <div class="stat-card"><div class="stat-value" style="color:#10b981">{strong}</div><div class="stat-label">强烈 ★★★</div></div>
        <div class="stat-card"><div class="stat-value" style="color:#f59e0b">{moderate}</div><div class="stat-label">关注 ★★</div></div>
        <div class="stat-card"><div class="stat-value">{ai_positive}</div><div class="stat-label">AI正成长股</div></div>
    </div>
    <div class="section">
        <h2 style="font-size:18px;font-weight:600;margin-bottom:16px;display:flex;align-items:center;gap:8px;"><span style="width:8px;height:8px;border-radius:50%;background:#6366f1;"></span>今日选股信号</h2>
{cards}    </div>
    <div class="cta-section">
        <h2 style="font-size:22px;font-weight:700;margin-bottom:8px;">订阅每日量化信号</h2>
        <p style="color:#94a3b8;margin-bottom:24px;font-size:15px;">每个交易日盘后自动推送选股信号，双策略交叉验证</p>
        <div class="cta-price"><span class="amount">¥299</span><span class="period">/月</span></div>
        <div class="cta-features"><span>✓ 每日AI选股信号</span><span>✓ 高股息组合推荐</span><span>✓ 持仓诊断与建议</span><span>✓ 微信推送通知</span></div>
        <a href="subscribe.html" class="cta-button" style="text-decoration:none;">立即订阅 ¥299/月 →</a>
        <p style="margin-top:16px;font-size:13px;color:#64748b;">已验证策略年化收益 ~26% · 最大回撤 ~25% · 夏普比率 1.24</p>
    </div>
    <div class="disclaimer"><strong style="color:#f59e0b">⚠️ 风险提示：</strong>本报告基于量化模型自动生成，仅供学习研究，不构成投资建议。投资有风险，入市需谨慎。</div>
    <footer><p>AI量化信号系统 · 数据来源：腾讯财经API + 东方财富</p></footer>
</div>
</body>
</html>"""
    return html


def generate_subscribe_html(data: dict) -> str:
    """生成 subscribe.html（静态，仅引用最新信号计数）"""
    total = data['total_signals']
    strong = data['strong_signals']

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>订阅AI量化信号 | 299元/月</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif; background: #0a0e1a; color: #f1f5f9; line-height: 1.6; }}
.container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
header {{ padding: 40px 0 32px; text-align: center; }}
.logo-row {{ display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 16px; }}
.logo-icon {{ width: 48px; height: 48px; background: linear-gradient(135deg, #6366f1, #818cf8); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; }}
h1 {{ font-size: 24px; font-weight: 700; }}
.subtitle {{ color: #94a3b8; font-size: 14px; margin-top: 8px; }}
.price-card {{ background: linear-gradient(135deg, rgba(99,102,241,0.12), rgba(16,185,129,0.08)); border: 1px solid rgba(99,102,241,0.25); border-radius: 16px; padding: 40px 32px; text-align: center; margin: 32px 0; }}
.price {{ font-size: 48px; font-weight: 800; color: #10b981; }}
.period {{ font-size: 16px; color: #64748b; }}
.features {{ text-align: left; margin: 24px 0; }}
.feature {{ padding: 8px 0; color: #cbd5e1; font-size: 15px; }}
.feature::before {{ content: "✓ "; color: #10b981; font-weight: bold; }}
.stats {{ display: flex; justify-content: center; gap: 24px; margin: 24px 0; padding: 16px; background: rgba(255,255,255,0.03); border-radius: 12px; }}
.stat {{ text-align: center; }}
.stat-value {{ font-size: 20px; font-weight: 700; color: #a5b4fc; }}
.stat-label {{ font-size: 12px; color: #64748b; }}
.signal-preview {{ background: #111827; border: 1px solid #1e293b; border-radius: 12px; padding: 20px; margin: 24px 0; text-align: left; }}
.signal-preview h3 {{ font-size: 15px; color: #94a3b8; margin-bottom: 12px; }}
.signal-preview .count {{ font-size: 24px; font-weight: 700; color: #10b981; }}
.contact-section {{ margin: 40px 0; padding: 32px; background: #111827; border: 1px solid #1e293b; border-radius: 16px; text-align: center; }}
.contact-section h3 {{ font-size: 18px; margin-bottom: 24px; }}
.step {{ display: flex; align-items: flex-start; gap: 16px; text-align: left; margin-bottom: 20px; }}
.step-num {{ flex-shrink: 0; width: 32px; height: 32px; background: linear-gradient(135deg, #6366f1, #818cf8); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px; }}
.step-text {{ padding-top: 4px; }}
.step-text strong {{ display: block; margin-bottom: 2px; }}
.step-text span {{ color: #94a3b8; font-size: 14px; }}
.cta-button {{ display: inline-flex; align-items: center; gap: 8px; padding: 16px 36px; background: linear-gradient(135deg, #10b981, #059669); color: #fff; font-size: 18px; font-weight: 600; border-radius: 12px; border: none; cursor: pointer; text-decoration: none; margin-top: 16px; }}
.cta-button:hover {{ opacity: 0.9; }}
.disclaimer {{ padding: 16px; background: rgba(245,158,11,0.08); border: 1px solid rgba(245,158,11,0.2); border-radius: 8px; font-size: 13px; color: #64748b; margin-bottom: 32px; }}
footer {{ padding: 24px 0; border-top: 1px solid #1e293b; text-align: center; font-size: 13px; color: #64748b; }}
.back-link {{ display: inline-block; color: #6366f1; text-decoration: none; margin-bottom: 24px; font-size: 14px; }}
.back-link:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
<div class="container">
    <a href="index.html" class="back-link">← 返回信号首页</a>

    <header>
        <div class="logo-row"><div class="logo-icon">\U0001f4ca</div><h1>AI量化信号</h1></div>
        <p class="subtitle">AI选股 + 高股息策略 · 双重验证</p>
    </header>

    <div class="price-card">
        <div class="price">¥299 <span class="period">/月</span></div>
        <div class="features">
            <div class="feature">每日AI选股信号（盘后推送）</div>
            <div class="feature">高股息组合推荐</div>
            <div class="feature">持仓诊断与调仓建议</div>
            <div class="feature">微信推送通知</div>
        </div>
        <div class="stats">
            <div class="stat"><div class="stat-value">~26%</div><div class="stat-label">年化收益</div></div>
            <div class="stat"><div class="stat-value">~25%</div><div class="stat-label">最大回撤</div></div>
            <div class="stat"><div class="stat-value">1.24</div><div class="stat-label">夏普比率</div></div>
        </div>
    </div>

    <div class="signal-preview">
        <h3>今日信号概览</h3>
        <p><span class="count">{total}</span> 个信号 · <span class="count">{strong}</span> 个强烈信号</p>
        <p style="color:#64748b;font-size:13px;margin-top:8px;">订阅后每日查看完整信号详情</p>
    </div>

    <div class="contact-section">
        <h3>如何订阅</h3>
        <div class="step">
            <div class="step-num">1</div>
            <div class="step-text"><strong>扫码关注公众号</strong><span>关注「AI量化信号」公众号</span></div>
        </div>
        <div class="step">
            <div class="step-num">2</div>
            <div class="step-text"><strong>发送"订阅"</strong><span>在公众号后台发送"订阅"获取联系方式</span></div>
        </div>
        <div class="step">
            <div class="step-num">3</div>
            <div class="step-text"><strong>确认订阅</strong><span>通过微信完成订阅，每日盘后自动推送信号</span></div>
        </div>
        <a href="https://mp.weixin.qq.com/" target="_blank" class="cta-button">前往微信公众号 →</a>
    </div>

    <div class="disclaimer"><strong style="color:#f59e0b">⚠️ 风险提示：</strong>本报告基于量化模型自动生成，仅供学习研究，不构成投资建议。投资有风险，入市需谨慎。</div>
    <footer><p>AI量化信号系统 · 数据来源：腾讯财经API + 东方财富</p></footer>
</div>
</body>
</html>"""
    return html


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate GitHub Pages HTML from signal data')
    parser.add_argument('--output-dir', default='.',
                        help='Output directory for HTML files (default: current directory)')
    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Generating GitHub Pages HTML...")

    data = load_latest_signal()
    if data is None:
        sys.exit(1)

    # Generate index.html
    index_html = generate_index_html(data)
    index_path = output_dir / 'index.html'
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_html)
    print(f"[OK] index.html -> {index_path}")

    # Generate subscribe.html
    subscribe_html = generate_subscribe_html(data)
    subscribe_path = output_dir / 'subscribe.html'
    with open(subscribe_path, 'w', encoding='utf-8') as f:
        f.write(subscribe_html)
    print(f"[OK] subscribe.html -> {subscribe_path}")

    print(f"[OK] Generated pages for {data['date']} ({data['total_signals']} signals)")


if __name__ == '__main__':
    main()
