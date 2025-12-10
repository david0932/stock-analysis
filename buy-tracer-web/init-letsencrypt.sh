#!/bin/bash

# ============================================
# Let's Encrypt SSL 證書初始化腳本
# ============================================

set -e

# 配置
DOMAIN="tearice.win"
EMAIL="your-email@example.com"  # 請修改為您的電子郵件
STAGING=0  # 設為 1 使用測試環境，設為 0 使用正式環境

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "============================================"
echo "   Let's Encrypt SSL 證書初始化"
echo "============================================"
echo ""

# 檢查域名
if [ -z "$DOMAIN" ] || [ "$DOMAIN" = "tearice.win" ]; then
    print_warning "請檢查域名設定"
fi

# 檢查電子郵件
if [ "$EMAIL" = "your-email@example.com" ]; then
    read -p "請輸入您的電子郵件地址: " EMAIL
fi

print_info "域名: $DOMAIN"
print_info "電子郵件: $EMAIL"
echo ""

# 確認
read -p "繼續嗎？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# 創建必要的目錄
print_info "創建必要的目錄..."
mkdir -p certbot/conf
mkdir -p certbot/www
mkdir -p certbot/logs

# 檢查是否已有證書
if [ -d "certbot/conf/live/$DOMAIN" ]; then
    print_warning "已存在 $DOMAIN 的證書"
    read -p "是否續期現有證書？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "續期證書..."
        docker-compose run --rm certbot renew
        print_success "證書續期完成"
        exit 0
    else
        exit 0
    fi
fi

# 下載 TLS 參數
if [ ! -e "certbot/conf/options-ssl-nginx.conf" ] || [ ! -e "certbot/conf/ssl-dhparams.pem" ]; then
    print_info "下載推薦的 TLS 參數..."
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "certbot/conf/options-ssl-nginx.conf"
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > "certbot/conf/ssl-dhparams.pem"
    print_success "TLS 參數下載完成"
fi

# 啟動 nginx（不含 SSL）
print_info "啟動 nginx..."
docker-compose up -d nginx

# 等待 nginx 啟動
print_info "等待 nginx 啟動..."
sleep 5

# 刪除現有的 nginx 容器中的證書掛載（如果存在）
print_info "準備獲取證書..."

# 設定證書請求參數
CERTBOT_ARGS="certonly --webroot -w /var/www/certbot"
CERTBOT_ARGS="$CERTBOT_ARGS --email $EMAIL"
CERTBOT_ARGS="$CERTBOT_ARGS -d $DOMAIN -d www.$DOMAIN"
CERTBOT_ARGS="$CERTBOT_ARGS --agree-tos"
CERTBOT_ARGS="$CERTBOT_ARGS --no-eff-email"

if [ $STAGING != "0" ]; then
    CERTBOT_ARGS="$CERTBOT_ARGS --staging"
    print_warning "使用測試環境（Staging）"
fi

# 獲取證書
print_info "請求 Let's Encrypt 證書..."
docker-compose run --rm certbot $CERTBOT_ARGS

if [ $? -eq 0 ]; then
    print_success "證書獲取成功！"

    # 重啟 nginx 以加載證書
    print_info "重啟 nginx 以啟用 SSL..."
    docker-compose restart nginx

    # 啟動 certbot 自動續期服務
    print_info "啟動證書自動續期服務..."
    docker-compose up -d certbot

    echo ""
    echo "============================================"
    print_success "SSL 證書設置完成！"
    echo "============================================"
    echo ""
    echo "您的網站現在可以通過以下網址訪問："
    echo "  - https://$DOMAIN"
    echo "  - https://www.$DOMAIN"
    echo ""
    echo "證書將每 12 小時自動檢查續期"
    echo "Nginx 將每 6 小時自動重載配置"
    echo ""
else
    print_error "證書獲取失敗"
    print_info "請檢查："
    print_info "  1. 域名 DNS 是否正確指向此伺服器"
    print_info "  2. 防火牆是否開放 80 和 443 端口"
    print_info "  3. Docker 容器是否正常運行"
    echo ""
    print_info "查看詳細日誌："
    echo "  docker-compose logs nginx"
    echo "  docker-compose logs certbot"
    exit 1
fi
