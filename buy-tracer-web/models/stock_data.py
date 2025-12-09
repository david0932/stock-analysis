"""
股票數據模型
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class StockData:
    """股票基本數據模型"""
    ticker: str
    stock_name: str
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    capacity: Optional[int] = None

    def to_dict(self):
        """轉換為字典"""
        return {
            'ticker': self.ticker,
            'stock_name': self.stock_name,
            'date': self.date,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'capacity': self.capacity
        }

    @classmethod
    def from_dict(cls, data: dict):
        """從字典創建對象"""
        return cls(
            ticker=data.get('ticker'),
            stock_name=data.get('stock_name'),
            date=data.get('date'),
            open=data.get('open'),
            high=data.get('high'),
            low=data.get('low'),
            close=data.get('close'),
            volume=data.get('volume'),
            capacity=data.get('capacity')
        )


@dataclass
class TechnicalIndicators:
    """技術指標數據模型"""
    date: str
    ma5: Optional[float] = None
    ma20: Optional[float] = None
    ma60: Optional[float] = None
    ema12: Optional[float] = None
    ema26: Optional[float] = None
    dif: Optional[float] = None
    dem: Optional[float] = None
    osc: Optional[float] = None
    avg_volume5: Optional[float] = None

    def to_dict(self):
        """轉換為字典"""
        return {
            'date': self.date,
            'ma5': self.ma5,
            'ma20': self.ma20,
            'ma60': self.ma60,
            'ema12': self.ema12,
            'ema26': self.ema26,
            'dif': self.dif,
            'dem': self.dem,
            'osc': self.osc,
            'avg_volume5': self.avg_volume5
        }


@dataclass
class BuySignal:
    """買點訊號數據模型"""
    date: str
    signal_type: str
    close: float
    ma20: float
    volume: int
    avg_volume5: float
    dif: float
    dem: float
    osc: float

    def to_dict(self):
        """轉換為字典"""
        return {
            'date': self.date,
            'signal_type': self.signal_type,
            'close': self.close,
            'ma20': self.ma20,
            'volume': self.volume,
            'avg_volume5': self.avg_volume5,
            'dif': self.dif,
            'dem': self.dem,
            'osc': self.osc
        }
