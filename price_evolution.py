from forward_price_curve import ForwardPriceCurve
from price_process import PriceProcess
from typing import List
from IPython.display import clear_output
from datetime import date
from time import sleep

def display_evolving_fpc(
    fpc: ForwardPriceCurve, 
    process: PriceProcess, 
    observation_dates: List[date]
):
    """
    Displays a pyplot showing a price curve evolving over time according
    to the given process
    """
    initial_observation_date = fpc.observation_date
    for d in observation_dates:
        fpc.draw_curve(initial_observation_date)
        clear_output(wait=True)
        sleep(0.5)
        fpc = process.evolve(fpc, d)