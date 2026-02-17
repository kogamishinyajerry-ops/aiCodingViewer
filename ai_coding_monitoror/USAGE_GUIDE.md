# AI Coding Monitoror 实际使用指南

## 📖 前言

AI Coding Monitoror 的核心价值在于：**监控和规范 AI coding 过程**，防止：
1. 记忆丢失导致前后代码不一致
2. AI 破坏之前正常工作的功能
3. 偏离原始开发目标

---

## 🎯 实际应用场景

### 场景 1: VS Code 中使用 AI 助手开发

#### 步骤 1: 启动监控服务

```bash
cd /workspace/ai_coding_monitoror
./start.sh
```

服务启动后，您会看到：
- 后端服务: `http://localhost:8000`
- 前端界面: `http://localhost:8001`
- WebSocket: `ws://localhost:8000/ws/{session_id}`

#### 步骤 2: 初始化监控会话

在开始新功能开发前，通过 API 初始化会话：

```bash
curl -X POST http://localhost:8000/sessions/init \
  -H "Content-Type: application/json" \
  -d '{
    "project_path": "/workspace/your_project",
    "language": "python",
    "description": "开发用户认证功能"
  }'
```

返回：
```json
{
  "session_id": "sess_20250217_001",
  "status": "initialized"
}
```

**保存这个 session_id，之后所有操作都需要它！**

#### 步骤 3: 创建辅助脚本（推荐）

创建一个辅助脚本 `ai_helper.py`，集成到您的开发流程：

```python
#!/usr/bin/env python3
"""
AI Coding Assistant Helper
在您与 AI 对话时自动调用 Monitoror API
"""

import requests
import os
from pathlib import Path

# 监控服务配置
MONITOROR_URL = "http://localhost:8000"
SESSION_FILE = ".monitoror_session.json"

class AICodingMonitor:
    def __init__(self):
        self.session_id = self._load_session()
    
    def _load_session(self):
        """加载当前会话"""
        if os.path.exists(SESSION_FILE):
            import json
            with open(SESSION_FILE) as f:
                data = json.load(f)
                return data.get("session_id")
        return None
    
    def _save_session(self, session_id):
        """保存会话"""
        import json
        with open(SESSION_FILE, "w") as f:
            json.dump({"session_id": session_id}, f)
        self.session_id = session_id
    
    def init_session(self, project_path, language="python"):
        """初始化监控会话"""
        response = requests.post(
            f"{MONITOROR_URL}/sessions/init",
            json={"project_path": project_path, "language": language}
        )
        session_id = response.json()["session_id"]
        self._save_session(session_id)
        print(f"✅ 监控会话已创建: {session_id}")
        return session_id
    
    def log_ai_request(self, prompt, context_files=[]):
        """记录 AI 请求"""
        if not self.session_id:
            print("⚠️  请先初始化会话")
            return
        
        response = requests.post(
            f"{MONITOROR_URL}/analyze/ai-request",
            json={
                "request_id": f"req_{len(os.listdir('.monitoror'))}",
                "prompt": prompt,
                "context": {"files": context_files}
            }
        )
        print(f"📝 AI 请求已记录: {prompt[:50]}...")
    
    def save_before_change(self, file_path):
        """修改前保存快照"""
        if not self.session_id:
            return
        
        content = Path(file_path).read_text()
        response = requests.post(
            f"{MONITOROR_URL}/sessions/{self.session_id}/snapshot",
            json={
                "file_path": file_path,
                "content": content
            }
        )
        print(f"💾 已保存快照: {file_path}")
    
    def log_ai_response(self, changed_files):
        """记录 AI 响应和代码变更"""
        if not self.session_id:
            return
        
        code_changes = []
        for file_path in changed_files:
            if os.path.exists(file_path):
                content = Path(file_path).read_text()
                code_changes.append({
                    "file_path": file_path,
                    "content": content
                })
        
        response = requests.post(
            f"{MONITOROR_URL}/analyze/ai-response",
            json={
                "response_id": f"resp_{len(os.listdir('.monitoror'))}",
                "request_id": f"req_{len(os.listdir('.monitoror'))-1}",
                "code_changes": code_changes
            }
        )
        
        # 检查是否有告警
        if response.json().get("alerts"):
            print(f"⚠️  检测到 {len(response.json()['alerts'])} 个告警！")
            for alert in response.json()['alerts']:
                print(f"   - [{alert['type']}] {alert['message']}")
        else:
            print("✅ 代码变更验证通过")
    
    def validate_code(self, file_path):
        """验证代码"""
        content = Path(file_path).read_text()
        response = requests.post(
            f"{MONITOROR_URL}/validate/code",
            json={"file_path": file_path, "content": content}
        )
        
        issues = response.json().get("issues", [])
        if issues:
            print(f"❌ 发现 {len(issues)} 个问题:")
            for issue in issues:
                print(f"   - {issue['type']}: {issue['message']}")
        else:
            print("✅ 代码验证通过")
        
        return response.json()

# 全局监控器实例
monitor = AICodingMonitor()
```

#### 步骤 4: 在开发流程中使用

**工作流程示例：**

```python
# 您的开发脚本
from ai_helper import monitor

# 1. 开始新功能
monitor.init_session("/workspace/my_project", "python")

# 2. 记录您给 AI 的请求
monitor.log_ai_request(
    "创建一个用户认证类，包含 login 和 register 方法",
    context_files=["auth.py"]
)

# 3. 修改代码前保存快照
monitor.save_before_change("auth.py")

# 4. AI 修改代码后（您或 AI 工具修改后）
# auth.py 已被修改
monitor.log_ai_response(["auth.py"])

# 5. 验证代码
monitor.validate_code("auth.py")
```

---

## 🔄 完整的 AI Coding 工作流

### 推荐的开发节奏

```
1. 初始化会话
   ↓
2. 保存初始快照（所有相关文件）
   ↓
3. 记录 AI 请求（prompt）
   ↓
4. [AI 生成代码]
   ↓
5. 保存变更前快照
   ↓
6. AI 修改文件
   ↓
7. 记录 AI 响应 + 分析变更
   ↓
8. 运行验证（如果有告警，检查是否接受）
   ↓
9. 回到步骤 3，继续迭代
```

### 自动化脚本示例

创建 `auto_monitor.py`，自动监控文件变更：

```python
#!/usr/bin/env python3
"""
自动监控文件变更，配合 AI coding 使用
"""

import time
import hashlib
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from ai_helper import monitor

class CodeChangeHandler(FileSystemEventHandler):
    def __init__(self, monitor):
        self.monitor = monitor
        self.file_hashes = {}
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        # 只监控 .py 文件
        if not event.src_path.endswith('.py'):
            return
        
        file_path = event.src_path
        file_content = Path(file_path).read_text()
        file_hash = hashlib.md5(file_content.encode()).hexdigest()
        
        # 检查是否真的改变了
        if file_path in self.file_hashes and \
           self.file_hashes[file_path] != file_hash:
            
            print(f"\n📄 检测到文件变更: {file_path}")
            
            # 保存变更前的版本（如果需要）
            # 实际使用时，需要在 AI 修改前调用 save_before_change
            
            # 验证代码
            monitor.validate_code(file_path)
            
            # 记录 AI 响应（假设这是 AI 修改的）
            monitor.log_ai_response([file_path])
        
        self.file_hashes[file_path] = file_hash

# 使用示例
if __name__ == "__main__":
    # 初始化会话
    monitor.init_session("/workspace/my_project")
    
    # 保存初始快照
    for py_file in Path("/workspace/my_project").glob("**/*.py"):
        monitor.save_before_change(str(py_file))
    
    # 启动文件监控
    observer = Observer()
    handler = CodeChangeHandler(monitor)
    observer.schedule(handler, "/workspace/my_project", recursive=True)
    observer.start()
    
    print("🚀 文件监控已启动，按 Ctrl+C 停止")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()
```

---

## 💡 实际使用技巧

### 技巧 1: 定期保存上下文

每隔 10-15 轮对话，手动保存一个快照点：

```bash
# 保存当前会话上下文
curl -X POST http://localhost:8000/sessions/{session_id}/reconstruct \
  -H "Content-Type: application/json" \
  -d '{"target_step": "current"}'

# 之后如果 AI 忘记了，可以重建到这个快照点
```

### 技巧 2: 前端实时监控

访问 `http://localhost:8001`，实时查看：

- 📊 当前会话的代码快照数量
- 🔔 实时告警（红色=严重，黄色=警告）
- 📝 上下文历史
- 🔧 快速重建按钮

### 技巧 3: 集成到 Git 流程

创建 Git hook，在 commit 前验证：

```bash
# .git/hooks/pre-commit
#!/bin/bash
echo "🔍 运行 AI Coding Monitoror 验证..."

python3 /workspace/ai_coding_monitoror/tools/git_hook.py

if [ $? -ne 0 ]; then
  echo "❌ 代码验证失败，请检查告警后再提交"
  exit 1
fi

echo "✅ 验证通过"
```

### 技巧 4: 会话持久化

Monitoror 会自动保存所有会话数据到 `data/` 目录：

```
data/
├── sessions/
│   ├── sess_20250217_001.json
│   └── sess_20250217_002.json
├── snapshots/
│   ├── snap_20250217_001_auth.py
│   └── snap_20250217_002_auth.py
└── alerts/
    └── alert_20250217_001.json
```

即使重启服务，数据也不会丢失。

---

## 🎯 针对您当前会话的使用方案

### 在这个对话中使用

由于您现在正处于一个 AI coding 对话中，可以这样使用：

#### 方法 1: 手动记录（推荐用于当前会话）

1. **启动监控服务**（在另一个终端）

```bash
cd /workspace/ai_coding_monitoror
./start.sh
```

2. **初始化会话**

```python
import requests

# 初始化
response = requests.post(
    "http://localhost:8000/sessions/init",
    json={
        "project_path": "/workspace",
        "language": "python",
        "description": "监控当前对话的 AI coding 过程"
    }
)

session_id = response.json()["session_id"]
print(f"会话 ID: {session_id}")
```

3. **在关键步骤调用 API**

每次 AI 修改代码前后，调用：

```python
# 修改前：保存快照
def save_before(file_path):
    content = open(file_path).read()
    requests.post(
        f"http://localhost:8000/sessions/{session_id}/snapshot",
        json={"file_path": file_path, "content": content}
    )

# 修改后：验证
def validate_after(file_path):
    content = open(file_path).read()
    result = requests.post(
        f"http://localhost:8000/validate/code",
        json={"file_path": file_path, "content": content}
    )
    return result.json()
```

#### 方法 2: 自动化监控（长期使用）

创建一个守护进程，监控 `/workspace` 的所有文件变更：

```bash
# 终端 1: 启动监控服务
cd /workspace/ai_coding_monitoror
./start.sh

# 终端 2: 启动文件监控
cd /workspace
python3 -c "
from auto_monitor import monitor
monitor.init_session('/workspace')
# 启动 watcher...
"
```

---

## 🔔 如何解读告警

### REGRESSION（回归）

**示例**:
```
⚠️  REGRESSION: 函数 'validate_user' 已被删除
   严重性: CRITICAL
   建议: 检查是否误删除，如需要可恢复快照
```

**处理**:
1. 访问前端查看详情
2. 检查是否是预期删除
3. 如果不是，恢复快照：
   ```bash
   curl -X POST http://localhost:8000/sessions/{id}/reconstruct \
     -d '{"target_step": "last_valid"}'
   ```

### CONTEXT_DRIFT（上下文漂移）

**示例**:
```
⚠️  CONTEXT_DRIFT: 当前请求偏离原始目标 45%
   原始意图: 用户认证功能
   当前重点: 日志记录功能
   建议: 确认是否需要切换目标
```

**处理**:
1. 检查是否真的是新需求
2. 如果是，可以忽略告警
3. 如果不是，提醒 AI 回到正题

### MEMORY_LOSS（记忆丢失）

**示例**:
```
⚠️  MEMORY_LOSS: 检测到潜在记忆丢失
   建议: 重建到步骤 15 的上下文
```

**处理**:
```python
# 重建上下文
requests.post(
    f"http://localhost:8000/sessions/{session_id}/reconstruct",
    json={"target_step": 15}
)
```

---

## 📊 监控效果评估

使用一段时间后，您可以评估：

```python
# 获取会话统计
response = requests.get(f"http://localhost:8000/sessions/{session_id}/stats")
stats = response.json()

print(f"总请求次数: {stats['total_requests']}")
print(f"代码变更次数: {stats['total_changes']}")
print(f"捕获的问题: {stats['caught_issues']}")
print(f"防止的破坏: {stats['prevented_regressions']}")
```

---

## 🚀 下一步

1. **立即开始**: 启动服务，初始化会话
2. **集成到流程**: 创建 `ai_helper.py` 辅助脚本
3. **长期使用**: 开发 VS Code 插件，自动化整个流程

---

## 💬 常见问题

### Q: 需要在每个会话中都手动调用 API 吗？

A: 不需要。开发 VS Code 插件后，可以自动捕获 AI 对话和代码变更。

### Q: 会拖慢开发速度吗？

A: 几乎不会。AST 分析和验证很快（<100ms），而且可以异步进行。

### Q: 可以同时监控多个会话吗？

A: 可以。每个会话有唯一的 `session_id`，可以并行管理。

### Q: 数据存储在哪里？

A: 默认存储在 `data/` 目录的 JSON 文件中。可以扩展为数据库。

---

**版本**: 0.1.0  
**更新日期**: 2026-02-17
