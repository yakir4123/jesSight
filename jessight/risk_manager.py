from typing import List

from jessight.strategy_interface import Strategy
from jessight.strategy_scheduler import Scheduler
from jessight.exceptions.UnchangeableCapital import UnchangeableCapitalException

# TODO: Add implementation for this class
# TODO: All prints should be changed to logger


class RiskManager:
	# Capital will be split equally by default
	# TODO: Add logger to this class
	def __init__(self, capital: float, strategy_scheduler: Scheduler):
		self.capital = capital

		self.strategy_scheduler: Scheduler = strategy_scheduler
