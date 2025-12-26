#!/bin/bash

# ============================================
# 快速更新腳本（一鍵更新）
# ============================================
# 用途: 快速從 Git 拉取並重新部署
# 使用: ./quick-update.sh
# ============================================

set -e

echo "🚀 開始快速更新..."
echo ""

# 拉取最新代碼
echo "📥 拉取最新代碼..."
git pull origin master

# 重新啟動容器（使用標準 docker-compose.yml）
echo "🔄 重新啟動 Docker 容器..."
sudo docker compose down
sudo docker compose up -d --build

# 等待服務啟動
echo "⏳ 等待服務啟動..."
sleep 5

# 檢查健康狀態
if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
    echo ""
    echo "✅ 更新完成！服務已就緒"
    echo ""
    echo "📝 最新提交:"
    git log -1 --oneline
    echo ""
    echo "🔧 查看日誌: sudo docker compose logs -f"
else
    echo ""
    echo "⚠️  服務可能未正常啟動，請檢查日誌:"
    echo "   sudo docker compose logs"
fi

echo ""
