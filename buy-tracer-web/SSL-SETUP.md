# Let's Encrypt SSL 證書設置指南

本指南將幫助您為 `tearice.win` 設置免費的 Let's Encrypt SSL 證書。

## 前置條件

1. **域名 DNS 設置**
   - 確保 `tearice.win` 和 `www.tearice.win` 的 A 記錄都指向您的伺服器 IP
   - 可以使用以下命令檢查：
     ```bash
     dig tearice.win +short
     dig www.tearice.win +short
     ```

2. **防火牆設置**
   - 確保開放 80 和 443 端口
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw status
   ```

3. **Docker 環境**
   - 已安裝 Docker 和 Docker Compose
   - 可以使用 `deploy.sh` 腳本自動安裝

## 快速設置步驟

### 步驟 1：修改電子郵件地址

編輯 `init-letsencrypt.sh`，將電子郵件改為您的真實郵箱：

```bash
EMAIL="your-email@example.com"  # 改為您的郵箱
```

或者在運行時輸入。

### 步驟 2：執行初始化腳本

```bash
# 給腳本執行權限
chmod +x init-letsencrypt.sh
chmod +x renew-cert.sh

# 執行初始化
./init-letsencrypt.sh
```

腳本會自動：
- 創建必要的目錄
- 下載 TLS 安全參數
- 啟動 nginx
- 向 Let's Encrypt 請求證書
- 配置自動續期

### 步驟 3：驗證 HTTPS

訪問您的網站：
- https://tearice.win
- https://www.tearice.win

檢查 SSL 證書：
```bash
# 查看證書信息
openssl s_client -connect tearice.win:443 -servername tearice.win < /dev/null 2>/dev/null | openssl x509 -noout -dates

# 檢查 SSL 評級（可選）
# 訪問 https://www.ssllabs.com/ssltest/analyze.html?d=tearice.win
```

## 測試環境（Staging）

如果您想先在測試環境測試，避免達到 Let's Encrypt 的請求限制：

編輯 `init-letsencrypt.sh`，設置：
```bash
STAGING=1  # 使用測試環境
```

測試成功後，將其改回 `STAGING=0` 並重新運行腳本以獲取正式證書。

## 證書管理

### 自動續期

系統已配置自動續期：
- Certbot 容器每 12 小時檢查一次證書是否需要續期
- Nginx 容器每 6 小時重載配置以應用新證書

### 手動續期

如需手動續期證書：
```bash
./renew-cert.sh
```

或使用 docker compose：
```bash
sudo docker compose run --rm certbot renew
sudo docker compose exec nginx nginx -s reload
```

### 查看證書狀態

```bash
# 查看證書信息
sudo docker compose run --rm certbot certificates

# 查看證書有效期
sudo ls -la /var/lib/docker/volumes/buy-tracer-web_certbot-etc/_data/live/tearice.win/
```

## 常見問題排查

### 1. 證書請求失敗

**錯誤：無法連接到域名**

檢查項目：
```bash
# 檢查 DNS 解析
dig tearice.win +short

# 檢查端口是否開放
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443

# 檢查 nginx 是否運行
sudo docker ps | grep nginx
sudo docker compose logs nginx
```

**錯誤：達到請求限制**

Let's Encrypt 有以下限制：
- 每個域名每週最多 5 次失敗請求
- 每個註冊域名每週最多 50 個證書

解決方法：
1. 使用 `STAGING=1` 進行測試
2. 等待一週後重試
3. 查看詳細錯誤：`sudo docker compose logs certbot`

### 2. HTTPS 無法訪問

檢查項目：
```bash
# 檢查 nginx 配置
sudo docker compose exec nginx nginx -t

# 檢查容器狀態
sudo docker compose ps

# 查看 nginx 日誌
sudo docker compose logs nginx

# 檢查證書掛載
sudo docker compose exec nginx ls -la /etc/letsencrypt/live/tearice.win/
```

### 3. 證書自動續期失敗

檢查 certbot 日誌：
```bash
sudo docker compose logs certbot

# 手動測試續期
sudo docker compose run --rm certbot renew --dry-run
```

## 進階配置

### 修改域名

如果要為其他域名設置證書，修改 `init-letsencrypt.sh`：

```bash
DOMAIN="your-new-domain.com"
```

同時更新 `nginx.conf` 中的 `server_name`。

### 添加多個域名

在 `init-letsencrypt.sh` 中：
```bash
CERTBOT_ARGS="$CERTBOT_ARGS -d domain1.com -d www.domain1.com -d domain2.com"
```

同時更新 `nginx.conf` 中的 `server_name`。

### 強制 HTTPS

已在 `nginx.conf` 中配置，所有 HTTP 請求自動重定向到 HTTPS：
```nginx
location / {
    return 301 https://$host$request_uri;
}
```

### HSTS Preload

如需加入 HSTS Preload 列表，確認網站已穩定運行 HTTPS 後：
1. 訪問 https://hstspreload.org/
2. 輸入您的域名並提交

## 維護命令速查

```bash
# 查看所有容器狀態
sudo docker compose ps

# 重啟服務
sudo docker compose restart nginx
sudo docker compose restart certbot

# 查看日誌
sudo docker compose logs -f nginx
sudo docker compose logs -f certbot

# 停止服務
sudo docker compose down

# 完全重新部署
sudo docker compose down -v
./init-letsencrypt.sh

# 備份證書
sudo tar -czf letsencrypt-backup-$(date +%Y%m%d).tar.gz \
  /var/lib/docker/volumes/buy-tracer-web_certbot-etc/_data/
```

## 證書有效期

- Let's Encrypt 證書有效期：90 天
- 自動續期觸發時間：到期前 30 天
- 續期檢查頻率：每 12 小時

## 安全評級

配置已優化以獲得 A+ SSL Labs 評級：
- TLS 1.2 和 1.3
- 強加密套件
- HSTS（HTTP Strict Transport Security）
- OCSP Stapling
- 安全標頭（X-Frame-Options, X-Content-Type-Options 等）

檢查評級：https://www.ssllabs.com/ssltest/analyze.html?d=tearice.win

## 支援

如遇問題，請檢查：
1. Let's Encrypt 社群：https://community.letsencrypt.org/
2. Certbot 文檔：https://certbot.eff.org/docs/
3. 本專案 GitHub Issues
