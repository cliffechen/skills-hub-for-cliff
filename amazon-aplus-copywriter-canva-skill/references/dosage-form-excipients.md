# 辅料与剂型模块（外壳 / 填充物 / 辅料的相对优势）

写进 JSON 的 `excipients`，生成「辅料与剂型」sheet。目标：把 Supplement Facts 的 **Other Ingredients** 和剂型写成 3 版图片文案（headline + subheadline + 支撑卖点），供 Supplement Facts 配套图、成分透明图或副图使用。

## 何时生成

- `工作区/03-SupplementFacts-可选/` 有标签图，或用户在对话里贴了标签 / Other Ingredients → 默认生成（A+ 与副图批次都适用），plan 里写明，用户可关。
- 没有标签，但用户特意提到剂型（"这次是软胶囊""软糖款"）→ 按所说剂型生成；具体辅料未知的，plan 里列为待确认项，文案只写剂型层面能成立的内容，不编造成分。
- 都没有 → 不生成。

## 第1步：识别剂型（优先级从高到低）

1. 用户在对话里明确说的剂型。
2. 标签 Serving size / 容器单位：Capsules、Softgels、Gummies、Tablets、Caplets、Scoop/g、mL。
3. Other Ingredients 的外壳/基质关键词：

| 关键词 | 剂型判断 |
|---|---|
| vegetable cellulose / HPMC / hypromellose / pullulan | 植物硬胶囊 |
| gelatin（无 glycerin）+ Capsules | 明胶硬胶囊 |
| gelatin / bovine gelatin / fish gelatin + glycerin (+ water) ；carrageenan + modified starch + glycerin | 软胶囊（明胶 / 植物软胶囊） |
| pectin 或 gelatin + glucose syrup / sugar / tapioca syrup + citric acid | 软糖 |
| croscarmellose / dicalcium phosphate / film coating / shellac + Tablets | 片剂 |
| 无外壳、按 g/scoop | 粉剂 |
| water / glycerin 基质、按 mL | 液体 |

剂型和依据（"标签 Serving size: 2 Capsules + vegetable cellulose"）写进 `excipients.form` 和事实底座。标签上的剂型与 listing / 构图不一致时，以标签为准并进冲突表。

## 第2步：给每个辅料定角色

| 剂型 | 外壳/基质 | 填充/载体 | 助流/抗粘 | 甜味/着色/涂层 |
|---|---|---|---|---|
| 硬胶囊 | vegetable cellulose（plant-based shell）、pullulan（plant-based, fermented from tapioca）、gelatin | microcrystalline cellulose（plant-derived, holds contents together）、rice flour | magnesium stearate、silicon dioxide（flow aid for uniform filling） | — |
| 软胶囊 | gelatin（bovine/fish，按标签）、carrageenan + starch（plant-based softgel）、glycerin、water | MCT oil / olive oil / sunflower oil（carrier oil the active is dissolved in）、beeswax、lecithin | — | annatto、caramel color（按标签写来源） |
| 软糖 | pectin（plant-based, gelatin 的替代）或 gelatin | — | coconut oil / carnauba wax（keeps gummies from sticking） | sugar / syrup、citric acid、natural flavors、colors from fruit & vegetable juice（按标签） |
| 片剂 | — | microcrystalline cellulose、dicalcium phosphate（binder） | magnesium stearate、silicon dioxide | croscarmellose（helps tablet break apart）、film coating（easier to swallow） |
| 粉剂 | — | 无或少量 | silicon dioxide（anti-caking） | sweetener / flavor（按标签） |
| 液体 | water / glycerin | — | — | preservatives、flavor（按标签） |

只写标签上真实出现的成分；表中的英文描述是功能性说明，可以写，但不要上升为功效。

## 第3步：三个固定角度（每种剂型都套用）

| 版本 | 角度 | headline 方向 | subheadline |
|---|---|---|---|
| A | 外壳/基质 | 这个剂型的外壳/基质是什么、来自哪里（植物胶囊 / 果胶软糖 / 鱼明胶软胶囊） | 1 句写清材料与适合人群（vegetarian 等，须有标签依据） |
| B | 辅料清单短而透明 | "Only N Other Ingredients" 类，N 必须等于标签 Other Ingredients 的数量 | 1 句点名全部辅料，或说明都写在标签上 |
| C | 每个成分各司其职 | "Every Ingredient Has a Job" 类 | 1 句把外壳/填充/助流的分工串起来，落回主成分剂量 |

- headline ≤2 行、≤45 字符为佳；subheadline 1 句、≤110 字符。
- `points` 3–4 条支撑卖点，单元格内换行分隔，可直接上图或做 bullet。
- 软胶囊的 A 版可写 carrier oil（"Urolithin A suspended in MCT oil"），只写"含有"，不写吸收；软糖的 A 版可写口感/形态（chewable、no water needed），不写好吸收。

## 证据红线

| 写法 | 处理 |
|---|---|
| no fillers / filler-free | 标签有 MCC、rice flour、dicalcium phosphate 等填充剂时**禁止**（scan FLAG） |
| better absorption / bioavailability / fast-acting | 辅料不能支撑，**禁止**（scan FLAG） |
| vegan | 标签写 Vegetarian 时不得升级；需要标签或供应商 vegan 声明（scan WARN） |
| gelatin-free / no gelatin | 植物外壳在标签上已列明可写；软糖/软胶囊须核对（scan WARN 提醒复核） |
| non-GMO、gluten-free、sugar-free、free from X | 需要标签或供应商声明（scan WARN） |
| bovine / fish / porcine gelatin 来源 | 只按标签或供应商规格书写 |
| clean、pure | 不单用；写成具体事实（"Only 3 other ingredients"） |

每条 item 标 `level`：✅ 标签直接支撑；⚠️ 需供应商声明或用户确认；`risk` 写清依据缺口。

## JSON

```json
"excipients": {
  "form": "硬胶囊（vegetable cellulose 植物胶囊）",
  "source": "标签图（用户提供 2026-10-03）",
  "items": [
    {"id": "EXC-A", "angle": "外壳/基质", "headline": "...", "subheadline": "...",
     "points": "...\n...\n...", "zh": "中文释义", "facts": "F14", "level": "✅", "risk": "..."}
  ]
}
```
