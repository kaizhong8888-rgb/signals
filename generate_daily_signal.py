#!/usr/bin/env python3
"""
每日量化信号生成器

结合AI选股 + 高股息策略 + 持仓诊断，生成每日信号报告。
输出：JSON + HTML（用于微信文章/网页展示）

变现路径：付费订阅（299-999元/月），知识星球，公众号付费文章
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

from typing import Optional

# 路径设置
BUSINESS_DIR = Path.home() / 'Business'
AI_PICKS_PATH = BUSINESS_DIR / 'ai_stock_picks.json'
DIVIDEND_PATH = BUSINESS_DIR / 'high_dividend_maoge_result.json'
PORTFOLIO_PATH = BUSINESS_DIR / 'portfolio-holdings.md'
REPORTS_DIR = BUSINESS_DIR / 'quant_signal_service' / 'reports'


def load_json(path: Path) -> Optional[dict]:
    """安全加载JSON文件"""
    if not path.exists():
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_daily_signal(ai_data: dict, div_data: dict) -> dict:
    """
    生成每日量化信号

    规则：
    1. AI选股Top20中过滤掉利润增速<0的（避开衰退股）
    2. 高股息策略中筛选分红可持续的
    3. 交叉验证：两个策略都选中的重点标记
    4. 给出明确的买入/持有/卖出信号
    """
    today = datetime.now().strftime('%Y-%m-%d')

    # AI选股 - 过滤负增长
    ai_picks = ai_data.get('top_picks', [])
    ai_positive_growth = [s for s in ai_picks if s.get('profit_growth', 0) > 0]

    # AI选股 - 高ROE (>15%) + 正增长（高质量成长股）
    ai_quality = [
        s for s in ai_positive_growth
        if s.get('roe', 0) > 15 and s.get('profit_growth', 0) > 15
    ]

    # AI选股 - 低估值（PE < 25）+ 正增长（价值成长）
    ai_value_growth = [
        s for s in ai_positive_growth
        if s.get('pe', 999) < 25 and s.get('profit_growth', 0) > 10
    ]

    # 高股息策略
    div_portfolio = div_data.get('portfolio', [])
    div_sustainable = [s for s in div_portfolio if s.get('sustainable', False)]

    # 交叉验证：同时在两个策略中
    ai_codes = {s['code'] for s in ai_picks}
    div_codes = {s['code'] for s in div_portfolio}
    overlap_codes = ai_codes & div_codes

    # 生成信号
    signals = []

    # 1. 高质量成长信号（AI选股Top，ROE>15%，增长>15%）
    for s in ai_quality[:5]:
        signals.append({
            'type': 'BUY',
            'strength': 'STRONG' if s['roe'] > 25 and s['profit_growth'] > 25 else 'MODERATE',
            'code': s['code'],
            'name': s['name'],
            'price': s['price'],
            'reason': f"高ROE({s['roe']}%) + 高成长({s['profit_growth']}%)，AI评分{s['score']:.2f}",
            'strategy': 'quality_growth',
            'pe': s['pe'],
            'roe': s['roe'],
            'profit_growth': s['profit_growth'],
        })

    # 2. 价值成长信号（低PE + 正增长）
    for s in ai_value_growth[:3]:
        # 跳过已经在quality中的
        if s['code'] in [x['code'] for x in ai_quality[:5]]:
            continue
        signals.append({
            'type': 'BUY',
            'strength': 'MODERATE',
            'code': s['code'],
            'name': s['name'],
            'price': s['price'],
            'reason': f"低估值(PE:{s['pe']}) + 成长({s['profit_growth']}%)",
            'strategy': 'value_growth',
            'pe': s['pe'],
            'roe': s['roe'],
            'profit_growth': s['profit_growth'],
        })

    # 3. 高股息信号
    for s in div_sustainable:
        if s['code'] in overlap_codes:
            strength = 'STRONG'  # 双策略共振
            reason = f"双策略共振！股息率{s['avg_dividend_yield']}%，ROE:{s['roe']}%，AI评分:{next((x['score'] for x in ai_picks if x['code'] == s['code']), 0):.2f}"
        else:
            strength = 'MODERATE'
            reason = f"高股息({s['avg_dividend_yield']}%) + 分红可持续，评分{s['score']}"

        signals.append({
            'type': 'BUY',
            'strength': strength,
            'code': s['code'],
            'name': s['name'],
            'price': s.get('price', 0),
            'reason': reason,
            'strategy': 'dividend',
            'pe': s.get('pe', 0),
            'roe': s.get('roe', 0),
            'profit_growth': s.get('profit_growth', 0),
        })

    # 按强度排序
    signals.sort(key=lambda x: 0 if x['strength'] == 'STRONG' else 1)

    return {
        'date': today,
        'generated_at': datetime.now().isoformat(),
        'total_signals': len(signals),
        'strong_signals': len([s for s in signals if s['strength'] == 'STRONG']),
        'moderate_signals': len([s for s in signals if s['strength'] == 'MODERATE']),
        'signals': signals,
        'market_summary': {
            'ai_total': len(ai_picks),
            'ai_positive_growth': len(ai_positive_growth),
            'ai_quality_count': len(ai_quality),
            'ai_value_growth_count': len(ai_value_growth),
            'dividend_sustainable': len(div_sustainable),
            'overlap_count': len(overlap_codes),
        }
    }


def generate_html_report(signal_data: dict) -> str:
    """生成HTML报告（可用于微信文章/网页/邮件）"""
    today = signal_data['date']
    total = signal_data['total_signals']
    strong = signal_data['strong_signals']
    moderate = signal_data['moderate_signals']
    signals = signal_data['signals']

    # 信号行HTML
    signal_rows = ''
    for i, s in enumerate(signals, 1):
        strength_color = '#e74c3c' if s['strength'] == 'STRONG' else '#f39c12'
        strength_label = '★★★ 强烈' if s['strength'] == 'STRONG' else '★★ 关注'
        signal_rows += f"""
        <tr>
            <td style="padding:12px 8px;border-bottom:1px solid #eee;">{i}</td>
            <td style="padding:12px 8px;border-bottom:1px solid #eee;">
                <strong style="color:#2c3e50;">{s['name']}</strong>
                <br><span style="color:#7f8c8d;font-size:12px;">{s['code']}</span>
            </td>
            <td style="padding:12px 8px;border-bottom:1px solid #eee;text-align:center;">
                <span style="background:{strength_color};color:#fff;padding:3px 8px;border-radius:4px;font-size:12px;">{strength_label}</span>
            </td>
            <td style="padding:12px 8px;border-bottom:1px solid #eee;text-align:center;">¥{s['price']:.2f}</td>
            <td style="padding:12px 8px;border-bottom:1px solid #eee;text-align:center;">{s['pe']:.1f}</td>
            <td style="padding:12px 8px;border-bottom:1px solid #eee;text-align:center;">{s['roe']:.1f}%</td>
            <td style="padding:12px 8px;border-bottom:1px solid #eee;">
                <span style="font-size:13px;color:#555;">{s['reason']}</span>
            </td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>量化每日信号 | {today}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif; background: #f8f9fa; color: #2c3e50; line-height: 1.6; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #1a237e 0%, #283593 100%); color: #fff; padding: 30px 20px; border-radius: 12px; margin-bottom: 24px; }}
        .header h1 {{ font-size: 24px; margin-bottom: 8px; }}
        .header .date {{ opacity: 0.8; font-size: 14px; }}
        .summary {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }}
        .summary-card {{ background: #fff; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        .summary-card .number {{ font-size: 32px; font-weight: 700; color: #1a237e; }}
        .summary-card .label {{ font-size: 13px; color: #7f8c8d; margin-top: 4px; }}
        .table-container {{ background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 24px; }}
        .table-container table {{ width: 100%; border-collapse: collapse; }}
        .table-container th {{ background: #f1f3f4; padding: 14px 8px; font-size: 13px; color: #555; text-align: center; font-weight: 600; }}
        .disclaimer {{ background: #fff3cd; padding: 16px; border-radius: 8px; font-size: 13px; color: #856404; border: 1px solid #ffeaa7; }}
        .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #999; }}
        .footer a {{ color: #1a237e; text-decoration: none; }}
        @media (max-width: 600px) {{ .summary {{ grid-template-columns: 1fr; }} table {{ font-size: 13px; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 量化每日选股信号</h1>
            <div class="date">{today} | AI选股 + 高股息策略 双重验证</div>
        </div>

        <div class="summary">
            <div class="summary-card">
                <div class="number">{total}</div>
                <div class="label">总信号数</div>
            </div>
            <div class="summary-card">
                <div class="number" style="color:#e74c3c;">{strong}</div>
                <div class="label">强烈信号 ★★★</div>
            </div>
            <div class="summary-card">
                <div class="number" style="color:#f39c12;">{moderate}</div>
                <div class="label">关注信号 ★★</div>
            </div>
        </div>

        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>排名</th>
                        <th>股票</th>
                        <th>强度</th>
                        <th>现价</th>
                        <th>PE</th>
                        <th>ROE</th>
                        <th>推荐理由</th>
                    </tr>
                </thead>
                <tbody>
                    {signal_rows}
                </tbody>
            </table>
        </div>

        <div class="disclaimer">
            <strong>⚠️ 风险提示：</strong>本报告基于量化模型自动生成，仅供学习研究，不构成投资建议。投资有风险，入市需谨慎。建议先进行充分回测验证，实盘交易前建议小资金测试。
        </div>

        <div class="footer">
            <p>由 AI量化信号系统 自动生成 | 数据来源：腾讯财经API + 东方财富</p>
            <p>订阅每日信号推送 → 关注公众号"AI量化参考" | <a href="#">付费订阅 299元/月</a></p>
        </div>
    </div>
</body>
</html>"""

    return html


def generate_wechat_article(signal_data: dict) -> str:
    """
    生成微信公众号文章格式的HTML
    （微信公众号编辑器支持内联样式HTML）
    """
    today = signal_data['date']
    signals = signal_data['signals']
    strong = signal_data['strong_signals']

    article = f"""
<section style="padding: 20px;">
    <section style="background: linear-gradient(135deg, #1a237e 0%, #283593 100%); padding: 24px 20px; border-radius: 12px; margin-bottom: 20px;">
        <h1 style="color: #fff; font-size: 22px; margin: 0 0 8px 0;">📊 量化每日选股信号</h1>
        <p style="color: rgba(255,255,255,0.85); font-size: 14px; margin: 0;">{today} | AI选股 + 高股息策略 | 强烈信号: {strong}个</p>
    </section>
"""

    for i, s in enumerate(signals, 1):
        is_strong = s['strength'] == 'STRONG'
        border_color = '#e74c3c' if is_strong else '#3498db'
        badge = '★★★' if is_strong else '★★'

        article += f"""
    <section style="border-left: 3px solid {border_color}; padding: 16px; margin-bottom: 16px; background: #f8f9fa; border-radius: 0 8px 8px 0;">
        <p style="font-size: 18px; font-weight: 600; margin: 0 0 8px 0; color: #2c3e50;">
            {i}. {s['name']} ({s['code']}) <span style="color: {border_color}; font-size: 14px;">{badge}</span>
        </p>
        <p style="margin: 0 0 12px 0; color: #555; font-size: 14px;">
            现价: ¥{s['price']:.2f} | PE: {s['pe']:.1f} | ROE: {s['roe']:.1f}% | 利润增速: {s['profit_growth']:.1f}%
        </p>
        <p style="margin: 0; padding: 10px; background: #fff; border-radius: 6px; font-size: 14px; color: #666;">
            💡 {s['reason']}
        </p>
    </section>
"""

    article += f"""
    <section style="padding: 16px; background: #fff3cd; border-radius: 8px; border: 1px solid #ffeaa7;">
        <p style="margin: 0; font-size: 13px; color: #856404;">
            ⚠️ <strong>风险提示：</strong>本报告基于量化模型自动生成，仅供学习研究，不构成投资建议。投资有风险，入市需谨慎。
        </p>
    </section>
</section>
"""

    return article


def main():
    """主流程：加载数据 -> 生成信号 -> 输出报告"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始生成每日量化信号...")

    # 加载数据
    ai_data = load_json(AI_PICKS_PATH)
    div_data = load_json(DIVIDEND_PATH)

    if not ai_data:
        print("[ERROR] 未找到AI选股数据，请先运行 ai_stock_picker.py")
        sys.exit(1)

    if not div_data:
        print("[ERROR] 未找到高股息策略数据，请先运行 high_dividend_maoge_strategy.py")
        sys.exit(1)

    # 生成信号
    signal_data = generate_daily_signal(ai_data, div_data)

    # 保存JSON信号
    today = signal_data['date']
    json_path = REPORTS_DIR / f"signal_{today}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(signal_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] JSON信号已保存: {json_path}")

    # 保存HTML报告
    html_content = generate_html_report(signal_data)
    html_path = REPORTS_DIR / f"signal_{today}.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"[OK] HTML报告已保存: {html_path}")

    # 保存微信文章
    wechat_html = generate_wechat_article(signal_data)
    wechat_path = REPORTS_DIR / f"wechat_{today}.html"
    with open(wechat_path, 'w', encoding='utf-8') as f:
        f.write(wechat_html)
    print(f"[OK] 微信文章已保存: {wechat_path}")

    # 保存最新信号（覆盖）
    latest_path = REPORTS_DIR / "latest_signal.json"
    with open(latest_path, 'w', encoding='utf-8') as f:
        json.dump(signal_data, f, ensure_ascii=False, indent=2)

    # 控制台摘要
    print(f"\n{'='*60}")
    print(f"  今日信号摘要 ({today})")
    print(f"{'='*60}")
    print(f"  总信号数: {signal_data['total_signals']}")
    print(f"  强烈信号: {signal_data['strong_signals']}")
    print(f"  关注信号: {signal_data['moderate_signals']}")
    print(f"\n  Top 3:")
    for i, s in enumerate(signal_data['signals'][:3], 1):
        strength = '★★★' if s['strength'] == 'STRONG' else '★★'
        print(f"  {i}. {s['name']}({s['code']}) {strength} ¥{s['price']:.2f}")
        print(f"     {s['reason']}")
    print(f"{'='*60}")

    return signal_data


if __name__ == '__main__':
    main()
