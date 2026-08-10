# -*- coding: utf-8 -*-
"""SerpApi PAA 旁路：对种子词调 Google Search API，提取 related_questions + related_searches。
Key 只从环境变量 SERPAPI_KEY 读取，不写入任何文件。
用法: SERPAPI_KEY=<key> python serpapi_paa.py <输出json路径> [种子词txt(一行一词)] [最大调用次数]"""
import json, os, sys, io, time, urllib.parse, urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

KEY = os.environ.get("SERPAPI_KEY", "")
if not KEY:
    sys.exit("SERPAPI_KEY env var missing")
if len(sys.argv) < 2:
    sys.exit("usage: SERPAPI_KEY=<key> python serpapi_paa.py <out.json> [seeds.txt] [max_calls]")
OUT = sys.argv[1]
MAX_CALLS = int(sys.argv[3]) if len(sys.argv) > 3 else 30

if len(sys.argv) > 2:
    with open(sys.argv[2], encoding="utf-8") as f:
        SEEDS = [ln.strip() for ln in f if ln.strip()]
else:
    SEEDS = []
if not SEEDS:
    sys.exit("no seeds: provide seeds txt (one keyword per line), 建议用 P0+P1 头部词 10~20 个")
SEEDS = SEEDS[:MAX_CALLS]

out = {"paa": [], "related": []}
for q in SEEDS:
    params = {"engine": "google", "q": q, "gl": "us", "hl": "en", "api_key": KEY}
    url = "https://serpapi.com/search.json?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            data = json.loads(r.read().decode("utf-8"))
    except Exception as e:
        print(f"[{q}] ERROR {e}")
        continue
    paa = [x.get("question", "") for x in data.get("related_questions", []) if x.get("question")]
    rel = [x.get("query", "") for x in data.get("related_searches", []) if x.get("query")]
    print(f"[{q}] PAA={len(paa)} related={len(rel)}")
    out["paa"].extend({"seed": q, "question": x} for x in paa)
    out["related"].extend({"seed": q, "query": x} for x in rel)
    time.sleep(0.5)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(f"saved -> {OUT} | calls={len(SEEDS)} PAA={len(out['paa'])} related={len(out['related'])}")
