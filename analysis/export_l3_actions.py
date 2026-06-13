# -*- coding: utf-8 -*-
"""
L3元动作导出脚本

================================================================================
用途：
    将所有L3提取文件中的元动作信息导出为一个CSV文件，以每个L3元动作为一行。
    用于构建L3元动作的完整清单，支持后续的统计分析和检索。

================================================================================
执行逻辑：
    1. 扫描 actions/by-category/l3_*.json 目录下的所有L3提取文件
    2. 逐个读取JSON文件，提取 action_sequence 中的每个 step
    3. 每个 step 对应一个L3元动作，作为CSV中的一行
    4. 同时关联场景元数据（从 data/scene-matrix-work.csv 读取行业信息等）
    5. 输出到 analysis/l3_actions_full.csv

================================================================================
输出字段说明：
    - scene_name_zh: 场景中文名（来源场景）
    - scene_name_en: 场景英文名
    - industry_code: 行业代码
    - industry_name: 行业名称
    - step_order: 步骤序号（该L3在场景中的执行顺序）
    - l1_id: L1大类编号
    - l1_name: L1大类名称
    - l2_id: L2类别编号
    - l2_name: L2类别名称
    - l3_id: L3元动作编号
    - l3_name: L3元动作名称
    - is_new_l3: 是否为新定义的L3（True/False）
    - human_description: 人工操作描述
    - duration_estimate: 预估耗时（秒）
    - parallel_with: 并行执行的步骤编号（如有）
    - boundary_note: 边界说明（如有）

================================================================================
执行方式：
    cd C:/HRIA
    python analysis/export_l3_actions.py

================================================================================
"""

import csv
import json
from pathlib import Path
from datetime import datetime

# 路径配置
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
L3_DIR = PROJECT_ROOT / "actions" / "by-category"
SCENE_CSV = PROJECT_ROOT / "data" / "scene-matrix-work.csv"
OUTPUT_CSV = PROJECT_ROOT / "analysis" / "l3_actions_full.csv"


def load_scene_metadata():
    """
    加载场景元数据，建立场景名到行业信息的映射

    返回：{scene_name_zh: {industry_code, industry_name, scene_name_en, ...}}
    """
    scene_meta = {}

    # 尝试多种编码
    encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312', 'gb18030']

    for encoding in encodings:
        try:
            with open(SCENE_CSV, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    scene_name = row.get('scene_name_zh', '')
                    if scene_name:
                        scene_meta[scene_name] = {
                            'scene_name_en': row.get('scene_name_en', ''),
                            'industry_code': row.get('industry_code', ''),
                            'industry_name': row.get('source_major_name', ''),
                            'process_step': row.get('process_step', ''),
                        }
            print(f"   使用编码: {encoding}")
            break
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"   编码 {encoding} 失败: {e}")
            continue

    return scene_meta


def extract_l3_actions(scene_meta):
    """
    从所有L3文件中提取元动作信息

    返回：L3动作列表，每个元素是一个字典
    """
    l3_actions = []
    l3_files = list(L3_DIR.glob("l3_*.json"))

    print(f"扫描到 {len(l3_files)} 个L3文件")

    for file_path in l3_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            scene_name = data.get('scene_name', '')
            scene_id = data.get('scene_id', '')
            total_steps = data.get('total_steps', 0)

            # 获取场景元数据
            meta = scene_meta.get(scene_name, {})

            # 提取每个步骤
            for step in data.get('action_sequence', []):
                l3_action = {
                    # 场景信息
                    'scene_name_zh': scene_name,
                    'scene_name_en': meta.get('scene_name_en', ''),
                    'scene_id': scene_id,
                    'industry_code': meta.get('industry_code', ''),
                    'industry_name': meta.get('industry_name', ''),
                    'process_step': meta.get('process_step', ''),
                    'total_steps_in_scene': total_steps,

                    # 步骤信息
                    'step_order': step.get('step_order', ''),

                    # L1-L2-L3层级信息
                    'l1_id': step.get('l1_id', ''),
                    'l1_name': step.get('l1_name', ''),
                    'l2_id': step.get('l2_id', ''),
                    'l2_name': step.get('l2_name', ''),
                    'l3_id': step.get('l3_id', ''),
                    'l3_name': step.get('l3_name', ''),

                    # 其他属性
                    'is_new_l3': step.get('is_new_l3', ''),
                    'human_description': step.get('human_description', ''),
                    'duration_estimate': step.get('duration_estimate', ''),
                    'parallel_with': step.get('parallel_with', ''),
                    'boundary_note': step.get('boundary_note', ''),

                    # 来源文件
                    'source_file': file_path.name,
                }

                l3_actions.append(l3_action)

        except Exception as e:
            print(f"读取文件失败 {file_path.name}: {e}")

    return l3_actions


def save_to_csv(l3_actions):
    """
    保存L3动作列表到CSV文件
    """
    if not l3_actions:
        print("没有L3动作数据可导出")
        return

    # CSV字段顺序
    fieldnames = [
        'l3_id', 'l3_name', 'l2_id', 'l2_name', 'l1_id', 'l1_name',
        'scene_name_zh', 'scene_name_en', 'industry_code', 'industry_name',
        'process_step', 'step_order', 'total_steps_in_scene',
        'is_new_l3', 'human_description', 'duration_estimate',
        'parallel_with', 'boundary_note', 'scene_id', 'source_file'
    ]

    with open(OUTPUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(l3_actions)

    return OUTPUT_CSV


def print_summary(l3_actions):
    """
    打印统计摘要
    """
    # 统计
    unique_l3 = set(a['l3_id'] for a in l3_actions if a['l3_id'])
    unique_l2 = set(a['l2_id'] for a in l3_actions if a['l2_id'])
    unique_l1 = set(a['l1_id'] for a in l3_actions if a['l1_id'])
    unique_scenes = set(a['scene_name_zh'] for a in l3_actions if a['scene_name_zh'])
    unique_industries = set(a['industry_name'] for a in l3_actions if a['industry_name'])

    print("\n" + "=" * 50)
    print("导出完成")
    print("=" * 50)
    print(f"总记录数（L3动作出现次数）：{len(l3_actions)}")
    print(f"唯一L3动作数：{len(unique_l3)}")
    print(f"唯一L2类别数：{len(unique_l2)}")
    print(f"唯一L1大类数：{len(unique_l1)}")
    print(f"涉及场景数：{len(unique_scenes)}")
    print(f"涉及行业数：{len(unique_industries)}")
    print(f"输出文件：{OUTPUT_CSV}")
    print("=" * 50)


def main():
    print("=" * 50)
    print("L3元动作导出脚本")
    print("=" * 50)

    # 1. 加载场景元数据
    print("\n1. 加载场景元数据...")
    scene_meta = load_scene_metadata()
    print(f"   加载了 {len(scene_meta)} 个场景的元数据")

    # 2. 提取L3动作
    print("\n2. 提取L3动作...")
    l3_actions = extract_l3_actions(scene_meta)
    print(f"   提取了 {len(l3_actions)} 条L3动作记录")

    # 3. 保存CSV
    print("\n3. 保存CSV...")
    output_path = save_to_csv(l3_actions)
    print(f"   已保存到 {output_path}")

    # 4. 打印摘要
    print_summary(l3_actions)


if __name__ == "__main__":
    main()
