# QIDI 官方技能市场

QIDI Work 客户端的官方技能/插件分发仓库。客户端首次运行会自动注册本仓库为官方市场源。

## 目录结构（客户端按此约定解析，勿随意改动）

```
.grok-plugin/marketplace.json   # 市场索引：plugins/ 下各插件的元数据
default-skills/<skill>/SKILL.md # 默认技能：随客户端自动安装/刷新，用户无需操作
plugins/<plugin>/               # 可选插件：用户主动安装
  ├── plugin.json               # 插件清单（name/version/description…）
  └── skills/<skill>/SKILL.md   # 插件携带的技能
```

## 发布新内容的流程

1. 技能放 `default-skills/`（全员自动同步，务必精选、脱敏）或 `plugins/`（用户自选安装）。
2. 新插件需在 `.grok-plugin/marketplace.json` 的 `plugins` 数组登记，`source` 用相对路径
   （如 `./plugins/foo`）。
3. push 到 main 即生效；用户侧执行 `qidiwork plugin marketplace update` 或重启客户端拉取。

## 内容红线

- 本仓库公开可访问：禁止包含任何密钥、内部服务地址、未公开的产品源码或模型路由细节。
- 每个 SKILL.md 的 frontmatter 必须有 `name` 与 `description`（description 决定 AI 何时触发）。
