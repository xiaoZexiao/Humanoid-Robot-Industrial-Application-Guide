# 元动作分类体系说明

> 🚧 **待完善** - 本文档将由 T10 任务生成

## 概述

本文档定义人形机器人工业应用的元动作分类体系。

## 层级结构

```
L1 大类（6-10个）
  └─ L2 中类（每个大类下5-10个）
      └─ L3 小类（每个中类下5-15个）
          └─ L4 参数化实例
```

## L1 大类定义

| 代码 | 名称 | 英文 | 描述 |
|------|------|------|------|
| LOCO | 移动类 | Locomotion | 行走、转向、上下楼梯等 |
| GRASP | 抓取类 | Grasping | 各种抓取姿态和策略 |
| MANIP | 操作类 | Manipulation | 旋拧、按压、滑动等 |
| ASSEM | 装配类 | Assembly | 对位、嵌合、紧固 |
| HANDL | 搬运类 | Handling | 举起、放置、传递 |
| INSP | 检测类 | Inspection | 视觉、触觉、力觉检测 |
| INTER | 交互类 | Interaction | 人机协作、信号交互 |
| POST | 姿态类 | Posture | 弯腰、蹲下、伸展 |

## 编号规则

```
MA-[L1代码]-[L2代码]-[三位数序号]

示例：MA-GRASP-PINCH-001
```

## 标准字段

每个元动作包含以下字段：

| 字段 | 说明 |
|------|------|
| action_id | 唯一编号 |
| name_zh | 中文名称 |
| name_en | 英文名称 |
| level | 层级 (L1/L2/L3/L4) |
| parent_id | 上级动作ID |
| description | 动作描述 |
| dof_requirement | 自由度需求 |
| payload_range | 负载范围 |
| precision_requirement | 精度要求 |
| speed_range | 速度范围 |
| difficulty_level | 难度等级 (1-5) |
| tech_maturity | 技术成熟度 (TRL 1-9) |
| typical_scenes | 关联场景ID列表 |
| hardware_requirement | 硬件要求 |
| training_approach | 建议训练方式 |
| common_failures | 常见失败模式 |

## 详细定义

详见 `actions/action-overview.md` 和 `actions/action-library.json`
