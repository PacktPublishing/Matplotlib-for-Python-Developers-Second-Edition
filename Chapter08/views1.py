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

    # Create a new Matplotlib figure
    fig, ax = plt.subplots()

    # Prepare a candlestick plot
    candlestick_ohlc(ax, candlestick_data.values, width=0.6)

    ax.xaxis.set_major_locator(WeekdayLocator(MONDAY)) # major ticks on the mondays
    ax.xaxis.set_minor_locator(DayLocator()) # minor ticks on the days
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    ax.xaxis_date() # treat the x data as dates
    
    # rotate all ticks to vertical
    plt.setp(ax.get_xticklabels(), rotation=90, horizontalalignment='right') 

    ax.set_ylabel('Price (US $)') # Set y-axis label
    
    plt.tight_layout()
    
    # Create a bytes buffer for saving image
    fig_buffer = BytesIO()
    plt.savefig(fig_buffer, dpi=150)
    
    # Save the figure as a HttpResponse
    response = HttpResponse(content_type='image/png')
    response.write(fig_buffer.getvalue())
    fig_buffer.close()
    
    return response


