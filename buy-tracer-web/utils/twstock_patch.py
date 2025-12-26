"""
twstock 套件修補程式
修復證交所 API 資料格式變更導致的錯誤

問題背景
--------
日期: 2025-12-26
症狀: Data.__new__() takes 10 positional arguments but 11 were given
錯誤位置: twstock.stock.TWSEFetcher._make_datatuple() 和 TPEXFetcher._make_datatuple()

根本原因
--------
台灣證券交易所 API 資料格式發生變更：
- 舊格式：每筆資料 9 個欄位
  ['日期', '成交股數', '成交金額', '開盤價', '最高價', '最低價', '收盤價', '漲跌價差', '成交筆數']

- 新格式：每筆資料 10 個欄位（最後多了空字串）
  ['日期', '成交股數', '成交金額', '開盤價', '最高價', '最低價', '收盤價', '漲跌價差', '成交筆數', '']

但 twstock 套件的 DATATUPLE 結構仍為 9 個欄位，導致參數數量不匹配。

解決方案
--------
使用 Monkey Patching 技術修補 _make_datatuple 方法：
- 只取 API 回傳資料的前 9 個欄位：data[:9]
- 忽略最後的空字串
- 在應用啟動時（app.py:create_app()）自動套用

兼容性
------
- 支援 twstock 1.3.1, 1.4.0 及未來版本
- 如果 twstock 官方修復此問題，此修補程式仍可安全運行（最多做兩次 [:9] 切片）
- 向後兼容所有 API 格式

參考資料
--------
- TWSE API: http://www.twse.com.tw/exchangeReport/STOCK_DAY
- twstock GitHub: https://github.com/mlouielu/twstock
"""
import datetime
import twstock.stock


def patched_make_datatuple_twse(self, data):
    """修補後的 TWSEFetcher._make_datatuple 方法"""
    data[0] = datetime.datetime.strptime(self._convert_date(data[0]), "%Y/%m/%d")
    data[1] = int(data[1].replace(",", ""))
    data[2] = int(data[2].replace(",", ""))
    data[3] = None if data[3] == "--" else float(data[3].replace(",", ""))
    data[4] = None if data[4] == "--" else float(data[4].replace(",", ""))
    data[5] = None if data[5] == "--" else float(data[5].replace(",", ""))
    data[6] = None if data[6] == "--" else float(data[6].replace(",", ""))
    # +/-/X表示漲/跌/不比價
    data[7] = float(
        0.0 if data[7].replace(",", "") == "X0.00" else data[7].replace(",", "")
    )
    data[8] = int(data[8].replace(",", ""))
    # 修復：只取前9個元素，忽略第10個空字串
    return twstock.stock.DATATUPLE(*data[:9])


def patched_make_datatuple_tpex(self, data):
    """修補後的 TPEXFetcher._make_datatuple 方法"""
    data[0] = datetime.datetime.strptime(
        self._convert_date(data[0].replace("＊", "")), "%Y/%m/%d"
    )
    data[1] = int(data[1].replace(",", "")) * 1000
    data[2] = int(data[2].replace(",", "")) * 1000
    data[3] = None if data[3] == "--" else float(data[3].replace(",", ""))
    data[4] = None if data[4] == "--" else float(data[4].replace(",", ""))
    data[5] = None if data[5] == "--" else float(data[5].replace(",", ""))
    data[6] = None if data[6] == "--" else float(data[6].replace(",", ""))
    data[7] = float(data[7].replace(",", ""))
    data[8] = int(data[8].replace(",", ""))
    # 修復：只取前9個元素，忽略第10個空字串（如果存在）
    return twstock.stock.DATATUPLE(*data[:9])


def apply_twstock_patch():
    """
    應用 twstock 修補程式
    必須在使用 twstock 之前呼叫此函數
    """
    twstock.stock.TWSEFetcher._make_datatuple = patched_make_datatuple_twse
    twstock.stock.TPEXFetcher._make_datatuple = patched_make_datatuple_tpex
    print("[OK] twstock 修補程式已套用（修復證交所 API 格式變更）")
