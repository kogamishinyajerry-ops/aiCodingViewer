#!/usr/bin/env python3
"""
快速启动示例 - 在当前 AI coding 会话中立即使用
"""

import requests
import json
import os
from pathlib import Path

# 配置
MONITOROR_URL = "http://localhost:8000"
DATA_DIR = Path.home() / ".monitoror"
SESSION_FILE = DATA_DIR / "current_session.json"

class QuickMonitor:
    """简化的监控器，适合快速使用"""
    
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.session_id = self._load_session()
    
    def _load_session(self):
        """加载当前会话"""
        if SESSION_FILE.exists():
            with open(SESSION_FILE) as f:
                data = json.load(f)
                return data.get("session_id")
        return None
    
    def _save_session(self, session_id):
        """保存会话"""
        with open(SESSION_FILE, "w") as f:
            json.dump({
                "session_id": session_id,
                "created_at": str(Path.ctime(SESSION_FILE))
            }, f, indent=2)
        self.session_id = session_id
    
    def start(self, project_path, description=""):
        """开始监控"""
        if self.session_id:
            print(f"✅ 已有活跃会话: {self.session_id}")
            return self.session_id
        
        try:
            response = requests.post(
                f"{MONITOROR_URL}/sessions/init",
                json={
                    "project_path": project_path,
                    "language": "python",
                    "description": description
                },
                timeout=5
            )
            
            if response.status_code == 200:
                session_id = response.json()["session_id"]
                self._save_session(session_id)
                print(f"✅ 监控已启动，会话 ID: {session_id}")
                print(f"📊 前端界面: http://localhost:8001")
                return session_id
            else:
                print(f"❌ 启动失败: {response.text}")
                return None
        except Exception as e:
            print(f"❌ 连接失败，请确保监控服务已启动")
            print(f"   启动命令: cd /workspace/ai_coding_monitoror && ./start.sh")
            return None
    
    def snapshot(self, file_path):
        """保存文件快照"""
        if not self.session_id:
            print("⚠️  请先调用 start()")
            return
        
        try:
            content = Path(file_path).read_text()
            response = requests.post(
                f"{MONITOROR_URL}/sessions/{self.session_id}/snapshot",
                json={"file_path": file_path, "content": content},
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"💾 快照已保存: {file_path}")
            else:
                print(f"⚠️  快照保存失败: {response.text}")
        except Exception as e:
            print(f"⚠️  快照保存失败: {e}")
    
    def validate(self, file_path):
        """验证代码"""
        if not self.session_id:
            print("⚠️  请先调用 start()")
            return
        
        try:
            content = Path(file_path).read_text()
            response = requests.post(
                f"{MONITOROR_URL}/validate/code",
                json={"file_path": file_path, "content": content},
                timeout=5
            )
            
            result = response.json()
            issues = result.get("issues", [])
            
            if issues:
                print(f"❌ 发现 {len(issues)} 个问题:")
                for i, issue in enumerate(issues, 1):
                    print(f"   {i}. [{issue['type']}] {issue['message']}")
            else:
                print(f"✅ {file_path} 验证通过")
            
            return result
        except Exception as e:
            print(f"⚠️  验证失败: {e}")
            return None
    
    def log_request(self, prompt):
        """记录 AI 请求"""
        if not self.session_id:
            print("⚠️  请先调用 start()")
            return
        
        try:
            import uuid
            response = requests.post(
                f"{MONITOROR_URL}/analyze/ai-request",
                json={
                    "request_id": str(uuid.uuid4()),
                    "prompt": prompt,
                    "context": {}
                },
                timeout=5
            )
            
            print(f"📝 请求已记录: {prompt[:60]}...")
            return response.json()
        except Exception as e:
            print(f"⚠️  记录失败: {e}")
            return None
    
    def log_response(self, changed_files):
        """记录 AI 响应"""
        if not self.session_id:
            print("⚠️  请先调用 start()")
            return
        
        try:
            import uuid
            code_changes = []
            
            for file_path in changed_files:
                if Path(file_path).exists():
                    content = Path(file_path).read_text()
                    code_changes.append({
                        "file_path": file_path,
                        "content": content
                    })
            
            response = requests.post(
                f"{MONITOROR_URL}/analyze/ai-response",
                json={
                    "response_id": str(uuid.uuid4()),
                    "request_id": str(uuid.uuid4()),
                    "code_changes": code_changes
                },
                timeout=5
            )
            
            result = response.json()
            
            # 显示告警
            alerts = result.get("alerts", [])
            if alerts:
                print(f"⚠️  检测到 {len(alerts)} 个告警:")
                for alert in alerts:
                    severity = alert.get("severity", "INFO")
                    print(f"   [{severity}] {alert['message']}")
            else:
                print("✅ 代码变更分析通过")
            
            return result
        except Exception as e:
            print(f"⚠️  分析失败: {e}")
            return None
    
    def get_stats(self):
        """获取统计信息"""
        if not self.session_id:
            print("⚠️  请先调用 start()")
            return
        
        try:
            response = requests.get(
                f"{MONITOROR_URL}/sessions/{self.session_id}/context",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n📊 会话统计:")
                print(f"   会话 ID: {self.session_id}")
                print(f"   快照数量: {len(data.get('snapshots', []))}")
                print(f"   活跃文件: {len(data.get('active_files', []))}")
                print(f"   上下文长度: {len(str(data.get('context', '')))} 字符")
                return data
        except Exception as e:
            print(f"⚠️  获取统计失败: {e}")
            return None

# ============== 使用示例 ==============

if __name__ == "__main__":
    print("🚀 AI Coding Monitoror - 快速启动")
    print("=" * 50)
    
    # 创建监控器实例
    monitor = QuickMonitor()
    
    # 1. 开始监控
    print("\n[步骤 1] 初始化监控会话")
    monitor.start(
        project_path="/workspace",
        description="AI coding 示例会话"
    )
    
    # 2. 保存初始快照
    print("\n[步骤 2] 保存示例文件快照")
    example_file = __file__
    if Path(example_file).exists():
        monitor.snapshot(example_file)
    
    # 3. 记录一个 AI 请求
    print("\n[步骤 3] 模拟 AI 请求")
    monitor.log_request("优化代码性能，添加缓存机制")
    
    # 4. 验证代码
    print("\n[步骤 4] 验证示例文件")
    monitor.validate(example_file)
    
    # 5. 记录 AI 响应（模拟代码变更）
    print("\n[步骤 5] 模拟 AI 响应")
    monitor.log_response([example_file])
    
    # 6. 查看统计
    print("\n[步骤 6] 查看会话统计")
    monitor.get_stats()
    
    print("\n" + "=" * 50)
    print("✅ 示例完成！")
    print("\n💡 提示: 在您的代码中导入并使用:")
    print("   from quick_start import monitor")
    print("   monitor.start('/workspace/your/project')")
    print("   monitor.snapshot('your_file.py')")
    print("   monitor.validate('your_file.py')")
