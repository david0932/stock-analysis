# 專案開發指南

## 文檔導覽

本專案提供完整的設計文檔，建議按以下順序閱讀：

### 1️⃣ 快速入門
- **[README.md](README.md)** - 專案概述、快速開始、功能特色

### 2️⃣ 設計文檔（位於 docs/ 目錄）

#### 架構理解
1. **[系統架構設計](01-系統架構設計.md)**
   - 📖 閱讀時間：15-20 分鐘
   - 📌 重點：了解整體架構、模組劃分、數據流程
   - 🎯 適合：架構師、技術主管、後端開發者

#### API 開發
2. **[API 規格文檔](02-API規格文檔.md)**
   - 📖 閱讀時間：20-25 分鐘
   - 📌 重點：REST API 端點、請求/響應格式、錯誤處理
   - 🎯 適合：後端開發者、前端開發者、API 整合人員

#### 數據管理
3. **[資料存儲格式](03-資料存儲格式.md)**
   - 📖 閱讀時間：15-20 分鐘
   - 📌 重點：JSON 結構、快取策略、數據驗證
   - 🎯 適合：後端開發者、數據工程師

#### 前端開發
4. **[前端介面設計](04-前端介面設計.md)**
   - 📖 閱讀時間：25-30 分鐘
   - 📌 重點：頁面設計、組件結構、JavaScript 架構
   - 🎯 適合：前端開發者、UI/UX 設計師

#### 部署運維
5. **[部署與使用說明](05-部署與使用說明.md)**
   - 📖 閱讀時間：30-40 分鐘
   - 📌 重點：安裝步驟、環境配置、生產部署、疑難排解
   - 🎯 適合：DevOps 工程師、系統管理員、所有開發者

## 開發路徑建議

### 🔰 新手開發者
```
1. README.md（了解專案）
   ↓
2. 部署與使用說明（動手安裝）
   ↓
3. 系統架構設計（理解架構）
   ↓
4. 選擇性閱讀其他文檔
```

### 🎨 前端開發者
```
1. README.md
   ↓
2. 系統架構設計（理解後端架構）
   ↓
3. API 規格文檔（了解 API）
   ↓
4. 前端介面設計（重點閱讀）
   ↓
5. 部署與使用說明
```

### ⚙️ 後端開發者
```
1. README.md
   ↓
2. 系統架構設計（重點閱讀）
   ↓
3. API 規格文檔（重點閱讀）
   ↓
4. 資料存儲格式（重點閱讀）
   ↓
5. 前端介面設計（了解前端需求）
   ↓
6. 部署與使用說明
```

### 🚀 DevOps / 運維人員
```
1. README.md
   ↓
2. 部署與使用說明（重點閱讀）
   ↓
3. 系統架構設計（了解系統依賴）
   ↓
4. 資料存儲格式（了解數據備份）
```

## 開發環境設置

### 1. 克隆專案
```bash
git clone https://github.com/your-repo/buy-tracer-web.git
cd buy-tracer-web
```

### 2. 創建虛擬環境
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 安裝依賴
```bash
pip install -r requirements.txt
```

### 4. 配置環境變數
```bash
cp .env.example .env
# 編輯 .env 文件
```

### 5. 創建必要目錄
```bash
# Windows
mkdir data\cache data\logs data\metadata

# macOS/Linux
mkdir -p data/cache data/logs data/metadata
```

### 6. 啟動開發服務器
```bash
python app.py
```

訪問：http://localhost:5000

## 開發規範

### 代碼風格
- **Python**: 遵循 PEP 8
- **JavaScript**: 使用 ES6+ 語法
- **HTML/CSS**: 遵循 Bootstrap 規範

### Git 提交規範
```
feat: 新增功能
fix: 修復 Bug
docs: 文檔更新
style: 代碼格式調整
refactor: 重構
test: 測試相關
chore: 構建/工具鏈相關
```

範例：
```bash
git commit -m "feat: 新增多股票批次分析功能"
git commit -m "fix: 修復 MACD 計算錯誤"
git commit -m "docs: 更新 API 規格文檔"
```

### 分支策略
```
main        # 生產環境分支
develop     # 開發分支
feature/*   # 功能分支
hotfix/*    # 緊急修復分支
```

## 常用指令

### 開發
```bash
# 啟動開發服務器
python app.py

# 或使用 Flask CLI
flask run

# 啟用除錯模式
FLASK_ENV=development flask run

# 指定端口
flask run --port=8000
```

### 測試
```bash
# 執行所有測試
pytest

# 執行特定測試
pytest tests/test_services.py

# 顯示詳細輸出
pytest -v

# 測試覆蓋率
pytest --cov=services --cov-report=html
```

### 代碼品質
```bash
# 格式化代碼
black .

# 檢查代碼風格
flake8 .

# 排序 import
isort .

# 型別檢查（如有安裝 mypy）
mypy .
```

### 生產部署
```bash
# 使用 Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# 使用 Waitress (Windows)
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

## 專案結構速覽

```
buy-tracer-web/
├── 📄 app.py                    # Flask 應用入口
├── 📄 config.py                 # 配置管理
├── 📁 services/                 # 核心業務邏輯
│   ├── stock_data_service.py   # 📊 股票數據服務
│   ├── indicator_service.py    # 📈 技術指標計算
│   ├── signal_service.py       # 🎯 買點訊號生成
│   └── chart_service.py        # 📉 圖表生成
├── 📁 utils/                    # 工具函式
│   ├── cache_manager.py        # 💾 快取管理
│   └── date_utils.py           # 📅 日期工具
├── 📁 routes/                   # API 路由
│   ├── web_routes.py           # 🌐 網頁路由
│   └── api_routes.py           # 🔌 API 路由
├── 📁 templates/                # HTML 模板
│   ├── base.html               # 基礎模板
│   ├── index.html              # 首頁
│   ├── analyze.html            # 分析頁面
│   └── history.html            # 歷史記錄
├── 📁 static/                   # 靜態資源
│   ├── css/style.css
│   ├── js/main.js
│   └── images/
├── 📁 data/                     # 數據存儲
│   ├── cache/                  # JSON 快取
│   ├── logs/                   # 日誌文件
│   └── metadata/               # 元數據
└── 📁 docs/                     # 設計文檔 ⭐
    ├── 01-系統架構設計.md
    ├── 02-API規格文檔.md
    ├── 03-資料存儲格式.md
    ├── 04-前端介面設計.md
    └── 05-部署與使用說明.md
```

## 核心概念速查

### 買點策略
- **🚀 趨勢確立買點**: MA5 突破 MA20 + 多頭排列 + 量能放大
- **✨ 拉回支撐買點**: MACD 多頭 + OSC 反彈 + MA20 支撐

### 技術指標
- **MA5/20/60**: 移動平均線
- **MACD**: 趨勢動能指標（DIF、DEM、OSC）
- **成交量**: 市場參與度

### 快取機制
- **首次查詢**: 下載完整歷史數據
- **增量更新**: 僅補足缺失日期
- **智能判斷**: 自動排除週末與假日

## 疑難排解快速參考

| 問題 | 快速解決 |
|------|----------|
| 端口被佔用 | `flask run --port=5001` |
| twstock 下載失敗 | 檢查網路、稍後重試 |
| JSON 快取損壞 | 刪除對應 .json 文件 |
| 記憶體不足 | 清理舊快取、限制快取數量 |

詳細疑難排解請參考：[05-部署與使用說明.md](docs/05-部署與使用說明.md#6-疑難排解)

## 貢獻指南

1. Fork 專案
2. 創建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

## 聯絡方式

- **Issues**: [GitHub Issues](https://github.com/your-repo/buy-tracer-web/issues)
- **Email**: your-email@example.com

## 資源連結

- [Flask 官方文檔](https://flask.palletsprojects.com/)
- [Bootstrap 5 文檔](https://getbootstrap.com/docs/5.3/)
- [Plotly Python 文檔](https://plotly.com/python/)
- [twstock 文檔](https://github.com/mlouielu/twstock)

---

**祝開發順利！** 🎉

如有任何問題，請參考完整文檔或開啟 Issue。
