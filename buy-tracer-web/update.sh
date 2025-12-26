#!/bin/bash

# ============================================
# 股票分析 Web 應用 - Docker 更新腳本
# ============================================
# 用途: 從 Git 拉取最新代碼並更新 Docker 容器
# 使用: ./update.sh [options]
# ============================================

set -e  # 遇到錯誤立即退出

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 預設值
COMPOSE_FILE="docker-compose.yml"
SKIP_BACKUP=false
SKIP_GIT_PULL=false
FORCE_REBUILD=false

# 函數：打印訊息
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

print_step() {
    echo -e "${CYAN}==>${NC} $1"
}

# 顯示使用說明
show_usage() {
    cat << EOF
使用方法: ./update.sh [選項]

選項:
    -h, --help              顯示此幫助訊息
    -s, --simple            使用簡單模式部署（僅應用）
    -f, --force             強制重新構建映像
    --skip-backup           跳過資料備份
    --skip-git-pull         跳過 Git 拉取（僅重啟容器）

範例:
    ./update.sh                 # 標準更新（拉取代碼 + 重新部署）
    ./update.sh --simple        # 使用簡單模式更新
    ./update.sh --skip-git-pull # 僅重啟容器，不拉取代碼
    ./update.sh -f              # 強制重新構建映像

EOF
}

# 解析命令列參數
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -s|--simple)
                COMPOSE_FILE="docker-compose.simple.yml"
                shift
                ;;
            -f|--force)
                FORCE_REBUILD=true
                shift
                ;;
            --skip-backup)
                SKIP_BACKUP=true
                shift
                ;;
            --skip-git-pull)
                SKIP_GIT_PULL=true
                shift
                ;;
            *)
                print_error "未知選項: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

# 檢查 Docker 和 Docker Compose
check_docker() {
    print_step "檢查 Docker 環境..."

    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安裝"
        exit 1
    fi

    # 檢查是否可以使用 docker（需要 sudo 或在 docker 群組中）
    if ! sudo docker ps &> /dev/null; then
        print_error "無法執行 Docker 命令，請確認權限"
        exit 1
    fi

    print_success "Docker 環境正常"
}

# 顯示當前狀態
show_current_status() {
    print_step "當前部署狀態..."
    echo ""

    # 顯示正在運行的容器
    if sudo docker ps --filter "name=stock-analysis" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -q "stock-analysis"; then
        sudo docker ps --filter "name=stock-analysis" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    else
        print_warning "未發現運行中的容器"
    fi
    echo ""
}

# 備份重要資料
backup_data() {
    if [ "$SKIP_BACKUP" = true ]; then
        print_warning "跳過資料備份"
        return
    fi

    print_step "備份應用資料..."

    BACKUP_DIR="backups"
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_PATH="$BACKUP_DIR/backup_$TIMESTAMP"

    mkdir -p "$BACKUP_DIR"

    # 備份 Docker volume 資料
    if sudo docker volume ls | grep -q "buy-tracer-web_app-data"; then
        print_info "備份 app-data volume..."
        mkdir -p "$BACKUP_PATH"
        sudo docker run --rm \
            -v buy-tracer-web_app-data:/data \
            -v "$(pwd)/$BACKUP_PATH":/backup \
            alpine tar czf /backup/app-data.tar.gz -C /data .
        print_success "資料備份完成: $BACKUP_PATH/app-data.tar.gz"
    else
        print_warning "未找到 app-data volume，跳過備份"
    fi

    # 只保留最近 5 個備份
    if [ -d "$BACKUP_DIR" ]; then
        cd "$BACKUP_DIR"
        ls -t | tail -n +6 | xargs -r rm -rf
        cd - > /dev/null
        print_info "清理舊備份，保留最近 5 個"
    fi
}

# 從 Git 拉取最新代碼
pull_latest_code() {
    if [ "$SKIP_GIT_PULL" = true ]; then
        print_warning "跳過 Git 拉取"
        return
    fi

    print_step "從 Git 拉取最新代碼..."

    # 檢查是否為 git 倉庫
    if [ ! -d ".git" ]; then
        print_error "當前目錄不是 Git 倉庫"
        exit 1
    fi

    # 顯示當前分支和版本
    CURRENT_BRANCH=$(git branch --show-current)
    CURRENT_COMMIT=$(git rev-parse --short HEAD)
    print_info "當前分支: $CURRENT_BRANCH ($CURRENT_COMMIT)"

    # 檢查是否有未提交的更改
    if ! git diff-index --quiet HEAD --; then
        print_warning "發現未提交的更改"
        git status --short
        echo ""
        read -p "是否繼續更新？(y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_error "更新已取消"
            exit 1
        fi
    fi

    # 拉取最新代碼
    print_info "拉取最新代碼..."
    git fetch origin

    LOCAL_COMMIT=$(git rev-parse HEAD)
    REMOTE_COMMIT=$(git rev-parse origin/$CURRENT_BRANCH)

    if [ "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]; then
        print_success "代碼已是最新版本"
        return
    fi

    # 顯示即將更新的提交
    print_info "即將更新的提交:"
    echo ""
    git log --oneline --graph --decorate HEAD..origin/$CURRENT_BRANCH
    echo ""

    # 執行拉取
    git pull origin $CURRENT_BRANCH

    NEW_COMMIT=$(git rev-parse --short HEAD)
    print_success "代碼更新完成: $CURRENT_COMMIT -> $NEW_COMMIT"
}

# 停止並移除容器
stop_containers() {
    print_step "停止現有容器..."

    if sudo docker compose -f "$COMPOSE_FILE" ps --quiet 2>/dev/null | grep -q .; then
        sudo docker compose -f "$COMPOSE_FILE" down
        print_success "容器已停止"
    else
        print_info "沒有運行中的容器"
    fi
}

# 構建並啟動容器
start_containers() {
    print_step "啟動應用容器..."

    if [ "$FORCE_REBUILD" = true ]; then
        print_info "強制重新構建映像..."
        sudo docker compose -f "$COMPOSE_FILE" build --no-cache
    fi

    # 啟動容器
    sudo docker compose -f "$COMPOSE_FILE" up -d --build

    print_success "容器啟動完成"
}

# 等待服務就緒
wait_for_service() {
    print_step "等待服務就緒..."

    MAX_RETRIES=30
    RETRY_COUNT=0

    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if sudo docker compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
            # 檢查應用健康狀態
            if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
                print_success "服務已就緒"
                return 0
            fi
        fi

        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo -n "."
        sleep 2
    done

    echo ""
    print_error "服務啟動超時"
    print_info "查看容器日誌:"
    sudo docker compose -f "$COMPOSE_FILE" logs --tail=50
    exit 1
}

# 顯示更新後狀態
show_update_status() {
    print_step "更新後狀態..."
    echo ""

    # 顯示容器狀態
    sudo docker compose -f "$COMPOSE_FILE" ps

    echo ""
    print_info "容器日誌（最後 20 行）:"
    sudo docker compose -f "$COMPOSE_FILE" logs --tail=20

    echo ""
}

# 顯示訪問資訊
show_access_info() {
    echo ""
    echo "============================================"
    print_success "更新完成！"
    echo "============================================"
    echo ""

    # 獲取公網 IP
    PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "localhost")

    if [ -f ".env" ] && grep -q "DOMAIN=" .env; then
        DOMAIN=$(grep "^DOMAIN=" .env | cut -d'=' -f2)
        if [ -n "$DOMAIN" ]; then
            echo "🌐 應用網址: https://$DOMAIN"
            echo "🌐 備用網址: http://$DOMAIN"
        fi
    else
        if [ "$COMPOSE_FILE" = "docker-compose.simple.yml" ]; then
            echo "🌐 應用網址: http://$PUBLIC_IP:5000"
        else
            echo "🌐 應用網址: http://$PUBLIC_IP"
        fi
    fi

    echo ""
    echo "📊 健康檢查: http://localhost:5000/api/health"
    echo ""
    echo "🔧 管理命令:"
    echo "   查看日誌: sudo docker compose -f $COMPOSE_FILE logs -f"
    echo "   重啟應用: sudo docker compose -f $COMPOSE_FILE restart"
    echo "   停止應用: sudo docker compose -f $COMPOSE_FILE down"
    echo ""

    # 顯示最新提交
    if [ "$SKIP_GIT_PULL" = false ]; then
        echo "📝 最新提交:"
        git log -1 --pretty=format:"   %h - %s (%an, %ar)" HEAD
        echo ""
    fi

    echo ""
    echo "============================================"
}

# 清理舊映像
cleanup_images() {
    print_step "清理未使用的 Docker 映像..."

    # 移除懸空映像
    DANGLING=$(sudo docker images -f "dangling=true" -q)
    if [ -n "$DANGLING" ]; then
        sudo docker rmi $DANGLING 2>/dev/null || true
        print_success "已清理懸空映像"
    else
        print_info "沒有需要清理的映像"
    fi
}

# 主函數
main() {
    echo ""
    echo "============================================"
    echo "   股票分析 Web 應用 - Docker 更新腳本"
    echo "============================================"
    echo ""

    # 解析參數
    parse_args "$@"

    # 顯示更新配置
    print_info "更新配置:"
    echo "  - Compose 檔案: $COMPOSE_FILE"
    echo "  - 跳過備份: $SKIP_BACKUP"
    echo "  - 跳過 Git 拉取: $SKIP_GIT_PULL"
    echo "  - 強制重建: $FORCE_REBUILD"
    echo ""

    # 執行更新流程
    check_docker
    show_current_status
    backup_data
    pull_latest_code
    stop_containers
    start_containers
    wait_for_service
    show_update_status
    cleanup_images
    show_access_info

    print_success "所有更新步驟已完成！"
    echo ""
}

# 執行主函數
main "$@"
