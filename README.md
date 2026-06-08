# 人形机器人工业场景应用建设指南

> 🚧 **项目建设中** - 本指南正在持续完善中

本项目是一份面向人形机器人工业应用的开源建设指南，系统梳理工业场景和标准化工业元动作，为每个场景提供从技术选型到实施落地的完整建设方案。

## 项目概览

| 指标 | 数量 |
|------|------|
| 覆盖场景 | 目标100个 |
| 元动作库 | 目标N千个 |
| 覆盖行业 | 10+ |

## 快速导航

根据您的角色快速找到所需内容：

- **机器人公司决策者**：哪些场景最容易落地？→ [`analysis/quick-win-scenes.md`](analysis/quick-win-scenes.md)
- **数据采集公司**：应该采集哪些动作数据？→ [`analysis/high-reuse-actions.md`](analysis/high-reuse-actions.md)
- **制造企业**：我所在行业的场景指南 → [`scenes/`](scenes/)
- **研究人员**：元动作分类体系 → [`framework/action-taxonomy.md`](framework/action-taxonomy.md)

## 目录结构

```
├── framework/          # 分类框架
│   ├── scene-taxonomy.md       # 场景分类矩阵
│   ├── action-taxonomy.md      # 元动作分类体系
│   └── field-definitions.md    # 标准字段定义
│
├── scenes/             # 场景指南（按行业分类）
│   ├── automotive/             # 汽车整车及零部件
│   ├── electronics-3c/         # 3C电子
│   ├── new-energy/             # 锂电/光伏新能源
│   ├── logistics/              # 物流仓储
│   └── food-pharma/            # 食品医药
│
├── actions/            # 元动作库
│   ├── action-library.json     # 完整元动作库
│   ├── action-overview.md      # 元动作总览
│   └── by-category/            # 按类别详细说明
│
├── analysis/           # 分析与洞察
│   ├── difficulty-ranking.md   # 实施难度排名
│   ├── high-reuse-actions.md   # 高复用元动作
│   └── quick-win-scenes.md     # 快速落地推荐
│
├── data/               # 结构化数据
│   ├── scene-matrix.csv        # 场景分类矩阵
│   └── scene-action-mapping.json
│
└── docs/               # 附加文档
    ├── methodology.md          # 研究方法
    └── references.md           # 参考标准
```

## 核心价值

1. **实战导向**：基于实地调研，非纯理论推演
2. **结构化元动作库**：可直接用于机器人训练数据规划
3. **踩坑指南**：真实项目中的问题和规避方案
4. **开放协作**：欢迎行业从业者补充完善

## 参与贡献

我们特别欢迎以下类型的贡献：
- 补充真实项目中的"典型踩坑点"
- 校准技术参数（基于实测数据）
- 新增未覆盖的工业场景

详见 [CONTRIBUTING.md](CONTRIBUTING.md)

## 作者

[待补充：作者介绍]

## 许可协议

本项目采用 [CC BY-SA 4.0](LICENSE) 协议开源。

您可以自由地共享和演绎本作品，但需要署名并以相同协议分发衍生作品。
