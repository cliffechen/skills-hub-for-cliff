# 写完后的逐句检查：七关、换牌测试、去 AI 腔

第 5 步写完初稿后、第 7 步跑脚本前做。`conversion-copy.md` 管“有没有购买冲动”，这里管“每一句立不立得住”。改过的句子记进 JSON 的 `sweeps`，Excel 出「检查记录」表，用户能看到哪句为什么改。

方法改写自 coreyhaines31/marketingskills（MIT）的 `copy-editing`（逐遍检查）和 `copywriting`（AI 腔清单），按亚马逊补剂图片文案删改；未照搬原文。

## 1. 七关

一次只看一件事；后面的关改了句子，回头再过前面的关。

| 关 | 问什么 | 不过关的样子 | 怎么改 |
|---|---|---|---|
| 1 清楚 | 读者一遍能懂吗 | Calcium for your frame（frame 指什么？）；一句话塞两件事 | 换成具体的词；一句一个意思 |
| 2 语气 | 像这个品牌吗 | 前面克制，后面突然喊口号 | 对照品牌档案 |
| 3 所以呢 | 这句话对读者意味着什么 | 只列成分名和认证名 | 补上“它给你什么”：Vitamin D3 helps your body absorb that calcium.* |
| 4 凭什么信 | 每个说法指得到依据吗 | 写了“随早餐”但没有标签用法；写了“磨砂玻璃瓶”但只来自一条评论 | 指到 F / E 编号；指不到就删，或标 `[NEED: …]` |
| 5 够不够具体 | 能换成数字、对象、时刻吗 | for the years ahead；Six actives | 400 mg, 31% of your Daily Value；写不具体的多半是废话，删 |
| 6 情绪 | 读者有没有感觉到什么 | 全是平铺的参数 | 用处境、生活时刻、反差（`conversion-copy.md` §6）；不吓人 |
| 7 顾虑 | 读者的疑问答了吗 | 换牌者最想知道的“钙量够不够”全组没有一处回答 | 产品上下文里每条反对意见至少在一张图上用事实回答 |

**第 7 关在亚马逊上的做法**：原方法靠保证、退款、免费试用来降低风险，这些词在 A+ 里违规，不能用。这里改成用事实回答疑问：含量和 %DV、每天几粒、检测了什么、在哪种工厂生产。A+ 或轮播里可以做成问答表（How many a day? | Two softgels.）。

## 2. 换牌测试

把品牌名和产品名遮住，这句话放到另一个品牌、另一个成分的图上还成立吗？成立就重写。

- 不过关：Clear Label. Clear Choice. / Thoughtfully Packaged. Carefully Formulated. / Made for Every Active Day / Stay Active. Age Well.
- 过关的句子里有本品才有的东西：一个标签上的数字、一个成分、一个剂型事实、一条来自本品买家的处境。
- 这是 `conversion-copy.md` §1“换成分测试”的加强版：不只换成分，连品牌一起换。
- 缺差异点、改不动时，标 `[NEED: 差异点]`，不要硬凑。

**lockup 的规则（用户 2026-10-13）**：两行 lockup 可以保留“两个短句”的形式，但**必须过换牌测试**。做法二选一：

1. 句子里带本品特有的词或数字（`meta.swap_terms` 里的词，或任何数字）——脚本自动放行。
2. 不带的，在该行写 `"swap_ok": "为什么别的品牌用不了这句"`。写不出理由，就是没过。

`scan_copy.py` 对 lockup 位的两短句做这项检查：既没有特有词和数字，也没有 `swap_ok`，即 FLAG。

## 3. 去 AI 腔

读者一旦觉得这页是生成的，会连带怀疑旁边的说法。句子的形状比用词更容易露馅。

**不写（出现一次就是问题）**

| 形状 | 例 | 改法 |
|---|---|---|
| 否定对比 | Calcium Was Never the Whole Story. / One Routine, Not Five Bottles. / It's not X, it's Y. | 直接说 Y，带上理由或事实：Your Calcium Arrives With Five Other Actives. |
| 否定清单 | No fillers, no gelatin, no guesswork. | 说有什么。真正算卖点的“没有”只说一次：Vegan Softgel, No Gelatin. |
| 句尾堆砌 | 一句话说完了，逗号后面再接一串好处 | 在主张结束处断句 |
| 自问自答、冒号揭晓 | The result? …… / The best part: …… | 删掉问句，留答案。读者自己会问的问题不算（Switching Brands?） |
| 铺垫句 | You should not have to take our word for it. / Here's the thing | 删，直接给内容 |
| 套话 | Say goodbye to / Unlock / Take it to the next level / X, reimagined | 换成它代表的事实 |
| 标题里的破折号 | Made to Be Taken Every Day — | 用句号或换行 |

**限量**

- 三连短句（Six Actives. Two Softgels. One Bottle.）和三项并列：一张图最多一处。
- 否定对比如果是品牌签名句式（如品牌档案里的 Not more ___. Better ___.）或用户认可过的原句：每个读者版本整组最多一句，脚本超过一句即 FLAG。
- seamless、powerful、premium、clean 这类词：换成它代表的事实。
- 一组图里各张的句子形状要有变化，不要每张都是“两个短句对仗”。

**怎么改**：回到事实（机理、数字、对象、步骤）重写。换同义词只会造出新的套话。

**事实不够时**：在文案里写 `[NEED: 标签上的服用说明]`，这一条进③待确认，不编。`scan_copy.py` 遇到未解决的 `[NEED:` 即 FLAG，所以交付前要么拿到事实，要么把这句改成不依赖它的写法。

**不用改的**：FDA 声明；标签原文；问答表里的问句；靠近事实的一句“没有”（No Gelatin）；逗号后面确实多了一个新事实的从句。

## 4. 多疑买家通读

七关过完，换成最挑剔的那类买家（通常是产品上下文里的换牌者或成分党）从第一张读到最后一张，列出他会停下来的地方：哪个数字没有基准、哪个说法没有出处、哪个疑问没人回答。把这些点改掉或写进③待确认。只列问题，不打分——模拟出来的分数没有依据。

## 5. 检查记录

改动写进 JSON：

```json
"sweeps": [
  {"location": "副图 P4-B 标题", "old": "Calcium Was Never\nthe Whole Story.",
   "failed": "去 AI 腔：否定对比", "problem": "先否定一个没人说过的想法",
   "new": "Your Calcium Arrives With\nFive Other Actives."}
]
```

没有改动的批次可以不写。改用户认可过的原句之前先问用户。

## 6. 脚本替你查的和查不了的

| 检查 | 脚本 | 结果 |
|---|---|---|
| 自问自答、冒号揭晓、套话、否定清单 | `scan_copy.py` | FLAG |
| 未解决的 `[NEED:` | `scan_copy.py` | FLAG |
| lockup 两短句没过换牌测试 | `scan_copy.py`（需 `meta.swap_terms`） | FLAG |
| 保守行出现敏感功效词 | `scan_copy.py`（需 `meta.claims.sensitive`） | FLAG |
| 否定对比 | `scan_copy.py` | 每处 WARN；同一读者版本超过一句 FLAG |
| 三连短句、短文案里的破折号、标题没有本品特有词 | `scan_copy.py` | WARN，人工确认 |
| 所以呢、凭什么信、标题是否给图配字幕、疑问是否都答了 | 无 | 只能人工过 |
