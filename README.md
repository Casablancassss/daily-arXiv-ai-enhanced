# 🚀 daily-arXiv-ai-enhanced

> [!CAUTION]
> 若您所在法域对学术数据有审查要求，谨慎运行本代码；任何二次分发版本必须履行合规审查（包括但不限于原始论文合规性、AI合规性）义务，否则一切法律后果由下游自行承担。

> [!CAUTION]
> If your jurisdiction has censorship requirements for academic data, run this code with caution; any secondary distribution version must remove the entrance accessible to China and fulfill the content review obligations, otherwise all legal consequences will be borne by the downstream.

---

**Languages:** [English](./README.md) | [中文](./README.zh-cn.md)

---

Transform your daily arXiv paper tracking with AI-powered crawling, summarization, and smart relevance scoring.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎯 **Zero Infrastructure** | GitHub Actions + Pages, no server needed |
| 🤖 **AI Summarization** | DeepSeek-powered paper summaries |
| 📊 **Smart Scoring** | Research profile-based relevance ranking |
| 💰 **Cost Effective** | ~0.2 CNY/day |
| 📱 **Cross-Platform** | Desktop & mobile compatible |

**[Try it now](https://Casablancassss.github.io/daily-arXiv-ai-enhanced/)** · **[Star ⭐](https://github.com/Casablancassss/daily-arXiv-ai-enhanced)**

---

## 🚀 Quick Start

### 1. Fork & Configure

| Step | Action |
|------|--------|
| 1 | Fork this repository |
| 2 | Go to **Settings → Secrets and variables → Actions** |
| 3 | Add **Secrets**: `OPENAI_API_KEY`, `OPENAI_BASE_URL` |
| 4 | Add **Variables**: `CATEGORIES`, `LANGUAGE`, `MODEL_NAME`, `EMAIL`, `NAME` |
| 5 | (Optional) Add `ACCESS_PASSWORD` secret for privacy |

### 2. Configure Research Profile

Just describe your research area in natural language:

```
Settings → Secrets and variables → Actions → Variables
Add: RESEARCH_DESCRIPTION = "I'm researching human motion generation using
diffusion models and LoRA. But it's hard to get high-quality 3D human
motion data, and inference is slow."
```

AI will automatically extract:
- **field** - Main research area
- **pain_points** - Current challenges
- **methods** - Techniques you use
- **keywords** - Related terms

### 3. Run Workflow

1. Go to **Actions → arXiv-daily-ai-enhanced**
2. Click **Run workflow**
3. Wait ~1 hour for processing

### 4. Enable GitHub Pages

**Settings → Pages → Build and deployment:**
- Source: Deploy from a branch
- Branch: main / (root)

Access at: `https://<username>.github.io/daily-arXiv-ai-enhanced/`

---

## 📋 Configuration Reference

### Variables (Settings → Secrets and variables → Actions → Variables)

| Variable | Required | Example |
|----------|----------|---------|
| `CATEGORIES` | ✅ | `cs.CV, cs.CL, cs.AI` |
| `LANGUAGE` | ✅ | `Chinese` or `English` |
| `MODEL_NAME` | ✅ | `deepseek-chat` |
| `EMAIL` | ✅ | `you@example.com` |
| `NAME` | ✅ | `Your Name` |
| `RESEARCH_DESCRIPTION` | ❌ | Your research description |

### Secrets (Settings → Secrets and variables → Actions → Secrets)

| Secret | Required | Example |
|--------|----------|---------|
| `OPENAI_API_KEY` | ✅ | `sk-...` |
| `OPENAI_BASE_URL` | ✅ | `https://api.deepseek.com` |
| `ACCESS_PASSWORD` | ❌ | Your password |

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  arXiv Crawler  │ ──▶ │  AI Enhancement  │ ──▶ │ Relevance Score │
│   (Scrapy)      │     │  (LLM Summary)   │     │ (LLM Scoring)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   GitHub Pages  │ ◀── │   Markdown Gen   │ ◀── │   JSONL Data    │
│   (Website)     │     │   (Template)     │     │   (Daily)       │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

---

## 📁 Project Structure

```
.
├── ai/                      # AI processing scripts
│   ├── enhance.py          # Paper summarization
│   ├── score_relevance.py  # Relevance scoring
│   ├── parse_profile.py    # Research profile parser
│   └── generate_report.py  # Report generation
├── daily_arxiv/            # arXiv crawler (Scrapy)
├── to_md/                  # Markdown converter
├── .github/workflows/      # GitHub Actions
└── data/                   # Daily paper data
```

---

## 🔧 Customization

### Change Categories
```bash
# In workflow or variables
CATEGORIES=cs.CV,cs.CL,cs.AI,cs.LG
```

### Change Language
```bash
LANGUAGE=English  # or Chinese
```

### Use Different LLM
```bash
MODEL_NAME=gpt-4o
```

---

## 📄 License

MIT License - Feel free to use and modify!
