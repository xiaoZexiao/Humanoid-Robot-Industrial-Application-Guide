# 贡献指南 | Contributing Guide

感谢您对《人形机器人工业场景应用建设指南》的关注！我们欢迎来自行业从业者、研究人员和技术专家的贡献。

## 如何贡献

### 1. 报告问题
- 发现内容错误（技术参数、流程描述等）
- 发现格式问题或链接失效
- 提出改进建议

请通过 [GitHub Issues](../../issues) 提交，并尽量提供：
- 问题所在的文件路径
- 具体的错误描述
- 建议的修正方案（如有）

### 2. 补充场景内容
如果您有实际工业场景的落地经验，特别欢迎您补充：
- **典型踩坑点**：您在实际项目中遇到的真实问题和解决方案
- **技术参数校准**：基于实测数据的参数修正
- **新场景贡献**：目前未覆盖但有实际需求的场景

### 3. 元动作库扩展
- 补充新的元动作定义
- 完善现有元动作的参数说明
- 提供元动作的训练数据采集经验

## 贡献流程

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/your-contribution`)
3. 提交您的修改 (`git commit -m '添加XXX场景的踩坑经验'`)
4. 推送到分支 (`git push origin feature/your-contribution`)
5. 创建 Pull Request

## 内容规范

### 场景指南
- 遵循 `docs/scene-template.md` 中定义的模板结构
- 技术参数需注明数据来源
- "典型踩坑点"应基于真实经验，避免泛泛而谈

### 元动作定义
- 遵循 `framework/action-taxonomy.md` 中的分类体系
- 填写完整的标准字段
- 新增动作需关联至少一个应用场景

## 署名
所有被接受的贡献都将在 README 的贡献者列表中致谢。

## 许可协议
提交贡献即表示您同意将您的贡献以 CC BY-SA 4.0 协议发布。

---

# Contributing Guide (English)

Thank you for your interest in the Humanoid Robot Industrial Application Guide!

## How to Contribute

1. **Report Issues**: Technical errors, broken links, improvement suggestions
2. **Add Content**: Real-world pitfalls, parameter corrections, new scenarios
3. **Expand Action Library**: New action definitions, training data insights

## Process

1. Fork this repository
2. Create your branch (`git checkout -b feature/your-contribution`)
3. Commit changes (`git commit -m 'Add XXX'`)
4. Push and create Pull Request

## License
Contributions are licensed under CC BY-SA 4.0.
