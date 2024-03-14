# Import trading ranges class
from TradeRanges.trade_ranges import TradeRanges


def __init__():
    ticker = "MARA"
    tr = TradeRanges(ticker, months=3, data_source="Yahoo")
    tr.plot_graph()


__init__()
