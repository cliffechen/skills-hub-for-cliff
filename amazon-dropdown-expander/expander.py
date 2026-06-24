# -*- coding: utf-8 -*-
"""
亚马逊下拉框拓词工具 · 美国站专用 (Amazon US search suggestion expander)
复刻 "亚马逊下拉框拓词.exe" 的核心能力：字母表轰炸 + 去重 + 输出 csv

原理：调用亚马逊美国站公开的搜索联想接口
      https://completion.amazon.com/api/2017/suggestions
对每个种子词，依次查询  "<seed>"、"<seed> a" ... "<seed> z"，
收集每次返回的下拉推荐词，去重后输出。

功能：
  - 多种子词、文件批量输入
  - 一级 / 二级拓词 (--depth，默认 2)
  - 词频统计 + CSV 导出 (供 Excel 直接打开)

提示：美国站对英语、西语种子词都适用——直接输入西语词(如 "pañales para bebé")
      即可拿到西语联想词，无需切换语言或站点。

仅依赖 Python 标准库，无需第三方包。
"""
import argparse
import collections
import csv
import datetime
import os
import json
import random
import re
import string
import sys
import time
import urllib.parse
import urllib.request

# 美国站接口配置: (联想接口域名, 市场ID mid, 语言 lop)
US_HOST = "completion.amazon.com"
US_MID = "ATVPDKIKX0DER"
US_LOP = "en_US"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")


def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def safe_print(msg):
    """跨平台安全打印：Windows 控制台默认 GBK，遇到非 GBK 字符(如西语 ñ/é)不报错。"""
    try:
        print(msg)
    except UnicodeEncodeError:
        enc = (getattr(sys.stdout, "encoding", None) or "utf-8")
        sys.stdout.write(msg.encode(enc, "replace").decode(enc, "replace") + "\n")


def rand_request_id():
    return "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))


def fetch_suggestions(prefix, limit=11, timeout=15):
    """请求一次美国站联想接口，返回推荐词列表 (保持接口顺序)。"""
    base = "https://%s/api/2017/suggestions" % US_HOST
    params = {
        "session-id": "000-0000000-0000000",
        "customer-id": "",
        "request-id": rand_request_id(),
        "page-type": "Search",
        "lop": US_LOP,
        "site-variant": "desktop",
        "client-info": "amazon-search-ui",
        "mid": US_MID,
        "alias": "aps",
        "b2b": "0",
        "fresh": "0",
        "ks": "65",
        "prefix": prefix,
        "event": "onKeyPress",
        "limit": str(limit),
        "fb": "1",
        "suggestion-type": "KEYWORD",
    }
    url = base + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.9",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.loads(r.read().decode("utf-8"))
    out = []
    for s in data.get("suggestions", []):
        v = s.get("value")
        if v:
            out.append(v.strip())
    return out


def build_alphabet(mode):
    if mode == "az":
        return list(string.ascii_lowercase)
    if mode == "az09":
        return list(string.ascii_lowercase) + list(string.digits)
    if mode == "none":
        return []
    raise ValueError("unknown alphabet mode: %s" % mode)


def expand(seeds, alphabet_mode="az", delay=0.3, limit=11,
           retries=2, depth=2, l2_top=20, log_fp=None):
    """
    返回 records 列表，每项: {keyword, count(词频), depth(发现层级), source(来源种子)}
    """
    suffixes = [""] + [" " + c for c in build_alphabet(alphabet_mode)]

    def log(msg):
        safe_print(msg)
        if log_fp:
            log_fp.write(msg + "\n")
            log_fp.flush()

    seen = set()
    records = []                      # 去重后保持发现顺序
    freq = collections.Counter()      # 关键词出现总次数(跨所有查询)
    queried = set()                   # 已查询过的前缀,避免重复请求

    def run_seed_list(seed_list, level):
        total = len(seed_list)
        for si, seed in enumerate(seed_list, 1):
            log("正在采集(美国站)[第%d层] 第 %d / %d 项: %s" % (level, si, total, seed))
            for suf in suffixes:
                query = seed + suf
                if query in queried:
                    continue
                queried.add(query)
                sugg = []
                for attempt in range(retries + 1):
                    try:
                        sugg = fetch_suggestions(query, limit=limit)
                        break
                    except Exception as e:
                        if attempt < retries:
                            time.sleep(delay * (attempt + 1) + 0.5)
                        else:
                            log("%s\t%s\t[请求失败] %s" % (now(), query, e))
                n = len(sugg)
                for i, kw in enumerate(sugg, 1):
                    log("%s \t%s\t (%d / %d) --->\t%s" % (now(), query, i, n, kw))
                    low = kw.lower()
                    freq[low] += 1
                    if low not in seen:
                        seen.add(low)
                        records.append({"keyword": kw, "depth": level, "source": seed})
                time.sleep(delay)
            log("种子词 [%s] 采集完成，当前去重后关键词总数: %d\n" % (seed, len(records)))

    # 第一层
    run_seed_list(seeds, 1)

    # 第二层：取一级结果中词频最高的 l2_top 个(排除原始种子)作为新种子
    if depth >= 2:
        seed_lower = set(s.lower() for s in seeds)
        level1 = [r["keyword"] for r in records
                  if r["depth"] == 1 and r["keyword"].lower() not in seed_lower]
        level1.sort(key=lambda k: -freq[k.lower()])
        l2_seeds = level1[:l2_top]
        log("=" * 60)
        log("进入【二级拓词】：从一级结果中选取词频最高的 %d 个词作为新种子" % len(l2_seeds))
        log("=" * 60 + "\n")
        run_seed_list(l2_seeds, 2)

    for r in records:
        r["count"] = freq[r["keyword"].lower()]
    return records


def read_seeds(args):
    seeds = []
    if args.keywords:
        seeds.extend(args.keywords)
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    seeds.append(line)
    out, s = [], set()
    for k in seeds:
        if k.lower() not in s:
            s.add(k.lower())
            out.append(k)
    return out


def write_csv(path, records):
    """按词频降序导出 CSV (utf-8-sig 便于 Excel 直接打开)。"""
    rows = sorted(records, key=lambda r: (-r["count"], r["keyword"].lower()))
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["排名", "关键词", "词频", "发现层级", "来源种子词", "词数(空格分词)"])
        w.writerow([
            "📖 通俗解释",
            "亚马逊买家在搜索框输入时，系统自动推荐的搜索词——代表真实买家的搜索意图",
            "这个词在所有查询中反复出现的次数。数字越大 = 越多不同的搜索路径都指向这个词，说明它越核心、越热门",
            "1 = 第一轮采集（直接用您给的种子词拓出来的词）；2 = 第二轮（用第一轮里最热的词继续深挖出来的长尾词）",
            "这个词是从哪个种子词拓出来的，方便您追溯每个词的挖掘脉络，看哪些种子词带来的有效词最多",
            "关键词由几个单词组成。词数越多通常代表越精准的长尾词，竞争越小、转化潜力越高",
        ])
        w.writerow([
            "🎯 选词建议",
            "高频词优先埋入 listing 标题、五点和后台 ST；低频但有相关性的长尾词可补充到 PPC 广告和 A+ 文案",
            "词频≥5 的词建议作为核心词重点优化；词频 3-4 的作为辅助词覆盖；词频 1-2 的长尾词可用于 PPC 低竞争投放",
            "层级1的词更主流、搜索量更大，适合标题和五点；层级2的词更细分长尾，适合 PPC 精准投放和差异化卖点",
            "若某个种子词拓出的高频词特别多，说明该方向市场需求大，值得围绕它打造产品线或变体",
            "5-7 词的长尾词适合 PPC 精准匹配和差异化卖点文案；2-3 词的短词适合标题核心词和广泛匹配广告",
        ])
        for rank, r in enumerate(rows, 1):
            w.writerow([rank, r["keyword"], r["count"], r["depth"],
                        r["source"], len(r["keyword"].split())])


def make_slug(seeds, maxlen=40):
    """从种子词生成用于文件名的标识，让用户看文件名就知道是哪个关键词的调研。"""
    first = seeds[0] if seeds else "keywords"
    s = first.strip().lower()
    s = re.sub(r'[\\/:*?"<>|]+', "", s)      # 去掉文件名非法字符
    s = re.sub(r"\s+", "-", s).strip("-")    # 空格转连字符
    s = s[:maxlen].strip("-") or "keywords"
    if len(seeds) > 1:                        # 多种子词时标注数量
        s = "%s-etc%d" % (s, len(seeds))
    return s


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    p = argparse.ArgumentParser(description="亚马逊下拉框拓词工具 · 美国站专用")
    p.add_argument("-k", "--keywords", nargs="*", help="种子关键词(可多个;英语/西语均可)")
    p.add_argument("-i", "--input", help="种子关键词文件(一行一个)")
    p.add_argument("-o", "--outdir", default=".", help="输出目录")
    p.add_argument("--alphabet", default="az", choices=["az", "az09", "none"],
                   help="后缀字母表: az(默认) / az09(含数字) / none(仅原词)")
    p.add_argument("--depth", type=int, default=2, choices=[1, 2],
                   help="拓词层级: 1 / 2(默认,用一级高频词再拓一轮)")
    p.add_argument("--l1-only", dest="depth", action="store_const", const=1,
                   help="只做一级拓词(等价于 --depth 1)")
    p.add_argument("--l2-top", type=int, default=20,
                   help="二级拓词时选取的一级高频种子数量(控制规模), 默认20")
    p.add_argument("--delay", type=float, default=0.3, help="每次请求间隔秒数")
    p.add_argument("--limit", type=int, default=11, help="每次请求最多取多少词")
    p.add_argument("--txt", action="store_true",
                   help="额外输出纯关键词 txt(默认只交付 csv + log)")
    args = p.parse_args()

    seeds = read_seeds(args)
    if not seeds:
        raise SystemExit("请用 -k 或 -i 提供至少一个种子关键词")

    os.makedirs(args.outdir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    slug = make_slug(seeds)
    base = "%s_%s" % (ts, slug)
    log_path = os.path.join(args.outdir, "%s_log.txt" % base)
    csv_path = os.path.join(args.outdir, "%s_out.csv" % base)
    out_path = os.path.join(args.outdir, "%s_out.txt" % base)

    banner = ("*" * 76 + "\n"
              "亚马逊下拉框拓词工具 · 美国站专用\n"
              "根据您提供的关键词，自动采集亚马逊美国站前台下拉框中的推荐词\n"
              "拓词层级: %d\n" % args.depth
              + "*" * 76 + "\n")

    with open(log_path, "w", encoding="utf-8") as log_fp:
        log_fp.write(banner)
        safe_print(banner)
        start = time.time()
        records = expand(seeds,
                         alphabet_mode=args.alphabet,
                         delay=args.delay, limit=args.limit,
                         depth=args.depth, l2_top=args.l2_top,
                         log_fp=log_fp)
        elapsed = time.time() - start
        n1 = sum(1 for r in records if r["depth"] == 1)
        n2 = sum(1 for r in records if r["depth"] == 2)
        summary = ("\n累计耗时: %.1f 秒. 种子词 %d 个, 去重后共 %d 个关键词 "
                   "(一级 %d, 二级新增 %d)." % (elapsed, len(seeds), len(records), n1, n2))
        safe_print(summary)
        log_fp.write(summary + "\n")

    # 主交付物: CSV (含全部关键词 + 词频统计)
    write_csv(csv_path, records)
    outputs = [csv_path, log_path]

    # 可选: 额外输出纯关键词 txt (--txt)
    if args.txt:
        with open(out_path, "w", encoding="utf-8") as f:
            for r in records:
                f.write(r["keyword"] + "\n")
        outputs.append(out_path)

    print("\n结果已写入:")
    for pth in outputs:
        safe_print("  " + pth)


if __name__ == "__main__":
    main()
