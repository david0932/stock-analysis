# 快速啟動指南

## 環境需求

- Python 3.9 或以上
- pip (Python 套件管理器)

## 安裝步驟

### 1. 安裝依賴套件

```bash
# Windows
python -m pip install -r requirements.txt

# macOS/Linux
pip3 install -r requirements.txt
```

### 2. 設定環境變數（可選）

```bash
# 複製環境變數範例
cp .env.example .env

# 編輯 .env 文件（可選，使用預設值也可以）
```

### 3. 啟動應用

```bash
# 直接執行
python app.py

# 或使用 Flask CLI
flask run
```

### 4. 訪問應用

開啟瀏覽器，訪問：http://localhost:5000

## 使用方式

### 分析股票

1. 在首頁輸入股票代號（例如：2330）
2. 點擊「分析」按鈕
3. 查看技術分析結果與買點訊號

### 查看歷史記錄

1. 點擊導航欄的「歷史記錄」
2. 查看所有已分析的股票
3. 可以重新分析或刪除快取

## 常見問題

### Q: 無法啟動服務器（端口被佔用）

A: 更換端口號

```bash
# 方法 1: 修改 .env 文件
PORT=5001

# 方法 2: 直接指定端口
flask run --port=5001
```

### Q: 無法下載股票數據

A: 檢查網路連接，確保可以訪問 twstock 服務

### Q: 圖表無法顯示

A: 檢查瀏覽器控制台是否有錯誤，確保已載入 Plotly.js

## 下一步

- 閱讀完整文檔：[README.md](README.md)
- 查看設計文檔：[docs/](docs/)
- 查看專案導覽：[PROJECT_GUIDE.md](PROJECT_GUIDE.md)

## 疑難排解

如遇問題，請查看：
- [部署與使用說明](docs/05-部署與使用說明.md#6-疑難排解)
- [GitHub Issues](https://github.com/your-repo/buy-tracer-web/issues)

---

**祝使用愉快！** 🎉
