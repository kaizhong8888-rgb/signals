#!/usr/bin/env python3
"""
每日信号微信推送自动化

流程：
1. 运行AI选股 + 高股息策略（如果今天还没跑）
2. 生成信号报告
3. 创建微信公众号草稿
4. 打开后台供手动发布

用法:
    python3 publish_signal.py           # 完整流程
    python3 publish_signal.py --draft-only  # 仅创建草稿（假设信号已生成）
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

BUSINESS_DIR = Path.home() / 'Business'
SIGNAL_SERVICE_DIR = BUSINESS_DIR / 'quant_signal_service'
REPORTS_DIR = SIGNAL_SERVICE_DIR / 'reports'
WECHAT_DIR = BUSINESS_DIR / 'wechat_mp_automation'


def run_command(cmd: list, cwd: str = None):
    """运行命令并返回输出"""
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"[WARN] Command failed: {' '.join(cmd)}")
        print(f"  stderr: {result.stderr[:200]}")
        return None
    return result.stdout


def ensure_signals_generated():
    """确保今日信号已生成，如果没有则运行"""
    today = datetime.now().strftime('%Y-%m-%d')
    signal_file = REPORTS_DIR / f"signal_{today}.json"

    if signal_file.exists():
        print(f"[OK] 今日信号已存在: {signal_file}")
        return True

    print(f"[INFO] 今日信号未生成，运行完整流程...")

    # Step 1: AI选股
    print("  [1/3] 运行AI选股...")
    out = run_command(['python3', 'ai_stock_picker.py'],
                      cwd=str(BUSINESS_DIR / 'ai_stock_picker'))
    if out is None:
        print("[ERROR] AI选股失败")
        return False
    print("  [OK] AI选股完成")

    # Step 2: 高股息策略
    print("  [2/3] 运行高股息策略...")
    out = run_command(['python3', 'high_dividend_maoge_strategy.py'],
                      cwd=str(BUSINESS_DIR))
    if out is None:
        print("[WARN] 高股息策略失败，继续生成信号")

    # Step 3: 信号生成器
    print("  [3/3] 生成信号报告...")
    out = run_command(['python3', 'generate_daily_signal.py'],
                      cwd=str(SIGNAL_SERVICE_DIR))
    if out is None:
        print("[ERROR] 信号生成失败")
        return False
    print("  [OK] 信号报告已生成")

    return True


def generate_wechat_content(signal_data: dict) -> str:
    """生成微信公众号文章HTML"""
    today = signal_data['date']
    signals = signal_data['signals']
    total = signal_data['total_signals']
    strong = signal_data['strong_signals']

    # 标题
    if strong > 0:
        title = f"【{today}】量化信号 | {strong}个强烈信号，重点关注这些标的"
    else:
        title = f"【{today}】量化信号 | {total}个关注信号，{signal_data.get('moderate_signals', 0)}个值得跟踪"

    # 文章正文
    article = f"""
<section style="padding: 20px 16px;">
    <section style="background: linear-gradient(135deg, #1a237e, #283593); padding: 24px 20px; border-radius: 12px; margin-bottom: 24px;">
        <p style="color: #fff; font-size: 20px; font-weight: 700; margin: 0 0 4px 0;">📊 量化每日选股信号</p>
        <p style="color: rgba(255,255,255,0.7); font-size: 13px; margin: 0;">{today} | AI选股 + 高股息策略 | 信号总数: {total} | 强烈: {strong}</p>
    </section>
"""

    # 策略概述
    article += f"""
    <section style="padding: 16px; background: #f8f9fa; border-radius: 8px; margin-bottom: 24px;">
        <p style="font-size: 15px; font-weight: 600; margin: 0 0 8px 0; color: #2c3e50;">📋 今日策略概览</p>
        <p style="margin: 0; font-size: 14px; color: #555; line-height: 1.8;">
            • AI选股扫描 <strong>{signal_data['market_summary']['ai_total']}</strong> 只股票，正成长 <strong>{signal_data['market_summary']['ai_positive_growth']}</strong> 只<br/>
            • 高股息策略筛选出 <strong>{signal_data['market_summary']['dividend_sustainable']}</strong> 只可持续分红股<br/>
            • 双策略共振 <strong>{signal_data['market_summary']['overlap_count']}</strong> 只
        </p>
    </section>
"""

    # 信号列表
    article += f"""
    <section style="margin-bottom: 16px;">
        <p style="font-size: 16px; font-weight: 600; color: #2c3e50; margin: 0 0 16px 0; padding-left: 12px; border-left: 3px solid #1a237e;">🎯 今日信号详情</p>
"""

    for i, s in enumerate(signals, 1):
        is_strong = s['strength'] == 'STRONG'
        border_color = '#e74c3c' if is_strong else '#3498db'
        badge_text = '强烈' if is_strong else '关注'
        badge_bg = '#e74c3c' if is_strong else '#f39c12'

        profit_growth = s.get('profit_growth', 0)
        profit_color = '#e74c3c' if profit_growth < 0 else '#10b981'
        profit_arrow = '↓' if profit_growth < 0 else '↑'

        article += f"""
        <section style="border-left: 3px solid {border_color}; padding: 16px; margin-bottom: 16px; background: #fafbfc; border-radius: 0 8px 8px 0;">
            <p style="font-size: 17px; font-weight: 600; margin: 0 0 8px 0; color: #2c3e50;">
                {i}. {s['name']} <span style="color: #999; font-size: 13px;">({s['code']})</span>
                <span style="background: {badge_bg}; color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-left: 8px;">{badge_text}</span>
            </p>
            <p style="margin: 0 0 10px 0; font-size: 14px; color: #666;">
                现价: ¥{s['price']:.2f} | PE: {s['pe']:.1f} | ROE: <strong>{s['roe']:.1f}%</strong> | 利润增速: <span style="color: {profit_color}; font-weight: 600;">{profit_arrow} {abs(profit_growth):.1f}%</span>
            </p>
            <p style="margin: 0; padding: 10px 12px; background: #fff; border-radius: 6px; font-size: 14px; color: #555; border: 1px solid #eee;">
                💡 {s['reason']}
            </p>
        </section>
"""

    # 结尾
    article += f"""
    </section>

    <section style="padding: 16px; background: #fff3cd; border-radius: 8px; border: 1px solid #ffeaa7; margin-top: 24px;">
        <p style="margin: 0; font-size: 13px; color: #856404; line-height: 1.6;">
            ⚠️ <strong>风险提示：</strong>本报告基于量化模型自动生成，仅供学习研究，不构成投资建议。投资有风险，入市需谨慎。建议先进行充分回测验证，实盘交易前建议小资金测试。
        </p>
    </section>

    <section style="text-align: center; padding: 24px 16px; color: #999; font-size: 13px;">
        <p style="margin: 0 0 8px 0;">由 <strong style="color: #1a237e;">AI量化信号系统</strong> 自动生成</p>
        <p style="margin: 0;">数据来源：腾讯财经API + 东方财富</p>
    </section>
</section>
"""

    return title, article


def create_wechat_draft(title: str, content: str):
    """使用公众号API创建草稿"""
    publish_script = WECHAT_DIR / 'publish.py'

    if not publish_script.exists():
        print(f"[ERROR] 微信发布脚本不存在: {publish_script}")
        return None

    # 先把内容写入临时文件
    content_file = SIGNAL_SERVICE_DIR / 'web' / 'wechat_content.html'
    with open(content_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"[INFO] 创建草稿: {title}")

    # 调用publish.py创建草稿
    result = subprocess.run(
        ['python3.11', str(publish_script), 'draft',
         '--title', title,
         '--content-file', str(content_file)],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"[ERROR] 创建草稿失败:")
        print(f"  stdout: {result.stdout[:500]}")
        print(f"  stderr: {result.stderr[:500]}")

        # Try with python3 fallback
        result2 = subprocess.run(
            ['python3', str(publish_script), 'draft',
             '--title', title,
             '--content-file', str(content_file)],
            capture_output=True, text=True
        )

        if result2.returncode != 0:
            print(f"[ERROR] python3 也失败了:")
            print(f"  stderr: {result2.stderr[:500]}")
            return None
        else:
            print(result2.stdout)
            return True
    else:
        print(result.stdout)
        return True


def main():
    """主流程"""
    print(f"\n{'='*60}")
    print(f"  每日量化信号微信推送")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    # Step 1: 确保信号已生成
    if not ensure_signals_generated():
        print("\n[ERROR] 信号生成失败，无法推送")
        sys.exit(1)

    # Step 2: 加载信号数据
    today = datetime.now().strftime('%Y-%m-%d')
    signal_file = REPORTS_DIR / f"signal_{today}.json"

    with open(signal_file, 'r', encoding='utf-8') as f:
        signal_data = json.load(f)

    print(f"\n[INFO] 加载信号: {signal_data['total_signals']} 个信号")

    # Step 3: 生成微信内容
    title, content = generate_wechat_content(signal_data)
    print(f"[OK] 文章标题: {title}")

    # Step 4: 创建微信草稿
    print(f"\n[INFO] 创建公众号草稿...")
    success = create_wechat_draft(title, content)

    if success:
        print(f"\n[OK] 草稿创建成功！")
        print(f"\n下一步: 登录公众号后台 → 草稿箱 → 点击「发表」")
        print(f"       运行: python3.11 {WECHAT_DIR}/publish.py open-backend")
    else:
        print(f"\n[WARN] 草稿创建失败，请手动操作")
        print(f"\n备选方案:")
        print(f"  1. 打开微信文章HTML: {REPORTS_DIR / f'wechat_{today}.html'}")
        print(f"  2. 复制内容到公众号编辑器")
        print(f"  3. 点击发表")


if __name__ == '__main__':
    main()
