# 賣點策略功能實作說明

## 📊 功能概述

系統已成功實作**賣點策略分析功能**，現在可以同時追蹤買點與賣點訊號，提供完整的進出場參考。

## 🎯 賣點策略

### 策略一：趨勢反轉賣點 ⬇️

**適用情境：** 上升趨勢結束，及時退場保護獲利

**訊號條件：**
1. **死亡交叉** - MA5 向下跌破 MA20
2. **空頭排列** - MA5 < MA20 < MA60
3. **量能確認** - 成交量 > 5日均量（確認賣壓）

**程式碼實作：**
```python
death_cross = (df['ma5'].shift(1) > df['ma20'].shift(1)) & (df['ma5'] < df['ma20'])
bear_arrangement = (df['ma5'] < df['ma20']) & (df['ma20'] < df['ma60'])
sell_volume_confirm = df['volume'] > df['avg_volume5']

df['sell_signal_type1'] = (death_cross & bear_arrangement & sell_volume_confirm).apply(
    lambda x: "⬇️ 趨勢反轉賣點" if x else ""
)
```

---

### 策略二：MACD 轉弱賣點 🔶

**適用情境：** MACD 指標轉弱，趨勢動能衰退

**訊號條件：**
1. **MACD轉空** - DIF < DEM
2. **柱狀體下降** - OSC < OSC前一日
3. **跌破MA20** - 收盤價 < MA20

**程式碼實作：**
```python
macd_bear = df['dif'] < df['dem']
osc_decline = df['osc'] < df['osc'].shift(1)
break_ma20 = df['close'] < df['ma20']

df['sell_signal_type2'] = (macd_bear & osc_decline & break_ma20).apply(
    lambda x: "🔶 MACD轉弱賣點" if x else ""
)
```

---

## 📁 修改的檔案

### 1. 後端服務

#### `services/signal_service.py`
**變更內容：**
- ✅ 新增賣點訊號生成邏輯（兩種策略）
- ✅ 更新 `generate_signals()` 方法同時生成買賣訊號
- ✅ 更新 `get_signal_df()` 支援過濾買點/賣點/全部訊號
- ✅ 更新 `get_latest_signals()` 返回買賣訊號並標註類別
- ✅ 更新 `get_signal_summary()` 提供買賣訊號分類統計

**返回資料格式：**
```python
{
    'total_count': 15,  # 總訊號數
    'buy_total_count': 8,  # 買點總數
    'buy_type1_count': 3,  # 趨勢買點
    'buy_type2_count': 5,  # 拉回買點
    'sell_total_count': 7,  # 賣點總數
    'sell_type1_count': 2,  # 趨勢賣點
    'sell_type2_count': 5,  # MACD賣點
    'latest_signal': {
        'date': '2025-12-08',
        'type': '⬇️ 趨勢反轉賣點',
        'category': 'sell',
        'close': 123.45
    }
}
```

#### `services/chart_service.py`
**變更內容：**
- ✅ 更新 `create_candlestick_chart()` 支援顯示買賣點標記
- ✅ 買點標記：綠色向上三角形 ▲ (位於價格下方)
- ✅ 賣點標記：紅色向下三角形 ▼ (位於價格上方)
- ✅ 優化圖例佈局，水平顯示於圖表上方

**視覺效果：**
- **買點** - 綠色三角形 🟢▲
- **賣點** - 紅色三角形 🔴▼
- Hover 顯示詳細訊號類型和價格

---

### 2. 前端界面

#### `templates/analyze.html`

**變更內容：**

1. **訊號統計卡片重新設計**
   ```html
   <!-- 買點訊號統計 -->
   <div class="card border-success">
       <div class="card-header bg-success text-white">
           📈 買點訊號統計
       </div>
       <div class="card-body">
           總買點 / 趨勢買點 / 拉回買點
       </div>
   </div>

   <!-- 賣點訊號統計 -->
   <div class="card border-danger">
       <div class="card-header bg-danger text-white">
           📉 賣點訊號統計
       </div>
       <div class="card-body">
           總賣點 / 趨勢賣點 / 轉弱賣點
       </div>
   </div>
   ```

2. **訊號表格樣式**
   - 買點訊號：綠色 badge
   - 賣點訊號：紅色 badge + 淡紅色背景行

3. **最新訊號提示**
   - 買點：綠色 alert + 📈 icon
   - 賣點：紅色 alert + 📉 icon

4. **JavaScript 更新**
   ```javascript
   // 根據訊號類別設定樣式
   const isBuy = signal.signal_category === 'buy';
   const badgeClass = isBuy ? 'bg-success' : 'bg-danger';
   const rowClass = isBuy ? '' : 'table-danger';
   ```

#### `templates/index.html`

**變更內容：**

1. **系統標題更新**
   - "股票買點追蹤系統" → "股票買賣點追蹤系統"
   - 副標題包含買賣點說明

2. **策略說明新增賣點策略**
   - 買點策略 (📈)
     - 趨勢確立買點
     - 拉回支撐買點
   - 賣點策略 (📉)
     - 趨勢反轉賣點
     - MACD轉弱賣點

3. **功能特色卡片更新**
   - "雙策略買點" → "完整買賣策略"
   - 列出買賣點類型

---

## 🎨 UI/UX 設計

### 配色方案

| 元素 | 顏色 | 用途 |
|------|------|------|
| 買點統計卡片 | 綠色 (`#10b981`) | 買點訊號背景 |
| 賣點統計卡片 | 紅色 (`#ef4444`) | 賣點訊號背景 |
| 買點圖表標記 | 綠色向上三角 | K線圖買點標示 |
| 賣點圖表標記 | 紅色向下三角 | K線圖賣點標示 |
| 買點 Badge | `bg-success` | 表格訊號類型 |
| 賣點 Badge | `bg-danger` | 表格訊號類型 |
| 賣點表格行 | `table-danger` | 淡紅色背景 |

### 圖表標記位置
- **買點**: 位於收盤價 98% 位置（稍低於K線）
- **賣點**: 位於收盤價 102% 位置（稍高於K線）

---

## 📊 資料流程

```
1. 後端計算訊號
   ↓
   SignalService.generate_signals(df)
   - 生成 buy_signal_type1, buy_signal_type2
   - 生成 sell_signal_type1, sell_signal_type2
   - 合併為 buy_signal, sell_signal, signal
   ↓
2. API 返回統計
   ↓
   SignalService.get_signal_summary(df)
   - 統計買點數量（總數、類型1、類型2）
   - 統計賣點數量（總數、類型1、類型2）
   - 最新訊號（含類別標註）
   ↓
3. 前端顯示
   ↓
   - 更新買點統計卡片
   - 更新賣點統計卡片
   - 圖表顯示買賣點標記
   - 表格列出所有訊號（買賣混合）
```

---

## 🧪 測試建議

### 測試案例

1. **測試上市股票（2330）**
   ```
   預期結果:
   - ✅ 顯示買點統計（趨勢買點、拉回買點）
   - ✅ 顯示賣點統計（趨勢賣點、MACD賣點）
   - ✅ K線圖顯示綠色▲和紅色▼標記
   - ✅ 訊號表格混合顯示買賣訊號
   - ✅ 最新訊號顯示正確類別和顏色
   ```

2. **測試訊號少的股票**
   ```
   預期結果:
   - ✅ 買賣點統計顯示 0 或少量訊號
   - ✅ 不會出現錯誤
   - ✅ 空狀態正確顯示
   ```

3. **測試圖表互動**
   ```
   預期結果:
   - ✅ Hover 買點標記顯示訊號類型和價格
   - ✅ Hover 賣點標記顯示訊號類型和價格
   - ✅ 圖例可點擊顯示/隱藏買賣點
   ```

### 測試步驟

1. **啟動應用**
   ```bash
   cd buy-tracer-web
   uv run python app.py
   ```

2. **訪問首頁**
   - 確認標題顯示「股票買賣點追蹤系統」
   - 確認策略說明包含買賣點策略

3. **分析股票（2330）**
   - 輸入 2330 並點擊分析
   - 確認買點統計顯示
   - 確認賣點統計顯示
   - 確認圖表顯示買賣點標記
   - 確認表格顯示買賣訊號

4. **檢查控制台**
   - 無 JavaScript 錯誤
   - API 請求成功
   - 數據格式正確

---

## 🔄 與原有功能的對比

| 功能 | 舊版本 | 新版本 |
|------|--------|--------|
| 訊號類型 | 僅買點 | 買點 + 賣點 |
| 策略數量 | 2 種買點策略 | 2 買點 + 2 賣點 = 4 種 |
| 圖表標記 | 僅綠色▲ | 綠色▲ + 紅色▼ |
| 統計卡片 | 單一卡片 | 分開顯示買賣統計 |
| 訊號表格 | 僅買點 | 買賣點混合（顏色區分） |
| 最新訊號 | 僅綠色 alert | 綠色/紅色 alert（依類別） |

---

## 💡 使用建議

### 交易策略組合

1. **積極進場策略**
   - 買點: 趨勢確立買點 🚀
   - 賣點: MACD轉弱賣點 🔶（提早退場）

2. **穩健持倉策略**
   - 買點: 拉回支撐買點 ✨
   - 賣點: 趨勢反轉賣點 ⬇️（確認反轉才退）

3. **完整循環**
   ```
   趨勢啟動 → 🚀 趨勢買點
   ↓
   上升趨勢持續
   ↓
   回檔 → ✨ 拉回買點（加碼）
   ↓
   繼續上升
   ↓
   MACD減弱 → 🔶 MACD賣點（減碼）
   ↓
   死亡交叉 → ⬇️ 趨勢賣點（全數退場）
   ```

---

## 📈 後續優化方向

### 可考慮新增的功能

1. **進階賣點策略**
   - 停損賣點（跌破關鍵支撐）
   - 獲利了結賣點（達成獲利目標）
   - 量價背離賣點

2. **訊號篩選**
   - 前端增加篩選按鈕（僅買點/僅賣點/全部）
   - 依日期範圍篩選訊號

3. **訊號統計圖表**
   - 買賣訊號分佈圓餅圖
   - 每月訊號數量柱狀圖
   - 訊號成功率統計

4. **訊號提醒**
   - 當日新訊號提醒
   - Email/Line 通知

---

## ✅ 完成清單

- [x] 實作賣點策略一：趨勢反轉賣點
- [x] 實作賣點策略二：MACD轉弱賣點
- [x] 更新 SignalService 支援買賣訊號
- [x] 更新 ChartService 顯示買賣點標記
- [x] 更新前端統計卡片（分開顯示）
- [x] 更新前端訊號表格（買賣混合顯示）
- [x] 更新首頁策略說明
- [x] 更新系統標題和描述
- [x] 測試買賣訊號功能

---

## 📝 總結

賣點策略功能已成功實作並整合到系統中，現在提供：

✅ **完整的買賣訊號追蹤**
✅ **清晰的視覺區分**（綠色買點、紅色賣點）
✅ **詳細的統計資訊**（分類統計）
✅ **互動式圖表標記**
✅ **友善的使用者界面**

系統現在不僅能告訴您何時買入，更能提示您何時應該考慮退場，提供更完整的交易決策參考！
