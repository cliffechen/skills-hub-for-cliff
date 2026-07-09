"""Offline smoke test for either the Codex or WorkBuddy package layout."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


def main() -> int:
    if sys.version_info < (3, 9):
        print("SMOKE_TEST_FAILED: Python 3.9 or newer is required")
        return 1

    script_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(script_dir))

    with TemporaryDirectory(prefix="supplement-monitor-smoke-") as temp_dir:
        os.environ["SUPPLEMENT_MONITOR_WORKSPACE"] = temp_dir

        import config
        from analyzer import TrendData, assign_tier
        from classifier import SupplementClassifier
        from reporter import generate_report
        from scraper import parse_page
        from validation import load_validated_analysis

        assert config.WORKSPACE_ROOT == Path(temp_dir).resolve()
        assert config.DICT_PATH.exists()
        assert (Path(config.DATA_DIR) / "exclusion_rules.json").exists()
        assert (Path(config.TEMPLATE_DIR) / "report.html").exists()

        dictionary = json.loads(config.DICT_PATH.read_text(encoding="utf-8"))
        assert {"ingredients", "benefits", "brands", "health_markers"} <= set(dictionary)

        sample_html = """
        <div class="table-body-item">
          <a class="table-body-item-words-word"><span>ashwagandha gummies</span></a>
          <div class="table-body-item-rank">
            <span>500</span><span>1,500</span><span>1,000</span>
            <div class="table-body-item-rank-fluctuation"><img src="/up.svg"></div>
          </div>
        </div>
        """
        entries = parse_page(sample_html, "smoke")
        assert len(entries) == 1
        assert entries[0].rank_change == 1000
        assert assign_tier(entries[0].current_rank, entries[0].rank_change, entries[0].previous_rank) == 1

        exchange_dir = Path(config.EXCHANGE_DIR)
        exchange_dir.mkdir(parents=True, exist_ok=True)
        (exchange_dir / "llm_input.json").write_text(
            json.dumps({"keywords": ["ashwagandha gummies"]}, ensure_ascii=False),
            encoding="utf-8",
        )
        (exchange_dir / "llm_output.json").write_text(
            json.dumps(
                {
                    "ashwagandha gummies": {
                        "label": "ingredient",
                        "zh": "南非醉茄软糖",
                    }
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        classifications, translations = SupplementClassifier().read_llm_results()
        assert classifications == {"ashwagandha gummies": "ingredient"}
        assert translations == {"ashwagandha gummies": "南非醉茄软糖"}
        kept, excluded = SupplementClassifier.apply_exclusion_rules(
            {"vitamin c face mask": "ingredient"}
        )
        assert not kept
        assert "vitamin c face mask" in excluded

        analysis_path = exchange_dir / "analysis_output.json"
        valid_analysis = {
            "keyword_analysis": {"ashwagandha gummies": "离线自检分析。"},
            "tracks": [
                {
                    "name": "自检赛道",
                    "icon": "✅",
                    "keywords": ["ashwagandha gummies"],
                    "summary": "仅用于验证模板。",
                }
            ],
            "core_findings": ["离线自检通过。"],
        }
        analysis_path.write_text(
            json.dumps(valid_analysis, ensure_ascii=False),
            encoding="utf-8",
        )
        assert load_validated_analysis(
            str(analysis_path), ["ashwagandha gummies"]
        ) == valid_analysis

        trend = TrendData(
            keyword="ashwagandha gummies",
            tier=1,
            current_rank=500,
            previous_rank=1500,
            rank_change=1000,
            category="ingredient",
            combo_label="smoke",
            zh_name="南非醉茄软糖",
        )
        report_path = Path(
            generate_report(
                results=[trend],
                total_scraped=1000,
                total_supplement=1,
                new_dict_words={"ingredients": [], "benefits": [], "brands": [], "health_markers": []},
                analysis=valid_analysis,
            )
        )
        rendered = report_path.read_text(encoding="utf-8")
        assert "ashwagandha gummies" in rendered
        assert "离线自检通过" in rendered

    print("SMOKE_TEST_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
