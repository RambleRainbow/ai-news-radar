# AI News Radar

本项目是为了开发一个遵守 [agent skill](https://agentskills.io/specification) 规范的 skill。

## 项目目的

开发一个符合 agentskills.io 规范的 AI 新闻聚合与监控 skill。

## 参考规范

- Agent Skills Specification: https://agentskills.io/specification

## 注意事项

- **变更日志应放在 git commit 中，不要记录在项目文档文件中**
- CLAUDE.md 只记录项目的基本信息、目录结构说明和使用方式，不记录变更历史

## 目录结构

本项目采用清晰的目录结构，将 skill 交付物与开发代码分离：

```
ai-news-radar/
├── skill/                    # Skill 包（最终交付物）
│   ├── SKILL.md             # 核心 skill 定义
│   ├── scripts/             # skill 的可执行脚本
│   │   └── main.py
│   ├── references/          # skill 引用文档（按需加载）
│   └── assets/              # skill 静态资源
│       ├── data/            # 数据文件（sources.yaml, keywords.yaml, sample_opml.opml）
│       └── templates/       # 模板文件
│
├── src/                      # 核心实现代码
│   ├── parsers/             # 解析器模块
│   ├── filters/             # 过滤器模块
│   ├── storage/             # 存储模块
│   └── utils/               # 工具函数
│
├── tests/                    # 测试代码
│   ├── test_parsers.py
│   └── test_filters.py
│
├── docs/                     # 开发文档（非 skill 的一部分）
│   ├── ARCHITECTURE.md
│   ├── DEPLOYMENT.md
│   ├── FILTERING_RULES.md
│   └── SOURCE_MAPPING.md
│
├── requirements.txt
├── CLAUDE.md
└── README.md
```

### 设计原则

1. **skill/ 目录**：按照 agentskills.io 规范组织，可直接作为 skill 包分发
2. **src/ 目录**：实现代码，便于开发和维护
3. **tests/ 目录**：测试代码，与实现代码分离
4. **docs/ 目录**：开发文档，不会被加载到 skill 上下文中

## 使用方式

```bash
# 运行 skill
python skill/scripts/main.py

# 运行测试（从项目根目录）
pytest tests/
```
