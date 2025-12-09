"""
日期工具函式
"""
from datetime import datetime, timedelta
from typing import List


class DateUtils:
    """日期處理工具類"""

    @staticmethod
    def is_trading_day(date: datetime) -> bool:
        """
        判斷是否為交易日（排除週末）

        Args:
            date: 日期

        Returns:
            bool: 是否為交易日
        """
        # 週六=5, 週日=6
        return date.weekday() < 5

    @staticmethod
    def get_trading_days_between(start_date: datetime, end_date: datetime) -> List[str]:
        """
        獲取兩個日期之間的交易日列表

        Args:
            start_date: 開始日期
            end_date: 結束日期

        Returns:
            List[str]: 交易日期列表 (YYYY-MM-DD)
        """
        trading_days = []
        current = start_date

        while current <= end_date:
            if DateUtils.is_trading_day(current):
                trading_days.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)

        return trading_days

    @staticmethod
    def get_previous_trading_day(date: datetime = None) -> datetime:
        """
        獲取前一個交易日

        Args:
            date: 參考日期，默認為今天

        Returns:
            datetime: 前一個交易日
        """
        if date is None:
            date = datetime.now()

        previous = date - timedelta(days=1)

        # 如果是週末，繼續往前找
        while not DateUtils.is_trading_day(previous):
            previous -= timedelta(days=1)

        return previous

    @staticmethod
    def parse_date(date_str: str, fmt: str = '%Y-%m-%d') -> datetime:
        """
        解析日期字符串

        Args:
            date_str: 日期字符串
            fmt: 日期格式

        Returns:
            datetime: 日期對象
        """
        return datetime.strptime(date_str, fmt)

    @staticmethod
    def format_date(date: datetime, fmt: str = '%Y-%m-%d') -> str:
        """
        格式化日期

        Args:
            date: 日期對象
            fmt: 日期格式

        Returns:
            str: 格式化的日期字符串
        """
        return date.strftime(fmt)

    @staticmethod
    def get_yesterday() -> str:
        """
        獲取昨天的日期

        Returns:
            str: 昨天的日期 (YYYY-MM-DD)
        """
        yesterday = datetime.now() - timedelta(days=1)
        return yesterday.strftime('%Y-%m-%d')

    @staticmethod
    def get_date_range_months(start_date: datetime, end_date: datetime) -> List[tuple]:
        """
        獲取日期範圍內的所有年月組合

        Args:
            start_date: 開始日期
            end_date: 結束日期

        Returns:
            List[tuple]: (year, month) 元組列表
        """
        months = []
        current_year = start_date.year
        current_month = start_date.month

        while (current_year < end_date.year) or \
              (current_year == end_date.year and current_month <= end_date.month):
            months.append((current_year, current_month))

            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1

        return months
