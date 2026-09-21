---
name: skill-marketplace
version: 1.0.0
description: "指导用户从 QIDI 官方技能市场同步、搜索、安装、更新技能与插件。用户询问『怎么装 skill』『有没有 XX 技能』『同步技能』『更新插件/市场』时使用。触发词：安装skill、同步技能、找技能、skill怎么用、市场、marketplace、插件更新。"
---

# 技能市场同步与安装

QIDI Work 的技能（skill）与插件通过官方市场仓库分发。本技能帮助你引导用户完成同步和安装。

## 基本事实

- 技能存放位置：用户级 `~/.qidi/skills/<技能名>/SKILL.md`，项目级 `<项目>/.qidi/skills/`。
- 官方市场仓库：`https://github.com/qidiai/plugin-marketplace`，客户端首次运行会自动注册。
- 官方市场里 `default-skills/` 下的技能会随客户端自动安装/刷新，无需用户操作；
  `plugins/` 下的插件需要用户主动安装。

## 常用命令

```
qidiwork plugin marketplace list                 # 查看已注册的市场源及其插件
qidiwork plugin marketplace update               # 强制刷新所有市场源（重新拉取 git）
qidiwork plugin marketplace add <git-url|本地路径>  # 添加第三方市场源
qidiwork plugin list --json --available          # 列出已安装 + 市场可用的插件
qidiwork plugin install <名称|url>               # 安装插件
qidiwork plugin update [名称]                    # 更新插件（省略名称=全部）
```

## 操作要点

1. 用户说"同步技能"：先执行 `qidiwork plugin marketplace update`，完成后告知哪些技能有更新。
2. 用户找某类技能：用 `qidiwork plugin list --json --available` 检索可用插件，向用户展示名称和描述，
   **安装前必须让用户确认**，不要替用户静默安装。
3. 安装第三方源的插件前提醒用户：第三方内容不受官方审核，确认来源可信再装。
4. GitHub 访问慢或失败时：告知用户可稍后重试，或让管理员配置国内镜像源后用 `marketplace add` 添加。
5. 用户想自制技能：直接在 `~/.qidi/skills/<名字>/` 下写一个 `SKILL.md`
   （YAML frontmatter 至少含 `name` 和 `description`）即可被识别，无需安装步骤。
