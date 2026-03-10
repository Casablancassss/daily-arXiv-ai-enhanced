# 🚀 daily-arXiv-ai-enhanced

> [!CAUTION]
> 若您所在法域对学术数据有审查要求，谨慎运行本代码；任何二次分发版本必须履行合规审查（包括但不限于原始论文合规性、AI合规性）义务，否则一切法律后果由下游自行承担。

> [!CAUTION]
> If your jurisdiction has censorship requirements for academic data, run this code with caution; any secondary distribution version must remove the entrance accessible to China and fulfill the content review obligations, otherwise all legal consequences will be borne by the downstream.

---

## Languages | 语言
[English](./README.md) | [中文](./README.zh-cn.md)

---

This innovative tool transforms how you stay updated with arXiv papers by combining automated crawling with AI-powered summarization.


## ✨ Key Features

🎯 **Zero Infrastructure Required**
- Leverages GitHub Actions and Pages - no server needed
- Completely free to deploy and use

🤖 **Smart AI Summarization**
- Daily paper crawling with DeepSeek-powered summaries
- Cost-effective: Only ~0.2 CNY per day

💫 **Smart Reading Experience**
- Personalized paper highlighting based on your interests
- Research profile-based relevance scoring and sorting
- Cross-device compatibility (desktop & mobile)
- Local preference storage for privacy
- Flexible date range filtering

👉 **[Try it now!](https://Casablancassss.github.io/daily-arXiv-ai-enhanced/)** - No installation required



# How to use
This repo will daily crawl arXiv papers about **cs.CV, cs.GR, cs.CL and cs.AI**, and use **DeepSeek** to summarize the papers in **Chinese**.
If you wish to crawl other arXiv categories, use other LLMs, or other languages, please follow the instructions.
Otherwise, you can directly use this repo in https://Casablancassss.github.io/daily-arXiv-ai-enhanced/. Please star it if you like :)

**Instructions:**
1. Fork this repo to your own account.
2. Go to: your-own-repo -> Settings -> Secrets and variables -> Actions
3. Go to Secrets. Secrets are encrypted and used for sensitive data
4. Create two repository secrets named `OPENAI_API_KEY` and `OPENAI_BASE_URL`, and input corresponding values.
5. [Optional] Set a password in `secrets.ACCESS_PASSWORD` if you do not wish others to access your page.
6. Go to Variables. Variables are shown as plain text and are used for non-sensitive data
7. Create the following repository variables:
   1. `CATEGORIES`: separate the categories with ",", such as "cs.CL, cs.CV"
   2. `LANGUAGE`: such as "Chinese" or "English"
   3. `MODEL_NAME`: such as "deepseek-chat"
   4. `EMAIL`: your email for push to GitHub
   5. `NAME`: your name for push to GitHub
   6. [Optional] `RESEARCH_PROFILE`: JSON string for research profile matching (see below)

#### Research Profile (Optional)
Configure a research profile to enable AI-powered paper relevance scoring. The system will calculate relevance scores and sort papers by relevance.

**Format:**
```json
{
  "field": "研究方向，如：大模型推理",
  "pain_points": ["当前痛点，如：长上下文部署"],
  "methods": ["关注方法，如：LoRA, quantization, PagedAttention"]
}
```

**Example:**
```json
{"field":"大模型推理","pain_points":["长上下文部署"],"methods":["LoRA","quantization","PagedAttention"]}
```

**Scoring Weights:**
- Field match (weight 1.0): Match research field in title, summary, AI tldr/motivation
- Pain points match (weight 1.5): Match current pain points
- Methods match (weight 2.0): Match methods in AI method/result

8. Go to your-own-repo -> Actions -> arXiv-daily-ai-enhanced
9. You can manually click **Run workflow** to test if it works well (it may take about one hour). By default, this action will automatically run every day. You can modify it in `.github/workflows/run.yml`
10. Set up GitHub pages: Go to your own repo -> Settings -> Pages. In `Build and deployment`, set `Source="Deploy from a branch"`, `Branch="main", "/(root)"`. Wait for a few minutes, go to https://\<username\>.github.io/daily-arXiv-ai-enhanced/.
