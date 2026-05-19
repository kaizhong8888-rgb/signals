#!/bin/bash
# 更新 GitHub Pages 信号站点
# 用法: ./scripts/update_github_pages.sh
# 建议在 crontab 中配置: 每个交易日 16:30 运行
# crontab -e
# 30 16 * * 1-5 cd ~/Business/quant_signal_service && bash scripts/update_github_pages.sh >> /tmp/update_github_pages.log 2>&1

set -e

PROJECT_DIR="$HOME/Business/quant_signal_service"
SIGNALS_REPO="$HOME/Business/signals"
GITHUB_REPO="https://github.com/kaizhong8888-rgb/signals"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 更新 GitHub Pages 开始 ==="

# Step 1: 确保信号数据存在
TODAY=$(date '+%Y-%m-%d')
SIGNAL_FILE="$PROJECT_DIR/reports/latest_signal.json"

if [ ! -f "$SIGNAL_FILE" ]; then
    echo "[$(date '+%H:%M:%S')] [ERROR] 信号文件不存在: $SIGNAL_FILE"
    echo "[$(date '+%H:%M:%S')] 请先运行 generate_daily_signal.py 生成信号"
    exit 1
fi

# Step 2: 生成 GitHub Pages HTML
echo "[$(date '+%H:%M:%S')] [1/3] 生成 GitHub Pages HTML..."
cd "$PROJECT_DIR"
python3 generate_pages.py --output-dir "$SIGNALS_REPO"

# Step 3: 提交并推送到 signals 仓库
echo "[$(date '+%H:%M:%S')] [2/3] 提交更改..."

# 如果 signals 仓库不存在，clone 下来
if [ ! -d "$SIGNALS_REPO/.git" ]; then
    echo "[$(date '+%H:%M:%S')] Cloning signals repository..."
    git clone "$GITHUB_REPO" "$SIGNALS_REPO"
fi

cd "$SIGNALS_REPO"

# 配置 git 用户信息（GitHub Actions / cron 需要）
git config user.email "kaizhong8888@users.noreply.github.com"
git config user.name "AI Quant Signal Bot"

# 检查是否有更改
if git diff --quiet -- index.html subscribe.html 2>/dev/null; then
    # 检查是否有 untracked files
    UNTRACKED=$(git ls-files --others --exclude-standard | grep -E '^(index|subscribe)\.html$' || true)
    if [ -z "$UNTRACKED" ]; then
        echo "[$(date '+%H:%M:%S')] 没有更改，跳过提交"
        exit 0
    fi
fi

git add index.html subscribe.html
git commit -m "update: daily signals $TODAY"
echo "[$(date '+%H:%M:%S')] [OK] 已提交: update: daily signals $TODAY"

# Step 4: 推送
echo "[$(date '+%H:%M:%S')] [3/3] 推送到 GitHub..."
git push origin main
echo "[$(date '+%H:%M:%S')] [OK] 推送完成"

echo "[$(date '+%H:%M:%S')] === 更新 GitHub Pages 完成 ==="
echo "[$(date '+%H:%M:%S')] 查看: https://kaizhong8888-rgb.github.io/signals/"
