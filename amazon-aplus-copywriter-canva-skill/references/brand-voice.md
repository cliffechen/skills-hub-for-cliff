# 品牌调性文案：洞察式品牌宣言（insight-led manifesto copy）

## 什么时候用（满足任一条即触发）

1. 用户在对话里要求写"品牌调性 / 腔调 / 品牌感 / 有态度的话"。
2. 构图文件名含有这类语义：品牌调性、品牌标语、品牌宣言、品牌态度、品牌收尾、腔调、slogan、tagline、manifesto、brand voice。
3. 构图里的占位文字本身在要求写调性，例如"这里写一些有腔调的话"。

触发后，在第 3 步把这些文字位记为品牌调性位，plan 的任务卡里标出来；在 JSON 里给这些行（包括该图的 ALT 行）加 `"voice": "brand"`，scan_copy 会对它们做专项检查。Logo 旁边已经定好的品牌 slogan 原样保留，不算品牌调性位。

品牌有档案（`references/brand-profiles/{品牌}.md`）时，用档案里的语气、词汇和签名句式写；下面的两拍结构照常适用。

## 风格是什么

标杆句（用户提供）：

- *Your days feel different. The support you take should be too.\**
- *Start where aging actually starts.*

这种风格是**两拍**：

1. **第一拍说出读者已经有的感受或常识**，比如 "Your days feel different."，或者 "aging starts somewhere"。
2. **第二拍把这个感受翻转成品牌立场**，比如 "should be too"，或者 "actually starts"。

它的特点：

- 用第二人称，口语化的陈述句，句子短。
- 前后两拍用同一个词或同一个结构呼应（different → too；starts → starts）。
- 卖的是态度和看问题的角度，不讲参数。
- 句末留白，让读者自己补全意思。

## 句型模板（原创示例，按产品替换）

| 句型 | 示例 |
|---|---|
| Your X is ___. Your Y should be too. | Your days feel different. Your support should too.* |
| Start where X actually starts. | Start where energy actually starts.* |
| Not more X. Better Y. | Not more steps. Better ones. |
| Built for the ___ you don't see. | Built for the work your cells do quietly.* |
| You ___. We ___. | You show up every day. So should your support. |
| The ___ is invisible. The difference isn't. | The work is cellular. The days are yours. |

## 写法

- 两拍，每拍大约 8 个词以内；整句不超过 16 个词。
- 用陈述句，不用感叹号，不用反问连发。
- 构图有标题位和副句位时，分工如下：标题放洞察，副句放翻转；或者标题放整句，副句给一个画面感短语。两处不能说同一件事。
- 用词落在 listing 的功效方向上，或者落在用户确认过的情绪主题上。
- **品牌调性图的 alt 文本**：写品牌名、产品名和情绪主张，不写规格。例如：`ZAB Urolithin A, cellular support for the days you're building`。

## 禁止

- 数字、剂量、粒数、份数、天数。
- 认证或检测词：cGMP、lab tested、third-party、COA、vegan、non-GMO。
- 复述同一批前面图片已经说过的事实或短语。这些信息由前面的图负责，品牌调性位只负责态度。
- 参数罗列，比如 "Clear dose. Lab tested. No guesswork."。

## 合规

- 补剂合规包（`compliance-supplements.md`）照常适用。
- **aging 可以作为情绪主题**（用户 2026-10-02 决定），例如 "Start where aging actually starts."。仍然禁止 reverse、anti-aging、turn back the clock 等逆转或抗衰说法。
- 句子只要暗示身体功能（energy、cells、aging、recovery 等），就加 `*`，并且同一张图要有 FDA 声明行。

## 自检

1. 遮住品牌名再读，这句话仍然要成立，而且有态度。
2. 把这句话删掉后，读者不会损失任何参数信息。如果会损失，说明写错了，应该改回参数位。
3. 和同一批其他行没有连续 4 个词以上的重复（scan 会检查）。
