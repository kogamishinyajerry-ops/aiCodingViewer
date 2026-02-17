#!/bin/bash
# 自动上传到 GitHub 脚本

set -e

echo "=========================================="
echo "自动上传到 GitHub 脚本"
echo "=========================================="
echo ""

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo "检测到未提交的更改，正在提交..."
    echo ""

    # 添加所有更改
    git add -A

    # 获取当前时间作为提交信息
    current_time=$(date "+%Y-%m-%d %H:%M:%S")
    commit_message="feat: 更新项目 - $current_time"

    # 提交更改
    git commit -m "$commit_message"

    echo "✅ 提交完成"
    echo ""
fi

# 推送到 GitHub
echo "正在推送到 GitHub..."
echo ""

git push -u origin main

echo ""
echo "✅ 推送完成！"
echo ""
echo "项目地址: https://github.com/kogamishinyajerry-ops/aiHolmes"
echo ""
