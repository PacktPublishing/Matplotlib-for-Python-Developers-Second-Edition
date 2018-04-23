from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
from urllib.request import urlopen
import json
import datetime
import pandas as pd
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.dates import date2num, WeekdayLocator, DayLocator, DateFormatter, MONDAY
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.ticker import FuncFormatter
from stockstats import StockDataFrame


def get_bitcoin_dataset():
    """Obtain and parse a quandl bitcoin dataset in Pandas DataFrame format

    Quandl returns dataset in JSON format, where data is stored as a 
    list of lists in response['dataset']['data'], and column headers
    stored in response['dataset']['column_names'].
           
    Returns:
        df: Pandas DataFrame of a Quandl dataset

    """
    # Input your own API key here
    api_key = ""
    
    # Quandl code for Bitcoin historical price in BitStamp exchange
    code = "BCHARTS/BITSTAMPUSD"
    base_url = "https://www.quandl.com/api/v3/datasets/"
    url_suffix = ".json?api_key="
    
    # We want to get the data within a one-year window only
    time_now = datetime.datetime.now()
    one_year_ago = time_now.replace(year=time_now.year-1)
    start_date = one_year_ago.date().isoformat()
    end_date = time_now.date().isoformat()
    date = "&start_date={}&end_date={}".format(start_date, end_date)

    # Fetch the JSON response 
    u = urlopen(base_url + code + url_suffix + api_key + date)
    response = json.loads(u.read().decode('utf-8'))
    
    # Format the response as Pandas Dataframe
    df = pd.DataFrame(response['dataset']['data'], columns=response['dataset']['column_names'])
    
    # Convert Date column from string to Python datetime object,
    # then to float number that is supported by Matplotlib.
    df["Datetime"] = date2num(pd.to_datetime(df["Date"], format="%Y-%m-%d").tolist())
    
    return df


def candlestick_ohlc(ax, quotes, width=0.2, colorup='k', colordown='r',
                     alpha=1.0):
    """
    Adapted from the deprecated matplotlib.finance package
    Plot the time, open, high, low, close as a vertical line ranging
    from low to high.  Use a rectangular bar to represent the
    open-close span.  If close >= open, use colorup to color the bar,
    otherwise use colordown
    Parameters
    ----------
    ax : `Axes`
        an Axes instance to plot to
    quotes : sequence of (time, open, high, low, close, ...) sequences
        As long as the first 5 elements are these values,
        the record can be as long as you want (e.g., it may store volume).
        time must be in float days format - see date2num
    width : float
        fraction of a day for the rectangle width
    colorup : color
        the color of the rectangle where close >= open
    colordown : color
         the color of the rectangle where close <  open
    alpha : float
        the rectangle alpha level
    Returns
    -------
    ret : tuple
        returns (lines, patches) where lines is a list of lines
        added and patches is a list of the rectangle patches added
    """

    OFFSET = width / 2.0

    lines = []
    patches = []
    for q in quotes:
        t, open, high, low, close = q[:5]

        if close >= open:
            color = colorup
            lower = open
            height = close - open
        else:
            color = colordown
            lower = close
            height = open - close

        vline = Line2D(
            xdata=(t, t), ydata=(low, high),
            color=color,
            linewidth=0.5,
            antialiased=True,
        )

        rect = Rectangle(
            xy=(t - OFFSET, lower),
            width=width,
            height=height,
            facecolor=color,
            edgecolor=color,
        )
        rect.set_alpha(alpha)

        lines.append(vline)
        patches.append(rect)
        ax.add_line(vline)
        ax.add_patch(rect)
    ax.autoscale_view()

    return lines, patches


# FuncFormatter to convert tick values to Millions
def millions(x, pos):
    return '%dM' % (x/1e6)
    
    
def bitcoin_chart(request):
    # Get a dataframe of bitcoin prices
    bitcoin_df = get_bitcoin_dataset()
    
    # candlestick_ohlc expects Date (in floating point number), Open, High, Low, Close columns only
    # So we need to select the useful columns first using DataFrame.loc[]. Extra columns can exist, 
    # but they are ignored. Next we get the data for the last 30 trading only for simplicity of plots.
    candlestick_data = bitcoin_df.loc[:, ["Datetime",
                                          "Open",
                                          "High",
                                          "Low",
                                          "Close",
                                          "Volume (Currency)"]].iloc[:30]
                                          
    # Convert to StockDataFrame
    # Need to pass a copy of candlestick_data to StockDataFrame.retype
    # Otherwise the original candlestick_data will be modified
    stockstats = StockDataFrame.retype(candlestick_data.copy())
    

    # 5-day exponential moving average on closing price
    ema_5 = stockstats["close_5_ema"]
    # 10-day exponential moving average on closing price
    ema_10 = stockstats["close_10_ema"]
    # 30-day exponential moving average on closing price
    ema_30 = stockstats["close_30_ema"]
    # Upper Bollinger band
    boll_ub = stockstats["boll_ub"]
    # Lower Bollinger band
    boll_lb = stockstats["boll_lb"]
    # 7-day Relative Strength Index
    rsi_7 = stockstats['rsi_7']
    # 14-day Relative Strength Index
    rsi_14 = stockstats['rsi_14']

    # Create 3 subplots spread acrosee three rows, with shared x-axis. 
    # The height ratio is specified via gridspec_kw
    fig, axarr = plt.subplots(nrows=3, ncols=1, sharex=True, figsize=(8,8),
                             gridspec_kw={'height_ratios':[3,1,1]})

    # Prepare a candlestick plot in the first axes
    candlestick_ohlc(axarr[0], candlestick_data.values, width=0.6)

    # Overlay stock indicators in the first axes
    axarr[0].plot(candlestick_data["Datetime"], ema_5, lw=1, label='EMA (5)')
    axarr[0].plot(candlestick_data["Datetime"], ema_10, lw=1, label='EMA (10)')
    axarr[0].plot(candlestick_data["Datetime"], ema_30, lw=1, label='EMA (30)')
    axarr[0].plot(candlestick_data["Datetime"], boll_ub, lw=2, linestyle="--", label='Bollinger upper')
    axarr[0].plot(candlestick_data["Datetime"], boll_lb, lw=2, linestyle="--", label='Bollinger lower')

    # Display RSI in the second axes
    axarr[1].axhline(y=30, lw=2, color = '0.7') # Line for oversold threshold
    axarr[1].axhline(y=50, lw=2, linestyle="--", color = '0.8') # Neutral RSI
    axarr[1].axhline(y=70, lw=2, color = '0.7') # Line for overbought threshold
    axarr[1].plot(candlestick_data["Datetime"], rsi_7, lw=2, label='RSI (7)')
    axarr[1].plot(candlestick_data["Datetime"], rsi_14, lw=2, label='RSI (14)')

    # Display trade volume in the third axes
    axarr[2].bar(candlestick_data["Datetime"], candlestick_data['Volume (Currency)'])

    # Label the axes
    axarr[0].set_ylabel('Price (US $)')
    axarr[1].set_ylabel('RSI')
    axarr[2].set_ylabel('Volume (US $)')

    axarr[2].xaxis.set_major_locator(WeekdayLocator(MONDAY)) # major ticks on the mondays
    axarr[2].xaxis.set_minor_locator(DayLocator()) # minor ticks on the days
    axarr[2].xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    axarr[2].xaxis_date() # treat the x data as dates
    axarr[2].yaxis.set_major_formatter(FuncFormatter(millions)) # Change the y-axis ticks to millions
    plt.setp(axarr[2].get_xticklabels(), rotation=90, horizontalalignment='right') # Rotate x-tick labels by 90 degree

    # Limit the x-axis range to the last 30 days
    time_now = datetime.datetime.now()
    datemin = time_now-datetime.timedelta(days=30)
    datemax = time_now
    axarr[2].set_xlim(datemin, datemax)

    # Show figure legend
    axarr[0].legend()
    axarr[1].legend()

    # Show figure title
    axarr[0].set_title("Bitcoin 30-day price trend", loc='left')
    
    plt.tight_layout()
    
    # Create a bytes buffer for saving image
    fig_buffer = BytesIO()
    plt.savefig(fig_buffer, dpi=150)
    
    # Save the figure as a HttpResponse
    response = HttpResponse(content_type='image/png')
    response.write(fig_buffer.getvalue())
    fig_buffer.close()
    
    return response


