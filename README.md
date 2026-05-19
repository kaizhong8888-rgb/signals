# AI量化信号服务

> 每日量化选股信号 · 双策略交叉验证 · 付费订阅制

## 快速开始

```bash
# 1. 生成今日信号
python3 generate_daily_signal.py

# 2. 启动服务（落地页 + API）
python3 server.py --port 8080

# 3. 打开浏览器查看
open http://127.0.0.1:8080
```

## 自动化运行

### 手动运行完整流程
```bash
bash scripts/run_daily.sh
```

### Cron定时任务（交易日15:30自动运行）
```bash
crontab -e
# 添加以下行
30 15 * * 1-5 cd ~/Business/quant_signal_service && bash scripts/run_daily.sh >> /tmp/quant_signal.log 2>&1
```

## 目录结构

```
quant_signal_service/
├── generate_daily_signal.py   # 信号生成器（核心）
├── server.py                   # HTTP服务（落地页+API）
├── web/
│   └── index.html              # 落地页
├── scripts/
│   └── run_daily.sh            # 每日自动化脚本
├── reports/
│   ├── signal_YYYY-MM-DD.json  # 每日信号JSON
│   ├── signal_YYYY-MM-DD.html  # 每日信号HTML报告
│   ├── wechat_YYYY-MM-DD.html  # 微信文章HTML
│   └── latest_signal.json      # 最新信号（覆盖）
└── README.md
```

## 变现路径

### 模式1：付费订阅（推荐）
- **定价**: 299元/月 或 999元/季
- **内容**: 每日盘后选股信号推送
- **渠道**: 微信公众号/知识星球/私域
- **目标**: 100付费用户 × 299元 = ~30K/月

### 模式2：知识星球
- 在知识星球发布每日信号 + 持仓分析
- 年费制（365-1999元/年）
- 叠加盘中实时提醒

### 模式3：公众号付费文章
- 免费推送摘要（1-2只）
- 完整信号列表（5-10只）设为付费阅读
- 单篇1-9元

### 模式4：SaaS工具
- 基于 design-assistant 的技术栈
- 搭建 web 应用，用户登录后查看信号
- 支持自定义筛选条件、历史回测
- 月费制（99-599元/月）

## API 接口

### GET /api/signal
返回最新信号数据
```json
{
  "date": "2026-05-19",
  "total_signals": 9,
  "strong_signals": 2,
  "signals": [...]
}
```

### GET /api/history
返回最近30天信号记录摘要

## 信号类型说明

| 类型 | 条件 | 说明 |
|------|------|------|
| 强烈 ★★★ | 双策略共振 或 ROE>25%+增速>25% | 强烈建议关注 |
| 关注 ★★ | AI选股正增长 或 高股息可持续 | 建议观察 |

## 策略来源

- **AI选股**: `~/Business/ai_stock_picker/ai_stock_picker.py`
  - 基于XGBoost + 多因子打分（价值/成长/质量/动量）
  - 行业中性化处理
  - 每日自动运行

- **高股息策略**: `~/Business/high_dividend_maoge_strategy.py`
  - 基于猫哥AI量化公众号文章核心逻辑
  - ROE>0 + 利润增速>0 + 经营现金流>0 三条件过滤
  - 行业分散 + 近三年平均股息率

## 部署选项

### 选项1：本机运行 + 公网访问（最快）
```bash
# 使用 ngrok 暴露本地端口
brew install ngrok
ngrok http 8080
```

### 选项2：部署到 Vercel
将 `web/index.html` 和 API 路由迁移到 Next.js 项目
（design-assistant 已有 Next.js 基础设施可复用）

### 选项3：部署到已有 ai-assistant 项目
在 `ai-assistant` 中添加 `/signals` 路由，复用现有数据库

## 合规提示

- 本报告仅供学习研究，不构成投资建议
- 未取得证券投资咨询业务资格前，不得对外提供付费荐股服务
- 建议以"量化研究参考"名义发布，避免"推荐买入/卖出"等表述
- 实际操作：先跑通产品、获取用户反馈，再咨询合规问题

## 下一步优化

- [ ] 接入实时行情（盘中信号）
- [ ] 增加策略回测展示（历史胜率/收益率曲线）
- [ ] 微信推送集成（复用 wechat_mp_automation）
- [ ] 用户注册/付费系统
- [ ] 邮件推送备选通道
- [ ] 移动端适配优化
