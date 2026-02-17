# GitHub 上传指南

## 📦 项目信息

**GitHub 仓库**: https://github.com/kogamishinyajerry-ops/aiHolmes
**远程仓库**: origin (https://github.com/kogamishinyajerry-ops/aiHolmes.git)

---

## 🚀 快速上传

### 方法1: 使用自动化脚本（推荐）

```bash
cd /workspace
./push_to_github.sh
```

这个脚本会自动：
1. 检查未提交的更改
2. 提交更改（带时间戳）
3. 推送到 GitHub

---

### 方法2: 手动上传

```bash
cd /workspace

# 添加所有更改
git add -A

# 提交更改
git commit -m "feat: 更新项目"

# 推送到 GitHub
git push -u origin main
```

---

## 📋 当前状态

### 已提交的内容

本次提交包含：

#### AI 侦探系统
- ✅ 完整的 AI 侦探系统（6轮迭代测试）
- ✅ 4个真实感测试案例
- ✅ 7份详细测试报告
- ✅ 总体评分 67/100

#### 职业碰瓷维权工具
- ✅ 深度分析报告（V2版，14章12000字）
- ✅ 行动检查清单生成器
- ✅ 言语举动分析工具
- ✅ 案件管理系统
- ✅ 胜算评估报告
- ✅ 完整的使用指南和文档

#### 其他内容
- ✅ AI 助手系统
- ✅ AI 阅读助手
- ✅ Skills 和 Agents 系统
- ✅ 完整的文档和示例

**统计数据**:
- 114 个文件变更
- 24,308 行新增代码
- 65 行删除

---

## 🔄 后续开发流程

每次开发完成后，按照以下流程上传：

### 步骤1: 检查状态

```bash
cd /workspace
git status
```

查看是否有未提交的更改。

---

### 步骤2: 添加更改

```bash
git add -A
```

或者只添加特定文件：

```bash
git add 某个文件名
```

---

### 步骤3: 提交更改

```bash
git commit -m "feat: 描述你的更改"
```

提交信息格式建议：

- `feat: 新功能`
- `fix: 修复bug`
- `docs: 文档更新`
- `style: 代码格式调整`
- `refactor: 重构`
- `test: 测试相关`
- `chore: 构建/工具链相关`

---

### 步骤4: 推送到 GitHub

```bash
git push -u origin main
```

或者使用自动化脚本：

```bash
./push_to_github.sh
```

---

## 📁 项目结构

```
workspace/
├── ai_detective/              # AI 侦探系统
│   ├── PROFESSIONAL_VICTIMIZATION_ANALYSIS_REPORT_V2.md  # 深度分析报告
│   ├── SUCCESS_PROBABILITY_ASSESSMENT.md  # 胜算评估报告
│   ├── VICTIMIZATION_INDEX.md  # 索引文件
│   ├── VICTIMIZATION_TOOLS_GUIDE.md  # 使用指南
│   ├── VICTIMIZATION_TOOLS_SUMMARY.md  # 项目总结
│   ├── action_checklist_generator.py  # 检查清单生成器
│   ├── speech_behavior_analyzer.py  # 言语举动分析工具
│   ├── victimization_case_manager.py  # 案件管理系统
│   ├── backend/  # 后端模块
│   ├── frontend/  # 前端模块
│   ├── test_cases/  # 测试案例
│   └── cases/  # 案例数据
├── agents/  # Agents 系统
├── skills/  # Skills 系统
├── ai_assistant.py  # AI 助手
├── ai_reading_helper/  # AI 阅读助手
├── push_to_github.sh  # 自动上传脚本
└── GITHUB_UPLOAD_GUIDE.md  # 本文件
```

---

## 💡 常用 Git 命令

### 查看状态

```bash
git status
```

### 查看提交历史

```bash
git log --oneline
```

### 查看远程仓库

```bash
git remote -v
```

### 拉取最新更改

```bash
git pull origin main
```

### 查看分支

```bash
git branch
```

### 创建新分支

```bash
git branch 新分支名
```

### 切换分支

```bash
git checkout 分支名
```

### 合并分支

```bash
git merge 分支名
```

---

## ⚠️ 注意事项

1. **备份重要数据**
   - 在推送前确保重要数据已备份
   - 不要推送敏感信息（密码、密钥等）

2. **提交信息规范**
   - 使用清晰的提交信息
   - 遵循提交信息格式规范

3. **推送频率**
   - 建议每天推送一次
   - 重要功能完成后立即推送

4. **冲突处理**
   - 如果遇到冲突，先拉取最新代码
   - 解决冲突后再推送

---

## 📞 获取帮助

- GitHub 官方文档: https://docs.github.com
- Git 官方文档: https://git-scm.com/doc
- 项目地址: https://github.com/kogamishinyajerry-ops/aiHolmes

---

## 📝 更新日志

### 2026-02-17

- ✅ 初次提交
- ✅ 添加 AI 侦探系统
- ✅ 添加职业碰瓷维权工具
- ✅ 添加自动化上传脚本

---

**最后更新**: 2026年2月17日
**状态**: ✅ 已提交，等待推送
