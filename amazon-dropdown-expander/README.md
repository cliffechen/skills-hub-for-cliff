# amazon-dropdown-expander

Amazon US 下拉框关键词拓词 skill。给定一个或多个种子关键词后，脚本会调用 Amazon autocomplete suggestion 接口，用 alphabet soup 方法采集联想词，去重并输出带词频的 CSV。

## 适用场景

- 做 Amazon US 关键词调研
- 收集搜索框下拉联想词
- 挖掘长尾词、PPC 精准词或 Listing 备选词
- 为新品关键词库、标题、五点、A+ 或广告结构提供词源

英语和西语种子词都可以使用，站点固定为 amazon.com。

## 运行环境

- Python 3.7+
- 无第三方依赖，只使用 Python 标准库
- 主脚本为同目录下的 `expander.py`

## 快速使用

```bash
python expander.py -k "saffron supplement"
```

多个种子词：

```bash
python expander.py -k "iphone case" "phone charger"
```

从文件读取种子词：

```bash
python expander.py -i seeds.txt
```

只跑一级拓词：

```bash
python expander.py -k "iphone case" --l1-only
```

指定输出目录：

```bash
python expander.py -k "saffron supplement" -o "outputs"
```

## 输出文件

默认输出两个文件，文件名会包含时间戳和种子词：

| 文件 | 用途 |
|---|---|
| `*_out.csv` | 主交付物，包含排名、关键词、词频、发现层级、来源种子词、词数 |
| `*_log.txt` | 采集日志 |
| `*_out.txt` | 可选，使用 `--txt` 时输出纯关键词列表 |

CSV 使用 `utf-8-sig`，Excel 可直接打开。词频越高，通常代表该词在多个查询前缀中反复出现，更适合作为重点词候选。

## 常用参数

| 参数 | 说明 | 默认 |
|---|---|---|
| `-k, --keywords` | 种子关键词，可传多个 | 无 |
| `-i, --input` | 一行一个种子词的输入文件 | 无 |
| `-o, --outdir` | 输出目录 | 当前目录 |
| `--alphabet` | 后缀范围：`az`、`az09`、`none` | `az` |
| `--depth` | 拓词层级：`1` 或 `2` | `2` |
| `--l1-only` | 只跑一级拓词 | 关闭 |
| `--l2-top` | 二级拓词使用的一级高频种子数量 | `20` |
| `--delay` | 请求间隔秒数 | `0.3` |
| `--limit` | 每次请求最多取词数 | `11` |
| `--txt` | 额外输出纯 txt 词表 | 关闭 |

## 目录结构

```text
amazon-dropdown-expander/
|-- README.md
|-- SKILL.md
`-- expander.py
```

## 注意事项

- 本 skill 仅面向 Amazon US，不支持其他站点。
- 下拉联想词会随时间、季节和新品热度变化，同一种子词不同时间跑出差异是正常现象。
- 默认二级拓词请求量较大，种子词多时建议调大 `--delay`。
- 本工具涉及公开接口抓取，使用前请自行评估是否符合平台条款和内部使用规范。
