# -*- coding: utf-8 -*-
"""
场景数据整合脚本

将场景基础数据、L3元动作数据、建设指南数据合并为一个完整的JSON文件
供可视化界面使用
"""

import json
import os
import re
import csv
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent

# 输入文件
SCENES_DATA = SCRIPT_DIR / "scenes-data.json"
SCENE_MATRIX_WORK = PROJECT_ROOT / "data" / "scene-matrix-work.csv"
L3_DIR = PROJECT_ROOT / "actions" / "by-category"
GUIDES_DIR = PROJECT_ROOT / "guides"

# 输出文件
OUTPUT_FILE = SCRIPT_DIR / "scenes-data-full.json"


def load_scene_status():
    """从 scene-matrix-work.csv 加载场景状态"""
    status_map = {}
    if not SCENE_MATRIX_WORK.exists():
        return status_map

    with open(SCENE_MATRIX_WORK, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            scene_name = row.get('scene_name_zh', '')
            if scene_name:
                status_map[scene_name] = {
                    'l3_extracted': row.get('l3_extracted', '') == 'done',
                    'guide_generated': row.get('guide_generated', '') == 'done'
                }
    return status_map


def load_scenes():
    """加载场景基础数据"""
    with open(SCENES_DATA, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_l3_data():
    """加载所有L3提取数据，按场景名索引"""
    l3_map = {}
    if not L3_DIR.exists():
        return l3_map

    for f in L3_DIR.glob("l3_*.json"):
        try:
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
                scene_name = data.get('scene_name', '')
                if scene_name:
                    l3_map[scene_name] = {
                        'total_steps': data.get('total_steps', 0),
                        'action_sequence': data.get('action_sequence', []),
                        'l2_usage_summary': data.get('l2_usage_summary', {}),
                        'new_l3_definitions': data.get('new_l3_definitions', [])
                    }
        except Exception as e:
            print(f"加载L3文件失败 {f.name}: {e}")

    return l3_map


def load_guides():
    """加载所有建设指南，按industry_code索引"""
    guide_map = {}
    if not GUIDES_DIR.exists():
        return guide_map

    for f in GUIDES_DIR.glob("*.json"):
        try:
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)

                # 优先从文件名提取 industry_code（格式如 9-91-00-Palletizing-xxx.json）
                filename = f.stem  # 不含扩展名
                parts = filename.split('-')
                # 找到第一个非数字部分之前的所有部分作为 industry_code
                code_parts = []
                for p in parts:
                    if p.isdigit() or (len(p) <= 4 and p.replace('-', '').isdigit()):
                        code_parts.append(p)
                    else:
                        break
                base_id = '-'.join(code_parts) if code_parts else ''

                # 如果从文件名提取失败，尝试从 scene_id 提取
                if not base_id:
                    scene_id = data.get('scene_id', '')
                    base_id = '-'.join(scene_id.split('-')[:3]) if scene_id else ''

                if base_id:
                    # 提取完整信息（v3.1: 保留更多数据）
                    part1 = data.get('part1_scene_portrait', {})
                    part2 = data.get('part2_task_analysis', {})
                    part3 = data.get('part3_construction', {})
                    part4 = data.get('part4_pitfalls', [])
                    part5 = data.get('part5_economics', {})
                    scene_id = data.get('scene_id', '')

                    guide_map[base_id] = {
                        'scene_id': scene_id,
                        # Part1: 场景画像
                        'portrait': {
                            'line_position': part1.get('line_position', ''),
                            'current_operation': part1.get('current_operation', ''),
                            'environment': part1.get('environment', ''),
                            'pain_point': part1.get('pain_point', ''),
                        },
                        # Part2: 任务分析
                        'task_analysis': {
                            'difficulty_summary': part2.get('difficulty_summary', ''),
                            'key_difficulties': [
                                {
                                    'step_ref': kd.get('step_ref', ''),
                                    'l3_id': kd.get('l3_id', ''),
                                    'l3_name': kd.get('l3_name', ''),
                                    'worker_method': kd.get('worker_method', ''),
                                    'physical_constraints': kd.get('physical_constraints', ''),
                                    'human_robot_diff': kd.get('human_robot_diff', ''),
                                    'failure_and_recovery': kd.get('failure_and_recovery', '')
                                }
                                for kd in part2.get('key_difficulties', [])
                            ]
                        },
                        # Part3: 建设方案
                        'construction': {
                            'phase1_validation': part3.get('phase1_validation', ''),
                            'phase2_first_deploy': part3.get('phase2_first_deploy', ''),
                            'phase3_expansion_criteria': part3.get('phase3_expansion_criteria', ''),
                            'conditions': [
                                {
                                    'name': c.get('name', ''),
                                    'layer': c.get('layer', ''),
                                    'stage': c.get('stage', ''),
                                    'status': c.get('status', ''),
                                    'current_state': c.get('current_state', ''),
                                    'action_needed': c.get('action_needed', ''),
                                    'estimated_cost': c.get('estimated_cost', ''),
                                    'estimated_duration': c.get('estimated_duration', '')
                                }
                                for c in part3.get('conditions', [])
                            ]
                        },
                        # Part4: 避坑指南
                        'pitfalls': [
                            {
                                'title': p.get('title', ''),
                                'symptom': p.get('symptom', ''),
                                'root_cause': p.get('root_cause', ''),
                                'mitigation': p.get('mitigation', '')
                            }
                            for p in part4
                        ],
                        # Part5: 经济性分析
                        'economics': {
                            'value_source': part5.get('value_source', ''),
                            'cost_items_human': part5.get('cost_items_human', []),
                            'cost_items_robot': part5.get('cost_items_robot', []),
                            'sensitivity_analysis': part5.get('sensitivity_analysis', ''),
                            'disclaimer': part5.get('disclaimer', '')
                        }
                    }
        except Exception as e:
            print(f"加载指南文件失败 {f.name}: {e}")

    return guide_map


def merge_data():
    """合并所有数据"""
    print("加载场景基础数据...")
    scenes = load_scenes()
    print(f"  共 {len(scenes)} 个场景")

    print("加载场景状态（从CSV）...")
    status_map = load_scene_status()
    print(f"  共 {len(status_map)} 个场景有状态记录")

    print("加载L3元动作数据...")
    l3_map = load_l3_data()
    print(f"  共 {len(l3_map)} 个L3数据文件")

    print("加载建设指南数据...")
    guide_map = load_guides()
    print(f"  共 {len(guide_map)} 个指南数据文件")

    # 统计（基于CSV状态）
    has_l3 = 0
    has_guide = 0
    has_both = 0

    # 合并
    for scene in scenes:
        scene_name = scene.get('scene_name_zh', '')
        industry_code = scene.get('industry_code', '')

        # 从CSV获取状态
        status = status_map.get(scene_name, {})
        l3_done = status.get('l3_extracted', False)
        guide_done = status.get('guide_generated', False)

        # 匹配L3数据（仅当CSV标记为done时）
        if l3_done:
            l3_data = l3_map.get(scene_name)
            scene['l3_data'] = l3_data
            has_l3 += 1
        else:
            scene['l3_data'] = None

        # 匹配建设指南（仅当CSV标记为done时）
        if guide_done:
            guide_data = guide_map.get(industry_code)
            scene['guide_data'] = guide_data
            has_guide += 1
        else:
            scene['guide_data'] = None

        # 统计同时有两者的
        if l3_done and guide_done:
            has_both += 1

        # 添加数据完整度标记（基于CSV状态）
        if l3_done and guide_done:
            scene['data_status'] = 'full'
        elif l3_done:
            scene['data_status'] = 'l3_only'
        elif guide_done:
            scene['data_status'] = 'guide_only'
        else:
            scene['data_status'] = 'basic'

    print(f"\n统计（基于CSV状态）:")
    print(f"  L3已提取: {has_l3}")
    print(f"  指南已生成: {has_guide}")
    print(f"  两者都有: {has_both}")
    print(f"  暂无扩展数据: {len(scenes) - has_l3 - has_guide + has_both}")

    # 保存
    print(f"\n保存到 {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(scenes, f, ensure_ascii=False, indent=2)

    print("完成!")
    return scenes


if __name__ == "__main__":
    merge_data()
