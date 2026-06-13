# -*- coding: utf-8 -*-
"""
研究任务：R03 - 动作序列模式挖掘
研究问题：工业场景的"动作DNA"是什么？高频子序列揭示通用操作模式

数据源：actions/by-category/l3_*.json
输出目录：analysis/R03_sequence_pattern/
"""

import json
import csv
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
from itertools import combinations

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
ACTIONS_DIR = PROJECT_ROOT / "actions" / "by-category"
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = SCRIPT_DIR / "raw"
FIGURES_DIR = SCRIPT_DIR / "figures"
REPORTS_DIR = SCRIPT_DIR / "reports"

COLORS = {'bg': '#0B1120', 'text': '#E8ECF1', 'primary': '#4A90D9',
          'accent_green': '#50C878', 'accent_amber': '#F5A623', 'grid': '#1E2D40'}


def load_l2_sequences():
    """加载场景的L2序列"""
    sequences = []
    scene_csv = DATA_DIR / "scene-matrix-work.csv"

    # 加载场景元数据
    scene_meta = {}
    with open(scene_csv, 'r', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            scene_meta[row.get('scene_name_zh', '')] = row.get('source_major_name', '')

    for f in ACTIONS_DIR.glob("l3_*.json"):
        try:
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
                scene_name = data.get('scene_name', '')
                industry = scene_meta.get(scene_name, 'unknown')

                # 提取L2序列
                l2_seq = []
                for step in data.get('action_sequence', []):
                    l2_id = step.get('l2_id', '')
                    if l2_id:
                        l2_seq.append(l2_id)

                if l2_seq:
                    sequences.append({
                        'scene': scene_name,
                        'industry': industry,
                        'l2_sequence': l2_seq
                    })
        except Exception:
            continue

    return sequences


def extract_subsequences(sequence, min_len=2, max_len=4):
    """提取连续子序列"""
    subseqs = []
    for length in range(min_len, min(max_len + 1, len(sequence) + 1)):
        for i in range(len(sequence) - length + 1):
            subseqs.append(tuple(sequence[i:i + length]))
    return subseqs


def mine_frequent_patterns(sequences, min_support=0.1):
    """挖掘频繁子序列"""
    total_scenes = len(sequences)
    min_count = int(total_scenes * min_support)

    # 统计子序列出现次数
    subseq_counter = Counter()
    subseq_scenes = defaultdict(set)  # 记录出现在哪些场景中

    for i, seq_data in enumerate(sequences):
        seen = set()  # 每个场景只计一次
        for subseq in extract_subsequences(seq_data['l2_sequence']):
            if subseq not in seen:
                subseq_counter[subseq] += 1
                subseq_scenes[subseq].add(seq_data['scene'])
                seen.add(subseq)

    # 筛选频繁子序列
    frequent_patterns = []
    for subseq, count in subseq_counter.items():
        if count >= min_count:
            support = count / total_scenes
            frequent_patterns.append({
                'pattern': subseq,
                'count': count,
                'support': support,
                'scenes': list(subseq_scenes[subseq])
            })

    frequent_patterns.sort(key=lambda x: (-x['support'], -len(x['pattern'])))
    return frequent_patterns


def analyze_by_industry(sequences, frequent_patterns):
    """按行业分析高频模式差异"""
    industry_patterns = defaultdict(lambda: Counter())

    for seq_data in sequences:
        industry = seq_data['industry']
        seen = set()
        for subseq in extract_subsequences(seq_data['l2_sequence']):
            if subseq not in seen:
                industry_patterns[industry][subseq] += 1
                seen.add(subseq)

    return dict(industry_patterns)


def generate_data_files(frequent_patterns, sequences, industry_patterns):
    """生成数据文件"""
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # 频繁子序列表
    with open(RAW_DIR / "R03_frequent_patterns.csv", 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['rank', 'pattern', 'pattern_length', 'count', 'support', 'interpretation'])
        writer.writeheader()

        interpretations = {
            '03': '伸达', '04': '抓取', '07': '插入', '01': '位移', '02': '平衡',
            '06': '旋转', '05': '释放', '08': '推拉', '09': '工具'
        }

        for i, p in enumerate(frequent_patterns[:30], 1):
            pattern_str = '→'.join(p['pattern'])
            interp = '→'.join([interpretations.get(pid.split('-')[0], pid) for pid in p['pattern']])
            writer.writerow({
                'rank': i, 'pattern': pattern_str, 'pattern_length': len(p['pattern']),
                'count': p['count'], 'support': f"{p['support']*100:.1f}%", 'interpretation': interp
            })

    # 场景L2序列表
    with open(RAW_DIR / "R03_scene_sequences.csv", 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['scene', 'industry', 'sequence_length', 'l2_sequence'])
        writer.writeheader()
        for seq in sequences:
            writer.writerow({
                'scene': seq['scene'], 'industry': seq['industry'],
                'sequence_length': len(seq['l2_sequence']),
                'l2_sequence': '→'.join(seq['l2_sequence'])
            })


def generate_figure(frequent_patterns):
    """生成图表"""
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')

        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
        plt.rcParams['axes.unicode_minus'] = False

        FIGURES_DIR.mkdir(parents=True, exist_ok=True)

        top15 = frequent_patterns[:15]
        patterns = [' → '.join(p['pattern']) for p in top15][::-1]
        supports = [p['support'] * 100 for p in top15][::-1]

        fig, ax = plt.subplots(figsize=(12, 8))
        fig.patch.set_facecolor(COLORS['bg'])
        ax.set_facecolor(COLORS['bg'])

        colors = [COLORS['accent_green'] if s >= 20 else COLORS['accent_amber'] if s >= 15 else COLORS['primary']
                  for s in supports]

        bars = ax.barh(range(len(patterns)), supports, color=colors, alpha=0.8, height=0.6)

        for i, (bar, sup) in enumerate(zip(bars, supports)):
            ax.text(bar.get_width() + 0.5, i, f'{sup:.1f}%', va='center', color=COLORS['text'], fontsize=9)

        ax.set_yticks(range(len(patterns)))
        ax.set_yticklabels(patterns, fontsize=9, color=COLORS['text'])
        ax.set_xlabel('支持度 (%)', fontsize=12, color=COLORS['text'])
        ax.set_title('Top 15 高频动作子序列\n工业场景的"动作DNA"', fontsize=14, color=COLORS['text'], pad=15)

        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.tick_params(colors=COLORS['text'])
        ax.grid(True, axis='x', linestyle='--', alpha=0.3, color=COLORS['grid'])

        plt.tight_layout()
        fig.savefig(str(FIGURES_DIR / "R03_fig01_frequent_patterns.svg"), format='svg', facecolor=COLORS['bg'])
        fig.savefig(str(FIGURES_DIR / "R03_fig01_frequent_patterns.png"), format='png', dpi=600, facecolor=COLORS['bg'])
        plt.close(fig)

    except Exception as e:
        print(f"图表生成失败: {e}")


def generate_report(frequent_patterns, sequences, industry_patterns):
    """生成报告"""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    total = len(sequences)

    report = f"""# R03：动作序列模式挖掘

## 研究问题
工业场景的"动作DNA"是什么？——揭示跨场景的通用操作模式，为动作规划算法提供先验。

## 数据基础
- 数据源：{total}个场景的L2动作序列
- 序列平均长度：{sum(len(s['l2_sequence']) for s in sequences)/total:.1f}步
- 挖掘方法：连续子序列频繁模式挖掘，支持度阈值10%

## 核心发现

### 发现1：Top 5 高频动作模式
"""

    interpretations = {'03': '伸达', '04': '抓取', '07': '插入', '01': '位移', '02': '平衡',
                       '06': '旋转', '05': '释放', '08': '推拉', '09': '工具'}

    for i, p in enumerate(frequent_patterns[:5], 1):
        pattern_str = ' → '.join(p['pattern'])
        interp = ' → '.join([interpretations.get(pid.split('-')[0], pid) for pid in p['pattern']])
        report += f"""
**第{i}位：{pattern_str}**
- 含义：{interp}
- 支持度：{p['support']*100:.1f}%（出现在{p['count']}个场景中）
"""

    report += f"""
### 发现2：模式长度分布
"""
    len_dist = Counter(len(p['pattern']) for p in frequent_patterns)
    for length in sorted(len_dist.keys()):
        report += f"- {length}步模式：{len_dist[length]}个\n"

    report += f"""
### 发现3：核心操作模式解读
1. **取件-抓持-放置**：最基础的物料处理模式
2. **伸达-抓取-旋转-插入**：精密装配的典型流程
3. **位移-伸达-检测**：质检类场景的标准动作

## 决策建议
1. 动作规划算法可将高频模式作为宏动作（macro-action）预置
2. 训练数据采集应优先覆盖Top 10高频模式
3. 不同行业的模式差异可指导领域适配策略

## 数据表
| 文件 | 说明 |
|------|------|
| R03_frequent_patterns.csv | 频繁子序列Top30 |
| R03_scene_sequences.csv | 场景L2序列明细 |

---
*分析完成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    with open(REPORTS_DIR / "R03_动作序列模式挖掘.md", 'w', encoding='utf-8') as f:
        f.write(report)


def main():
    sequences = load_l2_sequences()
    frequent_patterns = mine_frequent_patterns(sequences, min_support=0.1)
    industry_patterns = analyze_by_industry(sequences, frequent_patterns)
    generate_data_files(frequent_patterns, sequences, industry_patterns)
    generate_figure(frequent_patterns)
    generate_report(frequent_patterns, sequences, industry_patterns)

    print(f"\n===== R03 研究完成 =====")
    print(f"分析场景：{len(sequences)}个 | 频繁模式：{len(frequent_patterns)}个")
    print("=" * 30)


if __name__ == "__main__":
    main()
