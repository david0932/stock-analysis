# 快速修復 Nginx 重啟問題

## 問題診斷

您遇到的問題：
1. ❌ SSL 證書不存在（還沒有運行初始化腳本）
2. ❌ `app` 容器找不到（可能沒有啟動或網絡問題）
3. ⚠️ `listen ... http2` 語法已棄用（已修復）

## 快速修復步驟

### 步驟 1：停止所有容器

```bash
cd ~/stock-analysis/buy-tracer-web
sudo docker compose down
```

### 步驟 2：確認 app 容器可以正常運行

先測試簡單模式（僅 app，不含 nginx）：

```bash
# 使用簡單模式啟動
sudo docker compose -f docker-compose.simple.yml up -d

# 檢查容器狀態
sudo docker compose -f docker-compose.simple.yml ps

# 測試應用是否正常
curl http://localhost:5000/api/health

# 停止簡單模式
sudo docker compose -f docker-compose.simple.yml down
```

### 步驟 3：修改初始化腳本的郵箱

編輯 `init-letsencrypt.sh`：

```bash
nano init-letsencrypt.sh
```

將 `EMAIL="your-email@example.com"` 改為您的真實郵箱地址。

### 步驟 4：執行初始化腳本

```bash
# 給腳本執行權限
chmod +x init-letsencrypt.sh

# 運行初始化腳本
./init-letsencrypt.sh
```

腳本會自動：
1. 備份原始 `nginx.conf`
2. 使用臨時配置啟動服務（不含 SSL）
3. 請求 Let's Encrypt 證書
4. 恢復完整配置並啟用 HTTPS

### 步驟 5：驗證服務

```bash
# 檢查所有容器狀態
sudo docker compose ps

# 查看日誌
sudo docker compose logs -f

# 測試 HTTP（應該重定向到 HTTPS）
curl -I http://tearice.win

# 測試 HTTPS
curl -I https://tearice.win
```

## 如果初始化失敗

### 情況 A：DNS 還沒有設定好

如果您的域名 DNS 還沒指向伺服器，先用 HTTP 模式運行：

```bash
# 停止容器
sudo docker compose down

# 臨時使用 HTTP 配置
cp nginx.conf.http-only nginx.conf

# 啟動服務
sudo docker compose up -d

# 訪問 http://YOUR_SERVER_IP
```

等 DNS 設定好後，再運行 `init-letsencrypt.sh`。

### 情況 B：想先測試（避免 Let's Encrypt 限制）

編輯 `init-letsencrypt.sh`，設置：

```bash
STAGING=1  # 使用測試環境
```

測試成功後改回 `STAGING=0` 並重新運行。

### 情況 C：app 容器無法啟動

檢查 app 容器日誌：

```bash
sudo docker compose logs app

# 如果有 Python 錯誤，檢查依賴
sudo docker compose exec app pip list
```

## 手動修復（如果腳本失敗）

### 1. 使用 HTTP 配置

```bash
cd ~/stock-analysis/buy-tracer-web

# 備份原配置
cp nginx.conf nginx.conf.ssl

# 使用 HTTP 配置
cp nginx.conf.http-only nginx.conf

# 重啟服務
sudo docker compose down
sudo docker compose up -d
```

### 2. 手動獲取證書

```bash
# 確保 app 和 nginx 都在運行
sudo docker compose ps

# 手動運行 certbot
sudo docker compose run --rm certbot certonly \
  --webroot \
  -w /var/www/certbot \
  --email your-email@example.com \
  -d tearice.win \
  -d www.tearice.win \
  --agree-tos \
  --no-eff-email
```

### 3. 恢復 SSL 配置

```bash
# 恢復 SSL 配置
cp nginx.conf.ssl nginx.conf

# 重啟 nginx
sudo docker compose restart nginx

# 啟動 certbot 自動續期
sudo docker compose up -d certbot
```

## 常見錯誤排查

### 錯誤：host not found in upstream "app:5000"

**原因**：nginx 容器找不到 app 容器

**解決**：
```bash
# 檢查 app 是否運行
sudo docker compose ps app

# 檢查網絡
sudo docker network ls
sudo docker network inspect buy-tracer-web_stock-network

# 重啟所有服務
sudo docker compose down
sudo docker compose up -d
```

### 錯誤：cannot load certificate

**原因**：證書文件不存在

**解決**：使用 `nginx.conf.http-only` 或運行 `init-letsencrypt.sh`

### 錯誤：達到 Let's Encrypt 請求限制

**解決**：
1. 等待一週
2. 或使用 `STAGING=1` 測試環境

## 驗證清單

在運行初始化腳本之前，確認：

- [ ] 域名 `tearice.win` 的 A 記錄指向此伺服器
- [ ] 域名 `www.tearice.win` 的 A 記錄指向此伺服器
- [ ] 防火牆開放 80 和 443 端口
- [ ] Docker 和 Docker Compose 已安裝
- [ ] 修改了 `init-letsencrypt.sh` 中的郵箱地址

檢查 DNS：
```bash
dig tearice.win +short
dig www.tearice.win +short
# 應該返回您的伺服器 IP
```

檢查防火牆：
```bash
sudo ufw status
# 應該顯示 80/tcp 和 443/tcp 都是 ALLOW
```

## 完全重置（最後手段）

如果一切都不行，完全重置：

```bash
cd ~/stock-analysis/buy-tracer-web

# 停止並刪除所有容器、卷
sudo docker compose down -v

# 刪除所有 Docker 卷
sudo docker volume rm buy-tracer-web_certbot-etc || true
sudo docker volume rm buy-tracer-web_certbot-var || true
sudo docker volume rm buy-tracer-web_certbot-www || true
sudo docker volume rm buy-tracer-web_app-data || true

# 恢復原始配置
cp nginx.conf.http-only nginx.conf

# 重新開始
./init-letsencrypt.sh
```

## 需要幫助？

查看實時日誌：
```bash
# 所有日誌
sudo docker compose logs -f

# 只看 nginx
sudo docker compose logs -f nginx

# 只看 app
sudo docker compose logs -f app

# 只看 certbot
sudo docker compose logs -f certbot
```
