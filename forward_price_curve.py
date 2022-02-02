from datetime import date, timedelta
from numbers import Number
from typing import List, Dict
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter

def time_between(d0: date, d1: date):
    return (d1 - d0).days / 365.0

class ForwardPrice:
    """
    An observed price for some delivery day
    """
    def __init__(self, day: date, price: Number):
        self.day = day
        self.price = price
        
    def __mul__(self, x: Number):
        return ForwardPrice(self.day, self.price * x)
        
        
class ForwardPriceCurve:
    """
    A collection of prices for various delivery times, observed at some time
    
    Can draw itself as a pyplot
    """
    def __init__(self, observation_date: date, forward_prices: List[ForwardPrice]):
        self.observation_date = observation_date
        self.forward_prices = forward_prices
        self.delivery_days = [fp.day for fp in self.forward_prices]
        self.last_delivery_day = self.delivery_days[-1]
        
        # for interpolation
        self._ys = [fp.price for fp in self.forward_prices]
        self._xs = [time_between(self.observation_date, d) for d in self.delivery_days]
        
        
    def interpolated_price(self, delivery_date):
        x = time_between(self.observation_date, delivery_date)
        return np.interp(x, self._xs, self._ys)
        
    
    def remove_deliveries_expiring_before(self, boundary_date):
        return ForwardPriceCurve(
            self.observation_date,
            [fp for fp in self.forward_prices if fp.day >= boundary_date]
        )
    
    @staticmethod
    def from_market_data(observation_date: date, prices: Dict[date, Number]):
        """
        Builds a curve directly from the given sparse set of prices, but then interpolates this
        to produce an equivalent curve with more points. This is just to make scrolling smoother
        when we evolve prices and display the modified forward curve
        """
        delivery_dates = sorted(prices)
        coarse_fpc = ForwardPriceCurve(
            observation_date = observation_date,
            forward_prices = [ForwardPrice(day=d, price = prices[d]) for d in delivery_dates]
        )

        finer_dates = [observation_date + timedelta(i * 7) for i in range(100)]
        finer_dates += delivery_dates
        finer_dates = sorted(list(set(finer_dates)))
        return ForwardPriceCurve(
            observation_date = observation_date,
            forward_prices = [ForwardPrice(day=d, price = coarse_fpc.interpolated_price(d)) for d in finer_dates]
        )
    
    def draw_curve(self, initial_date):
        xs = [self.observation_date + timedelta(i) for i in range(30)]
        xs += [self.observation_date + timedelta(i * 10) for i in range(100)]
        xs.append(self.last_delivery_day)
        xs = [d for d in xs if d <= self.last_delivery_day]
        xs = sorted(list(set(xs)))
            
        ys = [self.interpolated_price(d) for d in xs]
        xtick_dates = [
            d 
            for y in range(2022, 2027) 
            for d in [date(y, 1, 1), date(y, 7, 1)] 
            if initial_date <= d and d <= self.last_delivery_day
        ]
        plt.rcParams['figure.figsize'] = [9, 6]
        fig, ax = plt.subplots()
        line, = ax.plot([])
        ax.xaxis.set_major_formatter(DateFormatter("%b/%y"))
        plt.xticks(xtick_dates)
        ax.set_xlim(initial_date, self.last_delivery_day)
        ax.set_ylim(0, 200)
        formatted_observation_date = self.observation_date.strftime("%d %b %y")
        ax.set_xlabel(f"Observation Date {formatted_observation_date}")
        ax.set_ylabel("TTF Price")
        line.set_data(xs, ys)
        plt.show()

        
def display_evolving_forward_prices(fpc, process, observation_dates):
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