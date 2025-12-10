#!/bin/bash                                                                                                                                                           │
│                                                                                                                                                                       │
│ # ============================================                                                                                                                        │
│ # 股票分析 Web 應用快速部署腳本                                                                                                                                       │
│ # ============================================                                                                                                                        │
│                                                                                                                                                                       │
│ set -e  # 遇到錯誤立即退出                                                                                                                                            │
│                                                                                                                                                                       │
│ # 顏色輸出                                                                                                                                                            │
│ RED='\033[0;31m'                                                                                                                                                      │
│ GREEN='\033[0;32m'                                                                                                                                                    │
│ YELLOW='\033[1;33m'                                                                                                                                                   │
│ BLUE='\033[0;34m'                                                                                                                                                     │
│ NC='\033[0m' # No Color                                                                                                                                               │
│                                                                                                                                                                       │
│ # 函數：打印訊息                                                                                                                                                      │
│ print_info() {                                                                                                                                                        │
│     echo -e "${BLUE}[INFO]${NC} $1"                                                                                                                                   │
│ }                                                                                                                                                                     │
│                                                                                                                                                                       │
│ print_success() {                                                                                                                                                     │
│     echo -e "${GREEN}[SUCCESS]${NC} $1"                                                                                                                               │
│ }                                                                                                                                                                     │
│                                                                                                                                                                       │
│ print_warning() {                                                                                                                                                     │
│     echo -e "${YELLOW}[WARNING]${NC} $1"                                                                                                                              │
│ }                                                                                                                                                                     │
│                                                                                                                                                                       │
│ print_error() {                                                                                                                                                       │
│     echo -e "${RED}[ERROR]${NC} $1"                                                                                                                                   │
│ }                                                                                                                                                                     │
│                                                                                                                                                                       │
│ # 檢查是否為 root 用戶                                                                                                                                                │
│ check_root() {                                                                                                                                                        │
│     if [ "$EUID" -eq 0 ]; then                                                                                                                                        │
│         print_warning "建議不要使用 root 用戶運行此腳本"                                                                                                              │
│         read -p "是否繼續？(y/n) " -n 1 -r                                                                                                                            │
│         echo                                                                                                                                                          │
│         if [[ ! $REPLY =~ ^[Yy]$ ]]; then                                                                                                                             │
│             exit 1                                                                                                                                                    │
│         fi                                                                                                                                                            │
│     fi                                                                                                                                                                │
│ }                                                                                                                                                                     │
│                                                                                                                                                                       │
│ # 檢查系統                                                                                                                                                            │
│ check_system() {                                                                                                                                                      │
│     print_info "檢查系統環境..."                                                                                                                                      │
│                                                                                                                                                                       │
│     # 檢查操作系統                                                                                                                                                    │
│     if [ -f /etc/os-release ]; then                                                                                                                                   │
│         . /etc/os-release                                                                                                                                             │
│         OS=$NAME                                                                                                                                                      │
│         VER=$VERSION_ID                                                                                                                                               │
│         print_success "作業系統: $OS $VER"                                                                                                                            │
│     else                                                                                                                                                              │
│         print_error "無法識別作業系統"                                                                                                                                │
│         exit 1                                                                                                                                                        │
│     fi                                                                                                                                                                │
│                                                                                                                                                                       │
│     # 檢查網路連接                                                                                                                                                    │
│     if ping -c 1 google.com &> /dev/null; then                                                                                                                        │
│         print_success "網路連接正常"                                                                                                                                  │
│     else                                                                                                                                                              │
│         print_error "無網路連接"                                                                                                                                      │
│         exit 1                                                                                                                                                        │
│     fi                                                                                                                                                                │
│ }                                                                                                                                                                     │
│                                                                                                                                                                       │
│ # 安裝 Docker                                                                                                                                                         │
│ install_docker() {                                                                                                                                                    │
│     print_info "檢查 Docker..."                                                                                                                                       │
│                                                                                                                                                                       │
│     if command -v docker &> /dev/null; then                                                                                                                           │
│         print_success "Docker 已安裝: $(docker --version)"                                                                                                            │
│     else                                                                                                                                                              │
│         print_info "安裝 Docker..."                                                                                                                                   │
│         curl -fsSL https://get.docker.com -o get-docker.sh                                                                                                            │
│         sudo sh get-docker.sh                                                                                                                                         │
│         sudo systemctl start docker                                                                                                                                   │
│         sudo systemctl enable docker                                                                                                                                  │
│                                                                                                                                                                       │
│         # 將當前用戶添加到 docker 群組                                                                                                                                │
│         sudo usermod -aG docker $USER                                                                                                                                 │
│         print_success "Docker 安裝完成"                                                                                                                               │
│         print_warning "請登出後重新登入以使 Docker 權限生效"                                                                                                          │
│     fi                                                                                                                                                                │
│ }                                                                                                                                                                     │
│                                                                                                                                                                       │
│ # 安裝 Docker Compose                                                                                                                                                 │
│ install_docker_compose() {                                                                                                                                            │
│     print_info "檢查 Docker Compose..."                                                                                                                               │
│                                                                                                                                                                       │
│     if command -v docker-compose &> /dev/null; then                                                                                                                   │
│         print_success "Docker Compose 已安裝: $(docker-compose --version)"                                                                                            │
│     else                                                                                                                                                              │
│         print_info "安裝 Docker Compose..."                                                                                                                           │
│         sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose             │
│         sudo chmod +x /usr/local/bin/docker-compose                                                                                                                   │
│         print_success "Docker Compose 安裝完成"                                                                                                                       │
│     fi                                                                                                                                                                │
│ }                                                                                                                                                                     │
│                                                                                                                                                                       │
│ # 設定防火牆                                                                                                                                                          │
│ setup_firewall() {                                                                                                                                                    │
│     print_info "設定防火牆..."                                                                                                                                        │
│                                                                                                                                                                       │
│     if command -v ufw &> /dev/null; then                                                                                                                              │
│         print_info "配置 UFW 防火牆..."                                                                                                                               │
│                                                                                                                                                                       │
│         sudo ufw --force enable                                                                                                                                       │
│         sudo ufw default deny incoming                                                                                                                                │
│         sudo ufw default allow outgoing                                                                                                                               │
│         sudo ufw allow ssh                                                                                                                                            │
│         sudo ufw allow 80/tcp                                                                                                                                         │
│         sudo ufw allow 443/tcp                                                                                                                                        │
│                                                                                                                                                                       │
│         print_success "防火牆設定完成"                                                                                                                                │
│     else                                                                                                                                                              │
│         print_warning "UFW 未安裝，跳過防火牆設定"                                                                                                                    │
│     fi                                                                                                                                                                │
│ }                                                                                                                                                                     │
│                                                                                                                                                                       │
│ # 創建環境變數文件                                                                                                                                                    │
│ create_env_file() {                                                                                                                                                   │
│     print_info "創建環境變數文件..."                                                                                                                                  │
│                                                                                                                                                                       │
│     if [ -f .env ]; then                                                                                                                                              │
│         print_warning ".env 文件已存在"                                                                                                                               │
│         read -p "是否覆蓋？(y/n) " -n 1 -r                                                                                                                            │
│         echo                                                                                                                                                          │
│         if [[ ! $REPLY =~ ^[Yy]$ ]]; then                                                                                                                             │
│             return                                                                                                                                                    │
│         fi                                                                                                                                                            │
│     fi                                                                                                                                                                │
│                                                                                                                                                                       │
│     # 生成隨機 SECRET_KEY                                                                                                                                             │
│     SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || openssl rand -hex 32)                                                       │
│                                                                                                                                                                       │
│     # 讀取域名                                                                                                                                                        │
│     read -p "請輸入您的域名（例如：example.com，留空表示使用 IP）: " DOMAIN                                                                                           │
│                                                                                                                                                                       │
│     # 創建 .env 文件                                                                                                                                                  │
│     cat > .env <<EOF                                                                                                                                                  │
│ # Flask 配置                                                                                                                                                          │
│ FLASK_ENV=production                                                                                                                                                  │
│ SECRET_KEY=$SECRET_KEY                                                                                                                                                │
│ HOST=0.0.0.0                                                                                                                                                          │
│ PORT=5000                                                                                                                                                             │
│                                                                                                                                                                       │
│ # 域名配置                                                                                                                                                            │
│ ${DOMAIN:+DOMAIN=$DOMAIN}                                                                                                                                             │
│                                                                                                                                                                       │
│ # 數據配置                                                                                                                                                            │
│ DEFAULT_START_DATE=2024-01-01                                                                                                                                         │
│ DEFAULT_PLOT_DAYS=120                                                                                                                                                 │
│                                                                                                                                                                       │
│ # 日誌配置                                                                                                                                                            │
│ LOG_LEVEL=INFO                                                                                                                                                        │
│ LOG_FILE=data/logs/app.log                                                                                                                                            │
│                                                                                                                                                                       │
│ # CORS 配置                                                                                                                                                           │
│ CORS_ORIGINS=*                                                                                                                                                        │
│                                                                                                                                                                       │
│ # 快取配置                                                                                                                                                            │
│ CACHE_EXPIRY_DAYS=7                                                                                                                                                   │
│ MAX_CACHED_STOCKS=50                                                                                                                                                  │
│ EOF                                                                                                                                                                   │
│                                                                                                                                                                       │
│     print_success ".env 文件創建完成"                                                                                                                                 │
│ }                                                                                                                                                                     │
│                                                                                                                                                                       │
│ # 構建並啟動應用                                                                                                                                                      │
│ start_application() {                                                                                                                                                 │
│     print_info "啟動應用程式..."                                                                                                                                      │
│                                                                                                                                                                       │
│     # 選擇部署模式                                                                                                                                                    │
│     echo ""                                                                                                                                                           │
│     echo "請選擇部署模式："                                                                                                                                           │
│     echo "1) 簡單模式（僅應用，端口 5000）"                                                                                                                           │
│     echo "2) 完整模式（應用 + Nginx，端口 80/443）"                                                                                                                   │
│     read -p "選擇 (1/2): " MODE                                                                                                                                       │
│                                                                                                                                                                       │
│     case $MODE in                                                                                                                                                     │
│         1)                                                                                                                                                            │
│             print_info "使用簡單模式部署..."                                                                                                                          │
│             docker-compose -f docker-compose.simple.yml up -d --build                                                                                                 │
│             ;;                                                                                                                                                        │
│         2)                                                                                                                                                            │
│             print_info "使用完整模式部署..."                                                                                                                          │
│             docker-compose up -d --build                                                                                                                              │
│             ;;                                                                                                                                                        │
│         *)                                                                                                                                                            │
│             print_error "無效的選擇"                                                                                                                                  │
│             exit 1                                                                                                                                                    │
│             ;;                                                                                                                                                        │
│     esac                                                                                                                                                              │
│                                                                                                                                                                       │
│     # 等待容器啟動                                                                                                                                                    │
│     sleep 5                                                                                                                                                           │
│                                                                                                                                                                       │
│     # 檢查容器狀態                                                                                                                                                    │
│     if docker ps | grep -q "stock-analysis"; then                                                                                                                     │
│         print_success "應用程式啟動成功！"                                                                                                                            │
│     else                                                                                                                                                              │
│         print_error "應用程式啟動失敗"                                                                                                                                │
│         docker-compose logs                                                                                                                                           │
│         exit 1                                                                                                                                                        │
│     fi                                                                                                                                                                │
│ }                                                                                                                                                                     │
│                                                                                                                                                                       │
│ # 安裝 SSL 證書                                                                                                                                                       │
│ install_ssl() {                                                                                                                                                       │
│     print_info "設定 SSL 證書..."                                                                                                                                     │
│                                                                                                                                                                       │
│     if [ -z "$DOMAIN" ]; then                                                                                                                                         │
│         print_warning "未設定域名，跳過 SSL 設定"                                                                                                                     │
│         return                                                                                                                                                        │
│     fi                                                                                                                                                                │
│                                                                                                                                                                       │
│     read -p "是否安裝 Let's Encrypt SSL 證書？(y/n) " -n 1 -r                                                                                                         │
│     echo                                                                                                                                                              │
│     if [[ ! $REPLY =~ ^[Yy]$ ]]; then                                                                                                                                 │
│         return                                                                                                                                                        │
│     fi                                       
                                                                                                                         │
│                                                                                                                                                                       │
│     # 安裝 Certbot                                                                                                                                                    │
│     if ! command -v certbot &> /dev/null; then                                                                                                                        │
│         print_info "安裝 Certbot..."                                                                                                                                  │
│         sudo apt update                                                                                                                                               │
│         sudo apt install -y certbot python3-certbot-nginx                                                                                                             │
│     fi                                                                                                                                                                │
│                                                                                                                                                                       │
│     # 獲取證書                                                                                                                                                        │
│     print_info "獲取 SSL 證書..."                                                                                                                                     │
│     sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN                                                                                                                    │
│                                                                                                                                                                       │
│     print_success "SSL 證書安裝完成"                                                                                                                                  │
│ }                                                                                                                                                                     │
│                                                                                                                                                                       │
│ # 顯示訪問資訊                                                                                                                                                        │
│ show_access_info() {                                                                                                                                                  │
│     echo ""                                                                                                                                                           │
│     echo "============================================"                                                                                                               │
│     print_success "部署完成！"                                                                                                                                        │
│     echo "============================================"                                                                                                               │
│     echo ""                                                                                                                                                           │
│                                                                                                                                                                       │
│     # 獲取公網 IP                                                                                                                                                     │
│     PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "無法獲取")                                                                                                   │
│                                                                                                                                                                       │
│     if [ -n "$DOMAIN" ]; then                                                                                                                                         │
│         echo "🌐 應用網址: https://$DOMAIN"                                                                                                                           │
│         echo "🌐 備用網址: http://$DOMAIN"                                                                                                                            │
│     else                                                                                                                                                              │
│         echo "🌐 應用網址: http://$PUBLIC_IP:5000"                                                                                                                    │
│     fi                                                                                                                                                                │
│                                                                                                                                                                       │
│     echo ""                                                                                                                                                           │
│     echo "📊 API 健康檢查: http://$PUBLIC_IP:5000/api/health"                                                                                                         │
│     echo ""                                                                                                                                                           │
│     echo "🔧 管理命令："                                                                                                                                              │
│     echo "   查看日誌: docker-compose logs -f"                                                                                                                        │
│     echo "   停止應用: docker-compose down"                                                                                                                           │
│     echo "   重啟應用: docker-compose restart"                                                                                                                        │
│     echo "   更新應用: git pull && docker-compose up -d --build"                                                                                                      │
│     echo ""                                                                                                                                                           │
│     echo "============================================"                                                                                                               │
│ }                                                                                                                                                                     │
│                                                                                                                                                                       │
│ # 主函數                                                                                                                                                              │
│ main() {                                                                                                                                                              │
│     echo "============================================"                                                                                                               │
│     echo "   股票分析 Web 應用 - 快速部署腳本"                                                                                                                        │
│     echo "============================================"                                                                                                               │
│     echo ""                                                                                                                                                           │
│                                                                                                                                                                       │
│     check_root                                                                                                                                                        │
│     check_system                                                                                                                                                      │
│     install_docker                                                                                                                                                    │
│     install_docker_compose                                                                                                                                            │
│     setup_firewall                                                                                                                                                    │
│     create_env_file                                                                                                                                                   │
│     start_application                                                                                                                                                 │
│     install_ssl                                                                                                                                                       │
│     show_access_info                                                                                                                                                  │
│                                                                                                                                                                       │
│     echo ""                                                                                                                                                           │
│     print_success "部署流程完成！"                                                                                                                                    │
│     echo ""                                                                                                                                                           │
│ }                                                                                                                                                                     │
│                                                                                                                                                                       │
│ # 執行主函數                                                                                                                                                          │
│ main                            