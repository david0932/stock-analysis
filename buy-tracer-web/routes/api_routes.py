"""
API 路由
負責處理 RESTful API 請求
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import traceback

from services import (
    StockDataService,
    IndicatorService,
    SignalService,
    ChartService
)
from config import Config

api_bp = Blueprint('api', __name__, url_prefix='/api')

# 初始化服務
stock_service = StockDataService()
indicator_service = IndicatorService()
signal_service = SignalService()
chart_service = ChartService()


def create_response(success=True, data=None, error=None):
    """
    創建統一的響應格式

    Args:
        success: 是否成功
        data: 數據
        error: 錯誤資訊

    Returns:
        dict: 響應字典
    """
    response = {
        'success': success,
        'meta': {
            'timestamp': datetime.now().isoformat(),
            'version': '1.0'
        }
    }

    if success:
        response['data'] = data
    else:
        response['error'] = error

    return response


@api_bp.route('/analyze', methods=['POST'])
def analyze_stock():
    """
    分析股票 API

    POST Body:
        {
            "ticker": "2330",
            "start_date": "2024-01-01",  // 可選
            "days": 120  // 可選
        }
    """
    try:
        # 獲取請求參數
        data = request.get_json()

        if not data or 'ticker' not in data:
            return jsonify(create_response(
                success=False,
                error={
                    'code': 'INVALID_REQUEST',
                    'message': '缺少必要參數: ticker'
                }
            )), 400

        ticker = data['ticker'].strip().upper()  # 轉為大寫以統一處理
        start_date = data.get('start_date', Config.DEFAULT_START_DATE)
        plot_days = data.get('days', Config.DEFAULT_PLOT_DAYS)

        # 驗證股票代號格式：4-6位數字，或4-6位數字+1個大寫字母（ETF）
        import re
        ticker_pattern = re.compile(r'^\d{4,6}[A-Z]?$')
        if not ticker_pattern.match(ticker):
            return jsonify(create_response(
                success=False,
                error={
                    'code': 'INVALID_TICKER_FORMAT',
                    'message': '股票代號格式錯誤（應為 4-6 位數字，或 4-6 位數字加一個字母，如：2330 或 00983A）'
                }
            )), 400

        # 獲取股票數據
        df = stock_service.get_stock_data(ticker, start_date)

        if df.empty:
            return jsonify(create_response(
                success=False,
                error={
                    'code': 'TICKER_NOT_FOUND',
                    'message': f'股票代號 {ticker} 不存在或無數據'
                }
            )), 404

        # 計算技術指標
        df_with_indicators = indicator_service.calculate_all(df)

        if len(df_with_indicators) < 60:
            return jsonify(create_response(
                success=False,
                error={
                    'code': 'INSUFFICIENT_DATA',
                    'message': '數據不足，需要至少 60 個交易日進行技術分析',
                    'details': f'當前僅有 {len(df_with_indicators)} 個交易日'
                }
            )), 400

        # 生成買點訊號
        df_with_signals = signal_service.generate_signals(df_with_indicators)

        # 取最近 N 天的數據用於繪圖
        plot_df = df_with_signals.tail(plot_days)
        signals_df = signal_service.get_signal_df(df_with_signals)

        # 篩選繪圖範圍內的訊號
        plot_start_date = plot_df.index[0]
        plot_signals = signals_df[signals_df.index >= plot_start_date]

        # 獲取訊號摘要
        signal_summary = signal_service.get_signal_summary(df_with_signals)
        recent_signals = signal_service.get_latest_signals(df_with_signals, limit=5)

        # 生成圖表
        candlestick_chart = chart_service.create_candlestick_chart(plot_df, plot_signals)
        volume_chart = chart_service.create_volume_chart(plot_df)
        macd_chart = chart_service.create_macd_chart(plot_df)

        # 獲取最新數據
        latest_row = df_with_signals.iloc[-1]
        latest_data = {
            'date': latest_row.name.strftime('%Y-%m-%d'),
            'close': round(latest_row['close'], 2),
            'volume': int(latest_row['volume']),
            'ma5': round(latest_row['ma5'], 2),
            'ma20': round(latest_row['ma20'], 2),
            'ma60': round(latest_row['ma60'], 2),
            'dif': round(latest_row['dif'], 2),
            'dem': round(latest_row['dem'], 2),
            'osc': round(latest_row['osc'], 2)
        }

        # 獲取快取資訊
        cache_info = stock_service.cache_manager.get_cache_info(ticker)

        # 獲取股票名稱
        stock_name = stock_service._get_stock_name(ticker)

        # 構建響應
        response_data = {
            'ticker': ticker,
            'stock_name': stock_name,
            'date_range': {
                'start': df_with_signals.index[0].strftime('%Y-%m-%d'),
                'end': df_with_signals.index[-1].strftime('%Y-%m-%d'),
                'total_days': len(df_with_signals)
            },
            'latest_data': latest_data,
            'signals': {
                'total_count': signal_summary['total_count'],
                'buy_total_count': signal_summary['buy_total_count'],
                'buy_type1_count': signal_summary['buy_type1_count'],
                'buy_type2_count': signal_summary['buy_type2_count'],
                'sell_total_count': signal_summary['sell_total_count'],
                'sell_type1_count': signal_summary['sell_type1_count'],
                'sell_type2_count': signal_summary['sell_type2_count'],
                'latest_signal': signal_summary['latest_signal'],
                'recent_signals': recent_signals
            },
            'chart': {
                'candlestick': candlestick_chart,
                'volume': volume_chart,
                'macd': macd_chart
            },
            'cache_info': {
                'is_cached': cache_info is not None,
                'last_update': cache_info['last_update'] if cache_info else None,
                'data_source': 'cache' if cache_info else 'fresh'
            }
        }

        return jsonify(create_response(success=True, data=response_data))

    except ValueError as e:
        return jsonify(create_response(
            success=False,
            error={
                'code': 'TICKER_NOT_FOUND',
                'message': str(e)
            }
        )), 404

    except Exception as e:
        print(f"API Error: {e}")
        print(traceback.format_exc())
        return jsonify(create_response(
            success=False,
            error={
                'code': 'INTERNAL_SERVER_ERROR',
                'message': '服務器內部錯誤',
                'details': str(e)
            }
        )), 500


@api_bp.route('/history', methods=['GET'])
def get_history():
    """獲取歷史記錄列表"""
    try:
        sort_by = request.args.get('sort_by', 'last_update')
        order = request.args.get('order', 'desc')

        stocks_info = stock_service.get_cached_stocks_info()

        # 排序
        reverse = (order == 'desc')
        if sort_by == 'ticker':
            stocks_info.sort(key=lambda x: x['ticker'], reverse=reverse)
        elif sort_by == 'last_update':
            stocks_info.sort(key=lambda x: x.get('last_update', ''), reverse=reverse)

        return jsonify(create_response(
            success=True,
            data={
                'total_count': len(stocks_info),
                'stocks': stocks_info
            }
        ))

    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={
                'code': 'INTERNAL_SERVER_ERROR',
                'message': str(e)
            }
        )), 500


@api_bp.route('/cache/<ticker>', methods=['GET'])
def get_cache_info(ticker):
    """獲取快取資訊"""
    try:
        cache_info = stock_service.cache_manager.get_cache_info(ticker)

        if not cache_info:
            return jsonify(create_response(
                success=False,
                error={
                    'code': 'CACHE_NOT_FOUND',
                    'message': f'股票代號 {ticker} 的快取不存在'
                }
            )), 404

        # 添加是否最新的資訊
        cache_info['is_up_to_date'] = stock_service.cache_manager.is_up_to_date(ticker)
        cache_info['missing_dates'] = stock_service.cache_manager.get_missing_dates(ticker)

        return jsonify(create_response(success=True, data=cache_info))

    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={
                'code': 'INTERNAL_SERVER_ERROR',
                'message': str(e)
            }
        )), 500


@api_bp.route('/cache/<ticker>', methods=['DELETE'])
def clear_cache(ticker):
    """清除快取"""
    try:
        success = stock_service.clear_cache(ticker)

        if not success:
            return jsonify(create_response(
                success=False,
                error={
                    'code': 'CACHE_NOT_FOUND',
                    'message': f'股票代號 {ticker} 的快取不存在'
                }
            )), 404

        return jsonify(create_response(
            success=True,
            data={
                'ticker': ticker,
                'deleted': True,
                'message': '快取已成功清除'
            }
        ))

    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={
                'code': 'INTERNAL_SERVER_ERROR',
                'message': str(e)
            }
        )), 500


@api_bp.route('/update/<ticker>', methods=['POST'])
def force_update(ticker):
    """強制更新股票數據"""
    try:
        result = stock_service.force_update(ticker)

        if not result['updated']:
            return jsonify(create_response(
                success=False,
                error={
                    'code': 'CACHE_NOT_FOUND',
                    'message': result['message']
                }
            )), 404

        return jsonify(create_response(success=True, data=result))

    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={
                'code': 'INTERNAL_SERVER_ERROR',
                'message': str(e)
            }
        )), 500


@api_bp.route('/stocks/list', methods=['GET'])
def get_stocks_list():
    """獲取所有股票列表（上市股票）"""
    try:
        import twstock

        stocks_list = []
        for ticker, info in twstock.twse.items():
            stocks_list.append({
                'ticker': ticker,
                'name': info.name,
                'display': f"{ticker} {info.name}"
            })

        # 按股票代號排序
        stocks_list.sort(key=lambda x: x['ticker'])

        return jsonify(create_response(
            success=True,
            data={
                'total_count': len(stocks_list),
                'stocks': stocks_list
            }
        ))

    except Exception as e:
        return jsonify(create_response(
            success=False,
            error={
                'code': 'INTERNAL_SERVER_ERROR',
                'message': str(e)
            }
        )), 500


@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康檢查"""
    import os

    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'cache_count': len(stock_service.cache_manager.get_all_cached_stocks()),
        'cache_dir_exists': os.path.exists(Config.CACHE_DIR)
    })
