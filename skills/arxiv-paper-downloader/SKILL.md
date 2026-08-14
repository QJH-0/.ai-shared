---
name: arxiv-paper-downloader
description: 从 arXiv 批量下载学术论文 PDF，并逐篇用首页标题校验正确性、自动纠正错误 ID。适用于"帮我下载几篇论文/综述"类需求。关键点：arXiv ID 极易记错（差一位会下到风马牛不相及的论文），必须先下后验。
agent_created: true
---

# arXiv 论文下载与校验

## 适用场景
用户要求下载学术论文（尤其 arXiv 来源），或要某领域的经典论文 / 综述。核心教训：**不要凭记忆硬编码 arXiv ID**，下载后必须逐篇核对标题。

## 标准流程
1. **确定清单**：结合用户研究背景挑论文，先 `ls` 目标目录（如 `NEW/papers/`）避免重复下载。
2. **核实 ID（易错点）**：用 WebSearch 搜索「论文标题 + arxiv」确认准确 ID。
   - 真实踩坑：MetricGAN+ 应为 `2104.03538`（非 03528）；CMGAN Interspeech 版应为 `2203.15149`（非 14349）。ID 差一位即下到无关论文。
3. **下载**（git bash / curl）：
   ```bash
   curl -sL --max-time 120 -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" -o "<name>.pdf" "https://arxiv.org/pdf/<id>"
   ```
4. **校验（关键，不可省）**：
   - %PDF 头检查：`head -c 5 file.pdf | grep -q "%PDF"`（arXiv 对错误 ID 返回 HTML/404，能捕获）。
   - 标题核对（最重要）：用 pypdf/PyPDF2 提取首页文本确认是目标论文：
     ```python
     from pypdf import PdfReader
     print((PdfReader("file.pdf").pages[0].extract_text() or "")[:600])
     ```
5. **纠正**：标题不符 → 重新 WebSearch 纠正 ID → 重下 → 再校验。
6. **内容提取（可选）**：已下载 PDF 用 pypdf 全文本 + 正则 grep 关键词，提取训练方式/评估指标/方法章节供总结。

## 注意事项
- 不在 arXiv 的会议论文（如 Eusipco 论文集 PDF）可直接 `curl` 其链接，同样用 %PDF 头校验即可。
- 标题提取为空可能是扫描版 PDF，改用 Read 工具读首页图像确认。
- 验证、纠正、再验证，形成闭环；交付时向用户列出「文件 / 论文 / arXiv ID」对照表。
- 用户已有论文时优先复用，避免重复占用空间。
