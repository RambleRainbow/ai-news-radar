# AI News Radar - 项目需求文档

## 项目背景

AI News Radar 是一个生产级的 AI/技术新闻聚合 skill，符合 [agentskills.io 规范](https://agentskills.io/specification)。

## 架构重构需求

### 1. 方案 A 实现：自包含 skill 包

**目标：** 将 `skill/` 目录做成完全独立的交付物，不依赖 `src/` 目录。

**实现要求：**
- [x] 将所有核心业务逻辑复制到 `skill/` 目录
  - [x] `skill/config.py` - 配置模块
  - [x] `skill/core/` - 核心业务逻辑
  - [x] `skill/parsers/` - 新闻源解析器
  - [x] `skill/filters/` - 新闻过滤器
  - [x] `skill/storage/` - 存储模块
  - [x] `skill/utils/` - 工具函数
  - [x] `skill/__init__.py` - 导出所有公共 API

**验收标准：**
- [x] `skill/scripts/main.py` 可以独立运行，不依赖 `src/`
- [x] 用户下载 `skill/` 目录后可以直接使用
- [x] 符合 agentskills.io 自包含原则

---

### 2. 重构：消除代码重复

**目标：** 删除 `src/` 目录中与 `skill/` 重复的代码，降低维护负担。

**实现要求：**
- [x] 删除 `src/` 中的所有业务逻辑模块：
  - [x] `src/parsers/`
  - [x] `src/filters/`
  - [x] `src/storage/`
  - [x] `src/utils/`
  - [x] `src/config.py`
  - [x] `src/core.py`

**保留内容：**
- [x] `src/__init__.py` - 仅包含版本号和开发说明

**验收标准：**
- [x] `src/` 目录只用于开发/测试参考
- [x] 无代码重复，单一真相源是 `skill/`

---

### 3. 数据源配置

**目标：** 从参考项目中提取信息源配置，填充 `skill/assets/data/` 目录。

**参考项目：** https://github.com/LearnPrompt/ai-news-radar

**实现要求：**
- [x] `skill/assets/data/sources.yaml` - 配置所有 RSS/HTML/OPML 信息源
  - [x] 包含中文 AI 资讯源（InfoQ、Hugging Face、ReadHub 等）
  - [x] 包含国际英语源（TechCrunch、Ars Technica 等）
  - [x] 包含聚合站（WaytoAI、Zeli）
  - [x] 支持优先级配置
  - [x] 支持自定义 OPML RSS 订阅

- [x] `skill/assets/data/keywords.yaml` - 配置 AI 过滤关键词
  - [x] 包含核心 AI/ML 术语
  - [x] 包含流行服务（ChatGPT、GPT、Claude 等）
  - [x] 包含中文 AI 术语
  - [x] 支持研究/行业术语

- [x] `skill/assets/data/custom_feeds.opml` - OPML RSS 订阅模板
  - [x] 支持批量导入 RSS 源

**验收标准：**
- [x] 所有数据文件都是 YAML 格式
- [x] 可以被 `skill/` 正确加载和解析
- [x] 至少包含 10 个可靠的信息源

---

### 4. YAML 格式规范

**目标：** 确保 `skill/assets/data/` 中的 YAML 文件格式正确，避免解析错误。

**实现要求：**
- [x] 创建 `.claude/memories/YAML_FORMAT.md` 记忆文件
- [x] 统一使用 2 空格缩进（无 tab）
- [x] 所有列表项使用短横线（`- name:`）
- [x] 注释使用 `#` 而非 markdown 代码块
- [x] 移除 markdown 代码块包裹 YAML 内容
- [x] 单一 `sources` 列表，不重复分类
- [x] 合理控制行长度（< 120 字符）

**验收标准：**
- [x] YAML 文件可以被 `yaml.safe_load()` 正确解析
- [x] 不包含语法错误（缩进、列表格式等）
- [x] 有格式指南供后续参考

**参考文件：** `.claude/memories/YAML_FORMAT.md`

---

## 5. Git 配置优化

**目标：** 优化 `.gitignore` 配置，正确管理临时文件和缓存。

**实现要求：**
- [x] `.gitignore` 追踪 `skill/assets/data/`（使用 `!skill/assets/data/`）
- [x] 忽略根目录的 `data/` 避免提交意外文件
- [x] 忽略测试和覆盖率文件
- [x] 忽略 IDE 和系统文件

**验收标准：**
- [x] `skill/assets/data/` 中的文件可以被提交
- [x] 缓存目录被忽略（`.cache/`）
- [x] 测试产物不会被误提交

---

## 6. 测试覆盖率

**目标：** 确保项目有足够的测试覆盖率。

**当前状态：**
- [x] 单元测试：171 个测试通过
- [x] 覆盖率：84.67%（目标 80%）

**验收标准：**
- [x] 所有核心模块都有测试覆盖
- [x] 覆盖率不低于 80%
- [x] 新增代码有对应测试

---

## 优先级

| 优先级 | 任务 | 状态 |
|--------|------|--------|
| **P0** | 方案 A 实现、重构、数据源配置 | ✅ 已完成 |
| **P1** | YAML 格式修复和记忆文件 | ✅ 已完成 |

## 验收清单

- [x] skill/ 目录可以独立运行
- [x] skill/ 包含所有必需的业务代码
- [x] src/ 目录无代码重复
- [x] skill/assets/data/ 包含完整的数据源配置
- [x] YAML 文件格式正确
- [x] 有格式指南文档
- [x] Git 配置优化
- [x] 测试覆盖率 > 80%

---

## 技术债务

- [ ] 无明确的技术债务
- [ ] 代码结构清晰，职责分明
