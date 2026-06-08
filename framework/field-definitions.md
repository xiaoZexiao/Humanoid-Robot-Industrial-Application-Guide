# 标准字段定义文档

> 🚧 **待完善** - 本文档将由 T13 任务生成

## 概述

本文档定义场景指南和元动作库中使用的所有标准字段。

## 场景字段

### 基本信息

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| scene_id | string | 是 | 场景唯一编号 |
| name_zh | string | 是 | 中文名称 |
| name_en | string | 是 | 英文名称 |
| industry | enum | 是 | 所属行业 |
| process | enum | 是 | 工序类型 |

### 技术参数

| 字段 | 类型 | 说明 | 取值范围 |
|------|------|------|----------|
| difficulty | int | 实施难度 | 1-5 |
| tech_maturity | string | 技术成熟度 | TRL 1-9 |
| dof_requirement | string | 自由度需求 | 如 "双臂≥7DoF" |
| payload | string | 负载需求 | 如 "5-10kg" |
| precision | string | 精度需求 | 如 "±0.5mm" |
| cycle_time | string | 节拍要求 | 如 "30s/件" |

### 难度等级定义

| 等级 | 符号 | 含义 |
|------|------|------|
| 1 | ★☆☆☆☆ | 非常容易，现有技术可直接实现 |
| 2 | ★★☆☆☆ | 较容易，需少量定制开发 |
| 3 | ★★★☆☆ | 中等，需要专项技术攻关 |
| 4 | ★★★★☆ | 较难，多项技术挑战需突破 |
| 5 | ★★★★★ | 非常难，属于前沿研究方向 |

## 元动作字段

详见 `framework/action-taxonomy.md`

## 枚举值定义

### 行业代码 (industry)

```
automotive, electronics-3c, new-energy, logistics, 
food-pharma, home-appliance, aerospace, steel-metallurgy, textile
```

### 工序代码 (process)

```
loading, assembly, handling, inspection, packaging, welding, spraying
```

### TRL等级 (tech_maturity)

```
TRL 1: 基本原理观察
TRL 2: 技术概念形成
TRL 3: 概念验证
TRL 4: 实验室验证
TRL 5: 相关环境验证
TRL 6: 相关环境演示
TRL 7: 系统原型演示
TRL 8: 系统完成并鉴定
TRL 9: 系统运行验证
```
