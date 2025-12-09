import yfinance as yf
import pandas as pd

# ----------------------------------------------------
# 參數設定
# ----------------------------------------------------
#TICKER_ID = "8110.TW"  # 華東 (8110) 的 Yahoo Finance 代號
TICKER_ID = "3363.TW"  # 上詮 (3363) 的 Yahoo Finance 代號
START_DATE = "2024-01-01"  # 設定回測/追蹤開始日期
END_DATE = pd.to_datetime('today').strftime('%Y-%m-%d') # 追蹤至今日

# ----------------------------------------------------
# 步驟 1: 數據獲取
# ----------------------------------------------------
def get_stock_data(ticker, start, end):
    """從 yfinance 獲取股價數據"""
    print(f"正在下載 {ticker} 數據...")
    # 設置 auto_adjust=False 讓 yfinance 輸出所有 6 個欄位 (含 Adj Close)
    df = yf.download(ticker, start=start, end=end, auto_adjust=False) # <--- 新增此參數
    
    # 保持原有的 6 個欄位命名
    df.columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
    return df

# ----------------------------------------------------
# 步驟 2: 計算技術指標 (MA & MACD)
# ----------------------------------------------------
def calculate_indicators(df):
    """計算移動平均線 (MA) 和 MACD"""
    # 移動平均線
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA60'] = df['Close'].rolling(window=60).mean()
    
    # MACD (標準參數 12, 26, 9)
    df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['DIF'] = df['EMA12'] - df['EMA26']  # 快線
    df['DEM'] = df['DIF'].ewm(span=9, adjust=False).mean()  # 慢線
    df['OSC'] = df['DIF'] - df['DEM']  # 柱狀體
    
    # 5日平均成交量
    df['Avg_Volume5'] = df['Volume'].rolling(window=5).mean()
    
    return df.dropna()

# ----------------------------------------------------
# 步驟 3: 定義買點訊號
# ----------------------------------------------------
def generate_buy_signals(df):
    """根據兩大策略生成買點訊號"""
    # 修正警告：明確地複製 DataFrame 以便進行修改
    df = df.copy()
    # 買點一：均線多頭確立與黃金交叉 (趨勢啟動買點)
    # 條件 1: MA5 向上穿越 MA20 (黃金交叉)
    cross_signal = (df['MA5'].shift(1) < df['MA20'].shift(1)) & (df['MA5'] > df['MA20'])
    # 條件 2: 均線多頭排列 (MA5 > MA20 > MA60)
    bull_arrangement = (df['MA5'] > df['MA20']) & (df['MA20'] > df['MA60'])
    # 條件 3: 價漲量增 (成交量 > 5日均量)
    volume_confirm = df['Volume'] > df['Avg_Volume5']
    
    # 綜合訊號
    df['Signal_Type1'] = (cross_signal & bull_arrangement & volume_confirm).apply(
        lambda x: "🚀 趨勢確立買點" if x else "")

    
    # 買點二：MACD 柱狀體二次翻紅 (拉回支撐買點)
    # 條件 1: MACD 仍為多頭 (DIF > DEM) - 確保趨勢向上
    macd_bull = df['DIF'] > df['DEM']
    # 條件 2: 柱狀體重新擴大 (OSC > 昨日OSC) - 動能重新增強
    osc_rebound = df['OSC'] > df['OSC'].shift(1)
    # 條件 3: 月線支撐有效 (Close > MA20)
    ma20_support = df['Close'] > df['MA20']

    # 綜合訊號
    df['Signal_Type2'] = (macd_bull & osc_rebound & ma20_support).apply(
        lambda x: "✨ 拉回支撐買點" if x else "")

    # 合併訊號
    df['Buy_Signal'] = df['Signal_Type1'] + df['Signal_Type2']
    
    # 篩選出有訊號的日期
    signal_df = df[df['Buy_Signal'] != ''].copy()
    
    return signal_df

# ----------------------------------------------------
# 步驟 4: 增加圖形化輸出 (新增函式)
# ----------------------------------------------------
import matplotlib.pyplot as plt
import mplfinance as mpf
# ----------------------------------------------------
# 中文亂碼修正 (新增)
# ----------------------------------------------------
# 1. 設定中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
# 2. 設定正常顯示負號
plt.rcParams['axes.unicode_minus'] = False 
# ----------------------------------------------------

def plot_signals(df, signals_df):
    """
    使用 mplfinance 繪製 K 線圖、均線、成交量與 MACD，
    並標註買點訊號。
    """
    
    # 準備 MACD 子圖
    macd_plot = mpf.make_addplot(df['DIF'], panel=2, color='red', secondary_y=False, ylabel='MACD')
    macd_signal_plot = mpf.make_addplot(df['DEM'], panel=2, color='green', secondary_y=False)
    macd_hist_plot = mpf.make_addplot(df['OSC'], type='bar', panel=2, color='green', secondary_y=False)
    
    add_plots = [macd_plot, macd_signal_plot, macd_hist_plot]
    
    # 準備買點標註
    # 訊號轉換成 mplfinance 繪圖所需的格式：使用箭頭標註
    buy_markers = [(date, row['Close']) for date, row in signals_df.iterrows()]
    buy_dates = [date for date, _ in buy_markers]
    
    # 創建標記列表，將買點日期對應的 K 線圖位置設為 Buy 箭頭
    buy_markers_series = pd.Series(index=df.index, dtype=float)
    for date, price in buy_markers:
        buy_markers_series.loc[date] = price * 0.98 # 箭頭位置略低於K線
    
    # 增加買點訊號箭頭
    signal_scatter = mpf.make_addplot(buy_markers_series, 
                                      type='scatter', 
                                      markersize=100, 
                                      marker='^', # 向上箭頭
                                      color='red', 
                                      panel=0)
    add_plots.append(signal_scatter)
    
    # 設定繪圖風格
    mc = mpf.make_marketcolors(up='r', down='g', inherit=True)
    s = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc)

    # 繪圖
    mpf.plot(
        df, 
        type='candle',
        style=s,
        title={'title': f'華東 (8110) 技術分析與買點追蹤', 'fontweight':'bold', 'fontname':'Microsoft JhengHei'},
        mav=(5, 20, 60), # 繪製 MA5, MA20, MA60
        volume=True,
        addplot=add_plots,
        figratio=(18,10), # 調整圖形比例
        hlines=dict(hlines=[df['MA20'].iloc[-1]], colors=['blue'], linestyle='--', linewidths=[1]), # 標註最新MA20價格
        vlines=dict(vlines=buy_dates, colors=['red'], linewidths=[0.5], linestyle='--'), # 標註買點日期垂直線
        show_nontrading=False,
        datetime_format='%Y-%m-%d',
        xrotation=0,
        tight_layout=True
    )
    plt.show()


# ----------------------------------------------------
# 步驟 5: 執行主程式
# ----------------------------------------------------
if __name__ == "__main__":
    
    # 1. 獲取數據
    data_df = get_stock_data(TICKER_ID, START_DATE, END_DATE)
    
    if data_df.empty:
        print("!!! 數據下載失敗或日期範圍無數據。")
    else:
        # 2. 計算指標
        analyzed_df = calculate_indicators(data_df)
        
        # 3. 產生訊號
        signal_results = generate_buy_signals(analyzed_df)
        
        if not signal_results.empty:
            
            # --- 【關鍵修正點 START】 ---
            # 這裡的邏輯是正確的，用於篩選繪圖範圍
            PLOT_DAYS = 120
            plot_df = analyzed_df.tail(PLOT_DAYS)
            plot_start_date = plot_df.index[0] 
            plot_signals_results = signal_results[signal_results.index >= plot_start_date]
            # --- 【關鍵修正點 END】 ---
            
            print("\n--- 🎯 華東 (8110) 追蹤買點訊號 ---")
            output_columns = ['Close', 'MA20', 'Volume', 'Avg_Volume5', 'DIF', 'DEM', 'OSC', 'Buy_Signal']
            latest_signals = signal_results[output_columns].tail(5)
            pd.options.display.float_format = '{:,.2f}'.format
            
            print(latest_signals)
            
            latest_day_signal = signal_results['Buy_Signal'].iloc[-1] if not signal_results.empty else "無"
            latest_price = analyzed_df['Close'].iloc[-1]
            print(f"\n💡 最新一個交易日 ({signal_results.index[-1].strftime('%Y-%m-%d')}) 的訊號判讀為：**{latest_day_signal}**")
            print(f"當日收盤價為：**{latest_price:,.2f}**")
            
            # ----------------------------------------------------
            # 步驟 4: 繪圖呼叫 (最終修正)
            # 這裡必須使用 plot_df 和 plot_signals_results！
            # ----------------------------------------------------
            plot_signals(plot_df, plot_signals_results) 
            # ----------------------------------------------------
            
        else:
            print("\n--- 🎯 華東 (8110) 追蹤買點訊號 ---")
            print("目前數據範圍內，尚未產生有效的買點訊號。")