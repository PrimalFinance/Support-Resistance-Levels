# Number manipulation
import numpy as np
import pandas as pd
from scipy.signal import argrelextrema

# Stock data
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries

# Date calculations
import datetime as dt

# Graph creation
import matplotlib.pyplot as plt
import plotly.graph_objects as go


# Trendline library
from TradeRanges.trend_lines import TrendLines


# API Keys
import os
from dotenv import load_dotenv

load_dotenv()

alpha_vantage_key = os.getenv("alpha_vantage_key")


class TradeRanges:
    def __init__(
        self,
        ticker: str,
        data_source: str,
        months: int = 6,
        interval: str = "5min",
        n1: int = 3,
        n2: int = 2,
    ):

        self.ticker = ticker
        self.data_source = data_source
        self.month_range = months
        self.interval = interval
        self.trend_start_offset = 0
        self.stock_data = pd.DataFrame()

        self.n1 = n1
        self.n2 = n2

    """--------------------------------------"""
    """--------------------------------------"""

    def set_stock_data(self) -> None:

        # If the data is retrieved from Yahoo Finance (Yfinance)
        if self.data_source == "Yahoo":
            # Get the start and end date for our window of time.
            start_date, end_date = self.get_start_end_dates()
            # Convert datetime objects to strings.
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            # Download data from Yahoo Finance.
            self.stock_data = yf.download(
                self.ticker, start=start_date_str, end=end_date_str
            )
        # If the data is retrieved from Alpha Vantage (alpha_vantage)
        elif self.data_source == "Alpha":
            ts = TimeSeries(key=alpha_vantage_key, output_format="pandas")
            # Retrieve intra-day stock data
            self.stock_data, meta_data = ts.get_intraday(
                symbol=self.ticker, interval=self.interval, outputsize="full"
            )
            self.stock_data.columns = ["Open", "High", "Low", "Close", "Volume"]

    """--------------------------------------"""

    def get_stock_data(self) -> pd.DataFrame:
        if self.stock_data.empty:
            self.set_stock_data()
        return self.stock_data

    """--------------------------------------"""
    """--------------------------------------"""
    """--------------------------------------"""
    """--------------------------------------"""
    """--------------------------------------"""
    """--------------------------------------"""
    """--------------------------------------"""
    """--------------------------------------"""
    """--------------------------------------"""
    """--------------------------------------"""
    """--------------------------------------"""
    """-------------------------------------- Utilities --------------------------------------"""

    def get_start_end_dates(self) -> str:
        end_date = dt.datetime.now().date()
        start_date = end_date - dt.timedelta(days=self.month_range * 30)
        return start_date, end_date

    """--------------------------------------"""
    """--------------------------------------"""
    """--------------------------------------"""
    """--------------------------------------"""
    """--------------------------------------"""
    """--------------------------------------"""
    """--------------------------------------"""
    """--------------------------------------"""
    """-------------------------------------- Graph Related Functions --------------------------------------"""
    """--------------------------------------"""

    def plot_graph(self) -> None:

        # Check if there is data. If not, set the data to the class variable "self.stock_data"
        if self.stock_data.empty:
            self.set_stock_data()

        # Remove the dates as indexes. Replace them with numerical values. The first entry should be indexed with "1".
        indexed_stock_data = self.stock_data.reset_index(drop=True)

        # Get the index of the last entry
        end = indexed_stock_data.index[-1]

        # Clean data according to the data source.
        if self.data_source == "Yahoo":
            start = indexed_stock_data.index[0]
        elif self.data_source == "Alpha":
            start = indexed_stock_data.index[-200]
            indexed_stock_data = indexed_stock_data[start:end]
            indexed_stock_data.reset_index(drop=True, inplace=True)

        print(f"Indexed: {indexed_stock_data.index}")
        layout = go.Layout(title=f"{self.ticker.upper()} || {self.month_range} months")
        # Create a plotly figure
        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=indexed_stock_data.index,
                    open=indexed_stock_data["Open"],
                    high=indexed_stock_data["High"],
                    low=indexed_stock_data["Low"],
                    close=indexed_stock_data["Close"],
                )
            ],
            layout=layout,
        )

        # Currently the resistance and support data is calculated locally. May change to class scope later.
        support, resistance = self.get_trendlines(indexed_stock_data)

        # Delete the overlapping trends
        support = self.delete_overlapping_trends(support)
        resistance = self.delete_overlapping_trends(resistance)

        print(
            f"""Data: {len(indexed_stock_data)}
                  Support: {len(support)}
                  Resistance: {len(resistance)}"""
        )

        # Add the trendline for support levels
        self.add_trendline(figure=fig, data=support, color="Green", end=end)

        # Add the trendline for resistance levels
        self.add_trendline(figure=fig, data=resistance, color="Red", end=end)

        fig.show()

    """--------------------------------------"""
    """--------------------------------------"""
    """--------------------------------------"""
    """--------------------------------------"""
    """--------------------------------------"""
    """--------------------------------------"""
    """--------------------------------------"""

    def support(self, l, data):
        """
        l: Index of the candle stick
        """
        for i in range(l - self.n1 + 1, l + 1):
            # Check if low values before the candle "l" are going in a increasing order. Return 0 as support line breaks out.
            if data.Low.iloc[i] > data.Low.iloc[i - 1]:
                return 0
        for i in range(l + 1, l + self.n2 + 1):
            if data.Low.iloc[i] < data.Low.iloc[i - 1]:
                return 0
        # If criteria is met return 1
        return 1

    """--------------------------------------"""

    def resistance(self, l, data):
        """
        l: Index of the candle stick
        data: Pandas dataframe of historical trading data.
        """

        for i in range(l - self.n1 + 1, l + 1):
            if data.High.iloc[i] < data.High.iloc[i - 1]:
                return 0

        for i in range(l + 1, l + self.n2 + 1):
            if data.High.iloc[i] > data.High.iloc[i - 1]:
                return 0
        return 1

    """--------------------------------------"""

    def get_trendlines(self, data: pd.DataFrame) -> tuple:
        # Create an empty list to hold support & resistance data.
        ss = []
        rr = []
        end_index = data.index[-1]
        for row in range(self.n1, end_index):
            # If the function returns a 1
            if self.support(l=row, data=data):
                # The 1 at the end, is the value assigned to support values.
                ss.append((row, data.Low.iloc[row]))
            if self.resistance(l=row, data=data):
                # The 2 at the end is the value assigned to resistance values.
                rr.append((row, data.High.iloc[row]))

        return ss, rr

    """--------------------------------------"""
    """--------------------------------------"""

    def delete_overlapping_trends(self, plotlist, sensitivity: float = 0.0005):
        """
        plotlist: List of data containing Support or Resistance levels.
        sensitivity: Determines the conditions for trends to be removed. The lower the value, the more sensitive.
        """

        for i in range(1, len(plotlist)):
            if i >= len(plotlist):
                break
            if abs(plotlist[i][1] - plotlist[i - 1][1]) <= sensitivity:
                plotlist.pop(i)

        return plotlist

    """--------------------------------------"""

    def add_trendline(self, figure, data: pd.DataFrame, color: str, end: int):

        c = 0
        while 1:
            if c > len(data) - 1:
                break
            figure.add_shape(
                type="line",
                x0=data[c][0] - self.trend_start_offset,
                y0=data[c][1],
                x1=end,
                y1=data[c][1],
                line=dict(color=color),
            )
            c += 1
