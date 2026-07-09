"""SQLite 数据查看工具

用法：
  python view_data.py              # 最新一周概览
  python view_data.py --tier 1     # 只看 Tier 1
  python view_data.py --keyword kava  # 搜索关键词
  python view_data.py --weeks      # 所有周统计
  python view_data.py --export     # 导出 CSV
"""
import sqlite3
import csv
import sys
import os
from pathlib import Path


WORKSPACE_ROOT = Path(
    os.environ.get("SUPPLEMENT_MONITOR_WORKSPACE", "") or Path.cwd()
).expanduser().resolve()
DB_PATH = WORKSPACE_ROOT / ".supplement-keyword-monitor" / "data" / "history.db"
REPORT_DIR = WORKSPACE_ROOT / "reports"


def get_conn():
    if not os.path.exists(DB_PATH):
        print(f"❌ 数据库文件不存在: {DB_PATH}")
        print("   请先运行 main.py 生成数据")
        sys.exit(1)
    return sqlite3.connect(DB_PATH)


def show_overview():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT week_label FROM weekly_snapshots ORDER BY week_label DESC LIMIT 1")
    row = cur.fetchone()
    if not row:
        print("📭 数据库为空，请先运行 main.py")
        return
    week = row[0]
    print(f"\n📊 最新数据: {week}")
    print("=" * 60)
    cur.execute("""
        SELECT tier, COUNT(*), MIN(current_rank), MAX(rank_change)
        FROM weekly_snapshots WHERE week_label = ? GROUP BY tier ORDER BY tier
    """, (week,))
    tier_labels = {1: "🔴 Tier 1 大潜力", 2: "🟡 Tier 2 中潜力", 3: "🟢 Tier 3 长尾"}
    total = 0
    for tier, count, best_rank, max_change in cur.fetchall():
        label = tier_labels.get(tier, f"Tier {tier}")
        print(f"  {label}: {count} 个词 | 最佳排名 {best_rank} | 最大涨幅 {max_change}")
        total += count
    print(f"  总计: {total} 个保健品相关词")
    print(f"\n🔥 涨幅 Top 10:")
    print(f"  {'关键词':<35s} {'排名':>6s} {'涨幅':>8s} {'Tier':>5s} {'分类':<12s}")
    print("  " + "-" * 70)
    cur.execute("""
        SELECT keyword, current_rank, rank_change, tier, category
        FROM weekly_snapshots WHERE week_label = ? ORDER BY rank_change DESC LIMIT 10
    """, (week,))
    for kw, rank, change, tier, cat in cur.fetchall():
        print(f"  {kw:<35s} {rank:>6d} {'+' + str(change):>8s} {'T' + str(tier):>5s} {cat or '':>12s}")
    conn.close()


def show_tier(tier_num):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT week_label FROM weekly_snapshots ORDER BY week_label DESC LIMIT 1")
    week = cur.fetchone()[0]
    tier_labels = {1: "🔴 Tier 1 大潜力", 2: "🟡 Tier 2 中潜力", 3: "🟢 Tier 3 长尾"}
    print(f"\n{tier_labels.get(tier_num, f'Tier {tier_num}')} - {week}")
    print("=" * 80)
    print(f"  {'关键词':<40s} {'本周排名':>8s} {'上周排名':>8s} {'涨幅':>8s} {'分类':<10s} {'爆发类型':<12s}")
    print("  " + "-" * 90)
    cur.execute("""
        SELECT keyword, current_rank, previous_rank, rank_change, category, burst_type
        FROM weekly_snapshots WHERE week_label = ? AND tier = ? ORDER BY rank_change DESC
    """, (week, tier_num))
    for kw, rank, prev, change, cat, burst in cur.fetchall():
        prev_str = str(prev) if prev else "NEW"
        print(f"  {kw:<40s} {rank:>8d} {prev_str:>8s} {'+' + str(change):>8s} {cat or '':>10s} {burst or '':>12s}")
    conn.close()


def search_keyword(query):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT week_label, keyword, current_rank, rank_change, tier, category, burst_type
        FROM weekly_snapshots WHERE keyword LIKE ? ORDER BY week_label DESC, current_rank ASC
    """, (f"%{query}%",))
    results = cur.fetchall()
    if not results:
        print(f"❌ 未找到包含 '{query}' 的关键词")
        return
    print(f"\n🔍 搜索 '{query}' - 找到 {len(results)} 条记录")
    print(f"  {'周':<12s} {'关键词':<35s} {'排名':>6s} {'涨幅':>8s} {'Tier':>5s} {'分类':<10s}")
    print("  " + "-" * 80)
    for week, kw, rank, change, tier, cat, burst in results:
        print(f"  {week:<12s} {kw:<35s} {rank:>6d} {'+' + str(change):>8s} {'T' + str(tier):>5s} {cat or '':>10s}")
    conn.close()


def show_weeks():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT week_label, COUNT(*),
               SUM(CASE WHEN tier=1 THEN 1 ELSE 0 END),
               SUM(CASE WHEN tier=2 THEN 1 ELSE 0 END),
               SUM(CASE WHEN tier=3 THEN 1 ELSE 0 END),
               MIN(captured_at)
        FROM weekly_snapshots GROUP BY week_label ORDER BY week_label DESC
    """)
    print(f"\n📅 历史数据周报")
    print(f"  {'周':<12s} {'总数':>6s} {'T1':>5s} {'T2':>5s} {'T3':>5s} {'采集时间':<20s}")
    print("  " + "-" * 60)
    for week, total, t1, t2, t3, captured in cur.fetchall():
        print(f"  {week:<12s} {total:>6d} {t1:>5d} {t2:>5d} {t3:>5d} {captured[:16]:<20s}")
    conn.close()


def export_csv():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT week_label FROM weekly_snapshots ORDER BY week_label DESC LIMIT 1")
    week = cur.fetchone()[0]
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    filename = REPORT_DIR / f"export_{week}.csv"
    cur.execute("""
        SELECT keyword, current_rank, previous_rank, rank_change, tier, category,
               burst_type, combo_label, volume_mom_change, historical_peak_rank
        FROM weekly_snapshots WHERE week_label = ? ORDER BY tier, rank_change DESC
    """, (week,))
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["关键词", "本周排名", "上周排名", "涨幅", "Tier", "分类",
                         "爆发类型", "来源组合", "月环比", "历史峰值排名"])
        writer.writerows(cur.fetchall())
    print(f"✅ 已导出到 {filename} ({week})")
    conn.close()


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--weeks" in args:
        show_weeks()
    elif "--tier" in args:
        idx = args.index("--tier")
        tier = int(args[idx + 1]) if idx + 1 < len(args) else 1
        show_tier(tier)
    elif "--keyword" in args:
        idx = args.index("--keyword")
        query = args[idx + 1] if idx + 1 < len(args) else ""
        search_keyword(query)
    elif "--export" in args:
        export_csv()
    else:
        show_overview()
