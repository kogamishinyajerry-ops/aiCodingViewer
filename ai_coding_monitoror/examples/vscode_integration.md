# VS Code 扩展集成指南

## 📖 概述

VS Code 扩展是 AI Coding Monitoror 最理想的集成方式，可以实现：
- 自动捕获 AI 请求/响应
- 实时监控文件变更
- 内联显示告警
- 一键恢复快照

---

## 🏗️ 扩展架构

```
VS Code Extension
│
├── AI Assistant Integration (Copilot/Cursor)
│   └── 捕获 AI 生成代码
│
├── File System Watcher
│   └── 监控文件变更
│
├── Command Palette Commands
│   ├── Monitoror: Start Session
│   ├── Monitoror: Save Snapshot
│   ├── Monitoror: Validate Code
│   └── Monitoror: Revert to Snapshot
│
├── Status Bar Indicator
│   └── 显示会话状态
│
├── Problem Matcher
│   └── 在问题面板显示告警
│
└── Webview Panel
    └── 监控仪表板
```

---

## 📦 package.json 示例

```json
{
  "name": "ai-coding-monitoror",
  "displayName": "AI Coding Monitoror",
  "version": "0.1.0",
  "description": "Monitor and protect AI coding sessions",
  "engines": {
    "vscode": "^1.80.0"
  },
  "categories": ["Other", "Linters"],
  "activationEvents": [
    "onStartupFinished"
  ],
  "main": "./out/extension.js",
  "contributes": {
    "commands": [
      {
        "command": "monitoror.startSession",
        "title": "Monitoror: Start Session",
        "icon": "$(play)"
      },
      {
        "command": "monitoror.saveSnapshot",
        "title": "Monitoror: Save Snapshot",
        "icon": "$(save)"
      },
      {
        "command": "monitoror.validateCode",
        "title": "Monitoror: Validate Code",
        "icon": "$(check)"
      },
      {
        "command": "monitoror.showDashboard",
        "title": "Monitoror: Show Dashboard",
        "icon": "$(dashboard)"
      }
    ],
    "statusBarItems": [
      {
        "command": "monitoror.showDashboard",
        "alignment": "right",
        "text": "$(eye) Monitoror",
        "tooltip": "Show AI Coding Monitoror"
      }
    ],
    "configuration": {
      "title": "AI Coding Monitoror",
      "properties": {
        "monitoror.apiUrl": {
          "type": "string",
          "default": "http://localhost:8000",
          "description": "Monitoror API URL"
        },
        "monitoror.autoSnapshot": {
          "type": "boolean",
          "default": true,
          "description": "Auto-save snapshot before AI edit"
        },
        "monitoror.autoValidate": {
          "type": "boolean",
          "default": true,
          "description": "Auto-validate after AI edit"
        }
      }
    }
  },
  "scripts": {
    "vscode:prepublish": "npm run compile",
    "compile": "tsc -p ./",
    "watch": "tsc -watch -p ./"
  },
  "devDependencies": {
    "@types/node": "^18.0.0",
    "@types/vscode": "^1.80.0",
    "typescript": "^5.0.0"
  },
  "dependencies": {
    "axios": "^1.6.0"
  }
}
```

---

## 🔧 核心功能实现

### 1. 扩展入口 (extension.ts)

```typescript
import * as vscode from 'vscode';
import axios from 'axios';

const API_URL = vscode.workspace.getConfiguration('monitoror').get('apiUrl') || 'http://localhost:8000';

let currentSessionId: string | undefined;
let statusBarItem: vscode.StatusBarItem;

export function activate(context: vscode.ExtensionContext) {
  console.log('AI Coding Monitoror activated');

  // 创建状态栏按钮
  statusBarItem = vscode.window.createStatusBarItem(
    vscode.StatusBarAlignment.Right,
    100
  );
  statusBarItem.command = 'monitoror.showDashboard';
  statusBarItem.text = '$(eye) Monitoror';
  statusBarItem.show();

  // 注册命令
  context.subscriptions.push(
    vscode.commands.registerCommand('monitoror.startSession', startSession),
    vscode.commands.registerCommand('monitoror.saveSnapshot', saveSnapshot),
    vscode.commands.registerCommand('monitoror.validateCode', validateCode),
    vscode.commands.registerCommand('monitoror.showDashboard', showDashboard)
  );

  // 监听文件变更
  const watcher = vscode.workspace.createFileSystemWatcher(
    '**/*.py',
    false,
    false,
    false
  );

  watcher.onDidChange(async (uri) => {
    if (vscode.workspace.getConfiguration('monitoror').get('autoValidate', true)) {
      await validateCode(uri.fsPath);
    }
  });

  // 监听 AI 响应（通过 Chat API 或扩展事件）
  vscode.workspace.onDidSaveTextDocument(async (document) => {
    if (document.languageId === 'python' && currentSessionId) {
      // 记录代码变更
      await logAIResponse([document.fileName]);
    }
  });
}

async function startSession() {
  const projectPath = vscode.workspace.rootPath;
  if (!projectPath) {
    vscode.window.showErrorMessage('请打开一个工作区');
    return;
  }

  try {
    const response = await axios.post(`${API_URL}/sessions/init`, {
      project_path: projectPath,
      language: 'python',
      description: `VS Code Session: ${new Date().toISOString()}`
    });

    currentSessionId = response.data.session_id;
    statusBarItem.text = `$(eye) Monitoror ✓`;
    statusBarItem.tooltip = `Session: ${currentSessionId}`;

    vscode.window.showInformationMessage(`✅ 监控已启动: ${currentSessionId}`);
  } catch (error) {
    vscode.window.showErrorMessage(`启动失败: ${error}`);
  }
}

async function saveSnapshot(filePath?: string) {
  if (!currentSessionId) {
    vscode.window.showWarningMessage('请先启动监控会话');
    return;
  }

  if (!filePath) {
    filePath = vscode.window.activeTextEditor?.document.fileName;
  }

  if (!filePath) {
    vscode.window.showWarningMessage('没有活动的文件');
    return;
  }

  try {
    const content = await vscode.workspace.fs.readFile(
      vscode.Uri.file(filePath)
    );
    const contentStr = Buffer.from(content).toString('utf8');

    await axios.post(
      `${API_URL}/sessions/${currentSessionId}/snapshot`,
      {
        file_path: filePath,
        content: contentStr
      }
    );

    vscode.window.showInformationMessage(`💾 快照已保存: ${filePath}`);
  } catch (error) {
    vscode.window.showErrorMessage(`保存失败: ${error}`);
  }
}

async function validateCode(filePath?: string) {
  if (!currentSessionId) {
    return; // 静默失败，避免打扰
  }

  if (!filePath) {
    filePath = vscode.window.activeTextEditor?.document.fileName;
  }

  if (!filePath) {
    return;
  }

  try {
    const content = await vscode.workspace.fs.readFile(
      vscode.Uri.file(filePath)
    );
    const contentStr = Buffer.from(content).toString('utf8');

    const response = await axios.post(
      `${API_URL}/validate/code`,
      {
        file_path: filePath,
        content: contentStr
      }
    );

    const issues = response.data.issues || [];

    if (issues.length > 0) {
      // 在问题面板显示
      const diagnostics: vscode.Diagnostic[] = issues.map((issue: any) => {
        const diagnostic = new vscode.Diagnostic(
          new vscode.Range(0, 0, 0, 0),
          issue.message,
          getSeverity(issue.type)
        );
        diagnostic.code = issue.type;
        return diagnostic;
      });

      const diagnosticCollection = vscode.languages.createDiagnosticCollection(
        'monitoror'
      );
      diagnosticCollection.set(vscode.Uri.file(filePath), diagnostics);

      vscode.window.showWarningMessage(
        `⚠️ 发现 ${issues.length} 个问题，请查看问题面板`
      );
    }
  } catch (error) {
    console.error('验证失败:', error);
  }
}

async function logAIResponse(changedFiles: string[]) {
  if (!currentSessionId) {
    return;
  }

  try {
    const codeChanges = [];

    for (const filePath of changedFiles) {
      const content = await vscode.workspace.fs.readFile(
        vscode.Uri.file(filePath)
      );
      codeChanges.push({
        file_path: filePath,
        content: Buffer.from(content).toString('utf8')
      });
    }

    const response = await axios.post(
      `${API_URL}/analyze/ai-response`,
      {
        response_id: `vscode_${Date.now()}`,
        request_id: `vscode_${Date.now()}`,
        code_changes: codeChanges
      }
    );

    const alerts = response.data.alerts || [];

    if (alerts.length > 0) {
      for (const alert of alerts) {
        if (alert.severity === 'CRITICAL') {
          vscode.window.showErrorMessage(
            `[${alert.type}] ${alert.message}`,
            '查看详情',
            '忽略'
          );
        } else {
          vscode.window.showWarningMessage(
            `[${alert.type}] ${alert.message}`
          );
        }
      }
    }
  } catch (error) {
    console.error('记录失败:', error);
  }
}

async function showDashboard() {
  const panel = vscode.window.createWebviewPanel(
    'monitororDashboard',
    'AI Coding Monitoror',
    vscode.ViewColumn.Two,
    {
      enableScripts: true
    }
  );

  panel.webview.html = getDashboardWebviewContent(currentSessionId);
}

function getSeverity(type: string): vscode.DiagnosticSeverity {
  switch (type) {
    case 'ERROR':
    case 'REGRESSION':
      return vscode.DiagnosticSeverity.Error;
    case 'WARNING':
      return vscode.DiagnosticSeverity.Warning;
    default:
      return vscode.DiagnosticSeverity.Information;
  }
}

function getDashboardWebviewContent(sessionId: string | undefined): string {
  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>AI Coding Monitoror</title>
  <style>
    body { font-family: var(--vscode-font-family); padding: 20px; }
    .header { margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid var(--vscode-panel-border); }
    .session-id { color: var(--vscode-textLink-foreground); }
    .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 20px 0; }
    .stat-card { padding: 15px; background: var(--vscode-editor-background); border: 1px solid var(--vscode-panel-border); border-radius: 5px; }
    .stat-value { font-size: 24px; font-weight: bold; color: var(--vscode-textLink-foreground); }
    .stat-label { font-size: 12px; color: var(--vscode-descriptionForeground); }
    .alerts { margin-top: 20px; }
    .alert { padding: 10px; margin: 5px 0; border-left: 4px solid; background: var(--vscode-editor-background); }
    .alert.critical { border-color: #f44336; }
    .alert.warning { border-color: #ff9800; }
    .alert.info { border-color: #2196f3; }
  </style>
</head>
<body>
  <div class="header">
    <h1>AI Coding Monitoror</h1>
    <p>会话 ID: <span class="session-id">${sessionId || '未启动'}</span></p>
  </div>

  <div class="stats">
    <div class="stat-card">
      <div class="stat-value" id="snapshots">-</div>
      <div class="stat-label">代码快照</div>
    </div>
    <div class="stat-card">
      <div class="stat-value" id="alerts">-</div>
      <div class="stat-label">告警数量</div>
    </div>
    <div class="stat-card">
      <div class="stat-value" id="files">-</div>
      <div class="stat-label">活跃文件</div>
    </div>
  </div>

  <div class="alerts">
    <h3>最近告警</h3>
    <div id="alerts-list"></div>
  </div>

  <script>
    const vscode = acquireVsCodeApi();
    // 这里可以添加从 API 获取实时数据的逻辑
  </script>
</body>
</html>
  `;
}

export function deactivate() {
  statusBarItem.dispose();
}
```

---

## 🚀 快速开始

### 1. 初始化项目

```bash
mkdir ai-coding-monitoror-vscode
cd ai-coding-monitoror-vscode

npm init -y
npm install -D @types/node @types/vscode typescript
npm install axios
```

### 2. 配置 TypeScript

```json
{
  "compilerOptions": {
    "module": "commonjs",
    "target": "es2020",
    "outDir": "out",
    "lib": ["es2020"],
    "sourceMap": true,
    "rootDir": "src",
    "strict": true
  },
  "exclude": ["node_modules", ".vscode-test"]
}
```

### 3. 安装并运行

```bash
# 打包扩展
npm install -g vsce
vsce package

# 或在 VS Code 中
# 按 F5 启动扩展开发宿主
```

---

## 🎯 核心特性

### ✅ 自动监控

- 监听文件保存事件
- 自动保存快照
- 自动验证代码
- 自动记录 AI 响应

### ✅ 实时告警

- 在问题面板显示
- 状态栏指示
- 弹窗通知（严重告警）

### ✅ 快捷命令

- `Ctrl+Shift+M` → 启动会话
- `Ctrl+Shift+S` → 保存快照
- `Ctrl+Shift+V` → 验证代码
- `Ctrl+Shift+D` → 显示仪表板

---

## 📊 效果预览

### 状态栏

```
[👁 Monitoror ✓]  ← 绿色=运行中
[👁 Monitoror]    ← 灰色=未启动
[👁 Monitoror ⚠]  ← 黄色=有告警
[👁 Monitoror ❌]  ← 红色=严重错误
```

### 问题面板

```
问题 (监视器)
├── [REGRESSION] 函数 'validate_user' 已被删除  (main.py:1)
├── [ERROR] 语法错误: invalid syntax (auth.py:45)
└── [WARNING] 类型检查失败: 类型不匹配 (utils.py:23)
```

---

## 🔗 与现有 AI 工具集成

### Copilot 集成

监听 `vscode.notebook` 事件：

```typescript
vscode.notebooks.onDidChangeCellContents(async (event) => {
  // 捕获 Copilot 生成的代码
  await saveSnapshot(event.document.uri.fsPath);
  await validateCode(event.document.uri.fsPath);
});
```

### Cursor 集成

使用 Cursor 提供的扩展 API：

```typescript
// Cursor 提供的特殊事件
vscode.workspace.onDidReceiveAICompletion(async (completion) => {
  await logAIResponse([completion.filePath]);
});
```

---

## 📝 后续开发计划

- [ ] 支持更多语言 (JS, TS, Go, Java)
- [ ] Git 集成 (commit hook)
- [ ] 代码差异可视化
- [ ] 一键回滚功能
- [ ] 团队协作 (共享会话)
- [ ] 性能优化 (增量分析)

---

**版本**: 0.1.0  
**更新日期**: 2026-02-17
