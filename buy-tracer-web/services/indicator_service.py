"""
技術指標服務
負責計算移動平均線、MACD 等技術指標
"""
import pandas as pd
from config import Config


class IndicatorService:
    """技術指標計算服務"""

    @staticmethod
    def calculate_all(df: pd.DataFrame) -> pd.DataFrame:
        """
        計算所有技術指標

        Args:
            df: 原始股票數據 DataFrame

        Returns:
            pd.DataFrame: 包含技術指標的 DataFrame
        """
        df = df.copy()

        # 計算移動平均線
        df = IndicatorService.calculate_ma(df)

        # 計算 MACD
        df = IndicatorService.calculate_macd(df)

        # 計算成交量均線
        df = IndicatorService.calculate_volume_ma(df)

        # 移除 NaN 值
        df = df.dropna()

        return df

    @staticmethod
    def calculate_ma(df: pd.DataFrame, periods: list = None) -> pd.DataFrame:
        """
        計算移動平均線

        Args:
            df: DataFrame
            periods: MA 週期列表

        Returns:
            pd.DataFrame: 包含 MA 的 DataFrame
        """
        if periods is None:
            periods = Config.MA_PERIODS

        df = df.copy()

        for period in periods:
            col_name = f'ma{period}'
            df[col_name] = df['close'].rolling(window=period).mean()

        return df

    @staticmethod
    def calculate_macd(df: pd.DataFrame,
                      fast: int = None,
                      slow: int = None,
                      signal: int = None) -> pd.DataFrame:
        """
        計算 MACD 指標

        Args:
            df: DataFrame
            fast: 快線週期
            slow: 慢線週期
            signal: 訊號線週期

        Returns:
            pd.DataFrame: 包含 MACD 的 DataFrame
        """
        if fast is None:
            fast = Config.MACD_FAST
        if slow is None:
            slow = Config.MACD_SLOW
        if signal is None:
            signal = Config.MACD_SIGNAL

        df = df.copy()

        # 計算 EMA
        df['ema12'] = df['close'].ewm(span=fast, adjust=False).mean()
        df['ema26'] = df['close'].ewm(span=slow, adjust=False).mean()

        # 計算 DIF (快線)
        df['dif'] = df['ema12'] - df['ema26']

        # 計算 DEM (慢線/訊號線)
        df['dem'] = df['dif'].ewm(span=signal, adjust=False).mean()

        # 計算 OSC (柱狀體)
        df['osc'] = df['dif'] - df['dem']

        return df

    @staticmethod
    def calculate_volume_ma(df: pd.DataFrame, period: int = 5) -> pd.DataFrame:
        """
        計算成交量移動平均

        Args:
            df: DataFrame
            period: 週期

        Returns:
            pd.DataFrame: 包含成交量均線的 DataFrame
        """
        df = df.copy()
        df['avg_volume5'] = df['volume'].rolling(window=period).mean()
        return df

    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        計算 RSI 指標（可選，未來擴展）

        Args:
            df: DataFrame
            period: 週期

        Returns:
            pd.DataFrame: 包含 RSI 的 DataFrame
        """
        df = df.copy()

        # 計算價格變動
        delta = df['close'].diff()

        # 分離上漲和下跌
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        # 計算 RS 和 RSI
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        return df

    @staticmethod
    def calculate_bollinger_bands(df: pd.DataFrame,
                                  period: int = 20,
                                  num_std: float = 2.0) -> pd.DataFrame:
        """
        計算布林通道（可選，未來擴展）

        Args:
            df: DataFrame
            period: 週期
            num_std: 標準差倍數

        Returns:
            pd.DataFrame: 包含布林通道的 DataFrame
        """
        df = df.copy()

        # 計算中軌（MA）
        df['bb_middle'] = df['close'].rolling(window=period).mean()

        # 計算標準差
        std = df['close'].rolling(window=period).std()

        # 計算上軌和下軌
        df['bb_upper'] = df['bb_middle'] + (std * num_std)
        df['bb_lower'] = df['bb_middle'] - (std * num_std)

        return df
