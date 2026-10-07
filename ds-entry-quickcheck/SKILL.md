---
name: ds-entry-quickcheck
description: 保健品成分入场速判（跟随者视角）：用卖家精灵数据画出某个成分的逐月入场曲线（新父体数、其中出单数、累计占比）并配同窗口的需求曲线，再用 SIF 拿核心词的点击→购买转化率（CVR），算 5 个指标——近期批次出单率、需求增速÷供给增速、入场加速度、新头部、核心词 CVR——给出"可跟进 / 谨慎 / 不建议 / 数据不足"。三档：lite 单成分速判卡、plus 加剂型/价格带/卖家国别/品牌集中度/周度形态、compare 2–5 个成分并排。用户说"这个成分能不能做/还能不能跟/入场速判/看看 X 的入场曲线/X 现在进场晚不晚/比较这几个成分/这个词转化怎么样好不好推"时使用。只判断入场时机，不算利润和供应链。
---

# 保健品成分入场速判

回答一个问题：**这个成分现在跟进，晚不晚、好不好推？** 输出是结论句加逐点分析，以文字为主。默认美国站、Health & Household 类目。

## 铁律
1. **只用卖家精灵和 SIF 的数据**，全部是估算值，卡片里已写明，转述时不要去掉：
   - 卖家精灵：`product_research`（供给）、`aba_research_trend`（需求）、`keyword_miner`（搜索→购买率，作对照）；plus 档另加 `aba_research_weekly`。
   - SIF：`market_screen_keyword_opportunities`（核心词 CVR、点击率、Top3 转化集中度、CPC）。
2. **转化率只用 SIF 的点击→购买 CVR 做判定**。卖家精灵的搜索→购买率只作对照，两者不能混用（口径不同，排名可能相反）。
3. **需求和供给必须在同一窗口里比**：截止月 M = ABA 月度数据的最新月；M 之后进场的新品单独列出，不参与指标计算。
4. **不给利润、成本、供应链判断。**
5. **合规提示词只提示，不参与判定**（例如糖尿病、处方药名、减肥类宣称）。
6. **跑之前先报备调用次数**：lite 约 3–12 次，plus 约 5–14 次，compare 约为 lite × 成分数（`--max-pages` 调大时，每多 1 页多 1 次）。有缓存时会更少。

## 用法
脚本目录：`${CLAUDE_SKILL_DIR}/scripts/`；Windows 下用 `python` 运行，并设置 `PYTHONUTF8=1`。输出写到**当前工作目录**下的 `entry-check/`，包括 `card.md`（分析要点）、`tables.md`（明细表）和 `data.json`。**默认不生成 HTML。**

```bash
python entry_check.py lite    --query "urolithin" --demand "urolithin a"
python entry_check.py plus    --query "goldenseal,golden seal" --demand "goldenseal"
python entry_check.py compare --items "urolithin|urolithin a; lymphatic|lymphatic drainage drops|3760901:23675621011"
```
- `--query`：标题匹配词，多个用逗号分隔、取并集。成分常有多种写法（goldenseal / golden seal），都列上。
- `--demand`：核心需求词。ABA 和 SIF 都用这个词，取买家最常搜的那个（例如 `urolithin a`，不要用 `urolithin a supplement for men`）。
- compare 的每一项写作 `query|demand|node`，node 可以省略。
- 可选参数：
  - `--node`：默认 3760901（Health & Household）；只看补充剂用 `3760901:23675621011`，可以排除器械类（例如淋巴引流刷），但蛋白粉不在这个节点下。
  - `--max-pages`：默认 10 页（400 个 ASIN）。大品类会被截断，可调到 20。
  - `--tables`：在对话里同时打印明细表（逐月入场、指标明细、剂型、长尾词 CVR）。
  - `--html`：另外生成离线 `report.html`，包含分析要点、入场柱状图、需求折线和折叠的数据附录。**只在用户要求时才加。**
  - 其他：`--min-units 100`、`--today YYYY-MM-DD`、`--no-cache`。

## 我的动作
1. 确认 query、demand、node。拿不准时给 1–2 个候选让用户挑；成分有常见别名就一起放进 query；品类里如果混有器械，就收窄到补充剂节点。
2. 报备调用次数，然后运行脚本。
3. **原样转述脚本输出的分析要点**（结论句 + 逐点分析）。这是给用户看的主体，**不要贴表格，不要罗列原始数字**，也不要把要点改写成数据清单。最多补一句要点里没有的观察。
4. **不要主动生成 HTML。** 转述完用一句话提醒：如果需要带图的报告，可以加 `--html` 生成；如果要看明细，可以加 `--tables`，或者直接看 `entry-check/` 下的 `tables.md`。只有用户明确要时才加 `--html` 重跑（走缓存，不会多消耗调用次数）。
5. 每个要点都要回答"这说明什么"。如果自己补充观察，也照这个格式写：先说事实（最多 1–2 个数字），再说含义。
6. 要点里提示"样本被截断"、带"至少"字样，或者"判断不了"时，建议调大 `--max-pages` 或收窄 `--node` 再跑；在卖品牌太少时，提醒结论可信度有限。

指标定义、阈值和已知局限见 `references/metrics.md`。阈值是起始值，用户要调就改 `entry_check.py` 里的 `TH`。
