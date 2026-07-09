"""SQLite 历史数据存储"""
import sqlite3
import json
import logging
from datetime import datetime

import config
from analyzer import TrendData

logger = logging.getLogger(__name__)


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(config.DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS weekly_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week_label TEXT NOT NULL,
            captured_at TEXT NOT NULL,
            keyword TEXT NOT NULL,
            zh_name TEXT DEFAULT '',
            current_rank INTEGER,
            previous_rank INTEGER,
            rank_change INTEGER,
            tier INTEGER,
            category TEXT,
            burst_type TEXT,
            combo_label TEXT,
            monthly_volumes TEXT,
            cpc_history TEXT,
            extended_keywords TEXT,
            volume_mom_change REAL,
            historical_peak_rank INTEGER
        );
        CREATE INDEX IF NOT EXISTS idx_week ON weekly_snapshots(week_label);
        CREATE INDEX IF NOT EXISTS idx_keyword ON weekly_snapshots(keyword);
    """)
    # 兼容旧表：如果 zh_name 列不存在则添加
    try:
        conn.execute("SELECT zh_name FROM weekly_snapshots LIMIT 1")
    except sqlite3.OperationalError:
        conn.execute("ALTER TABLE weekly_snapshots ADD COLUMN zh_name TEXT DEFAULT ''")
    conn.close()


def save_results(results: list[TrendData]):
    now = datetime.now()
    week_label = f"{now.year}-W{now.isocalendar()[1]:02d}"
    conn = get_conn()
    # 同周覆盖：先删除本周已有快照，避免同周多次运行产生重复行
    # （与报告/日志的"同周覆盖"约定保持一致）
    deleted = conn.execute("DELETE FROM weekly_snapshots WHERE week_label = ?", (week_label,)).rowcount
    if deleted:
        logger.info(f"清除本周已有快照 {deleted} 条（同周覆盖）")
    rows = []
    for td in results:
        rows.append((
            week_label, now.isoformat(), td.keyword, td.zh_name or "",
            td.current_rank, td.previous_rank, td.rank_change, td.tier,
            td.category, td.burst_type, td.combo_label,
            json.dumps(td.monthly_volumes, ensure_ascii=False),
            json.dumps(td.cpc_history, ensure_ascii=False),
            json.dumps(td.extended_keywords, ensure_ascii=False),
            td.volume_mom_change, td.historical_peak_rank,
        ))
    conn.executemany("""
        INSERT INTO weekly_snapshots
        (week_label, captured_at, keyword, zh_name, current_rank, previous_rank,
         rank_change, tier, category, burst_type, combo_label, monthly_volumes,
         cpc_history, extended_keywords, volume_mom_change, historical_peak_rank)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)
    conn.commit()
    conn.close()
    logger.info(f"已保存 {len(rows)} 条记录到数据库 (周: {week_label})")
