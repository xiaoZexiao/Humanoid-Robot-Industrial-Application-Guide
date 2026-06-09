# 标准字段定义文档

## 概述

本文档定义场景数据和元动作库中使用的所有标准字段，确保数据的一致性和可解析性。

---

## 场景字段定义

### 基本信息字段

| 字段 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| scene_name_zh | string | 是 | 中文名称（三段式） | 搬运码垛-精矿成品-25kg袋装 |
| scene_name_en | string | 是 | 英文名称 | Palletizing-ConcentrateProduct-25kgBagged |
| industry_code | string | 是 | 国标行业代码 | 09-91-00 |
| source_major_code | string | 是 | 大类代码 | 09 |
| source_major_name | string | 是 | 大类名称 | 有色金属矿采选业 |
| industry_chain | string | 是 | 行业工序链 | 采矿→选矿→脱水→包装→出库 |
| process_step | string | 是 | 所属工序 | 包装 |
| scene_description | string | 是 | 场景描述 | （详细描述工位情况） |
| selection_rationale | string | 是 | 入选理由 | （说明为何适合机器人） |

### 评分字段

每个评分维度包含 `score` 和 `basis` 两个子字段：

| 字段 | 类型 | 范围 | 说明 |
|------|------|------|------|
| labor_urgency | object | 1-5 | 人工替代紧迫性 |
| scale_potential | object | 1-5 | 规模化潜力 |
| superhuman_value | object | 1-5 | 超人类价值密度 |
| operation_complexity | object | 1-5 | 操作复杂度 |
| structure_level | object | 1-5 | 结构化程度 |
| fault_tolerance | object | 1-5 | 容错空间 |
| takt_pressure | object | 1-5 | 节拍压力 |

评分对象结构：

```json
{
  "score": 4,
  "basis": "年流动率约40%，需常年招聘"
}
```

### 状态追踪字段

| 字段 | 类型 | 说明 |
|------|------|------|
| l3_extracted | string | L3是否已提取（done/空） |
| l3_extracted_at | datetime | L3提取时间 |
| guide_generated | string | 指南是否已生成（done/空） |
| guide_generated_at | datetime | 指南生成时间 |

---

## 元动作字段定义

### L1-L2 分类字段

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| l1_id | string | L1编号 | L1-04 |
| l1_name_zh | string | L1中文名 | 手部抓握操控 |
| l1_name_en | string | L1英文名 | Hand Grasping & Manipulation |
| l1_boundary | string | L1边界规则 | （判定归属的标准） |
| l2_id | string | L2编号 | L2-04-01 |
| l2_name_zh | string | L2中文名 | 力量型抓握 |
| l2_name_en | string | L2英文名 | Power Grasp |
| l2_boundary_rule | string | L2边界规则 | （与相邻L2的区分标准） |
| l3_naming_pattern | string | L3命名模式 | [抓握]-[对象]-[约束] |

### L3 实例字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| l3_id | string | 是 | 唯一编号 |
| l3_name_zh | string | 是 | 中文名称 |
| l3_name_en | string | 否 | 英文名称 |
| parent_l2_id | string | 是 | 所属L2编号 |
| description | string | 是 | 动作描述 |
| object_category | string | 是 | 操作对象类别 |
| parameter_ranges | object | 是 | 参数范围 |
| source_scene | string | 是 | 来源场景 |
| is_new | boolean | 是 | 是否新定义 |

### 参数范围字段

```json
{
  "parameter_ranges": {
    "size_range": "400x300x200mm",
    "weight_range": "20-30kg",
    "force_range": "50-100N",
    "precision_requirement": "±2mm"
  }
}
```

---

## 枚举值定义

### 难度等级 (difficulty_level)

| 等级 | 符号 | 含义 |
|------|------|------|
| 1 | ★☆☆☆☆ | 非常容易，现有技术可直接实现 |
| 2 | ★★☆☆☆ | 较容易，需少量定制开发 |
| 3 | ★★★☆☆ | 中等，需要专项技术攻关 |
| 4 | ★★★★☆ | 较难，多项技术挑战需突破 |
| 5 | ★★★★★ | 非常难，属于前沿研究方向 |

### 技术成熟度 (TRL)

| 等级 | 阶段 | 说明 |
|------|------|------|
| TRL 1 | 基本原理 | 基本原理观察和报告 |
| TRL 2 | 概念形成 | 技术概念和应用形成 |
| TRL 3 | 概念验证 | 关键功能的分析和实验验证 |
| TRL 4 | 实验室验证 | 在实验室环境中验证组件 |
| TRL 5 | 相关环境验证 | 在相关环境中验证组件 |
| TRL 6 | 相关环境演示 | 在相关环境中演示系统/子系统模型 |
| TRL 7 | 原型演示 | 在运行环境中演示系统原型 |
| TRL 8 | 系统完成 | 实际系统完成并通过鉴定 |
| TRL 9 | 运行验证 | 实际系统在运行条件下验证成功 |

---

## 数据格式规范

### 日期时间格式

```
YYYY-MM-DD HH:MM:SS
示例：2026-06-09 10:30:00
```

### 编号格式

```
场景：[大类]-[中类]-[小类]-[场景标识]-[描述]
示例：36-361-00-RoadTest-FinishedVehicle-MultiCondition

L1：L1-XX
L2：L2-XX-XX
L3：L3-XX-XX-XXX
```

### 文件编码

- 所有文本文件使用 UTF-8 编码
- CSV 文件使用 UTF-8 with BOM（Excel 兼容）

---

## 相关文档

- [场景分类体系](scene-taxonomy.md)
- [元动作分类体系](action-taxonomy.md)
