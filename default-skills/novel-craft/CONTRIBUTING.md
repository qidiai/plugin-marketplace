# 贡献指南 / Contributing Guide

> 感谢你愿意改进 novel-craft。本指南说明如何高质量地贡献——无论是规格文档、作家技法、类型风格、脚本还是文档。

Thank you for improving novel-craft. This guide explains how to contribute high-quality work — whether specs, writer techniques, genre styles, scripts, or docs.

---

## 贡献类型 / Contribution Types

| 类型 | 说明 |
|---|---|
| **规格文档** | 新增/改进 references/ 下的 craft spec（视角/人物/节奏/修订等） |
| **作家技法** | 向 11-writers/ 添加作家，或深化已有条目 |
| **类型风格** | 向 12-genre-styles.md 添加新类型或深化已有类型 |
| **模板** | 改进 templates/ 下的项目文档/记忆模板 |
| **脚本** | 改进 scripts/check-chapter.py 或新增自动化工具 |
| **文档** | README / CONTRIBUTING / 示例 |

---

## 核心原则 / Core Principles

### 1. 通用性（最重要）/ Generality (most important)

> **所有规格只写通用表述，绝不绑定任何具体作品/项目。**

- ✅ 正确：用"正妻/女配/当家夫人/力量体系"等通用词
- ❌ 错误：用任何具体小说的人名/地名/功法/专有名词作规则
- 示例（教训）：
  - ❌ "主母能调度账房佣兵"（绑定了某本书的设定）
  - ✅ "当家的能调度管家佣人"（任何作品适用）
- **提交前自查**：grep 你的改动，确认没有具体作品名/项目名/专有设定词

### 2. 层次清晰 / Clear Routing

每个规格文档必须标注"**何时读**"（`每章必读` / `仅当涉及` / `发布用` 等）：

- 每章必读：视角/人物/反AI/节奏/风格/检查清单
- 仅当涉及：性场景/暴力/世界观/爽点/平台
- 用途：让助手只读需要的规格，不污染上下文

### 3. 可执行 / Actionable

每条规则带"**自检项**"（Checklist item），让助手能逐条核对：

- ❌ 只写"对话要自然"（无法核对）
- ✅ "对话符合各角色腔调？不千人一面？"（可逐条勾）

### 4. 五层流程对齐 / Aligned with 5-Stage Pipeline

新增规格请明确它在流程中的位置（①访谈/②拆分/③规格/④写作/⑤修订发布）——参考 SKILL.md 的索引表。

---

## 贡献流程 / Workflow

1. **Fork + 分支**：从 main 拉分支（如 `feat/revision-spec`）
2. **开发**：遵循上述原则修改
3. **自检**：
   - 通用性：无项目专属词（见上）
   - 格式：与其他规格文档风格一致（标题层级/何时读/自检项）
   - 更新 SKILL.md 索引（新增规格时）
4. **PR**：描述改动 + 理由；如新增规格，附"何时读"建议
5. **评审**：维护者会检查通用性/层次/可执行三点

---

## 新增规格文档的 Checklist

新增 references/NN-xxx.md 时：

- [ ] 文件名格式：`NN-名称.md`（NN 为序号，沿用现有编号）
- [ ] 标题含"何时读"（第 1-2 行）
- [ ] 内容用通用表述（无项目专属词）
- [ ] 每条规则带自检项
- [ ] 更新 `SKILL.md` 的规格索引表
- [ ] 如涉及记忆系统/模板，同步更新 `templates/`
- [ ] 说明在五层流程中的位置

---

## 新增作家的 Checklist

向 `11-writers/` 添加作家时：

- [ ] 用 `11-writers/00-template.md` 的统一 10 维度模板
- [ ] 一句话定位（可借鉴一句）
- [ ] 技法可操作（不是"文笔好"这种空话）
- [ ] 更新 `11-writers-craft.md` 总索引表

---

## 新增类型风格的 Checklist

向 `12-genre-styles.md` 添加类型时：

- [ ] 风格内核 / 世界观构造 / 主角模式 / 写作要点 / 名场面模板 五要素
- [ ] 与近邻类型的边界（防混淆）
- [ ] 更新 00c-genre-docs 的题材映射表（如需）

---

## 许可 / License

贡献即视为同意以 [MIT](LICENSE) 协议授权你的贡献。

By contributing, you agree that your contributions are licensed under the [MIT](LICENSE) license.
