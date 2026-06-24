#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
保健品（膳食补充剂）标题属性解析脚本

从 Top100 产品的标题和五点描述中提取保健品特有的属性维度：
- 成分大类
- 剂型
- 剂量标注（有/无）
- 功效方向
- 目标人群
- 包装规格
- 认证标签
- 配方类型

输入：top100_raw.json（category_report 解析后的产品列表）
输出：top100_parsed.json（每条产品增加属性列 + 置信度）
      uncertain_products.json（需要 product_detail 补充验证的产品列表）

用法：
  python parse_supplement_title.py --input top100_raw.json --output-dir ./
  python parse_supplement_title.py --input top100_raw.json --output-dir ./ --details details.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


# ---------------------------------------------------------------------------
# 成分大类关键词映射
# ---------------------------------------------------------------------------

INGREDIENT_CATEGORIES: dict[str, list[str]] = {
    "维生素类": [
        "vitamin", "vit ", "multivitamin", "multi-vitamin", "biotin",
        "folate", "folic acid", "niacin", "riboflavin", "thiamine",
        "retinol", "tocopherol", "ascorbic acid",
    ],
    "矿物质类": [
        "mineral", "calcium", "magnesium", "zinc", "iron", "selenium",
        "chromium", "potassium", "iodine", "copper", "manganese",
    ],
    "草本/植物类": [
        "ashwagandha", "turmeric", "curcumin", "ginger", "ginseng",
        "echinacea", "elderberry", "milk thistle", "saw palmetto",
        "valerian", "maca", "rhodiola", "berberine", "fenugreek",
        "black seed", "moringa", "green tea extract", "garlic",
        "oregano oil", "mushroom", "reishi", "lion's mane", "lions mane",
        "cordyceps", "chaga", "tongkat ali", "tribulus",
    ],
    "氨基酸/蛋白类": [
        "amino acid", "collagen", "protein", "creatine", "glutamine",
        "l-theanine", "l-carnitine", "bcaa", "taurine", "glycine",
        "nac", "n-acetyl cysteine", "peptide",
    ],
    "益生菌/消化类": [
        "probiotic", "prebiotic", "digestive enzyme", "fiber",
        "psyllium", "lactobacillus", "bifidobacterium", "cfu",
    ],
    "脂肪酸类": [
        "omega-3", "omega 3", "fish oil", "krill oil", "cod liver oil",
        "dha", "epa", "flaxseed oil", "algal oil",
    ],
    "抗氧化/抗衰类": [
        "nmn", "nicotinamide mononucleotide", "nr ", "nad+", "nad ",
        "coq10", "coenzyme q10", "resveratrol", "astaxanthin",
        "glutathione", "pqq", "quercetin", "urolithin", "spermidine",
    ],
    "特殊功能类": [
        "melatonin", "5-htp", "gaba", "dhea", "glucosamine",
        "chondroitin", "msm", "hyaluronic acid", "lutein",
    ],
}

# 复合/综合类单独处理（优先级最高）
MULTI_KEYWORDS = [
    "multivitamin", "multi-vitamin", "multi vitamin", "one-a-day",
    "one a day", "daily pack", "prenatal vitamin", "postnatal vitamin",
]


# ---------------------------------------------------------------------------
# 剂型关键词
# ---------------------------------------------------------------------------

DOSAGE_FORMS: dict[str, list[str]] = {
    "Capsules": ["capsule", "capsules", "veggie capsule", "vegetable capsule", "veg cap", "vcap"],
    "Softgels": ["softgel", "softgels", "soft gel", "soft gels", "liquid softgel"],
    "Gummies": ["gummy", "gummies", "gummi"],
    "Tablets": ["tablet", "tablets", "caplet", "caplets"],
    "Powder": ["powder", "mix", "scoop"],
    "Liquid/Drops": ["liquid", "drops", "tincture", "spray", "syrup", "elixir"],
    "Chewable": ["chewable", "chew", "lozenge"],
}


# ---------------------------------------------------------------------------
# 功效方向关键词
# ---------------------------------------------------------------------------

HEALTH_BENEFITS: dict[str, list[str]] = {
    "免疫支持": ["immune", "immunity", "immune support", "immune defense", "immune health"],
    "关节/骨骼健康": ["joint", "bone", "joint support", "bone health", "flexibility", "mobility", "cartilage"],
    "消化健康": ["digestive", "gut", "gut health", "digestion", "bloating", "regularity"],
    "能量/代谢": ["energy", "metabolism", "metabolic", "stamina", "vitality", "fatigue"],
    "抗氧化/抗衰": ["antioxidant", "anti-aging", "longevity", "cellular health", "mitochondria", "anti-inflammatory"],
    "认知/脑健康": ["brain", "cognitive", "memory", "focus", "mental clarity", "nootropic"],
    "心血管健康": ["heart", "cardiovascular", "blood pressure", "cholesterol", "circulation"],
    "美容/皮肤/头发": ["skin", "hair", "nails", "beauty", "glow", "complexion", "anti-wrinkle"],
    "运动/健身": ["workout", "muscle", "recovery", "performance", "pre-workout", "post-workout", "strength", "endurance"],
    "睡眠/放松": ["sleep", "relax", "calm", "stress", "anxiety", "mood"],
    "男性健康": ["testosterone", "prostate", "male health", "men's health", "libido"],
    "女性健康": ["prenatal", "postnatal", "menopause", "pms", "women's health", "fertility", "hormonal balance"],
    "儿童健康": ["kids", "children", "toddler", "pediatric", "growing", "development"],
    "眼部健康": ["eye", "vision", "macular", "eye health"],
    "体重管理": ["weight", "appetite", "fat burn", "thermogenic", "keto"],
}


# ---------------------------------------------------------------------------
# 目标人群关键词
# ---------------------------------------------------------------------------

TARGET_DEMOGRAPHICS: dict[str, list[str]] = {
    "Men": ["for men", "men's", "male", " man "],
    "Women": ["for women", "women's", "female", " her "],
    "Kids": ["kids", "children", "child", "toddler", "baby", "infant", "pediatric"],
    "Seniors": ["senior", "elderly", "50+", "over 50", "aging", "mature"],
    "Athletes": ["athlete", "sport", "workout", "gym", "bodybuilding", "fitness"],
    "Prenatal": ["prenatal", "pregnancy", "pregnant", "expecting", "postnatal", "postpartum"],
}


# ---------------------------------------------------------------------------
# 认证标签关键词
# ---------------------------------------------------------------------------

CERT_LABELS: dict[str, list[str]] = {
    "Non-GMO": ["non-gmo", "non gmo", "no gmo"],
    "Organic": ["organic", "usda organic"],
    "Vegan": ["vegan", "plant-based", "plant based"],
    "Vegetarian": ["vegetarian"],
    "Gluten-Free": ["gluten-free", "gluten free", "no gluten"],
    "GMP": ["gmp", "good manufacturing practice", "cgmp"],
    "Third-Party Tested": ["third-party tested", "third party tested", "3rd party", "independently tested", "usp verified", "nsf certified"],
    "Dairy-Free": ["dairy-free", "dairy free", "lactose-free"],
    "Soy-Free": ["soy-free", "soy free"],
    "Sugar-Free": ["sugar-free", "sugar free", "no sugar", "zero sugar"],
    "Keto-Friendly": ["keto", "keto-friendly"],
}


# ---------------------------------------------------------------------------
# 正则模式
# ---------------------------------------------------------------------------

# 剂量单位正则（排除包装数量）
RE_DOSAGE = re.compile(
    r'(\d[\d,]*\.?\d*)\s*'
    r'(mg|mcg|µg|ug|IU|iu|CFU|cfu|billion\s*CFU|billion\s*cfu'
    r'|g(?:ram)?|ml|oz|ppm|mcg\s*DFE|mg\s*NE|RAE|%)',
    re.IGNORECASE,
)

# 包装数量正则（用于排除误判）
RE_PACK_COUNT = re.compile(
    r'(\d[\d,]*)\s*'
    r'(count|ct|capsules?|softgels?|soft\s*gels?|gumm(?:y|ies|i)'
    r'|tablets?|caplets?|chewables?|servings?|doses?|pack|supply|bottle)',
    re.IGNORECASE,
)

# 包装规格提取正则
RE_PACKAGE_SIZE = re.compile(
    r'(\d[\d,]*)\s*'
    r'(count|ct|capsules?|softgels?|soft\s*gels?|gumm(?:y|ies|i)'
    r'|tablets?|caplets?|chewables?|servings?|doses?)',
    re.IGNORECASE,
)

# 复合配方指示词
RE_COMPOUND = re.compile(
    r'\b(complex|blend|formula|with\s+\w+|plus\s+\w+|\+|&)\b',
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# 解析函数
# ---------------------------------------------------------------------------

def _lower_text(title: str, bullets: str = "") -> str:
    """合并标题和五点描述为小写文本，用于关键词匹配。"""
    return f" {title} {bullets} ".lower()


def _match_keywords(text: str, keyword_map: dict[str, list[str]]) -> list[str]:
    """在文本中匹配关键词映射，返回所有匹配的类别。"""
    matched = []
    for category, keywords in keyword_map.items():
        for kw in keywords:
            if kw.lower() in text:
                matched.append(category)
                break
    return matched


def parse_ingredient_category(title: str, bullets: str = "") -> tuple[str, str]:
    """解析成分大类。返回 (主分类, 副分类)。"""
    text = _lower_text(title, bullets)

    # 优先检查综合维生素
    for kw in MULTI_KEYWORDS:
        if kw in text:
            return "复合/综合类", ""

    matched = _match_keywords(text, INGREDIENT_CATEGORIES)
    if not matched:
        return "未知", ""
    if len(matched) == 1:
        return matched[0], ""
    return matched[0], matched[1]


def parse_dosage_form(title: str, bullets: str = "") -> str:
    """解析剂型。"""
    text = _lower_text(title)
    for form, keywords in DOSAGE_FORMS.items():
        for kw in keywords:
            if kw in text:
                return form

    # 标题未匹配，尝试五点
    if bullets:
        text_b = _lower_text(bullets)
        for form, keywords in DOSAGE_FORMS.items():
            for kw in keywords:
                if kw in text_b:
                    return form

    return "其他/未知"


def parse_dosage_labeled(title: str, bullets: str = "") -> str:
    """判断是否有剂量标注。"""
    # 先从标题中找剂量
    dosage_matches = RE_DOSAGE.findall(title)
    if dosage_matches:
        return "有标注剂量"

    # 再从五点中找
    if bullets:
        dosage_matches = RE_DOSAGE.findall(bullets)
        if dosage_matches:
            return "有标注剂量"

    return "无标注剂量"


def parse_health_benefits(title: str, bullets: str = "") -> list[str]:
    """解析功效方向。"""
    # 优先从标题提取
    text_title = _lower_text(title)
    matched = _match_keywords(text_title, HEALTH_BENEFITS)
    if matched:
        return matched[:3]  # 最多 3 个

    # 标题无功效 claim，从五点提取
    if bullets:
        text_all = _lower_text(title, bullets)
        matched = _match_keywords(text_all, HEALTH_BENEFITS)
        if matched:
            return [f"{m}（⚠️ 推测）" for m in matched[:3]]

    return ["通用/未明确"]


def parse_target_demographic(title: str, bullets: str = "") -> str:
    """解析目标人群。"""
    text = _lower_text(title)
    matched = _match_keywords(text, TARGET_DEMOGRAPHICS)
    if matched:
        return matched[0]

    if bullets:
        text_all = _lower_text(title, bullets)
        matched = _match_keywords(text_all, TARGET_DEMOGRAPHICS)
        if matched:
            return matched[0]

    return "通用"


def parse_package_size(title: str) -> tuple[int | None, str]:
    """解析包装规格。返回 (数量, 分段)。"""
    matches = RE_PACKAGE_SIZE.findall(title)
    if not matches:
        return None, "未知"

    # 取最大数字（避免误取剂量数字）
    sizes = []
    for num_str, unit in matches:
        num = int(num_str.replace(",", ""))
        sizes.append(num)

    size = max(sizes)

    if size <= 30:
        return size, "≤30ct"
    elif size <= 60:
        return size, "31-60ct"
    elif size <= 90:
        return size, "61-90ct"
    elif size <= 120:
        return size, "91-120ct"
    elif size <= 180:
        return size, "121-180ct"
    else:
        return size, "180ct+"


def parse_cert_labels(title: str, bullets: str = "") -> list[str]:
    """解析认证标签。"""
    text = _lower_text(title, bullets)
    return _match_keywords(text, CERT_LABELS)


def parse_formula_type(title: str, bullets: str = "") -> str:
    """解析配方类型。"""
    text = _lower_text(title)

    # 优先检查综合维生素
    for kw in MULTI_KEYWORDS:
        if kw in text:
            return "综合维生素"

    # 检查复合配方指示词
    if RE_COMPOUND.search(title):
        return "复合配方"

    # 检查标题中是否出现多个成分大类
    matched_cats = _match_keywords(text, INGREDIENT_CATEGORIES)
    if len(matched_cats) >= 2:
        return "复合配方"

    return "单一成分"


def parse_product(product: dict[str, Any], detail_data: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    解析单个产品的所有保健品维度。

    Args:
        product: category_report 中的单条产品数据
        detail_data: 可选的 product_detail 返回数据（用于补充五点描述）

    Returns:
        包含所有属性标注的字典
    """
    title = product.get("title", product.get("标题", ""))
    bullets = ""
    if detail_data:
        # product_detail 返回的五点描述
        desc = detail_data.get("产品描述", detail_data.get("description", ""))
        if isinstance(desc, list):
            bullets = " ".join(desc)
        elif isinstance(desc, str):
            bullets = desc

    # 解析各维度
    ingredient_main, ingredient_sub = parse_ingredient_category(title, bullets)
    dosage_form = parse_dosage_form(title, bullets)
    dosage_labeled = parse_dosage_labeled(title, bullets)
    benefits = parse_health_benefits(title, bullets)
    demographic = parse_target_demographic(title, bullets)
    pkg_count, pkg_segment = parse_package_size(title)
    certs = parse_cert_labels(title, bullets)
    formula_type = parse_formula_type(title, bullets)

    # 置信度判断
    unknowns = 0
    if ingredient_main == "未知":
        unknowns += 1
    if dosage_form == "其他/未知":
        unknowns += 1
    if pkg_segment == "未知":
        unknowns += 1

    confidence = "高" if unknowns == 0 else ("中" if unknowns == 1 else "低")
    needs_detail = confidence == "低" and detail_data is None

    return {
        "成分大类": ingredient_main,
        "成分副分类": ingredient_sub,
        "剂型": dosage_form,
        "剂量标注": dosage_labeled,
        "功效方向": ", ".join(benefits),
        "目标人群": demographic,
        "包装数量": pkg_count,
        "包装规格段": pkg_segment,
        "认证标签": ", ".join(certs) if certs else "无",
        "认证标签数量": len(certs),
        "配方类型": formula_type,
        "置信度": confidence,
        "验证方式": "标题" if not detail_data else "标题+product_detail",
        "需要product_detail补充": needs_detail,
    }


# ---------------------------------------------------------------------------
# 批量处理
# ---------------------------------------------------------------------------

def parse_top100(
    products: list[dict[str, Any]],
    details: dict[str, dict[str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    批量解析 Top100 产品。

    Args:
        products: category_report 解析后的产品列表
        details: 可选的 {asin: product_detail_data} 映射

    Returns:
        (parsed_products, uncertain_products)
    """
    parsed = []
    uncertain = []

    for p in products:
        asin = p.get("asin", p.get("ASIN", ""))
        detail = details.get(asin) if details else None
        attrs = parse_product(p, detail)

        # 合并原始数据和属性标注
        merged = {**p, **attrs}
        parsed.append(merged)

        if attrs["需要product_detail补充"]:
            uncertain.append({
                "asin": asin,
                "title": p.get("title", p.get("标题", "")),
                "缺失维度": [],
            })
            if attrs["成分大类"] == "未知":
                uncertain[-1]["缺失维度"].append("成分大类")
            if attrs["剂型"] == "其他/未知":
                uncertain[-1]["缺失维度"].append("剂型")
            if attrs["包装规格段"] == "未知":
                uncertain[-1]["缺失维度"].append("包装规格")

    return parsed, uncertain


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="保健品标题属性解析")
    parser.add_argument("--input", required=True, help="top100_raw.json 路径")
    parser.add_argument("--output-dir", required=True, help="输出目录")
    parser.add_argument("--details", default=None, help="可选：product_detail 补充数据 JSON 路径")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 读取产品数据
    raw = json.loads(input_path.read_text(encoding="utf-8-sig"))

    # 处理 category_report 的特殊格式
    if isinstance(raw, list) and len(raw) > 0 and "text" in raw[0]:
        text_content = raw[0]["text"]
        json_start = text_content.index("{")
        data = json.loads(text_content[json_start:])
        products = data.get("products", data.get("data", []))
    elif isinstance(raw, dict):
        products = raw.get("products", raw.get("data", raw.get("items", [])))
    elif isinstance(raw, list):
        products = raw
    else:
        print(f"ERROR: 无法识别输入格式", file=sys.stderr)
        sys.exit(1)

    # 读取 product_detail 补充数据（如有）
    details = None
    if args.details:
        details_path = Path(args.details)
        if details_path.exists():
            details_raw = json.loads(details_path.read_text(encoding="utf-8-sig"))
            if isinstance(details_raw, dict):
                details = details_raw
            elif isinstance(details_raw, list):
                details = {d.get("asin", d.get("ASIN", "")): d for d in details_raw}

    # 解析
    parsed, uncertain = parse_top100(products, details)

    # 输出
    parsed_path = output_dir / "top100_parsed.json"
    uncertain_path = output_dir / "uncertain_products.json"

    parsed_path.write_text(
        json.dumps(parsed, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    uncertain_path.write_text(
        json.dumps(uncertain, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # 统计摘要
    total = len(parsed)
    high_conf = sum(1 for p in parsed if p["置信度"] == "高")
    mid_conf = sum(1 for p in parsed if p["置信度"] == "中")
    low_conf = sum(1 for p in parsed if p["置信度"] == "低")
    need_detail = len(uncertain)

    print(f"✅ 解析完成：共 {total} 条产品")
    print(f"   高置信度: {high_conf} | 中置信度: {mid_conf} | 低置信度: {low_conf}")
    print(f"   需要 product_detail 补充: {need_detail} 条")
    print(f"   输出: {parsed_path}")
    print(f"   待验证: {uncertain_path}")

    # 维度分布摘要
    from collections import Counter
    cat_dist = Counter(p["成分大类"] for p in parsed)
    form_dist = Counter(p["剂型"] for p in parsed)
    type_dist = Counter(p["配方类型"] for p in parsed)

    print(f"\n📊 成分大类分布:")
    for cat, cnt in cat_dist.most_common():
        print(f"   {cat}: {cnt} ({cnt/total*100:.0f}%)")

    print(f"\n📊 剂型分布:")
    for form, cnt in form_dist.most_common():
        print(f"   {form}: {cnt} ({cnt/total*100:.0f}%)")

    print(f"\n📊 配方类型分布:")
    for ft, cnt in type_dist.most_common():
        print(f"   {ft}: {cnt} ({cnt/total*100:.0f}%)")


if __name__ == "__main__":
    main()
