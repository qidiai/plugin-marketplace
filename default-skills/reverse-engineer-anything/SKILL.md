---
name: reverse-engineer-anything
description: >
  qidicode 生态逆向分析（REA 适配版）：对出厂二进制（qidi.exe 等 Rust PE）、安装包/固件、
  Electron/JS 产物、浏览器运行时、网络抓包（HAR/SAZ/PCAP）、SQLite 快照做证据分级逆向——
  解释功能原理、对比版本差异、反编译/反混淆、rebrand 品牌残留审计、upstream 仓库情报。
  仅当结论依赖出厂产物或运行时证据时使用；普通源码仓库架构分析用常规工具（git grep / read_file），
  不走本技能。触发词：逆向、逆向工程、reverse engineer、反编译、拆包、APK 分析、固件分析、
  抓包分析、协议逆向、品牌残留、grok 残留、x.ai 残留、版本对比、qidi.exe 分析、二进制分析、
  /reverse-engineer-anything
metadata:
  upstream_version: "42"
  version: "1.0.0"
---

# REA（reverse-engineer-anything · qidicode 适配版）

当结论依赖**出厂二进制/安装包**、**反编译结果**、**应用运行时被动证据**，或**现有源码无法确立的行为**时，使用 REA。
对完整源码仓库做常规架构分析时，用常规仓库工具（`git grep` / `read_file`），**不要**走 REA 就绪检查或 provider 命令。

## 证据三分（贯穿全程，不可省）

每个结论必须区分：

- **观测（observation）**——引擎/脚本直接读到的原始事实（字节、范围、哈希、记录序号）。
- **推断（inference）**——由观测推导的结论，须标注依据与置信度（如 rustc 提交号由只读 `/rustc/<40-hex>/` 路径推断）。
- **未知（unknown）**——证据不足或覆盖不全的部分；**缺失不等于否证**（无 `.dep-v0` ≠ 无依赖，无命中 ≠ 不存在）。

引用 **Evidence ID**，保留 `limitations` 与不完整覆盖，**静态分析绝不暗示观测到了执行**。运行时请求只在其声明的
target/action 范围内执行，不得自行扩大目标或动作。逆向结论落 `团队审计报告目录` 时按此三级分层（见 §本地技能联动）。

## Connect only when needed（按需连接）

**装本技能 ≠ 装 REA MCP server、≠ 装分析引擎。** 安装技能只提供说明，不注册 MCP、不安装引擎、不给已运行的 agent 加工具。

- 若 REA 工具已可用且注册未被判定为过期 → **直接开工**，不要每次都先跑诊断/安装。
- 若工具缺失、调用被客户端拦、或所需 provider 不可用 → 读 [连接与恢复](references/connection-and-recovery.md)。
  先**诊断观测到的阻塞点**，继续可做的部分，修复后再回到原任务。客户端审批、shell PATH、注册状态、引擎可用性
  各有不同解法，**不要对全部问题重复跑安装**。
- 诊断不改配置：`npx` 可能下载包并写 npm 缓存。命令模板（替换当前客户端 ID）：
  `npx -y rea-agents@latest doctor --client codex --json`。
  客户端 ID：`claude_code` / `claude_desktop` / `codex` / `cursor` / `gemini_cli` / `windsurf` / `devin` /
  `opencode` / `antigravity` / `copilot_cli` / `commandcode` / `qwen_code` / `vscode` / `trae` / `grok_build` /
  `omp` / `pi` / `hermes` / `qoder` / `droid` / `zcode` / `dsh` / `grok_bot`。
  ⚠️ 上游特例：`grok_bot` 无本地文件注册——`doctor` 会报 Grok Bot 聊天步，且 `setup` **不写** `mcp.json`。
  ⚠️ 不认识的客户端先用 `npx -y rea-agents@latest doctor --json` 摸底真实注册结果，再决定 `setup` 的范围。
- **配置修复必须先出只读计划**：`npx -y rea-agents@latest setup --client <id> --dry-run --json`，
  展示确切路径、备份、改动，**获批准后**再 `... setup --client <id> --yes`。`--install-hopper` 仅在该独立安装确需且明确批准时加。
- 修复后**重启/重连**受影响 agent，确认工具真的出现在会话里；仍缺失则查客户端启动错误，而不是循环重装。

REA 安装**从不**安装/升级 Node.js、npm、Homebrew、Java、Ghidra、IDA、JADX、Kuna、Binwalk、Unblob 等。
用既有前置；**不要为修 MCP 注册而装无关软件**。不支持的客户端用版本锁定的手动 stdio 注册或走 CLI。

**CLI fallback（本机首选通道，无需 MCP、无需原生引擎）**：

```bash
npx -y rea-agents@latest analyze-javascript-application /absolute/path/to/app --json
npx -y rea-agents@latest inspect-rust-binary /absolute/path/to/qidi.exe --json
```

注：`@latest` 仅用于首次摸底；首次跑通后按实际版本钉住（如 `npx -y rea-agents@<版本号>`），避免供应链漂移与不可复现。当前 registry 最新版本：**6.5.0**（2026-10-16 查询）。

CLI 返回的 Evidence 与 MCP 结果同源，按同等审慎阅读（graph/limitations/unknowns）。CLI fallback **不**建立"MCP 已配置"。
原生 CLI 任务仍需要其选定引擎（静态 JS 检查不需要 Hopper/Ghidra）。优先用已安装的 `rea`；无则用
`npx -y rea-agents@latest`。具体降级决策见下节「本机环境与降级路径」。

## Route the target first（先按目标路由）

按用户**实际交付的**目标类型选第一个工具。活跃目标型原生/归档工作流用 `open_binary`；target-free 工具自带显式路径，无需它。

- ASAR / 已解包 JS/Electron 树：`analyze_javascript_application`；需可读源码恢复用 `recover_javascript_sources`。
- 归档/包成员清单（ZIP/APK/IPA/MSIX/AppX/DMG）：`open_binary` + `inspect_artifact`（图与发现）。
- Android APK 代码/类/方法/入引用：`inspect_android_package`，再按需 `inspect_android_class` / `inspect_android_method` / `trace_android_references`。
- 托管 PE/CLI 程序集：`inspect_managed_artifact`。
- 固件镜像：`inspect_firmware_regions` / `extract_firmware`（调用方提供 Binwalk/Unblob，Linux）。
- .NET NativeAOT PE/ELF：走原生 Ghidra 路线（见 native-and-artifacts）。
- 已打开的浏览器页面：`list_browser_targets`；agent 需执行的动作：`capture_browser_scenario`。
- 已打开的 Electron 运行时：`list_electron_targets`（先 `inspect_electron_fuses` 查 fuse）。
- Fiddler `.saz`：`inspect_web_network_capture` + `format:"saz"`；实时流量接 Everywhere MCP。
- 存留的 HAR/SAZ/mitmproxy/aioquic qlog：`inspect_web_network_capture`。
- 录制的包捕获：`inspect_packet_capture`（需 Linux + prlimit + `REA_TSHARK_COMMAND`）；地址/DNS/SNI 汇总用 `inspect_pcap_capture`（需 Wireshark 4.x tshark）。
- 录制的逻辑/信号轨迹：`decode_signal_recording`（Linux + sigrok-cli 0.7.2）。
- 本地 WebAssembly：`inspect_wasm_artifact`（需 WABT 1.0.42，`REA_WABT_BIN_DIRECTORY`）。
- 本地 EVM 字节码：`inspect_evm_interface`。
- 嵌入的 Go 构建元数据：`inspect_go_binary`（target-free）。
- 嵌入的 cargo-auditable Rust 依赖元数据：`inspect_rust_binary`（target-free，显式 ELF/PE/thin Mach-O；**缺 `.dep-v0` = 空元数据，非无依赖**）。
- 本地 SQLite 快照：`inspect_sqlite_database`（需 Node 24.x ≥24.15 或 26+）。
- 本地 Linux ELF 布局/符号/重定位/静态缓解：`inspect_binary_layout`（**仅 ELF**，target-free）。
- Linux x86-64 ELF core：`inspect_recorded_crash`。
- PE 资源类型/名/语言树与图标组：`inspect_pe_resources`（便携、无需引擎）。
- 原生可执行/库/分析库：`open_binary` 后用聚焦分析工具；需要元数据/清单时 `binary_overview`。

若用户只说"我的 app"却没有名字/路径，先问是哪个再用。

## qidicode 目标路由（本技能适配重点）

在当前工作区（qidicode = 工作区根 Rust workspace，产品 exe `qidi.exe`）按目标类型路由；upstream 命令先设 `$UPSTREAM_GIT_DIR` = 团队上游镜像的 `.git` 路径（局域网 SMB 镜像，路径按团队环境配置）：

| 目标 | 首选工具 | 本机现实与降级 |
|---|---|---|
| qidi.exe 等 Rust PE（依赖清单/编译器） | `inspect_rust_binary`（读 `.dep-v0` cargo-auditable 元数据，target-free） | CLI `inspect-rust-binary`；无 Rust 安装也能读；**缺 `.dep-v0` = 空元数据 ≠ 无依赖** |
| PE 资源树/版本信息/图标 | `inspect_pe_resources`（target-free，无需引擎） | CLI 同上（`inspect-pe-resources`） |
| 品牌残留审计（grok.com/x.ai/Grok 字样） | 本技能脚本 `scripts/scan_brand_leftovers.py` | 纯 Python stdlib；**命中只作线索，须回源码确认** |
| 版本对比（历史 exe ↔ 当前） | SHA-256 + 体积 + `inspect_rust_binary` 依赖 diff + 字符串 diff | 历史 exe 在本机 exe 备份目录；当前在 `target/release/qidi.exe`；**对比前先备份/只读** |
| upstream 情报（xai-grok-* monorepo 镜像） | `git --git-dir=$UPSTREAM_GIT_DIR log/diff` | **只读情报源，非合并目标**；路径全不同只能按主题 cherry-pick；仅安全类修复（RUSTSEC）值得定期看 |
| SQLite 快照（cf-memory 记忆库等） | `inspect_sqlite_database` | 需 Node ≥24.15（本机 v24.18 ✅）；用前 `node -v`；先 schema 后表格；保留 WAL 双 digest |
| Electron/JS（office-workbench 前端 / website / ASAR） | `analyze_javascript_application` / `recover_javascript_sources` | CLI fallback `analyze-javascript-application <path> --json` **不需 MCP**；Wakaru 恢复仅 Linux x64 |
| 浏览器运行时观测 | `list_browser_targets` / `capture_browser_scenario` | 本机已装 **playwright MCP** 可作替代通道 |
| 抓包（HAR/SAZ/PCAP/qlog） | `inspect_web_network_capture` / `inspect_pcap_capture` | tshark/PCAP 路线需 Linux；Windows 上 HAR/SAZ 可用 |
| Android APK / 固件 / WASM / EVM / Go | 保留上游路由 | 本机无 JADX/Binwalk/WABT/sigrok——**用到再向用户申请安装，不擅自装** |

每类目标的详细操作手册见 [qidicode 目标手册](references/qidicode-targets.md)。

## 本机环境与降级路径

环境现状（按实际环境为准）：

- **无**：REA MCP server、IDA、Ghidra、`strings.exe`、JADX、Binwalk、WABT、sigrok-cli。
- **有**：node（≥24.15；`npx -y rea-agents@latest ...` CLI fallback 可行）、python 3.12、cargo、git
  （按团队网络策略为 github.com 配置 git 代理；其他域名原网络直连）。

**默认路径**：
1. **CLI fallback 优先**——如 `npx -y rea-agents@latest analyze-javascript-application <path> --json`、
   `npx -y rea-agents@latest inspect-rust-binary <path> --json`。CLI JSON 可能很大，**重定向到文件再读**，勿直接灌进上下文。
2. **MCP 工具仅在会话里确实出现时使用**——以连接到的 server 实际 `tools/list` 与 schema 为准（技能描述的能力可能新于已装的旧 npm 版本）。
3. **工具缺失 → 降级本地脚本 + 显式声明"未经引擎验证"**（用本技能 `scripts/` 或 python 探针）。
4. 不得为凑齐工具而擅自安装软件；需新增引擎时**向用户申请**。

**Windows 注意事项**：PowerShell **无 `&&`**（用 `;`）；控制台 **GBK 乱码**——脚本与输出一律 **UTF-8**，读日志用
`Get-Content -Encoding UTF8`；本机**无 `rg`**（grep 工具常返回空，用 `git grep` 或 `read_file`）。
PowerShell 的 `>` 重定向默认写 **UTF-16**——落盘用 `| Out-File -Encoding UTF8` 或直接用工具自带的 `-o` 参数（UTF-8）；读回乱码先转 UTF8 再读。

## Work summary-first（大目标先摘要）

先用默认结果与其内联 Evidence / graph 上下文。对体积未知或偏大的 JS 应用 / ELF 布局，先用 `"detail": "summary"` 调用
（`analyze_javascript_application` / `inspect_binary_layout`），再用 `inspect_analysis_view` 读被保留的 `parent_evidence_id`。

- 分页 module 身份并选中返回的 `node_id` 再取 item；一个路径可对应多个 graph 角色。
- **不要**重复相同的分析或重复一次被拒的调用——除非输入变了或阻塞已解除。
- 仅在返回结果留下**具体未答问题**时才做聚焦追问。

若 MCP 报 `resource_constraint`（`details.resource: "transport"`），用其报告的**同会话** Evidence 引用调 `inspect_analysis_view`
取 summary / 单 section / 稳定分页；或 `export_evidence_bundle` 导出完整会话。分析在账本里仍完整，别仅为了同样的超大响应而重跑。
客户端也可能在**无 REA 传输错误**下截断成功结果——把预览当作不完整，用 parent ID 取更小视图或导出，别把预览当规范 JSON 解析、别重跑 producer。

## Plan broader investigations（多特征分阶段）

跨多特征/子系统的请求，用分阶段工作流：

1. 把请求转成**问题清单**，列出每个答案所需的证据；先从对话/工作区解析目标身份与约束，再问。
2. 检查当前 REA session、产物身份、已存分析库、书签、先前证据；**复用匹配状态**，不重复开会话或重复相同分析。
3. 从**最小有用** overview/inventory 起；沿入口→数据→状态变化追到结果；围绕具体假设**批量**操作，仅当留下具体缺口时扩展。
4. 影响问题时，把相关打包资源与配置与代码一并检查；用格式感知解析器，**别凭文件名/字符串/布局臆测行为**。
5. 用结论**所需**的证据类型佐证；仅当静态证据无法回答且所需宿主运行时/OS 访问可用时，才用运行时观测。
6. 把工作**解耦为独立问题**：可并行且互不依赖时派独立 worker，分派不同 scope、指向既有证据、要求回传
   **sources / conclusions / gaps**（对应 [`dev-orchestra`]）；否则顺序做。
7. 维护简明的**finding ledger**：每条结论链接 Evidence ID、置信度/证据类型、搜索边界、剩余未知；更新共享索引/报告供后续复用。

收尾前复查原始清单，逐条标 answered / partially / unresolved；**有未决必需问题就不算完成**，有界负搜索保持有界。

## 与本地技能联动

- **audit-rubrics**（`docs/audit-rubrics/RUBRICS.md`）：三级证据分层（硬事实 / 推断+置信度 / 未知）与本技能
  证据三分同构；逆向审计结论按此分层落 `团队审计报告目录/YYYY-MM-DD-主题-类别.md`。
- **bt-panel-api**：Web API 逆向的本地实战范式（登录协议三段式、CSRF 层、通道选择、字节安全）——
  分析面板/Web 系统 API 时**先读它**。
- **check-work**：逆向产出（脚本 / 补丁）用验证子代理复核。
- **dev-orchestra**：多特征逆向对应上节 staged 第 6 步——独立问题派并行子代理，约定回传 sources/conclusions/gaps。

## Read only the relevant guide（只读相关指南）

- 原生二进制、托管程序集、归档与解包：[references/native-and-artifacts.md](references/native-and-artifacts.md)
- ASAR、已解包 JS、特征追踪、版本对比：[references/javascript-applications.md](references/javascript-applications.md)
- Android APK 声明、类、方法、静态引用：[references/android-applications.md](references/android-applications.md)
- 浏览器/Electron 观测（被动与场景）与静态/运行时对账：[references/runtime-observation.md](references/runtime-observation.md)
- Evidence 分页、对比、剩余未知、验证：[references/evidence-workflows.md](references/evidence-workflows.md)
- 连接、注册修复、审批、provider 阻塞恢复：[references/connection-and-recovery.md](references/connection-and-recovery.md)
- **qidicode 专用目标操作手册（中文）**：[references/qidicode-targets.md](references/qidicode-targets.md)

## Finish the task（收尾）

用平实语言解释发现并挂到返回的证据上；用户要"做东西"时用常规编码工具，并把**观测行为**与**设计选择**分开。
分析完成用 `close_binary` 关闭已打开的原生会话（`close_binary` 会清空 retained 引用——需要跨连接保留就先
`export_evidence_bundle` 导出）。

> 上游：[morluto/rea](https://github.com/morluto/rea)（MIT），本技能为其 reverse-engineer-anything 技能的 QIDI 适配版。
