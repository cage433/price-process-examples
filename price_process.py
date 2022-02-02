import numpy as np
from forward_price_curve import ForwardPriceCurve
from datetime import date
from abc import ABC, abstractmethod

class PriceProcess(ABC):
    """
    A price process has the ability to evolve forward prices from one day to the next
    """
    def __init__(self):
        self.rng = np.random.default_rng()
        
    @abstractmethod
    def evolve(fpc: ForwardPriceCurve, next_observation_date: date) -> ForwardPriceCurve:
        """ randomly perturb the forward curve"""
 
    @staticmethod
    def risk_adj(s, dt):
        return 0.5 * s * s * dt
