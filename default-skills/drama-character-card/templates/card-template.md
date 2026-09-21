# 角色卡模板（逐角色一份，存为 cards/card-<slug>.json）

七层分区，语言分工：人读字段中文；锁面 / 图片提示词 / 音色提示词**永远英文**。

```json
{
  "id": "CH-01",                          // 角色码，提示词正文用它指代（画面代称）
  "name": "苏砚秋",                        // 中文名（禁止出现在 image_prompt）
  "aliases": ["苏总"],                     // 别名，同样禁止出现在 image_prompt
  "tier": "protagonist",                  // protagonist | major | supporting | minor
  "one_liner": "一句话定位",

  "anchors": [                            // 识别锚点：可见、可生成、可比较，禁空泛质量词
    "黑色高马尾，发尾齐肩",
    "左眼角下一颗小痣"
  ],

  "locks": [                              // 连续性锁：三条件才上锁，一集 ≤5 把
    { "face": "black high ponytail with silver ribbon", "scope": "EP01" }
  ],

  "identity_block": "[IDENTITY] ... [NEGATIVE] ...",   // 6 段身份块，逐字复用，纯英文
  "image_prompt": "完整 ref sheet 提示词，纯英文，≤1500 字符，NOT ≤5，锁面逐字包含",

  "variants": [                           // 变体：身份不变，服装/伤势/状态变化
    { "name": "日常装", "episodes": "EP01-EP09", "delta": "..." }
  ],

  "voice": {
    "timbre_prompt": "English timbre prompt for TTS engines",
    "catchphrases": ["中文口头禅 ≥3 句"]
  },

  "persona": {
    "contrast": "反差点一句话",
    "five_closeups": ["特写 1 ...", "特写 2 ...", "特写 3 ...", "特写 4 ...", "特写 5 ..."],
    "signature_moves": ["标志性动作 ≥2"]
  }
}
```

## 出卡前三查

1. 同批其他角色的锚点/声线——不得撞车
2. 每条锚点是"可见事实"还是"质量词"（气质/优雅/美丽 ❌）
3. 想上锁的可见事实是否满足三条件（跨 ≥2 镜、观众可见、不随剧情变）

完整可跑示例见同目录 `card-example.json`（可直接喂 `card_check.py` 验证）。
