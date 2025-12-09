"""
服務層測試
"""
import pytest
import pandas as pd
from services import IndicatorService, SignalService


class TestIndicatorService:
    """測試技術指標服務"""

    def test_calculate_ma(self):
        """測試移動平均線計算"""
        # 創建測試數據
        data = {
            'close': [100, 102, 101, 103, 105, 104, 106, 108, 107, 109]
        }
        df = pd.DataFrame(data)

        # 計算 MA
        result = IndicatorService.calculate_ma(df, periods=[3, 5])

        # 驗證
        assert 'ma3' in result.columns
        assert 'ma5' in result.columns
        assert not result['ma3'].isna().all()

    def test_calculate_macd(self):
        """測試 MACD 計算"""
        # 創建測試數據
        data = {
            'close': [i for i in range(100, 150)]
        }
        df = pd.DataFrame(data)

        # 計算 MACD
        result = IndicatorService.calculate_macd(df)

        # 驗證
        assert 'ema12' in result.columns
        assert 'ema26' in result.columns
        assert 'dif' in result.columns
        assert 'dem' in result.columns
        assert 'osc' in result.columns


class TestSignalService:
    """測試訊號服務"""

    def test_generate_signals(self):
        """測試訊號生成"""
        # 創建包含技術指標的測試數據
        data = {
            'close': [100, 102, 101, 103, 105],
            'ma5': [99, 100, 101, 102, 103],
            'ma20': [98, 99, 100, 101, 102],
            'ma60': [97, 98, 99, 100, 101],
            'volume': [1000, 1100, 1050, 1200, 1300],
            'avg_volume5': [1000, 1000, 1000, 1000, 1100],
            'dif': [1, 1.5, 2, 2.5, 3],
            'dem': [0.5, 1, 1.5, 2, 2.5],
            'osc': [0.5, 0.5, 0.5, 0.5, 0.5]
        }
        df = pd.DataFrame(data)

        # 生成訊號
        result = SignalService.generate_signals(df)

        # 驗證
        assert 'buy_signal' in result.columns
        assert 'signal_type1' in result.columns
        assert 'signal_type2' in result.columns

    def test_get_signal_summary(self):
        """測試訊號摘要"""
        # 創建包含訊號的測試數據
        data = {
            'close': [100, 102, 101],
            'ma20': [98, 99, 100],
            'buy_signal': ['', '趨勢確立買點', ''],
            'signal_type1': ['', '趨勢確立買點', ''],
            'signal_type2': ['', '', '']
        }
        df = pd.DataFrame(data)

        # 獲取摘要
        summary = SignalService.get_signal_summary(df)

        # 驗證
        assert 'total_count' in summary
        assert 'type1_count' in summary
        assert 'type2_count' in summary
        assert summary['total_count'] >= 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
