#!/bin/bash
# 每日量化信号自动化脚本
# 用法: ./scripts/run_daily.sh
# 建议在crontab中配置: 每个交易日 15:30 运行
# crontab -e
# 30 15 * * 1-5 cd ~/Business/quant_signal_service && bash scripts/run_daily.sh >> /tmp/quant_signal.log 2>&1

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BUSINESS_DIR="$HOME/Business"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 每日量化信号开始 ==="

# Step 1: 运行AI选股
echo "[$(date '+%H:%M:%S')] [1/3] 运行AI选股..."
cd "$BUSINESS_DIR/ai_stock_picker"
python3 ai_stock_picker.py > /tmp/ai_stock_picker.log 2>&1
echo "[$(date '+%H:%M:%S')] [1/3] AI选股完成"

# Step 2: 运行高股息策略
echo "[$(date '+%H:%M:%S')] [2/3] 运行高股息策略..."
cd "$BUSINESS_DIR"
python3 high_dividend_maoge_strategy.py > /tmp/high_dividend.log 2>&1
echo "[$(date '+%H:%M:%S')] [2/3] 高股息策略完成"

# Step 3: 生成信号报告
echo "[$(date '+%H:%M:%S')] [3/3] 生成信号报告..."
cd "$PROJECT_DIR"
python3 generate_daily_signal.py
echo "[$(date '+%H:%M:%S')] [3/3] 信号报告生成完成"

# 清理
TODAY=$(date '+%Y-%m-%d')
if [ -f "$PROJECT_DIR/reports/signal_$TODAY.html" ]; then
    echo "[$(date '+%H:%M:%S')] 今日报告: $PROJECT_DIR/reports/signal_$TODAY.html"
    echo "[$(date '+%H:%M:%S')] 微信文章: $PROJECT_DIR/reports/wechat_$TODAY.html"
fi

echo "[$(date '+%H:%M:%S')] === 每日量化信号完成 ==="
