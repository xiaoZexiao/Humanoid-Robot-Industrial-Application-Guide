# 元动作库总览

> 🚧 **待完善** - 本文档将由 T10 任务生成

## 统计概览

| 指标 | 数量 |
|------|------|
| L1 大类 | 待定义 |
| L2 中类 | 待定义 |
| L3 小类 | 待定义 |
| 总计 | 待定义 |

## 分类树状图

```
元动作库
├── 移动类 (LOCOMOTION)
│   ├── 行走
│   ├── 转向
│   └── ...
├── 抓取类 (GRASPING)
│   ├── 单手抓取
│   ├── 双手协作
│   └── ...
├── 操作类 (MANIPULATION)
│   └── ...
├── 装配类 (ASSEMBLY)
│   └── ...
├── 搬运类 (HANDLING)
│   └── ...
├── 检测类 (INSPECTION)
│   └── ...
├── 交互类 (INTERACTION)
│   └── ...
└── 姿态类 (POSTURE)
    └── ...
```

## 使用指南

### 查找元动作

1. 按类别浏览：`actions/by-category/`
2. 完整库查询：`actions/action-library.json`
3. 场景关联查询：`data/scene-action-mapping.json`

### 引用格式

在场景指南中引用元动作时，使用以下格式：

```markdown
- [动作名称] - MA-XXX-XXX-001
```

### 新增元动作

如需新增元动作，请遵循 `framework/action-taxonomy.md` 中定义的规范。
