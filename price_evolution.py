from forward_price_curve import ForwardPriceCurve
from price_process import PriceProcess
from typing import List
from IPython.display import clear_output
from datetime import date, timedelta
from time import sleep
from numbers import Number
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter


def draw_curve(fpc, title, initial_date, ylim):
    xs = [fpc.observation_date + timedelta(i) for i in range(30)]
    xs += [fpc.observation_date + timedelta(i * 10) for i in range(100)]
    xs.append(fpc.last_delivery_day)
    xs = [d for d in xs if d <= fpc.last_delivery_day]
    xs = sorted(list(set(xs)))
            
    ys = [fpc.interpolated_price(d) for d in xs]
    xtick_dates = [
        d 
        for y in range(2022, 2027) 
        for d in [date(y, 1, 1), date(y, 7, 1)] 
        if initial_date <= d and d <= fpc.last_delivery_day
    ]
    plt.rcParams['figure.figsize'] = [9, 6]
    fig, ax = plt.subplots()
    plt.title(title)
    line, = ax.plot([])
    ax.xaxis.set_major_formatter(DateFormatter("%b/%y"))
    plt.xticks(xtick_dates)
    ax.set_xlim(initial_date, fpc.last_delivery_day)
    ax.set_ylim(0, ylim)
    formatted_observation_date = fpc.observation_date.strftime("%d %b %y")
    ax.set_xlabel(f"Observation Date {formatted_observation_date}")
    ax.set_ylabel("TTF Price")
    line.set_data(xs, ys)
    plt.show()

def display_evolving_fpc(
    fpc: ForwardPriceCurve, 
    process: PriceProcess, 
    title: str,
    day_step:int = 7,
    num_steps: int = 20,
    sleep_sec: Number = 0.5,
    restricted_relative_period=None
):
    """
    Displays a pyplot showing a price curve evolving over time according
    to the given process
    """
    observation_dates = [fpc.observation_date + timedelta(day_step * i) for i in range(num_steps)]
    initial_observation_date = fpc.observation_date
    ylim = 100
    for d in observation_dates:
        ylim = max(ylim, fpc.max_price() * 1.1)
        draw_curve(fpc, title, initial_observation_date, ylim)
        clear_output(wait=True)
        sleep(sleep_sec)
        fpc = process.evolve(fpc, d)