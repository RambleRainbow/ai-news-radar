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
├── tests/                    # 测试代码（分层结构）
│   ├── unit/               # 单元测试
│   ├── integration/        # 集成测试
│   ├── e2e/                # 端到端测试
│   ├── performance/         # 性能测试
│   ├── fixtures/           # 测试数据
│   └── conftest.py         # 全局 fixtures
│
├── docs/                     # 开发文档（非 skill 的一部分）
│   ├── ARCHITECTURE.md
│   ├── DEPLOYMENT.md
│   ├── FILTERING_RULES.md
│   └── SOURCE_MAPPING.md
│
├── .github/workflows/         # CI/CD 工作流
├── .pre-commit-config.yaml    # 预提交钩子
├── pytest.ini               # pytest 配置
├── requirements-dev.txt       # 开发依赖
├── requirements.txt          # 生产依赖
├── Makefile                 # 统一命令入口
├── CLAUDE.md
└── README.md
```

### 设计原则

1. **skill/ 目录**：按照 agentskills.io 规范组织，可直接作为 skill 包分发
2. **src/ 目录**：实现代码，便于开发和维护
3. **tests/ 目录**：测试代码分层（单元/集成/e2e/性能），与实现代码分离
4. **docs/ 目录**：开发文档，不会被加载到 skill 上下文中

## 使用方式

```bash
# 运行 skill
python skill/scripts/main.py

# 运行测试
pytest tests/              # 所有测试
pytest tests/unit/         # 只运行单元测试
pytest tests/integration/  # 只运行集成测试

# Make 目标
make validate             # 验证 skill 规范
make test                 # 运行单元测试
make test-all             # 运行所有测试
make lint                 # 代码检查
make format               # 代码格式化
make ci                   # 运行完整 CI 检查

# Pre-commit
pre-commit install        # 安装预提交钩子
pre-commit run --all-files # 手动运行所有检查
```

## CI/CD 工作流

| 工作流 | 触发条件 | 作用 |
|--------|----------|------|
| ci.yml | push/PR | 代码质量检查、单元测试 |
| skill-validation.yml | push/PR | agentskills.io 规范验证 |
| release.yml | tag v*.*.* | 创建 GitHub Release |

## 测试框架

- **pytest** - 测试框架
- **pytest-cov** - 覆盖率报告
- **pytest-mock** - Mock 支持
- **responses** - HTTP Mock
- **freezegun** - 时间控制

测试覆盖率目标：
- 单元测试：90%+
- 总体：80%+

