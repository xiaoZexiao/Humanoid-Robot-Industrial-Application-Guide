# 元动作库总览

## 概述

本元动作库是人形机器人工业应用的标准化动作分类体系，采用三级层次结构组织。

## 统计数据

| 层级 | 数量 | 说明 |
|------|------|------|
| L1 大类 | 9 | 基于运动学本质划分 |
| L2 中类 | 65 | 基于操作特征细分 |
| L3 实例 | 122+ | 具体场景的原子动作 |

### L2 覆盖情况

- 已覆盖 L2：57/65 (87.7%)
- 待补充 L2：8 个

## L1 大类分布

| L1 编号 | 名称 | L2 数量 | L3 数量 |
|---------|------|---------|---------|
| L1-01 | 全身位移 | 8 | 15 |
| L1-02 | 躯体姿态调整 | 7 | 13 |
| L1-03 | 上肢空间运动 | 8 | 20 |
| L1-04 | 手部抓握操控 | 7 | 18 |
| L1-05 | 线性力施加 | 7 | 12 |
| L1-06 | 旋转操作 | 7 | 9 |
| L1-07 | 约束路径操作 | 7 | 13 |
| L1-08 | 表面随形运动 | 7 | 8 |
| L1-09 | 感知定位运动 | 7 | 14 |

## 数据文件

### 完整库

- **JSON 格式**：`action-library.json`
- 包含全部 L3 定义和参数

### 按场景提取

- **目录**：`by-category/`
- 每个已处理场景一个 JSON 文件
- 包含动作序列和新增 L3 定义

## 数据结构

### action-library.json

```json
{
  "version": "1.0",
  "updated_at": "2026-06-09 10:00:00",
  "statistics": {
    "l3_count": 122
  },
  "actions": [
    {
      "l3_id": "L3-04-01-001",
      "l3_name_zh": "抓取-袋装物料-双手对握",
      "l3_name_en": "Grasp-BaggedMaterial-TwoHandSymmetric",
      "parent_l2_id": "L2-04-01",
      "description": "双手从两侧对称抓握袋装物料",
      "object_category": "袋装物料",
      "parameter_ranges": {
        "weight_range": "20-30kg",
        "size_range": "400x300x200mm"
      },
      "source_scene": "搬运码垛-精矿成品-25kg袋装",
      "is_new": true
    }
  ]
}
```

### 场景提取文件

```json
{
  "scene_id": "09-91-00",
  "scene_name": "搬运码垛-精矿成品-25kg袋装",
  "total_steps": 15,
  "action_sequence": [
    {
      "step_order": 1,
      "human_description": "从待码垛区走向物料堆放处",
      "l1_id": "L1-01",
      "l2_id": "L2-01-01",
      "l3_id": "L3-01-01-001",
      "is_new_l3": false
    }
  ],
  "new_l3_definitions": [],
  "l2_usage_summary": {
    "涉及的L2编号列表": ["L2-01-01", "L2-04-01"],
    "最高频L2": "L2-04-01",
    "涉及的L1数量": 5
  }
}
```

## 使用方式

### 查询特定 L2 下的所有 L3

```python
import json

with open('action-library.json', 'r', encoding='utf-8') as f:
    library = json.load(f)

l2_id = 'L2-04-01'
actions = [a for a in library['actions'] if a['parent_l2_id'] == l2_id]
```

### 统计 L3 来源场景

```python
from collections import Counter

scenes = Counter(a['source_scene'] for a in library['actions'])
print(scenes.most_common(10))
```

## 更新记录

- 2026-06-09：L3 数量达到 122
- 持续更新中...

## 相关文档

- [元动作分类体系](../framework/action-taxonomy.md)
- [高复用动作分析](../analysis/high-reuse-actions.md)
- [场景建设指南](../guides/)
