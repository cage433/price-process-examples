from forward_price_curve import ForwardPriceCurve
from price_process import PriceProcess
from typing import List
from IPython.display import clear_output
from datetime import date, timedelta
from time import sleep
from numbers import Number


def display_evolving_fpc(
    fpc: ForwardPriceCurve, 
    process: PriceProcess, 
    day_step:int = 7,
    num_steps: int = 20,
    sleep_sec: Number = 0.5
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
        fpc.draw_curve(initial_observation_date, ylim)
        clear_output(wait=True)
        sleep(sleep_sec)
        fpc = process.evolve(fpc, d)