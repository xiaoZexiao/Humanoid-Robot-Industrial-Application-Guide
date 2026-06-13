# -*- coding: utf-8 -*-
"""
工序环节价值密度分析脚本
最开始的一次的脚本
按process_step字段分组，计算每个工序环节的场景数量和7维评分均值
产出：工序价值密度排行
"""

import csv
import json
import re
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent

# 输入输出文件
INPUT_CSV = PROJECT_ROOT / "data" / "scene-matrix-work.csv"
OUTPUT_DIR = SCRIPT_DIR / "process-value-analysis"


def load_scenes():
    """加载全部场景数据"""
    scenes = []
    with open(INPUT_CSV, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
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

            # 计算综合分数
            value_score = (labor_urgency + scale_potential + superhuman_value) / 3
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
                'industry_chain': row.get('industry_chain', ''),
                'process_step': row.get('process_step', '').strip(),
                'source_major_code': row.get('source_major_code', ''),
                'source_major_name': row.get('source_major_name', ''),
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


def normalize_process_step(step):
    """标准化工序名称"""
    step = step.strip()
    # 处理一些常见的变体
    mapping = {
        '原料验收': '原料入库',
        '成品入库': '成品出库',
        '定期巡检': '设备巡检',
        '设备维护': '设备巡检',
        '安全监控': '安全巡检',
    }
    return mapping.get(step, step)


def categorize_process_step(step):
    """将工序归类到大类"""
    step_lower = step.lower()

    # 仓储物流类
    if any(k in step for k in ['入库', '出库', '仓储', '储运', '储存', '搬运', '转运', '配送']):
        return '仓储物流'

    # 原料处理类
    if any(k in step for k in ['原料', '备料', '预处理', '破碎', '粉碎', '筛分', '配料', '投料', '上料']):
        return '原料处理'

    # 加工制造类
    if any(k in step for k in ['加工', '制造', '生产', '成型', '压制', '冲压', '铸造', '锻造', '切削',
                               '焊接', '装配', '组装', '制丝', '纺纱', '织造', '染色', '印花', '热处理',
                               '熔炼', '精炼', '电解', '反应', '聚合', '合成', '蒸馏', '萃取', '烧成',
                               '煅烧', '窑', '炉']):
        return '加工制造'

    # 检测质控类
    if any(k in step for k in ['检测', '检验', '质检', '测试', '测量', '抽检', '品控', '质控']):
        return '检测质控'

    # 巡检维护类
    if any(k in step for k in ['巡检', '巡视', '巡查', '维护', '保养', '维修', '监测', '监控']):
        return '巡检维护'

    # 包装成品类
    if any(k in step for k in ['包装', '打包', '封装', '装箱', '码垛', '贴标']):
        return '包装成品'

    # 环保安全类
    if any(k in step for k in ['安全', '环保', '废水', '废气', '除尘', '脱硫', '脱硝', '尾矿']):
        return '环保安全'

    return '其他工序'


def analyze_by_process_step(scenes):
    """按工序环节分组分析"""
    process_groups = defaultdict(lambda: {
        'scenes': [],
        'labor_urgency_sum': 0,
        'scale_potential_sum': 0,
        'superhuman_value_sum': 0,
        'operation_complexity_sum': 0,
        'structure_level_sum': 0,
        'fault_tolerance_sum': 0,
        'takt_pressure_sum': 0,
        'value_score_sum': 0,
        'difficulty_score_sum': 0,
        'industries': defaultdict(int)
    })

    for scene in scenes:
        step = scene['process_step']
        if not step:
            step = '未分类'

        process_groups[step]['scenes'].append(scene)
        process_groups[step]['labor_urgency_sum'] += scene['labor_urgency']
        process_groups[step]['scale_potential_sum'] += scene['scale_potential']
        process_groups[step]['superhuman_value_sum'] += scene['superhuman_value']
        process_groups[step]['operation_complexity_sum'] += scene['operation_complexity']
        process_groups[step]['structure_level_sum'] += scene['structure_level']
        process_groups[step]['fault_tolerance_sum'] += scene['fault_tolerance']
        process_groups[step]['takt_pressure_sum'] += scene['takt_pressure']
        process_groups[step]['value_score_sum'] += scene['value_score']
        process_groups[step]['difficulty_score_sum'] += scene['difficulty_score']
        process_groups[step]['industries'][scene['source_major_name']] += 1

    # 计算统计值
    results = []
    for step, data in process_groups.items():
        n = len(data['scenes'])
        if n == 0:
            continue

        avg_labor_urgency = round(data['labor_urgency_sum'] / n, 2)
        avg_scale_potential = round(data['scale_potential_sum'] / n, 2)
        avg_superhuman_value = round(data['superhuman_value_sum'] / n, 2)
        avg_operation_complexity = round(data['operation_complexity_sum'] / n, 2)
        avg_structure_level = round(data['structure_level_sum'] / n, 2)
        avg_fault_tolerance = round(data['fault_tolerance_sum'] / n, 2)
        avg_takt_pressure = round(data['takt_pressure_sum'] / n, 2)
        avg_value_score = round(data['value_score_sum'] / n, 2)
        avg_difficulty_score = round(data['difficulty_score_sum'] / n, 2)

        # 价值密度 = 场景数量 × 平均价值分
        value_density = round(n * avg_value_score, 2)

        # 介入收益比 = 价值密度 / 平均难度分
        intervention_roi = round(value_density / max(avg_difficulty_score, 0.1), 2)

        # 工序大类
        category = categorize_process_step(step)

        # 覆盖行业数量
        industry_count = len(data['industries'])
        top_industries = sorted(data['industries'].items(), key=lambda x: -x[1])[:3]

        results.append({
            'process_step': step,
            'category': category,
            'scene_count': n,
            'industry_count': industry_count,
            'top_industries': top_industries,
            'avg_labor_urgency': avg_labor_urgency,
            'avg_scale_potential': avg_scale_potential,
            'avg_superhuman_value': avg_superhuman_value,
            'avg_operation_complexity': avg_operation_complexity,
            'avg_structure_level': avg_structure_level,
            'avg_fault_tolerance': avg_fault_tolerance,
            'avg_takt_pressure': avg_takt_pressure,
            'avg_value_score': avg_value_score,
            'avg_difficulty_score': avg_difficulty_score,
            'value_density': value_density,
            'intervention_roi': intervention_roi,
            'scenes': data['scenes']
        })

    return results


def analyze_by_category(process_results):
    """按工序大类汇总"""
    category_groups = defaultdict(lambda: {
        'process_steps': [],
        'scene_count': 0,
        'value_sum': 0,
        'difficulty_sum': 0,
        'industries': set()
    })

    for r in process_results:
        cat = r['category']
        category_groups[cat]['process_steps'].append(r['process_step'])
        category_groups[cat]['scene_count'] += r['scene_count']
        category_groups[cat]['value_sum'] += r['avg_value_score'] * r['scene_count']
        category_groups[cat]['difficulty_sum'] += r['avg_difficulty_score'] * r['scene_count']
        for ind, _ in r['top_industries']:
            category_groups[cat]['industries'].add(ind)

    results = []
    for cat, data in category_groups.items():
        n = data['scene_count']
        if n == 0:
            continue
        avg_value = round(data['value_sum'] / n, 2)
        avg_difficulty = round(data['difficulty_sum'] / n, 2)
        value_density = round(n * avg_value, 2)
        roi = round(value_density / max(avg_difficulty, 0.1), 2)

        results.append({
            'category': cat,
            'process_step_count': len(data['process_steps']),
            'scene_count': n,
            'industry_count': len(data['industries']),
            'avg_value_score': avg_value,
            'avg_difficulty_score': avg_difficulty,
            'value_density': value_density,
            'intervention_roi': roi,
            'process_steps': data['process_steps']
        })

    return sorted(results, key=lambda x: -x['value_density'])


def generate_outputs(scenes, process_results, category_results):
    """生成输出文件"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. 工序环节价值密度排行（核心表）
    output_density = OUTPUT_DIR / "01_process_value_density_ranking.csv"
    sorted_by_density = sorted(process_results, key=lambda x: -x['value_density'])

    with open(output_density, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = [
            'rank', 'process_step', 'category', 'scene_count', 'industry_count',
            'avg_value_score', 'avg_difficulty_score', 'value_density', 'intervention_roi',
            'avg_labor_urgency', 'avg_scale_potential', 'avg_superhuman_value',
            'avg_operation_complexity', 'avg_structure_level', 'avg_fault_tolerance', 'avg_takt_pressure',
            'top_industries', 'recommendation'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()

        for i, r in enumerate(sorted_by_density, 1):
            # 推荐等级
            if r['value_density'] >= 100 and r['avg_difficulty_score'] <= 1.5:
                rec = '强烈推荐'
            elif r['value_density'] >= 50 and r['avg_difficulty_score'] <= 2.0:
                rec = '推荐'
            elif r['value_density'] >= 20:
                rec = '可考虑'
            else:
                rec = '待观察'

            writer.writerow({
                'rank': i,
                'process_step': r['process_step'],
                'category': r['category'],
                'scene_count': r['scene_count'],
                'industry_count': r['industry_count'],
                'avg_value_score': r['avg_value_score'],
                'avg_difficulty_score': r['avg_difficulty_score'],
                'value_density': r['value_density'],
                'intervention_roi': r['intervention_roi'],
                'avg_labor_urgency': r['avg_labor_urgency'],
                'avg_scale_potential': r['avg_scale_potential'],
                'avg_superhuman_value': r['avg_superhuman_value'],
                'avg_operation_complexity': r['avg_operation_complexity'],
                'avg_structure_level': r['avg_structure_level'],
                'avg_fault_tolerance': r['avg_fault_tolerance'],
                'avg_takt_pressure': r['avg_takt_pressure'],
                'top_industries': '；'.join([f"{ind}({cnt})" for ind, cnt in r['top_industries']]),
                'recommendation': rec
            })
    print(f"已生成: {output_density.name} ({len(sorted_by_density)} 条)")

    # 2. 工序大类汇总表
    output_category = OUTPUT_DIR / "02_process_category_summary.csv"
    with open(output_category, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = [
            'rank', 'category', 'process_step_count', 'scene_count', 'industry_count',
            'avg_value_score', 'avg_difficulty_score', 'value_density', 'intervention_roi',
            'recommendation'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i, r in enumerate(category_results, 1):
            if r['value_density'] >= 300 and r['avg_difficulty_score'] <= 1.6:
                rec = '核心战场'
            elif r['value_density'] >= 150:
                rec = '重点布局'
            elif r['value_density'] >= 50:
                rec = '选择性进入'
            else:
                rec = '观望'

            writer.writerow({
                'rank': i,
                'category': r['category'],
                'process_step_count': r['process_step_count'],
                'scene_count': r['scene_count'],
                'industry_count': r['industry_count'],
                'avg_value_score': r['avg_value_score'],
                'avg_difficulty_score': r['avg_difficulty_score'],
                'value_density': r['value_density'],
                'intervention_roi': r['intervention_roi'],
                'recommendation': rec
            })
    print(f"已生成: {output_category.name} ({len(category_results)} 条)")

    # 3. 工序×行业交叉分析表
    output_cross = OUTPUT_DIR / "03_process_industry_cross.csv"
    process_industry = defaultdict(lambda: defaultdict(int))
    for scene in scenes:
        step = scene['process_step'] or '未分类'
        ind = scene['source_major_name']
        process_industry[step][ind] += 1

    # 获取所有行业列表（按总数排序）
    industry_totals = defaultdict(int)
    for step, inds in process_industry.items():
        for ind, cnt in inds.items():
            industry_totals[ind] += cnt
    top_industries = [ind for ind, _ in sorted(industry_totals.items(), key=lambda x: -x[1])[:15]]

    with open(output_cross, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = ['process_step', 'total'] + top_industries
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for step, inds in sorted(process_industry.items(), key=lambda x: -sum(x[1].values())):
            row = {'process_step': step, 'total': sum(inds.values())}
            for ind in top_industries:
                row[ind] = inds.get(ind, 0)
            writer.writerow(row)
    print(f"已生成: {output_cross.name}")

    # 4. 工序环节7维雷达图数据
    output_radar = OUTPUT_DIR / "04_process_radar_data.json"
    radar_data = []
    for r in sorted_by_density[:20]:  # Top20工序
        radar_data.append({
            'process_step': r['process_step'],
            'category': r['category'],
            'scene_count': r['scene_count'],
            'value_density': r['value_density'],
            'dimensions': {
                'labor_urgency': r['avg_labor_urgency'],
                'scale_potential': r['avg_scale_potential'],
                'superhuman_value': r['avg_superhuman_value'],
                'operation_complexity': r['avg_operation_complexity'],
                'structure_level': r['avg_structure_level'],
                'fault_tolerance': r['avg_fault_tolerance'],
                'takt_pressure': r['avg_takt_pressure']
            }
        })
    with open(output_radar, 'w', encoding='utf-8') as f:
        json.dump(radar_data, f, ensure_ascii=False, indent=2)
    print(f"已生成: {output_radar.name}")

    # 5. Top工序下的具体场景清单
    output_scenes = OUTPUT_DIR / "05_top_process_scenes.csv"
    with open(output_scenes, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = [
            'process_step', 'process_rank', 'scene_name_zh', 'source_major_name',
            'value_score', 'difficulty_score', 'labor_urgency', 'scale_potential', 'superhuman_value'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i, r in enumerate(sorted_by_density[:15], 1):  # Top15工序
            # 按价值分排序该工序下的场景
            step_scenes = sorted(r['scenes'], key=lambda x: (-x['value_score'], x['difficulty_score']))
            for scene in step_scenes[:10]:  # 每个工序最多10个场景
                writer.writerow({
                    'process_step': r['process_step'],
                    'process_rank': i,
                    'scene_name_zh': scene['scene_name_zh'],
                    'source_major_name': scene['source_major_name'],
                    'value_score': scene['value_score'],
                    'difficulty_score': scene['difficulty_score'],
                    'labor_urgency': scene['labor_urgency'],
                    'scale_potential': scene['scale_potential'],
                    'superhuman_value': scene['superhuman_value']
                })
    print(f"已生成: {output_scenes.name}")

    # 6. 工序介入收益比排行（价值密度/难度）
    output_roi = OUTPUT_DIR / "06_process_intervention_roi.csv"
    sorted_by_roi = sorted(process_results, key=lambda x: -x['intervention_roi'])

    with open(output_roi, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = [
            'rank', 'process_step', 'category', 'scene_count',
            'intervention_roi', 'value_density', 'avg_difficulty_score',
            'insight'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()

        for i, r in enumerate(sorted_by_roi, 1):
            # 生成洞察
            if r['intervention_roi'] > 100 and r['avg_difficulty_score'] < 1.0:
                insight = '极易切入，投入产出比最优'
            elif r['intervention_roi'] > 50:
                insight = '收益显著，值得优先布局'
            elif r['intervention_roi'] > 20 and r['avg_difficulty_score'] < 1.5:
                insight = '难度低，适合快速复制'
            elif r['scene_count'] >= 30:
                insight = '规模大，可逐步渗透'
            else:
                insight = '需评估具体场景'

            writer.writerow({
                'rank': i,
                'process_step': r['process_step'],
                'category': r['category'],
                'scene_count': r['scene_count'],
                'intervention_roi': r['intervention_roi'],
                'value_density': r['value_density'],
                'avg_difficulty_score': r['avg_difficulty_score'],
                'insight': insight
            })
    print(f"已生成: {output_roi.name}")

    # 7. 分析汇总报告数据
    output_summary = OUTPUT_DIR / "07_analysis_summary.json"
    summary = {
        'analysis_date': '2026-06-10',
        'total_scenes': len(scenes),
        'unique_process_steps': len(process_results),
        'process_categories': len(category_results),
        'methodology': {
            'value_score_formula': '(labor_urgency + scale_potential + superhuman_value) / 3',
            'difficulty_score_formula': '(operation_complexity + (5-structure_level) + (5-fault_tolerance) + (5-takt_pressure)) / 4',
            'value_density_formula': 'scene_count × avg_value_score',
            'intervention_roi_formula': 'value_density / avg_difficulty_score'
        },
        'top10_by_density': [
            {
                'rank': i + 1,
                'process_step': r['process_step'],
                'scene_count': r['scene_count'],
                'value_density': r['value_density']
            }
            for i, r in enumerate(sorted_by_density[:10])
        ],
        'category_ranking': [
            {
                'category': r['category'],
                'scene_count': r['scene_count'],
                'value_density': r['value_density']
            }
            for r in category_results
        ]
    }
    with open(output_summary, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"已生成: {output_summary.name}")

    return sorted_by_density, category_results


def main():
    print("=" * 60)
    print("工序环节价值密度分析")
    print("=" * 60)

    print("\n[1/4] 加载场景数据...")
    scenes = load_scenes()
    print(f"  成功加载 {len(scenes)} 个场景")

    print("\n[2/4] 按工序环节分组分析...")
    process_results = analyze_by_process_step(scenes)
    print(f"  发现 {len(process_results)} 个不同工序环节")

    print("\n[3/4] 按工序大类汇总...")
    category_results = analyze_by_category(process_results)
    print(f"  归纳为 {len(category_results)} 个工序大类")

    print("\n[4/4] 生成输出文件...")
    sorted_by_density, _ = generate_outputs(scenes, process_results, category_results)

    # 显示Top10
    print("\n" + "-" * 60)
    print("工序价值密度 Top 10：")
    print("-" * 60)
    print(f"{'排名':<4} {'工序环节':<20} {'场景数':<8} {'价值密度':<10} {'难度分':<8}")
    print("-" * 60)
    for i, r in enumerate(sorted_by_density[:10], 1):
        print(f"{i:<4} {r['process_step']:<20} {r['scene_count']:<8} {r['value_density']:<10} {r['avg_difficulty_score']:<8}")

    print("\n" + "=" * 60)
    print("分析完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
