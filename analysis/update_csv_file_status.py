# -*- coding: utf-8 -*-
"""
更新CSV文件状态标注脚本，确认L3和指南文件是否存在，并在CSV中标注文件路径。

功能：
在 data/scene-matrix-work.csv 中标注每个场景对应的L3文件和指南文件路径
- 如果文件存在：填入文件相对路径
- 如果文件不存在：填入空值或保持原状

执行方式：
    cd C:\HRIA
    python analysis/update_csv_file_status.py
"""

import csv
import json
from pathlib import Path

# 路径配置
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
CSV_PATH = PROJECT_ROOT / "data" / "scene-matrix-work.csv"
L3_DIR = PROJECT_ROOT / "actions" / "by-category"
GUIDE_DIR = PROJECT_ROOT / "guides"


def get_l3_files():
    """获取所有L3文件，按场景名索引"""
    l3_map = {}
    for f in L3_DIR.glob("l3_*.json"):
        scene_name = f.stem[3:]  # 去掉 "l3_" 前缀
        l3_map[scene_name] = f"actions/by-category/{f.name}"
    return l3_map


def get_guide_files():
    """
    获取所有指南文件名集合

    指南文件名格式：{industry_code}-{scene_name_en}.json
    例如：35-359-3595-VisualInspection-FirefightingEquipment-SurfaceDefects.json
    """
    guide_files = set()
    for f in GUIDE_DIR.glob("*.json"):
        guide_files.add(f.name)
    return guide_files


def update_csv():
    """更新CSV，标注文件路径"""
    # 加载文件索引
    l3_map = get_l3_files()
    guide_files = get_guide_files()

    print(f"找到L3文件：{len(l3_map)}个")
    print(f"找到指南文件：{len(guide_files)}个")

    # 读取CSV
    rows = []
    with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)

    # 确保有标注列
    if 'l3_file_path' not in fieldnames:
        fieldnames = list(fieldnames) + ['l3_file_path']
    if 'guide_file_path' not in fieldnames:
        fieldnames = list(fieldnames) + ['guide_file_path']

    # 更新每行
    l3_found = 0
    guide_found = 0

    for row in rows:
        scene_name_zh = row.get('scene_name_zh', '')
        scene_name_en = row.get('scene_name_en', '')
        industry_code = row.get('industry_code', '')

        # 检查L3文件（用中文场景名匹配）
        if scene_name_zh in l3_map:
            row['l3_file_path'] = l3_map[scene_name_zh]
            row['l3_extracted'] = 'TRUE'
            l3_found += 1
        else:
            row['l3_file_path'] = ''

        # 检查指南文件（用 industry_code-scene_name_en.json 格式匹配）
        expected_guide_name = f"{industry_code}-{scene_name_en}.json"
        if expected_guide_name in guide_files:
            row['guide_file_path'] = f"guides/{expected_guide_name}"
            row['guide_generated'] = 'TRUE'
            guide_found += 1
        else:
            row['guide_file_path'] = ''

    # 写回CSV
    with open(CSV_PATH, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n更新完成：")
    print(f"  场景总数：{len(rows)}")
    print(f"  匹配到L3文件：{l3_found}")
    print(f"  匹配到指南文件：{guide_found}")
    print(f"  已更新：{CSV_PATH}")


if __name__ == "__main__":
    update_csv()
