# 🚀 daily-arXiv-ai-enhanced

> [!CAUTION]
> 若您所在法域对学术数据有审查要求，谨慎运行本代码；任何二次分发版本必须履行合规审查（包括但不限于原始论文合规性、AI合规性）义务，否则一切法律后果由下游自行承担。

> [!CAUTION]
> If your jurisdiction has censorship requirements for academic data, run this code with caution; any secondary distribution version must remove the entrance accessible to China and fulfill the content review obligations, otherwise all legal consequences will be borne by the downstream.

---

## 语言 | Languages
[English](./README.md) | [中文](./README.zh-cn.md)

---

这款创新工具将自动化爬虫与 AI 智能摘要相结合，彻底改变您追踪 arXiv 论文的方式。

## ✨ 核心特性

🎯 **零基础设施要求**

- 依托 GitHub Actions 和 Pages，无需服务器
- 完全免费部署和使用

🤖 **智能 AI 摘要**

- 每日自动爬取论文，DeepSeek 驱动的智能摘要
- 成本效益：每日仅需约 0.2 元

💫 **智能阅读体验**

- 基于个人兴趣的论文高亮显示
- **研究画像相关性评分和排序**
- 跨设备兼容（桌面端和移动端）
- 本地偏好存储，保护隐私
- 灵活的日期范围筛选

👉 **[立即体验！](https://Casablancassss.github.io/daily-arXiv-ai-enhanced/)** - 无需安装

# 如何使用

本项目每日自动爬取 **cs.CV, cs.GR, cs.CL 和 cs.AI** 分类的 arXiv 论文，并使用大模型将论文摘要为**中文**。
如果您希望爬取其他 arXiv 分类、使用其他大模型或其他语言，请按照以下说明进行操作。
您也可以直接使用 https://Casablancassss.github.io/daily-arXiv-ai-enhanced/ 。如果喜欢的话，请给个 star :)

**使用步骤：**

1. 将本仓库 fork 到您的账户。
2. 进入：您的仓库 -> Settings -> Secrets and variables -> Actions
3. 进入 Secrets。Secrets 是加密的，用于敏感数据
4. 创建两个名为 `OPENAI_API_KEY` 和 `OPENAI_BASE_URL` 的 repository secrets，并输入对应的值。
5. [可选] 如果您不希望他人访问您的页面，可在 `secrets.ACCESS_PASSWORD` 中设置密码。
6. 进入 Variables。Variables 以纯文本形式显示，用于非敏感数据
7. 创建以下 repository variables：

   1. `CATEGORIES`：用 "," 分隔分类，例如 "cs.CL, cs.CV"
   2. `LANGUAGE`：例如 "Chinese" 或 "English"
   3. `MODEL_NAME`：例如 "deepseek-chat"
   4. `EMAIL`：您用于推送到 GitHub 的邮箱
   5. `NAME`：您用于推送到 GitHub 的用户名
   6. [可选] `RESEARCH_PROFILE`：研究画像配置的 JSON 字符串（见下文）

8. 进入您的仓库 -> Actions -> arXiv-daily-ai-enhanced
9. 您可以手动点击 **Run workflow** 来测试是否正常工作（可能需要约一小时）。默认情况下，此 action 每天自动运行。您可以在 `.github/workflows/run.yml` 中修改
10. 设置 GitHub pages：进入您的仓库 -> Settings -> Pages。在 `Build and deployment` 中，设置 `Source="Deploy from a branch"`，`Branch="main", "/(root)"`。等待几分钟后，访问 https://\<username\>.github.io/daily-arXiv-ai-enhanced/。

#### 研究画像配置（可选）

配置研究画像以启用 AI 驱动的论文相关性评分。系统将计算相关性分数并按相关性排序论文。

**格式：**

```json
{
  "field": "研究方向，如：大模型推理",
  "pain_points": ["当前痛点，如：长上下文部署"],
  "methods": ["关注方法，如：LoRA, quantization, PagedAttention"]
}
```

**示例：**

```json
{"field":"大模型推理","pain_points":["长上下文部署"],"methods":["LoRA","quantization","PagedAttention"]}
```

**评分权重：**

- 研究方向匹配（权重 1.0）：在标题、摘要、AI 摘要的 tldr/motivation 中匹配研究方向
- 痛点匹配（权重 1.5）：匹配当前痛点
- 方法匹配（权重 2.0）：在 AI 分析的 method/result 中匹配关注方法
