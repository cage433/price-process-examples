from forward_price_curve import ForwardPriceCurve
from price_process import PriceProcess
from typing import List, Optional, Tuple
from IPython.display import clear_output
from datetime import date, timedelta
from time import sleep
from numbers import Number
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter


class FPCGraphBuilder:
    def __init__(
        self,
        fpc: ForwardPriceCurve, 
        title: str, 
        y_axis_range: Tuple[Number, Number],
        x_axis_first_date: Optional[date]=None,
        x_axis_last_date: Optional[date]=None,
        max_relative_days: Optional[int]=None
    ):
        self.fpc = fpc
        self.title = title
        self.y_axis_range = y_axis_range
        self.x_axis_first_date = x_axis_first_date
        self.x_axis_last_date = x_axis_last_date
        self.max_relative_days = max_relative_days
        
    @property
    def _is_relative(self):
        return self.max_relative_days is not None
    
    @property
    def _x_axis_date_range(self):
        if self._is_relative:
            return self.fpc.observation_date, self.fpc.observation_date + timedelta(self.max_relative_days)
        return self.x_axis_first_date or self.fpc.observation_date, self.x_axis_last_date or self.fpc.last_delivery_day
    
    @property
    def delivery_days_to_draw(self):
        first_day, last_day = self._x_axis_date_range
        # Choice of days within the range is arbitrary. 
        # We use daily steps to avoid interpolation errors at the front, and larger steps after the first month
        # for speed
        spot_delivery_day = self.fpc.observation_date + timedelta(1)
        days = [spot_delivery_day + timedelta(i) for i in range(30)]
        days += [spot_delivery_day + timedelta(i * 10) for i in range(100)]
        days.append(self.fpc.last_delivery_day)
        days = [d for d in days if first_day <= d and d <= last_day]
        return sorted(list(set(days)))
        
    @property
    def relative_days_to_draw(self):
        first_day, _ = self._x_axis_date_range
        return [(d - first_day).days for d in self.delivery_days_to_draw]
        
        
    def show(self):
        
        ys = [self.fpc.interpolated_price(d) for d in self.delivery_days_to_draw]
        y_axis_range = min(self.y_axis_range[0], min(ys) * 0.9), max(self.y_axis_range[1], max(ys) * 1.1)
        plt.rcParams['figure.figsize'] = [9, 6]
        fig, ax = plt.subplots()
        line, = ax.plot([])
        if self._is_relative:
            xs = self.relative_days_to_draw
            ax.set_xlim(1, xs[-1])
            ax.set_xlabel("Days Ahead")
            plt.xticks(list(range(0, xs[-1] + 1, 10)))
        else:
            first_day, last_day = self._x_axis_date_range
            xs = self.delivery_days_to_draw
            ax.xaxis.set_major_formatter(DateFormatter("%b/%y"))
            ax.set_xlim(first_day, last_day)
            ax.set_xlabel("Delivery Day")
            plt.xticks([
                d 
                for y in range(2022, 2027) 
                for d in [date(y, 1, 1), date(y, 7, 1)] 
                if first_day <= d and d <= last_day
            ])
        ax.set_ylim(y_axis_range[0], y_axis_range[1])

        formatted_observation_date = self.fpc.observation_date.strftime("%d %b %y")
        plt.title(f"{self.title} {formatted_observation_date}")
        line.set_data(xs, ys)
        plt.show()
        return y_axis_range
        
        
def display_evolving_fpc(
    fpc: ForwardPriceCurve, 
    process: PriceProcess, 
    title: str,
    day_step:int = 7,
    num_steps: int = 20,
    sleep_sec: Number = 0.5,
    max_relative_days=None,
    initial_y_axis_range=None,
    x_axis_last_date=None
):
    """
    Displays a pyplot showing a price curve evolving over time according
    to the given process
    """
    observation_dates = [fpc.observation_date + timedelta(day_step * i) for i in range(num_steps)]
    initial_observation_date = fpc.observation_date
    y_axis_range = initial_y_axis_range or (0, 100)
    for d in observation_dates:
        y_axis_range = FPCGraphBuilder(
            fpc, title, 
            y_axis_range=y_axis_range, 
            x_axis_first_date=initial_observation_date, 
            x_axis_last_date=x_axis_last_date, 
            max_relative_days=max_relative_days
        ).show()
        clear_output(wait=True)
        sleep(sleep_sec)
        fpc = process.evolve(fpc, d)
        
        
        
        