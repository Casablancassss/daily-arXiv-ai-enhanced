# 🚀 daily-arXiv-ai-enhanced

> [!CAUTION]
> 若您所在法域对学术数据有审查要求，谨慎运行本代码；任何二次分发版本必须履行合规审查（包括但不限于原始论文合规性、AI合规性）义务，否则一切法律后果由下游自行承担。

> [!CAUTION]
> If your jurisdiction has censorship requirements for academic data, run this code with caution; any secondary distribution version must remove the entrance accessible to China and fulfill the content review obligations, otherwise all legal consequences will be borne by the downstream.

---

**语言：** [English](./README.md) | [中文](./README.zh-cn.md)

---

利用 AI 驱动的爬虫、摘要和智能相关性评分，彻底改变你追踪 arXiv 论文的方式。

## ✨ 功能特性

| 特性 | 描述 |
|------|------|
| 🎯 **零基础设施** | GitHub Actions + Pages，无需服务器 |
| 🤖 **AI 摘要** | DeepSeek 驱动的论文摘要 |
| 📊 **智能评分** | 基于研究画像的相关性排名 |
| 💰 **成本低廉** | 约 0.2 元/天 |
| 📱 **跨平台** | 桌面端和移动端兼容 |

**[立即体验](https://Casablancassss.github.io/daily-arXiv-ai-enhanced/)** · **[点赞 ⭐](https://github.com/Casablancassss/daily-arXiv-ai-enhanced)**

---

## 🚀 快速开始

### 1. Fork 并配置

| 步骤 | 操作 |
|------|------|
| 1 | Fork 本仓库 |
| 2 | 进入 **Settings → Secrets and variables → Actions** |
| 3 | 添加 **Secrets**：`OPENAI_API_KEY`、`OPENAI_BASE_URL` |
| 4 | 添加 **Variables**：`CATEGORIES`、`LANGUAGE`、`MODEL_NAME`、`EMAIL`、`NAME` |
| 5 | （可选）添加 `ACCESS_PASSWORD` secret 保护隐私 |

### 2. 配置研究画像

只需用自然语言描述你的研究领域：

```
Settings → Secrets and variables → Actions → Variables
添加：RESEARCH_DESCRIPTION = "我在研究人体动作生成，用扩散模型和LoRA。
但是现在很难获取高质量的3D人体动作数据，而且推理速度也很慢。"
```

AI 将自动提取：
- **field** - 主要研究领域
- **pain_points** - 当前面临的挑战
- **methods** - 使用的方法
- **keywords** - 相关技术术语

### 3. 运行工作流

1. 进入 **Actions → arXiv-daily-ai-enhanced**
2. 点击 **Run workflow**
3. 等待约 1 小时处理完成

### 4. 启用 GitHub Pages

**Settings → Pages → Build and deployment：**
- Source: Deploy from a branch
- Branch: main / (root)

访问：`https://<用户名>.github.io/daily-arXiv-ai-enhanced/`

---

## 📋 配置参考

### Variables (Settings → Secrets and variables → Actions → Variables)

| 变量 | 必填 | 示例 |
|------|------|------|
| `CATEGORIES` | ✅ | `cs.CV, cs.CL, cs.AI` |
| `LANGUAGE` | ✅ | `Chinese` 或 `English` |
| `MODEL_NAME` | ✅ | `deepseek-chat` |
| `EMAIL` | ✅ | `you@example.com` |
| `NAME` | ✅ | `Your Name` |
| `RESEARCH_DESCRIPTION` | ❌ | 你的研究描述 |

### Secrets (Settings → Secrets and variables → Actions → Secrets)

| Secret | 必填 | 示例 |
|--------|------|------|
| `OPENAI_API_KEY` | ✅ | `sk-...` |
| `OPENAI_BASE_URL` | ✅ | `https://api.deepseek.com` |
| `ACCESS_PASSWORD` | ❌ | 你的密码 |

---

## 🏗️ 架构

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  arXiv 爬虫器   │ ──▶ │   AI 增强处理    │ ──▶ │   相关性评分    │
│   (Scrapy)     │     │   (LLM 摘要)      │     │   (LLM 评分)     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   GitHub Pages  │ ◀── │   Markdown 生成  │ ◀── │   JSONL 数据    │
│     (网站)       │     │    (模板)         │     │     (每日)        │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

---

## 📁 项目结构

```
.
├── ai/                      # AI 处理脚本
│   ├── enhance.py          # 论文摘要
│   ├── score_relevance.py  # 相关性评分
│   ├── parse_profile.py    # 研究画像解析
│   └── generate_report.py  # 报告生成
├── daily_arxiv/            # arXiv 爬虫 (Scrapy)
├── to_md/                  # Markdown 转换器
├── .github/workflows/      # GitHub Actions
└── data/                   # 每日论文数据
```

---

## 🔧 自定义

### 修改分类
```bash
# 在 workflow 或 variables 中
CATEGORIES=cs.CV,cs.CL,cs.AI,cs.LG
```

### 修改语言
```bash
LANGUAGE=English  # 或 Chinese
```

### 使用其他 LLM
```bash
MODEL_NAME=gpt-4o
```

---

## 📄 许可证

MIT License - 欢迎使用和修改！
