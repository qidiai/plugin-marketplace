# 6 段 identity block 工业模板（ref 图提示词）

来源：OnlyShot `ref-prompt-industrial.md` v0.5.0（SD-002 实战 + 2026 即梦/Midjourney 最佳实践）。
适用：即梦 text2image 5.0 / Seedance 2.0 / 一般文生图模型的 character ref sheet。

## 0. 核心原则（铁律 5 条）

```
1. ref 图 ≠ 成片：ref 图必须 neutral flat lighting（不要戏剧化光）
2. prompt ≠ 一致性：一致性靠 visual reference anchoring（ref 图本身），prompt 只控质量
3. identity block 锁定：身份块独立成段，每次生成逐字复用
4. 视觉指纹放 prompt 开头（前 200 token 权重最高，不是末尾）
5. NOT 词 ≤5 个（堆砌 ≥6 个 NOT，5.0 模型生效率降到 30%）
```

## 1. 模板（按需裁剪，人形角色用标准版）

```
[IDENTITY] character_id: CH-<NN>, fixed character design,
character must remain consistent across all generations,

[BODY] <身高头身比/体型/轮廓 silhouette>, <标志性体态特征>,
single cohesive figure,

[FACE] <发型+发色>, <瞳色+眼型>, <眉形>, <唇形>,
<面部固定标记：痣/疤/泪痣等>, expression: <默认神态>,

[ATTIRE] <上装: 颜色+材质+形制>, <下装>, <鞋>,
<配饰: 位置+颜色+材质>, NO clothing drift,

[LAYOUT] character reference sheet, three-zone layout:
left ~34% waist-up portrait (face design baseline),
top-right full body front/side/back views with identical face,
bottom-row 4 detail close-ups (eyes / accessory / footwear / hand prop),
single character per zone, identical character in all zones,
NO text labels, NO watermarks,

[STYLE] <画风>, neutral studio lighting flat even,
solid pastel <color> background,

[NEGATIVE] not photorealistic, not cinematic, not multiple characters
```

每段独立行 + 显式标签 → 模型按段处理 → 信息不混。

## 2. 视觉指纹铁律

### 错误：戏剧化关键词污染 ref

```
❌ dramatic shoujo manga lighting   → 让 AI 记住"光的方向"而不是"角色外观"
❌ lens flare                      → 镜头光晕掩盖角色细节
❌ glittery rose petals            → 装饰物干扰主体 silhouette
❌ chiaroscuro                     → 阴影被误判为脸部特征
❌ cinematic                       → 引入电影级运镜，破坏 character sheet 用途
```

### 正确：ref 中性 / 后续氛围分层

```
ref 图（character sheet 阶段）：
  ✓ neutral studio lighting flat even
  ✓ solid pastel background
视频/分镜阶段再叠：dramatic lighting / lens flare —— 那是分镜的事
```

## 3. 上游偏置（OnlyShot 最大教训）

```
ref 工艺是分镜图工艺的上游。
ref 不纯，分镜图加 NOT humans 也救不回来。
IP 设计阶段就要避坑：设定越简单几何，一致性越好。
```

## 4. 生成后自查两件事

1. **一张图里两个长相**（三视图的脸 ≠ 半身像）→ 重跑
2. **为塞细节把人压扁**（比例失调）→ 重跑
