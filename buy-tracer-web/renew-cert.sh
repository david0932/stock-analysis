#!/bin/bash

# ============================================
# Let's Encrypt 證書手動續期腳本
# ============================================

set -e

# 顏色輸出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}[INFO]${NC} 開始續期 Let's Encrypt 證書..."

# 續期證書
sudo docker compose run --rm certbot renew

# 重載 nginx
sudo docker compose exec nginx nginx -s reload

echo -e "${GREEN}[SUCCESS]${NC} 證書續期完成並已重載 nginx"
