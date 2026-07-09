"""主流程编排 - 亚马逊保健品爆品关键词监测系统。

3 步流程：
  python main.py step1   # 抓取 + 本地匹配 → llm_input.json（等 Agent 分类）
  python main.py step2   # 合并 + Tier 分层 + Sorftime 异步查询 → analysis_input.json
  python main.py step3   # 校验 Agent 分析文字 → 生成最终 HTML 报告
"""
import os
import sys
import json
import logging
import warnings
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

import config
from scraper import scrape_all_combos, entries_to_dicts
from classifier import SupplementClassifier
from analyzer import analyze_keywords_basic, query_sorftime_batch, apply_sorftime_results
from reporter import generate_report
from db import init_db, save_results
from validation import load_validated_analysis

os.makedirs(config.REPORT_DIR, exist_ok=True)
os.makedirs(config.DATA_DIR, exist_ok=True)
os.makedirs(config.EXCHANGE_DIR, exist_ok=True)

_now = datetime.now()
_week_str = f"{_now.year}-W{_now.isocalendar()[1]:02d}"
_log_file = os.path.join(config.REPORT_DIR, f"run_{_week_str}.log")
# step1 开始新一轮周报时覆盖；step2/step3 追加，保留完整三步日志。
_requested_step = sys.argv[1] if len(sys.argv) > 1 else "step1"
_log_mode = "w" if _requested_step == "step1" else "a"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(_log_file, encoding="utf-8", mode=_log_mode),
    ],
)
# httpx 的 INFO 日志会包含带查询参数的 URL；禁止把 API Key 写入日志。
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger("main")

SCRAPED_PATH = os.path.join(config.EXCHANGE_DIR, "scraped.json")
LOCAL_MATCH_PATH = os.path.join(config.EXCHANGE_DIR, "local_match.json")
TIERED_PATH = os.path.join(config.EXCHANGE_DIR, "tiered.json")


def step1_scrape_and_local_match():
    """第 1 步：抓取 + 本地词典匹配 → 输出待 LLM 分类的关键词"""
    logger.info("=" * 60)
    logger.info("🧬 第 1 步: 抓取 + 本地词典匹配")
    logger.info("=" * 60)

    if not config.check_ready():
        logger.warning("Sorftime key 未配置，step2 的深度分析将跳过")

    init_db()

    logger.info("📡 抓取 AMZ123 ABA 热搜词...")
    entries = scrape_all_combos()
    entry_dicts = entries_to_dicts(entries)
    total_scraped = len(entry_dicts)
    logger.info(f"抓取完成: {total_scraped} 个去重关键词")
    if total_scraped < config.MIN_SCRAPED_KEYWORDS:
        logger.error(
            "抓取量异常: %s，低于安全阈值 %s。可能是网页结构变化或网络失败；"
            "为避免覆盖有效数据，本轮停止。",
            total_scraped,
            config.MIN_SCRAPED_KEYWORDS,
        )
        return False

    with open(SCRAPED_PATH, "w", encoding="utf-8") as f:
        json.dump(entry_dicts, f, ensure_ascii=False, indent=2)

    logger.info("🔬 本地词典匹配...")
    classifier = SupplementClassifier()
    all_keywords = [e["keyword"] for e in entry_dicts]
    local_results, llm_candidates = classifier.classify_all(all_keywords)

    with open(LOCAL_MATCH_PATH, "w", encoding="utf-8") as f:
        json.dump({"local_results": local_results, "total_scraped": total_scraped}, f, ensure_ascii=False, indent=2)

    if llm_candidates:
        classifier.request_llm_classification(llm_candidates)
        logger.info(f"✅ 第 1 步完成。{len(llm_candidates)} 个关键词待 agent 分类+翻译")
        logger.info(f'   返回格式: {{"keyword": {{"label": "ingredient", "zh": "中文翻译"}}}}')
    else:
        llm_input_path = os.path.join(config.EXCHANGE_DIR, "llm_input.json")
        if os.path.exists(llm_input_path):
            os.remove(llm_input_path)
        with open(os.path.join(config.EXCHANGE_DIR, "llm_output.json"), "w", encoding="utf-8") as f:
            json.dump({}, f)
        logger.info("✅ 第 1 步完成。所有关键词已由本地词典匹配")
    return True


def step2_analyze_and_report():
    """第 2 步：合并分类 → Tier 分层 → Sorftime 异步查询 → 输出 analysis_input.json"""
    logger.info("=" * 60)
    logger.info("📊 第 2 步: 分类合并 + 分层 + Sorftime 查询")
    logger.info("=" * 60)

    with open(SCRAPED_PATH, "r", encoding="utf-8") as f:
        entry_dicts = json.load(f)
    with open(LOCAL_MATCH_PATH, "r", encoding="utf-8") as f:
        local_data = json.load(f)

    classifier = SupplementClassifier()
    llm_classifications, llm_translations = classifier.read_llm_results()
    classifications = classifier.merge_llm_results(local_data["local_results"], llm_classifications)

    # 应用排除规则
    classifications, excluded_keywords = classifier.apply_exclusion_rules(classifications)
    total_supplement = len(classifications)
    logger.info(f"过滤完成: {total_supplement}/{local_data['total_scraped']} 个保健品相关词"
                f" (排除 {len(excluded_keywords)} 个)")

    results = analyze_keywords_basic(entry_dicts, classifications, llm_translations)

    tier1_kws = [r.keyword for r in results if r.tier == 1]
    tier2_kws = [r.keyword for r in results if r.tier == 2]
    sorftime_stats = {"total_calls": 0, "enriched": 0, "tier1_keywords": 0, "tier2_keywords": 0}
    if config.SORFTIME_API_KEY and (tier1_kws or tier2_kws):
        sorftime_data, sorftime_stats = query_sorftime_batch(tier1_kws, tier2_kws)
        results = apply_sorftime_results(results, sorftime_data)
    elif not config.SORFTIME_API_KEY:
        logger.warning("Sorftime key 未配置，跳过深度分析")

    # 存储
    logger.info("💾 存储到 SQLite...")
    save_results(results)

    # 保存分层结果供 step3 使用
    from dataclasses import asdict
    with open(TIERED_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "results": [asdict(r) for r in results],
            "total_scraped": local_data["total_scraped"],
            "total_supplement": total_supplement,
            "new_words": classifier.new_words,
            "excluded_keywords": excluded_keywords,
            "sorftime_stats": sorftime_stats,
        }, f, ensure_ascii=False, indent=2)

    # 输出 analysis_input.json 供 agent 写分析摘要
    analysis_input = os.path.join(config.EXCHANGE_DIR, "analysis_input.json")
    analysis_output = os.path.join(config.EXCHANGE_DIR, "analysis_output.json")
    if os.path.exists(analysis_output):
        os.remove(analysis_output)

    tier1_data = []
    for r in results:
        if r.tier == 1:
            tier1_data.append(asdict(r))

    with open(analysis_input, "w", encoding="utf-8") as f:
        json.dump({
            "task": "write_analysis",
            "prompt": (
                "为以下每个 Tier 1 关键词写一段中文分析摘要（2-3句话），包含：\n"
                "1. 搜索量/排名变化趋势解读\n"
                "2. CPC和竞争度判断\n"
                "3. 机会/风险评估\n\n"
                "同时，将所有 Tier 1 关键词按赛道/主题聚类（如'神经病变'、'亚甲蓝'、'NMN/NAD+'等），\n"
                "每个赛道写一个标题和简短描述。\n\n"
                "返回 JSON 格式：\n"
                '{\n'
                '  "keyword_analysis": {"keyword": "分析摘要文字", ...},\n'
                '  "tracks": [{"name": "赛道名", "icon": "emoji", "keywords": ["kw1","kw2"], "summary": "描述"}, ...],\n'
                '  "core_findings": ["发现1", "发现2", ...]\n'
                '}'
            ),
            "tier1_keywords": tier1_data,
        }, f, ensure_ascii=False, indent=2)

    t1 = len(tier1_kws)
    t2 = len(tier2_kws)
    t3 = sum(1 for r in results if r.tier == 3)
    logger.info(f"✅ 第 2 步完成。Tier1={t1} | Tier2={t2} | Tier3={t3}")
    logger.info(f"   请 agent 读取 reports/.exchange/analysis_input.json 写分析摘要")
    logger.info(f"   写入 reports/.exchange/analysis_output.json 后运行 step3")
    return True


def step3_render_report():
    """第 3 步：读取 agent 分析文字 → 生成最终 HTML 报告"""
    logger.info("=" * 60)
    logger.info("📝 第 3 步: 生成最终报告")
    logger.info("=" * 60)

    with open(TIERED_PATH, "r", encoding="utf-8") as f:
        tiered_data = json.load(f)

    # 读取并校验 Agent 分析结果
    analysis_path = os.path.join(config.EXCHANGE_DIR, "analysis_output.json")
    from analyzer import TrendData
    results = [TrendData(**r) for r in tiered_data["results"]]
    tier1_keywords = [r.keyword for r in results if r.tier == 1]
    analysis = load_validated_analysis(analysis_path, tier1_keywords)
    logger.info("已读取并校验分析摘要")

    report_path = generate_report(
        results=results,
        total_scraped=tiered_data["total_scraped"],
        total_supplement=tiered_data["total_supplement"],
        new_dict_words=tiered_data["new_words"],
        analysis=analysis,
        excluded_keywords=tiered_data.get("excluded_keywords", {}),
        sorftime_stats=tiered_data.get("sorftime_stats", {}),
    )

    logger.info("=" * 60)
    logger.info(f"✅ 完成! 报告: {report_path}")
    t1 = sum(1 for r in results if r.tier == 1)
    t2 = sum(1 for r in results if r.tier == 2)
    t3 = sum(1 for r in results if r.tier == 3)
    logger.info(f"   Tier1={t1} | Tier2={t2} | Tier3={t3}")
    logger.info("=" * 60)
    return report_path


if __name__ == "__main__":
    step = _requested_step
    if step == "step1":
        success = step1_scrape_and_local_match()
    elif step == "step2":
        success = step2_analyze_and_report()
    elif step == "step3":
        success = bool(step3_render_report())
    else:
        print("用法: python main.py [step1|step2|step3]")
        sys.exit(1)
    sys.exit(0 if success else 1)
