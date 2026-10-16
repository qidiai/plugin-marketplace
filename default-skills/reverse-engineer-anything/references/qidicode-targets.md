# qidicode 目标操作手册

本手册是 [SKILL.md](../SKILL.md) 「qidicode 目标路由」表的展开操作版。所有命令均为**只读**优先；任何写操作先备份。
证据一律按**观测 / 推断 / 未知**三分记录，引用 Evidence ID。

**npx 版本注**：`@latest` 仅用于首次摸底；首次跑通后按实际版本钉住（如 `npx -y rea-agents@6.5.0`），避免供应链漂移与不可复现。当前 registry 最新版本：**6.5.0**（2026-10-16 查询）。本手册各处 `npx -y rea-agents@latest` 命令同此，不逐条改。

---

## 1. qidi.exe（Rust PE）

### 1.1 依赖与编译器元数据 — `inspect_rust_binary`

**用途**：读取嵌在 `.dep-v0` 段（cargo-auditable）里的 crate 列表、版本、依赖序与依赖索引；由只读 `/rustc/<40-hex>/` 路径**推断** rustc 提交号。

- MCP：`inspect_rust_binary`，显式传本地 ELF/PE/thin Mach-O 路径，**target-free**，无需 `open_binary`、无需装 Rust、无需反汇编器。
- CLI（本机首选）：`npx -y rea-agents@latest inspect-rust-binary <工作区根>/target/release/qidi.exe --json`（大 JSON 重定向到文件再读）。

**输出解读边界**：
- 保留**包顺序**、**依赖索引**、段文件范围、产物 SHA-256。
- **观测**：段内的 crate 名/版本字节。
- **推断**：`/rustc/<40-hex>/` → rustc 提交号（路径是只读观测，提交号是推断，不能单独确证编译器）。
- **未知**：**缺 `.dep-v0` 段 = 空元数据，不等于"该二进制无依赖"**；被 strip / 非 cargo-auditable 构建都可能无段。省略的 package kind 保持 null。

### 1.2 资源树 / 版本信息 / 图标 — `inspect_pe_resources`

**用途**：便携检视 PE32/PE32+ 的资源类型/名/语言树、目录/数据/载荷范围、代码页、载荷哈希、静态图标组引用；**无需活跃目标或引擎**。

- MCP：`inspect_pe_resources`，显式绝对 `path`。
- CLI：`npx -y rea-agents@latest inspect-pe-resources <工作区根>/target/release/qidi.exe --json`。

**边界**：同语言图标解析是显式的；缺失引用与大小不符保持可见；其他载荷为**不透明**（不解码图像、不模拟 Windows 资源加载）。
可从中取 VERSIONINFO（`FILEVERSION`/`ProductVersion` 等）做版本线索，但**版本字符串是观测，不等于构建日期或提交**。

### 1.3 品牌残留审计串联 — `scripts/scan_brand_leftovers.py`

REA 的 rebrand（xai-grok-* → cf-*）在二进制里可能残留 grok/x.ai 字样。标准串联：

1. **扫**：`python scripts/scan_brand_leftovers.py <本机 exe 备份目录>/qidi.exe.old-20261007 -o brand.json`
   —— 输出每条关键词的命中次数与样本字符串（ASCII + UTF-16LE）。脚本自带免责声明：
   **命中仅为字符串线索，不等于功能残留**。
2. **命中 → 回源码确认**：拿命中字符串（如 `cli-chat-proxy.grok.com`、`docs.x.ai`、`QIDI_COM_METHOD_ID="grok.com"`）
   回到工作区根（`git grep <字串>`，本机无 `rg`）定位真实代码位置，判断是**真残留**还是**
   被正常引用的/无害的历史串**（如 grok 是 CLI 源出品牌、某些后端协议名不可改）。
3. **记录**：把确认后的清单按团队内部品牌残留清单登记：文件:行 + 当前值 + 目标值 + 风险级别
   （改涉存量会话鉴权者高危——**改前须用户拍板**）。
   ⚠️ **落盘纪律**：扫描样本可能带出文件内嵌的密钥/token 字样；输出 JSON 只落临时目录，不得把敏感样本贴进对外报告或提交物。
4. 结论按证据三分：命中=观测；"是功能残留"=推断（须源码佐证）；"是否需改"=另议。

**短词告警**：`grok` / `xai` / `GROK` 只作线索，误报常见（可能出现在第三方依赖名、注释、URL 片段），**必须回源码确认**。

### 1.4 PE 布局分析 — 本机降级

`inspect_binary_layout` **仅支持 Linux ELF**（target-free，用调用方 pwntools）。**PE 无对应 provider 时**：

- 降级：用 python 读 PE 头/节表（自写探针落临时目录），或
- 在结论中**显式声明"PE 布局未经引擎验证（unknown）"**，不得把自家脚本结果说成 REA 证据。

---

## 2. 版本对比工作流（历史 exe ↔ 当前）

**历史 exe 目录**：本机 exe 备份目录（只读，勿覆盖）。命名规则（实测快照）：

- `qidi.exe.old-<日期>`（如 `qidi.exe.old-20261007`）
- `qidi.exe.old_<日期>`（下划线变体，如 `qidi.exe.old_20261011`）
- `qidi-release-<日期>.exe`（如 `qidi-release-20260921.exe`）
- `qidi.exe.pre-a1-<日期>` / `qidi.exe.pre-zero-<日期>`（里程碑标记）
- `qidi.exe.running-<日期>` / `qidi.exe.v5..v8-<日期>`（当日迭代）
- `qidi_<短哈希>_<日期>.exe`（带提交短哈希，如 `qidi_47f3b281_20261015.exe`）

**当前产物**：<工作区根>/target/release/qidi.exe。

**对比步骤**（全部只读）：

1. **SHA-256 + 体积**：两版各算 `Get-FileHash -Algorithm SHA256` 与 `Length`；哈希相同 → 同一产物，直接停。
2. **依赖 diff**：分别 `inspect-rust-binary`，按 crate 名/版本对齐，列 **added / removed / 版本变化**。
   - 仅当**两侧 `.dep-v0` 都存在且完整**时才能断言 added/removed；缺段侧记 **unknown**，不记"移除"。
3. **品牌残留 diff**：分别跑 `scan_brand_leftovers.py`，比对各关键词命中数的增减（观测）。
4. **字符串 diff（可选）**：用 python 探针比对 ASCII/UTF-16LE 字符串集合，关注新增/消失的非通用串。
5. **结论**：按证据三分写。版本字符串差异=观测；"某功能某版引入"=需结合依赖/字符串/源码的推断；覆盖不足处=unknown。

**纪律**：对比**绝不**写回本机 exe 备份目录；需要落证据的中间产物放临时目录（`cargo clean` 可回收）。

---

## 3. upstream 情报（xai-grok-* monorepo 镜像）

**位置**：局域网 SMB 镜像（路径按团队环境配置，慢但可用）。**只读情报参考源，非合并目标**。

**先设路径变量**：

```powershell
$UPSTREAM_GIT_DIR = '<团队上游镜像>.git'
```

**可达性探测**：先 `Test-Path $UPSTREAM_GIT_DIR` 探测可达性（SMB 波动属正常，不可达稍后重试，勿急判定 upstream 不可用）。

**SMB 直读命令模板**（不要 `git fetch upstream`——会报 "shallow roots are not allowed to be updated"）：

```powershell
git --git-dir=$UPSTREAM_GIT_DIR log --oneline -20
git --git-dir=$UPSTREAM_GIT_DIR log --oneline --since=2026-10-01
git --git-dir=$UPSTREAM_GIT_DIR show <commit>
git --git-dir=$UPSTREAM_GIT_DIR diff <a> <b> -- <path>
git --git-dir=$UPSTREAM_GIT_DIR log -p -1 -- <path>
```

**定位声明（2026-10-05 用户确认）**：上游为**低频情报参考源、非合并目标**。

- 上游 crate 命名 `xai-grok-*`，我们已 rebrand 为 `cf-*`——**路径全不同，直接 merge 不可行**；同步只能按主题 **cherry-pick + 手工改名适配**。
- fork 以来从未同步；分叉已深且双向加速演进。
- **仅安全类修复（RUSTSEC / 依赖漏洞）值得定期扫一眼**；功能类改进一律以我们自己的设计与实现为准。

提交信息多称 "Synced from monorepo"（每周 1–3 次）。

---

## 4. SQLite 记忆库（cf-memory 等）

**工具**：`inspect_sqlite_database`（MCP），显式本地快照路径。

**版本门**：需 **Node.js 24.x ≥24.15 或 26+**（提供原生 `DatabaseSync.limits`）。用前先 `node -v` 验；
不满足则在结论中**声明该路线不可用**，不要装 Node。

**cf-memory 库位置**：`~/.qidi/memory/`——先 `Get-ChildItem` 确认**实际文件**（每个会话/工作区子目录内才是真正的库文件，**不要**猜文件名，先 ls）。仓库相关子目录形如 `qidicode-<hash>`。

**schema-first 流程**：

1. 先读 **schema**（默认紧凑清单）；需要完整存储 schema 才 `schema_scope: "database"`。
2. 需要行时**选一张精确的普通表**并指定 `columns`（避免无关/大单元格）；默认 selected-table schema + 20 行；用 `row_limit` 限定样本。
3. **WAL 双 digest**：同时保留数据库文件与既有 `-wal` 兄弟文件的**原始 digest**；用它前先取**静默一致的快照**，别假设"live 库+WAL 被原子拷贝"。
4. 虚拟表/影子表/视图是 schema 事实，**非取数目标**。行样本会报告截断且顺序未定义。REA 检查私有副本，源文件不动。

---

## 5. Electron/JS 与浏览器

### 5.1 JS/Electron 产物

**入口**（本机相关）：`office-workbench` 前端、`website`、以及任何解出的 ASAR / 树。

- 静态分析：MCP `analyze_javascript_application`（对调用方给的 ASAR 或已解包树）。
- **CLI fallback（不需 MCP、不需原生引擎）**：

  ```powershell
  npx -y rea-agents@latest analyze-javascript-application <绝对路径> --json > app-evidence.json
  ```

  CLI JSON 可能很大 → **重定向到文件**再读，勿直接进上下文。用 `--source-path`（可重复）可只读指定文件。
  ⚠️ PowerShell 的 `>` 重定向默认写 **UTF-16**——落盘用 `| Out-File -Encoding UTF8` 或直接用工具自带的 `-o` 参数（UTF-8）；读回乱码先转 UTF8 再读。
- 可读源码恢复：`recover_javascript_sources`（**Wakaru 仅 Linux x64**，本机不可用 → 声明该路线不可用）。

**大图先摘要**：`"detail": "summary"` → 用返回的 `parent_evidence_id` 调 `inspect_analysis_view` 分页 module（见
[javascript-applications.md](javascript-applications.md) 的 module-view / trace 配方）。版本对比用 `compare_application_versions`。

### 5.2 浏览器运行时观测

- 首选：MCP `list_browser_targets`（被动）/ `capture_browser_scenario`（agent 需执行动作）。
- **本机替代通道**：已装 **playwright MCP**（25 工具）——当 REA 浏览器工具不可用时，用 playwright MCP 做被动/场景观测，
  证据须**显式声明来自 playwright 而非 REA**。
- **静态观测 ≠ 执行**：绝不说 REA/playwright"点击/导航/求值/捕获了历史活动"，除非确实是该通道的声明的动作。

---

## 6. 抓包与网络

- **HAR / SAZ（Windows 可用）**：`inspect_web_network_capture`；SAZ 传 `format: "saz"`（加密归档不支持）。
  大捕获先 `detail: "summary"` 再用 `inspect_analysis_view` 分页（`view: {kind:"capture", detail:"preview", ...}`）。
  HAR 的 API 面分组用 `view: {kind:"api-surface"}`（格式匹配是**推断**，非 handler 身份/ schema）。
- **Fiddler Everywhere**：实时流量接 Everywhere 的独立 MCP server（显式 `sessionsSource`，如 `LiveTraffic`/`AgentCalls`）。
- **PCAP / 包字段**：`inspect_packet_capture`（Linux + util-linux prlimit + `REA_TSHARK_COMMAND`）；地址/DNS/SNI/协议汇总用
  `inspect_pcap_capture`（Wireshark 4.x tshark/capinfos）。**Windows 上 tshark 路线需 Job Objects 且非默认便捷**
  → 优先用 HAR/SAZ；确需 PCAP 时声明前置是否满足。这些只**读录制**，不做实时抓包。
- **qlog**：`inspect_web_network_capture`，aioquic 1.5.0 JSON 0.3 起；其他 qlog 布局与 PCAP 关联不支持。

---

## 7. 暂不可用路线清单（用到再向用户申请安装）

本机**缺前置工具**，以下路线暂不可跑；需要时**向用户申请**，**不擅自安装**：

| 路线 | 工具 | 缺的前置 |
|---|---|---|
| Android APK 代码/类/方法 | `inspect_android_package` 等 | 无 JADX MCP JAR 0.7.1 + JDK 17+ |
| 固件镜像区域/解包 | `inspect_firmware_regions` / `extract_firmware` | 无 Binwalk/Unblob（且需 Linux） |
| WebAssembly | `inspect_wasm_artifact` | 无 WABT 1.0.42 |
| 逻辑/信号轨迹 | `decode_signal_recording` | 无 sigrok-cli 0.7.2（且需 Linux） |
| 包捕获 PCAP | `inspect_packet_capture` | tshark/Linux prlimit（Windows 有限） |
| 崩溃 core | `inspect_recorded_crash` | 需 Linux x86-64 ELF core |
| 原生反编译 | `open_binary` + Hopper/Ghidra/IDA | 本机无 IDA/Ghidra |

另外 EVM（`inspect_evm_interface`）与 Go 元数据（`inspect_go_binary`）路线 target-free 无前置，可直接试——属可用但未在本机验证过的路线，结果须标注"未经本机引擎验证"。

对不可用路线：**先用可支持的静态/清单证据回答一部分**，把不可用证据**单列**为 unknown，**不要**拿另一目标顶替、
也**不要**把普通 shell 工具的输出标成 REA 证据。
