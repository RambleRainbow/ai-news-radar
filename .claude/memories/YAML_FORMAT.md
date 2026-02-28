# YAML 格式记忆文件
#
# 避免在 sources.yaml 等配置文件中出现 YAML 格式错误。

## 重要规则

### 1. 缩进
```yaml
# ✅ 正确：2 空格缩进
sources:
  - name: Source1
    url: https://example.com
# ❌ 错误：使用 tab 或混合缩进
sources:
	- name: Source1  # tab 缩进
```

### 2. 列表项
```yaml
# ✅ 正确：使用短横线 (hyphen)
sources:
  - name: Source1
    url: https://example.com
  - name: Source2
# ❌ 错误：使用下划线
sources:
  - name: Source1
    url: https://example.com
```

### 3. 不要使用 Markdown 代码块

```yaml
# ❌ 错误：使用 markdown 代码块包裹 YAML 内容
\`\`\`yaml
# 这会导致 YAML 解析错误
\`\`\`
```

```yaml
# ✅ 正确：直接写 YAML 内容
sources:
  - name: Source1
    url: https://example.com
```

### 4. 注释格式

```yaml
# ✅ 正确：使用 # 注释
# 这是一个注释
sources:
  - name: Source1
    url: https://example.com

# ❌ 错误：使用其他符号
# 这是一个注释
sources:
  - name: Source1
    url: https://example.com
```

### 5. 单一 sources 列表

```yaml
# ✅ 正确：所有源在一个 sources 列表下
sources:
  - name: Source1
    url: https://example.com
  - name: Source2
    url: https://example.com
```

# ❌ 错误：分类后重复 sources 关键字
## Core Sources
sources:
  - name: Source1
    url: https://example.com
## International Sources
sources:
  - name: Source2
    url: https://example.com
```

## 验证方法

```bash
# 使用 yamllint 或在线工具验证 YAML 格式
yamllint skill/assets/data/sources.yaml

# 或使用 Python 验证
python -c "import yaml; yaml.safe_load(open('skill/assets/data/sources.yaml'))"
```

## 常见错误及解决

| 错误 | 解决 |
|--------|--------|
| **tab 缩进** | 统一使用 2 空格缩进 |
| **markdown 代码块** | 移除 \`\` \` 等标记 |
| **重复 sources** | 所有源在单一列表下 |
| **注释格式** | 使用 # 而非 yaml 注释 |
| **长行** | 保持合理的行长度（建议 < 120 字符） |
