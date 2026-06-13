# -*- coding: utf-8 -*-
"""
场景优先级四象限分析脚本
最开始的一次的脚本
基于7维评分数据计算价值分和难度分，进行四象限划分
"""

import csv
import json
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent

# 输入输出文件
INPUT_CSV = PROJECT_ROOT / "data" / "scene-matrix-work.csv"
OUTPUT_DIR = SCRIPT_DIR / "quadrant-analysis"


def load_scenes():
    """加载全部场景数据"""
    scenes = []
    with open(INPUT_CSV, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 提取7维评分（处理空值）
            try:
                labor_urgency = int(row.get('labor_urgency_score', 0) or 0)
                scale_potential = int(row.get('scale_potential_score', 0) or 0)
                superhuman_value = int(row.get('superhuman_value_score', 0) or 0)
                operation_complexity = int(row.get('operation_complexity_score', 0) or 0)
                structure_level = int(row.get('structure_level_score', 0) or 0)
                fault_tolerance = int(row.get('fault_tolerance_score', 0) or 0)
                takt_pressure = int(row.get('takt_pressure_score', 0) or 0)
            except ValueError:
                continue

            # 计算价值分（越高越好）
            value_score = (labor_urgency + scale_potential + superhuman_value) / 3

            # 计算难度分（越低越好实施）
            # structure_level, fault_tolerance, takt_pressure 需要反转（5-x）
            # 因为原始分数越高表示越容易/越有余量
            difficulty_score = (
                operation_complexity +
                (5 - structure_level) +
                (5 - fault_tolerance) +
                (5 - takt_pressure)
            ) / 4

            scenes.append({
                'scene_name_zh': row.get('scene_name_zh', ''),
                'scene_name_en': row.get('scene_name_en', ''),
                'industry_code': row.get('industry_code', ''),
                'source_major_code': row.get('source_major_code', ''),
                'source_major_name': row.get('source_major_name', ''),
                'process_step': row.get('process_step', ''),
                # 原始7维分数
                'labor_urgency': labor_urgency,
                'scale_potential': scale_potential,
                'superhuman_value': superhuman_value,
                'operation_complexity': operation_complexity,
                'structure_level': structure_level,
                'fault_tolerance': fault_tolerance,
                'takt_pressure': takt_pressure,
                # 综合分数
                'value_score': round(value_score, 2),
                'difficulty_score': round(difficulty_score, 2),
                # 数据状态
                'l3_extracted': row.get('l3_extracted', '') == 'done',
                'guide_generated': row.get('guide_generated', '') == 'done'
            })

    return scenes


def classify_quadrant(value_score, difficulty_score, value_threshold=3.0, difficulty_threshold=2.0):
    """
    四象限分类

    基于阈值划分：
    - Q1: 高价值 + 低难度 = 优先实施 (Quick Wins)
    - Q2: 高价值 + 高难度 = 重点攻关 (Strategic)
    - Q3: 低价值 + 低难度 = 可填充 (Fill-ins)
    - Q4: 低价值 + 高难度 = 暂缓 (Avoid)
    """
    high_value = value_score >= value_threshold
    low_difficulty = difficulty_score <= difficulty_threshold

    if high_value and low_difficulty:
        return 'Q1-优先实施'
    elif high_value and not low_difficulty:
        return 'Q2-重点攻关'
    elif not high_value and low_difficulty:
        return 'Q3-可填充'
    else:
        return 'Q4-暂缓'


def analyze_scenes(scenes):
    """进行四象限分析"""
    # 计算阈值（使用中位数作为分界点）
    value_scores = [s['value_score'] for s in scenes]
    difficulty_scores = [s['difficulty_score'] for s in scenes]

    value_scores_sorted = sorted(value_scores)
    difficulty_scores_sorted = sorted(difficulty_scores)

    n = len(scenes)
    value_median = value_scores_sorted[n // 2]
    difficulty_median = difficulty_scores_sorted[n // 2]

    # 统计信息
    value_min = min(value_scores)
    value_max = max(value_scores)
    value_avg = sum(value_scores) / n

    difficulty_min = min(difficulty_scores)
    difficulty_max = max(difficulty_scores)
    difficulty_avg = sum(difficulty_scores) / n

    stats = {
        'total_scenes': n,
        'value_score': {
            'min': round(value_min, 2),
            'max': round(value_max, 2),
            'avg': round(value_avg, 2),
            'median': round(value_median, 2)
        },
        'difficulty_score': {
            'min': round(difficulty_min, 2),
            'max': round(difficulty_max, 2),
            'avg': round(difficulty_avg, 2),
            'median': round(difficulty_median, 2)
        },
        'thresholds': {
            'value_threshold': round(value_median, 2),
            'difficulty_threshold': round(difficulty_median, 2)
        }
    }

    # 为每个场景分配象限
    for scene in scenes:
        scene['quadrant'] = classify_quadrant(
            scene['value_score'],
            scene['difficulty_score'],
            value_median,
            difficulty_median
        )

    # 按象限统计
    quadrant_stats = defaultdict(lambda: {
        'count': 0,
        'scenes': [],
        'industries': defaultdict(int)
    })

    for scene in scenes:
        q = scene['quadrant']
        quadrant_stats[q]['count'] += 1
        quadrant_stats[q]['scenes'].append(scene)
        quadrant_stats[q]['industries'][scene['source_major_name']] += 1

    return scenes, stats, dict(quadrant_stats)


def generate_outputs(scenes, stats, quadrant_stats):
    """生成输出文件"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. 全量场景四象限分类表
    output_all = OUTPUT_DIR / "01_scene_quadrant_full.csv"
    with open(output_all, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = [
            'quadrant', 'scene_name_zh', 'scene_name_en', 'industry_code',
            'source_major_code', 'source_major_name', 'process_step',
            'value_score', 'difficulty_score',
            'labor_urgency', 'scale_potential', 'superhuman_value',
            'operation_complexity', 'structure_level', 'fault_tolerance', 'takt_pressure',
            'l3_extracted', 'guide_generated'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        # 按象限排序（Q1优先）后输出
        sorted_scenes = sorted(scenes, key=lambda x: (x['quadrant'], -x['value_score'], x['difficulty_score']))
        for scene in sorted_scenes:
            writer.writerow(scene)
    print(f"已生成: {output_all.name} ({len(scenes)} 条)")

    # 2. Q1优先实施场景清单（高价值+低难度）
    q1_scenes = quadrant_stats.get('Q1-优先实施', {}).get('scenes', [])
    output_q1 = OUTPUT_DIR / "02_priority_scenes_Q1.csv"
    with open(output_q1, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = [
            'priority_rank', 'scene_name_zh', 'scene_name_en', 'industry_code',
            'source_major_name', 'process_step',
            'value_score', 'difficulty_score',
            'labor_urgency', 'scale_potential', 'superhuman_value',
            'operation_complexity', 'structure_level', 'fault_tolerance', 'takt_pressure',
            'priority_reason', 'l3_extracted', 'guide_generated'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        # 按 (value_score DESC, difficulty_score ASC) 排序
        sorted_q1 = sorted(q1_scenes, key=lambda x: (-x['value_score'], x['difficulty_score']))
        for i, scene in enumerate(sorted_q1, 1):
            scene['priority_rank'] = i
            # 生成优先原因
            reasons = []
            if scene['labor_urgency'] >= 4:
                reasons.append('用工痛点突出')
            if scene['scale_potential'] >= 4:
                reasons.append('规模潜力大')
            if scene['superhuman_value'] >= 4:
                reasons.append('超人价值高')
            if scene['operation_complexity'] <= 2:
                reasons.append('操作简单')
            if scene['structure_level'] >= 4:
                reasons.append('环境结构化')
            if scene['fault_tolerance'] >= 4:
                reasons.append('容错空间大')
            scene['priority_reason'] = '；'.join(reasons) if reasons else '综合评分优秀'
            writer.writerow(scene)
    print(f"已生成: {output_q1.name} ({len(q1_scenes)} 条)")

    # 3. 行业×象限分布矩阵
    industry_quadrant = defaultdict(lambda: {'Q1-优先实施': 0, 'Q2-重点攻关': 0, 'Q3-可填充': 0, 'Q4-暂缓': 0, 'total': 0})
    for scene in scenes:
        ind = scene['source_major_name']
        q = scene['quadrant']
        industry_quadrant[ind][q] += 1
        industry_quadrant[ind]['total'] += 1

    output_matrix = OUTPUT_DIR / "03_industry_quadrant_matrix.csv"
    with open(output_matrix, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = ['source_major_code', 'source_major_name', 'total',
                      'Q1-优先实施', 'Q1_pct', 'Q2-重点攻关', 'Q2_pct',
                      'Q3-可填充', 'Q3_pct', 'Q4-暂缓', 'Q4_pct',
                      'priority_index']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # 计算每个行业的优先指数 = (Q1 + 0.5*Q2) / total
        rows = []
        for ind, data in industry_quadrant.items():
            code = ''
            for s in scenes:
                if s['source_major_name'] == ind:
                    code = s['source_major_code']
                    break
            total = data['total']
            q1 = data['Q1-优先实施']
            q2 = data['Q2-重点攻关']
            q3 = data['Q3-可填充']
            q4 = data['Q4-暂缓']
            priority_index = round((q1 + 0.5 * q2) / total, 3) if total > 0 else 0

            rows.append({
                'source_major_code': code,
                'source_major_name': ind,
                'total': total,
                'Q1-优先实施': q1,
                'Q1_pct': f"{round(q1/total*100, 1)}%",
                'Q2-重点攻关': q2,
                'Q2_pct': f"{round(q2/total*100, 1)}%",
                'Q3-可填充': q3,
                'Q3_pct': f"{round(q3/total*100, 1)}%",
                'Q4-暂缓': q4,
                'Q4_pct': f"{round(q4/total*100, 1)}%",
                'priority_index': priority_index
            })

        # 按优先指数降序排列
        rows.sort(key=lambda x: -x['priority_index'])
        for row in rows:
            writer.writerow(row)
    print(f"已生成: {output_matrix.name} ({len(rows)} 个行业)")

    # 4. 四象限统计汇总
    output_summary = OUTPUT_DIR / "04_quadrant_summary.json"
    summary = {
        'analysis_date': '2026-06-10',
        'methodology': {
            'value_score_formula': '(labor_urgency + scale_potential + superhuman_value) / 3',
            'difficulty_score_formula': '(operation_complexity + (5-structure_level) + (5-fault_tolerance) + (5-takt_pressure)) / 4',
            'quadrant_logic': {
                'Q1-优先实施': '高价值(≥中位数) + 低难度(≤中位数)',
                'Q2-重点攻关': '高价值(≥中位数) + 高难度(>中位数)',
                'Q3-可填充': '低价值(<中位数) + 低难度(≤中位数)',
                'Q4-暂缓': '低价值(<中位数) + 高难度(>中位数)'
            }
        },
        'statistics': stats,
        'quadrant_distribution': {}
    }

    for q_name in ['Q1-优先实施', 'Q2-重点攻关', 'Q3-可填充', 'Q4-暂缓']:
        q_data = quadrant_stats.get(q_name, {'count': 0, 'industries': {}})
        # 行业分布Top5
        top_industries = sorted(q_data.get('industries', {}).items(), key=lambda x: -x[1])[:5]
        summary['quadrant_distribution'][q_name] = {
            'count': q_data['count'],
            'percentage': f"{round(q_data['count']/stats['total_scenes']*100, 1)}%",
            'top_industries': [{'name': k, 'count': v} for k, v in top_industries]
        }

    with open(output_summary, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"已生成: {output_summary.name}")

    # 5. 散点图数据（供可视化使用）
    output_scatter = OUTPUT_DIR / "05_scatter_plot_data.json"
    scatter_data = {
        'thresholds': stats['thresholds'],
        'points': []
    }
    for scene in scenes:
        scatter_data['points'].append({
            'x': scene['difficulty_score'],
            'y': scene['value_score'],
            'name': scene['scene_name_zh'],
            'industry': scene['source_major_name'],
            'industry_code': scene['source_major_code'],
            'quadrant': scene['quadrant']
        })
    with open(output_scatter, 'w', encoding='utf-8') as f:
        json.dump(scatter_data, f, ensure_ascii=False, indent=2)
    print(f"已生成: {output_scatter.name}")

    # 6. 各象限Top20场景
    output_top = OUTPUT_DIR / "06_quadrant_top20.csv"
    with open(output_top, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = ['quadrant', 'rank', 'scene_name_zh', 'source_major_name',
                      'value_score', 'difficulty_score', 'highlight']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for q_name in ['Q1-优先实施', 'Q2-重点攻关', 'Q3-可填充', 'Q4-暂缓']:
            q_scenes = quadrant_stats.get(q_name, {}).get('scenes', [])
            if q_name == 'Q1-优先实施':
                sorted_q = sorted(q_scenes, key=lambda x: (-x['value_score'], x['difficulty_score']))
                highlight_logic = '价值最高、难度最低'
            elif q_name == 'Q2-重点攻关':
                sorted_q = sorted(q_scenes, key=lambda x: (-x['value_score'], -x['difficulty_score']))
                highlight_logic = '价值高但难度大'
            elif q_name == 'Q3-可填充':
                sorted_q = sorted(q_scenes, key=lambda x: (x['difficulty_score'], -x['value_score']))
                highlight_logic = '难度低可快速落地'
            else:
                sorted_q = sorted(q_scenes, key=lambda x: (x['value_score'], x['difficulty_score']))
                highlight_logic = '价值低且难度高'

            for i, scene in enumerate(sorted_q[:20], 1):
                writer.writerow({
                    'quadrant': q_name,
                    'rank': i,
                    'scene_name_zh': scene['scene_name_zh'],
                    'source_major_name': scene['source_major_name'],
                    'value_score': scene['value_score'],
                    'difficulty_score': scene['difficulty_score'],
                    'highlight': highlight_logic
                })
    print(f"已生成: {output_top.name}")

    # 7. 行业优先级排名
    output_industry_rank = OUTPUT_DIR / "07_industry_priority_ranking.csv"
    with open(output_industry_rank, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = ['rank', 'source_major_code', 'source_major_name',
                      'total_scenes', 'q1_count', 'q1_ratio',
                      'avg_value_score', 'avg_difficulty_score',
                      'priority_index', 'recommendation']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # 按行业聚合
        industry_agg = defaultdict(lambda: {
            'scenes': [], 'q1_count': 0, 'value_sum': 0, 'difficulty_sum': 0
        })
        for scene in scenes:
            ind = scene['source_major_name']
            industry_agg[ind]['scenes'].append(scene)
            if scene['quadrant'] == 'Q1-优先实施':
                industry_agg[ind]['q1_count'] += 1
            industry_agg[ind]['value_sum'] += scene['value_score']
            industry_agg[ind]['difficulty_sum'] += scene['difficulty_score']

        rows = []
        for ind, data in industry_agg.items():
            n = len(data['scenes'])
            code = data['scenes'][0]['source_major_code'] if data['scenes'] else ''
            avg_v = round(data['value_sum'] / n, 2)
            avg_d = round(data['difficulty_sum'] / n, 2)
            q1_ratio = round(data['q1_count'] / n * 100, 1)
            # 优先指数 = Q1占比 * 平均价值分 / 平均难度分
            priority_idx = round(q1_ratio * avg_v / max(avg_d, 0.1), 2)

            # 推荐等级
            if q1_ratio >= 30 and avg_v >= 3.5:
                rec = '强烈推荐'
            elif q1_ratio >= 20 or avg_v >= 3.3:
                rec = '推荐'
            elif q1_ratio >= 10:
                rec = '可考虑'
            else:
                rec = '暂缓'

            rows.append({
                'source_major_code': code,
                'source_major_name': ind,
                'total_scenes': n,
                'q1_count': data['q1_count'],
                'q1_ratio': f"{q1_ratio}%",
                'avg_value_score': avg_v,
                'avg_difficulty_score': avg_d,
                'priority_index': priority_idx,
                'recommendation': rec
            })

        rows.sort(key=lambda x: -x['priority_index'])
        for i, row in enumerate(rows, 1):
            row['rank'] = i
            writer.writerow(row)
    print(f"已生成: {output_industry_rank.name}")

    return stats


def main():
    print("=" * 60)
    print("场景优先级四象限分析")
    print("=" * 60)

    print("\n[1/4] 加载场景数据...")
    scenes = load_scenes()
    print(f"  成功加载 {len(scenes)} 个场景")

    print("\n[2/4] 计算综合分数并分类...")
    scenes, stats, quadrant_stats = analyze_scenes(scenes)
    print(f"  价值分范围: {stats['value_score']['min']} ~ {stats['value_score']['max']}")
    print(f"  价值分中位数: {stats['value_score']['median']}")
    print(f"  难度分范围: {stats['difficulty_score']['min']} ~ {stats['difficulty_score']['max']}")
    print(f"  难度分中位数: {stats['difficulty_score']['median']}")

    print("\n[3/4] 四象限分布:")
    for q in ['Q1-优先实施', 'Q2-重点攻关', 'Q3-可填充', 'Q4-暂缓']:
        count = quadrant_stats.get(q, {}).get('count', 0)
        pct = round(count / len(scenes) * 100, 1)
        print(f"  {q}: {count} 个场景 ({pct}%)")

    print("\n[4/4] 生成输出文件...")
    generate_outputs(scenes, stats, quadrant_stats)

    print("\n" + "=" * 60)
    print("分析完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
