from datetime import date, timedelta
from numbers import Number
from typing import List, Dict
import numpy as np
from sample_ttf_prices import TTF_28_JAN_PRICES

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
    
    def add_price_for_date(self, delivery_date):
        if delivery_date in self.delivery_days:
            return self
        return ForwardPriceCurve(
            self.observation_date,
            sorted(
                self.forward_prices + [ForwardPrice(delivery_date, self.interpolated_price(delivery_date))],
                key=lambda fp:fp.day
            )
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
    
    @staticmethod
    def jan_28_ttf_curve():
        return ForwardPriceCurve.from_market_data(date(2022, 1, 28), TTF_28_JAN_PRICES)
    

        
