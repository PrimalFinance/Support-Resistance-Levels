import pandas as pd


class TrendLines:
    def __init__(
        self, ticker: str, stock_data: pd.DataFrame, n1: int = 3, n2: int = 2
    ) -> None:
        """
        ticker: Stocker ticker of the company
        stock_data: Candle data from Yahoo Finance
        date_indexes: The trading days present in "stock_data"
        indexes: The index of the trading day in "stock_data"
        n1: Number of candles before the indexed candle
        n2: Number of candles after the indexed candle"""
        self.ticker = ticker
        self.stock_data = stock_data
        self.date_indexes = self.stock_data.index
        self.stock_data.reset_index(drop=True, inplace=True)
        self.indexes = self.stock_data.index
        self.n1 = n1
        self.n2 = n2

        self.sr = []
        self.ss = []
        self.rr = []

    """--------------------------------------"""

    def support(self, l):
        """
        l: Index of the candle stick
        n1: Number of candles before the index
        n2: Number of candles after the index
        """
        for i in range(l - self.n1 + 1, l + 1):
            # Check if low values before the candle "l" are going in a increasing order. Return 0 as support line breaks out.
            if self.stock_data.Low[i] > self.stock_data.Low[i - 1]:
                return 0
        for i in range(l + 1, l + self.n2 + 1):
            if self.stock_data.Low[i] < self.stock_data.Low[i - 1]:
                return 0
        # If criteria is met return 1
        return 1

    """--------------------------------------"""

    def resistance(self, l):
        """
        l: Index of the candle stick
        n1: Number of candles before the index
        n2: Number of candles after the index
        """

        for i in range(l - self.n1 + 1, l + 1):
            if self.stock_data.High[i] < self.stock_data.High[i - 1]:
                return 0

        for i in range(l + 1, l + self.n2 + 1):
            if self.stock_data.High[i] > self.stock_data.High[i - 1]:
                return 0
        return 1

    """--------------------------------------"""

    def set_trendlines(self, data=None):
        # If no data is passed, default to the class variable.
        if data.empty:
            for row in range(self.n1, self.indexes[-1]):
                # If the function returns a 1
                if self.support(row):
                    # The 1 at the end, is the value assigned to support values.
                    self.ss.append((row, self.stock_data.Low[row]))
                if self.resistance(row):
                    # The 2 at the end is the value assigned to resistance values.
                    self.rr.append((row, self.stock_data.High[row]))
        else:
            end_index = data.index[-1]
            for row in range(self.n1, end_index):
                # If the function returns a 1
                if self.support(row):
                    # The 1 at the end, is the value assigned to support values.
                    self.ss.append((row, data.Low[row]))
                if self.resistance(row):
                    # The 2 at the end is the value assigned to resistance values.
                    self.rr.append((row, data.High[row]))

    """--------------------------------------"""

    def get_trendlines(self, data=None) -> list:
        if self.ss == []:
            if data.empty:
                self.set_trendlines()
            else:
                self.set_trendlines(data)
        return self.ss, self.rr

    """--------------------------------------"""
    """--------------------------------------"""

    def set_stock_data(self, data):
        self.stock_data = data

    """--------------------------------------"""
    """--------------------------------------"""
    """--------------------------------------"""
    """--------------------------------------"""
    """--------------------------------------"""
    """--------------------------------------"""
    """--------------------------------------"""
    """--------------------------------------"""
