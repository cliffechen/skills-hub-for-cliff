"""三层漏斗过滤：本地词典匹配 + Agent 分类（含中文翻译）+ 自学习回写。

LLM 分类由当前 Agent 完成：
1. 将待分类关键词写入 exchange/llm_input.json
2. Agent 读取后分类+翻译，写入 exchange/llm_output.json
3. Python 读取结果继续流程
"""
import json
import logging
import os
import re
import time
from typing import Optional

import config

logger = logging.getLogger(__name__)


class SupplementClassifier:
    """保健品关键词分类器"""

    CATEGORIES = {"ingredient", "benefit", "brand", "condition", "form", "unrelated"}

    def __init__(self):
        self.dict_data = self._load_dict()
        self._build_patterns()
        self.new_words: dict[str, list[str]] = {
            "ingredients": [], "benefits": [], "brands": [], "health_markers": []
        }

    def _load_dict(self) -> dict:
        with open(config.DICT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def _build_patterns(self):
        self.patterns = {}
        for category, words in self.dict_data.items():
            sorted_words = sorted(words, key=len, reverse=True)
            escaped = [re.escape(w) for w in sorted_words]
            if escaped:
                self.patterns[category] = re.compile(
                    r'\b(' + '|'.join(escaped) + r')\b', re.IGNORECASE
                )

    def match_local(self, keyword: str) -> Optional[str]:
        kw = keyword.lower().strip()
        if self.patterns.get("ingredients") and self.patterns["ingredients"].search(kw):
            return "ingredient"
        if self.patterns.get("benefits") and self.patterns["benefits"].search(kw):
            return "benefit"
        if self.patterns.get("brands") and self.patterns["brands"].search(kw):
            return "brand"
        return None

    def has_health_marker(self, keyword: str) -> bool:
        if self.patterns.get("health_markers"):
            return bool(self.patterns["health_markers"].search(keyword.lower()))
        return False

    def request_llm_classification(self, keywords: list[str]) -> str:
        """将待分类关键词写入交换文件，返回输入文件路径。
        Agent 需同时返回分类标签和中文语义翻译。"""
        os.makedirs(config.EXCHANGE_DIR, exist_ok=True)
        input_path = os.path.join(config.EXCHANGE_DIR, "llm_input.json")
        output_path = os.path.join(config.EXCHANGE_DIR, "llm_output.json")
        if os.path.exists(output_path):
            os.remove(output_path)
        with open(input_path, "w", encoding="utf-8") as f:
            json.dump({
                "task": "supplement_classification",
                "prompt": (
                    "判断以下每个关键词是否与亚马逊保健品（Dietary Supplements）相关并分类，同时提供中文语义翻译。\n"
                    "分类标签：ingredient(成分), benefit(功效), brand(品牌), "
                    "condition(症状), form(剂型), unrelated(无关)\n"
                    '返回 JSON: {"keyword": {"label": "ingredient", "zh": "中文翻译"}, ...}\n'
                    "unrelated 的词也需要翻译。"
                ),
                "keywords": keywords,
            }, f, ensure_ascii=False, indent=2)
        logger.info(f"已写入 {len(keywords)} 个待分类关键词到 {input_path}")
        return input_path

    def read_llm_results(self) -> tuple[dict[str, str], dict[str, str]]:
        """严格校验 Agent 输出，返回 (分类 dict, 翻译 dict)。"""
        output_path = os.path.join(config.EXCHANGE_DIR, "llm_output.json")
        if not os.path.exists(output_path):
            raise FileNotFoundError(
                f"未找到分类结果文件: {output_path}。请先根据 llm_input.json 生成该文件。"
            )
        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("llm_output.json 顶层必须是 JSON 对象")

        input_path = os.path.join(config.EXCHANGE_DIR, "llm_input.json")
        expected_keywords: list[str] = []
        if os.path.exists(input_path):
            with open(input_path, "r", encoding="utf-8") as f:
                input_data = json.load(f)
            if not isinstance(input_data, dict) or not isinstance(input_data.get("keywords"), list):
                raise ValueError("llm_input.json 缺少 keywords 数组")
            expected_keywords = input_data["keywords"]

        expected = set(expected_keywords)
        actual = set(data)
        if expected != actual:
            missing = sorted(expected - actual)
            extra = sorted(actual - expected)
            raise ValueError(f"llm_output.json 关键词不匹配；缺少={missing}；多余={extra}")

        classifications = {}
        translations = {}
        for kw, val in data.items():
            if not isinstance(val, dict):
                raise ValueError(f"{kw} 的值必须是包含 label 和 zh 的对象")
            label = val.get("label")
            translation = val.get("zh")
            if label not in self.CATEGORIES:
                raise ValueError(f"{kw} 使用了无效分类标签: {label}")
            if not isinstance(translation, str) or not translation.strip():
                raise ValueError(f"{kw} 缺少非空中文翻译 zh")
            classifications[kw] = label
            translations[kw] = translation.strip()
        return classifications, translations

    def wait_for_llm_results(self, timeout: int = 300) -> tuple[dict[str, str], dict[str, str]]:
        """等待 agent 写入分类结果（轮询模式）"""
        output_path = os.path.join(config.EXCHANGE_DIR, "llm_output.json")
        start = time.time()
        while time.time() - start < timeout:
            if os.path.exists(output_path):
                time.sleep(1)
                return self.read_llm_results()
            time.sleep(2)
        logger.error(f"等待分类结果超时 ({timeout}s)")
        return {}, {}

    def writeback_new_words(self, classified: dict[str, str]):
        category_map = {
            "ingredient": "ingredients",
            "benefit": "benefits",
            "brand": "brands",
            "condition": "benefits",
            "form": "health_markers",
        }
        for keyword, label in classified.items():
            if label == "unrelated":
                continue
            dict_key = category_map.get(label)
            if dict_key and keyword.lower() not in [w.lower() for w in self.dict_data.get(dict_key, [])]:
                self.dict_data[dict_key].append(keyword.lower())
                self.new_words[dict_key].append(keyword.lower())
        with open(config.DICT_PATH, "w", encoding="utf-8") as f:
            json.dump(self.dict_data, f, ensure_ascii=False, indent=2)
        total_new = sum(len(v) for v in self.new_words.values())
        if total_new:
            logger.info(f"回写 {total_new} 个新词到本地词典")

    def classify_all(self, keywords: list[str]) -> tuple[dict[str, str], list[str]]:
        """第一阶段：本地词典匹配，返回 (已分类结果, 待LLM分类列表)"""
        results = {}
        llm_candidates = []
        for kw in keywords:
            label = self.match_local(kw)
            if label:
                results[kw] = label
            elif self.has_health_marker(kw):
                llm_candidates.append(kw)
        logger.info(f"本地词典命中 {len(results)} 个，可疑词 {len(llm_candidates)} 个待 LLM 分类")
        return results, llm_candidates

    def merge_llm_results(self, local_results: dict[str, str],
                          llm_classifications: dict[str, str]) -> dict[str, str]:
        """合并本地匹配和 LLM 分类结果"""
        merged = dict(local_results)
        for kw, label in llm_classifications.items():
            if label != "unrelated":
                merged[kw] = label
        self.writeback_new_words(llm_classifications)
        logger.info(f"最终识别 {len(merged)} 个保健品相关关键词")
        return merged


    @staticmethod
    def load_exclusion_rules() -> dict:
        """加载排除规则（独立配置，不侵入核心）"""
        rules_path = os.path.join(config.DATA_DIR, "exclusion_rules.json")
        if not os.path.exists(rules_path):
            return {}
        try:
            with open(rules_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    @staticmethod
    def apply_exclusion_rules(classifications: dict[str, str]) -> tuple[dict[str, str], dict[str, str]]:
        """应用排除规则，返回 (保留的分类, 被排除的 {kw: reason})"""
        rules = SupplementClassifier.load_exclusion_rules()
        if not rules:
            return classifications, {}

        excluded = {}
        kept = {}

        # 编译正则
        exclude_patterns = [re.compile(p, re.IGNORECASE) for p in rules.get("exclude_patterns", [])]
        usage_patterns = [re.compile(p, re.IGNORECASE) for p in rules.get("exclude_usage_patterns", [])]
        exact_excludes = set(kw.lower() for kw in rules.get("exclude_keywords", []))

        for kw, label in classifications.items():
            kw_lower = kw.lower()
            # 精确排除
            if kw_lower in exact_excludes:
                excluded[kw] = "精确排除（已知非人用保健品）"
                continue
            # 正则排除（宠物类等）
            hit = False
            for pat in exclude_patterns:
                if pat.search(kw_lower):
                    excluded[kw] = "正则排除（疑似非人用保健品）"
                    hit = True
                    break
            if hit:
                continue
            # 用途排除（外用、口腔护理等非膳食补充剂场景）
            for pat in usage_patterns:
                if pat.search(kw_lower):
                    excluded[kw] = "用途排除（疑似非口服膳食补充剂）"
                    hit = True
                    break
            if not hit:
                kept[kw] = label

        if excluded:
            logger.info(f"排除规则过滤: {len(excluded)} 个词被排除")
        return kept, excluded
