---
name: qidi-guide
version: 1.0.0
description: "QIDI Work 使用入门。用户询问『QIDI Work 怎么用』『有哪些功能』『怎么开始新任务』『技能和插件是什么』『怎么切换模型』时使用。触发词：入门、教程、怎么用、新手、quick start。"
---

# QIDI Work 使用入门

当用户对 QIDI Work 的用法不熟悉时，按以下要点引导。

## 核心概念

- **任务会话**：一个工作区可开多个任务，AI 在你的项目目录里读代码、改代码、跑命令。
- **技能（Skill）**：`SKILL.md` 形式的专项知识包，AI 会在合适时机自动调用；
  用户也可以用 `/技能名` 主动触发。存放于 `~/.qidi/skills/`（全局）或 `.qidi/skills/`（项目内）。
- **插件（Plugin）**：比技能更重的扩展包，可携带技能、子代理（agents）、hooks 和 MCP 服务。
- **市场（Marketplace）**：官方分发渠道，`qidiwork plugin marketplace list` 查看当前源。

## 账号与额度

- 登录：启动后按提示打开浏览器输入登录代码，或用客户端的设备码流程完成登录。
- 模型：`auto` 为智能路由（推荐）；`qidiwork` 网关也提供可选模型列表，按套餐（free/pro）可见。
- 额度：按日计请求数与 token 数，超限会提示 `quota_exceeded`，次日零点自动重置。

## 快速上手路径

1. 打开 QIDI Work，完成登录。
2. 在聊天框直接描述任务（会自动建立会话）。
3. 需要专项能力时同步市场：`qidiwork plugin marketplace update`。
4. 用 `qidiwork plugin list --json --available` 查看可安装的官方插件。
