# 青海大学高性能与云计算研究所 (HDACP Lab)

## 🔬 实验室简介
青海大学高性能与云计算研究所（High Performance and Cloud Computing Laboratory, HDACP Lab）致力于高性能计算、云计算、大数据分析及人工智能等前沿技术的研究与应用。我们拥有一支充满活力、勇于创新的科研团队，在分布式系统、并行算法、数据挖掘等领域取得了显著成果。

## 🎯 研究方向
我们主要关注以下五个核心研究领域：
*   **高性能计算 (HPC)**: 聚焦于高性能计算系统架构、并行算法优化及科学计算应用。
*   **图计算系统**: 研究大规模图数据的存储、处理与分析系统，应用于社交网络与知识图谱。
*   **深度学习**: 探索神经网络模型、训练算法及其在多模态数据分析中的应用。
*   **计算机视觉**: 专注于图像识别、目标检测与视频分析技术。
*   **绿色计算**: 致力于提升计算系统的能效比，研究低碳数据中心与节能调度策略。

## � 科研团队
实验室拥有一支高水平的指导教师队伍，包括王晓英教授、黄建强教授等多位专家学者，以及众多充满激情的博士、硕士研究生。团队注重理论与实践结合，旨在培养高素质的计算机专业人才。

## 📍 联系我们
*   **地址**: 青海省西宁市宁大路251号 青海大学计算机技术与应用系111实验室
*   **邮箱**: (请参阅网站联系方式)
*   **相关链接**:
    *   [青海大学](https://www.qhu.edu.cn/)
    *   [青海大学计算机技术与应用系](https://cs.qhu.edu.cn/)

---
*本网站由 HDACP Lab 维护。技术支持：Vue 3 + Vite。*

## 本地开发与发布

安装依赖并启动预览：

```sh
npm ci
npm run dev
```

网站部署在 https://02letter.github.io/HDACP/ 。推送到 `main` 后，GitHub Actions 自动构建并将产物更新到 `gh-pages`。

首次启用：仓库 **Settings → Pages** 中选择 **Deploy from a branch**，分支设为 `gh-pages`，目录设为 `/(root)`。

发布流程使用 `VITE_BASE_PATH=/HDACP/`，本地开发默认使用根路径。子页面采用 hash 路由，支持直接访问及刷新，无需服务器重写规则。

手动论文、新闻和活动分别维护在 `src/data/publications.json`、`src/data/news.json`、`src/data/life.json`。

## 自动抓取与发布

GitHub Actions 每天北京时间 **08:17** 左右抓取并发布，也可以在仓库 **Actions → Deploy to GitHub Pages → Run workflow** 手动运行。定时任务可能延迟；公开仓库长期无活动时 GitHub 可能停用定时运行，可在 Actions 中重新启用。

- **论文**：OpenAlex 公开元数据。`config/content-sources.json` 记录现有 8 位老师已核对的作者编号、ORCID 和核对来源。仅接受姓名与编号匹配、且该作者在这篇论文中署名青海大学的记录。默认同步 2025 年起已发布的文章、综述、会议论文及章节，排除撤稿、预印本与未来日期。不自动推断 CCF/SCI 等级。首页、论文页及对应老师主页展示新增成果；已观察到撤稿标记的自动条目会移除。
- **学生**：从 `team.json` 现有名单读取。英文别名仅用于识别已确认老师论文中的青海大学学生共同作者，不把拼音或同名搜索结果当成独立作者身份。未匹配学生仍参与学院新闻筛选；独立发表且没有已确认老师署名的学生论文目前需要核实作者身份后扩展配置。
- **新闻**：抓取青海大学计算机学院的学术交流、学科竞赛、院系动态栏目。只保留正文提到现有老师、至少两位成员，或明确提到本实验室的新闻。只含图片、没有可核对正文的新闻不会凭标题猜测归属；微信及未开放来源暂不抓取。
- **保留人工内容**：自动结果独立存放在 `src/data/auto-publications.json` 和 `src/data/auto-news.json`，与手动数据按标题及链接去重后展示。来源失败不会清空已有结果。个人简介、职称、毕业状态、照片和活动图库仍由人工维护。
- **查看抓取结果**：每次在线抓取的报告保存在 Actions 的 `content-sync-report` 下载附件中，包含名单覆盖、未匹配学生、候选条目及失败来源。部分来源失败时先发布保留的数据，再将任务标为失败以提示排查。

本地抓取（Python 3.11+，无需额外安装 Python 库）：

```sh
python scripts/sync_content.py
python -m unittest discover -s scripts -p "test_sync_content.py"
npm run build
```

本地报告默认在 `.backups/sync-report.json`。如 OpenAlex 要求认证或额度不足，在仓库 **Settings → Secrets and variables → Actions** 添加 `OPENALEX_API_KEY`；不要将密钥写进源码。可用环境变量 `HTTPS_PROXY` 设置本地代理。

每天抓取、源数据提交、构建和部署在同一流程内完成，因为使用 `GITHUB_TOKEN` 的自动提交不会再次触发 push 工作流。只在内容改变时提交，不会生成空提交。

原始网站源码来自 https://github.com/linyao-alxy/HDACP ，本仓库包含后续界面与交互改进。
