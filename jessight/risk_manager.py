from typing import List

from jessight.strategy_interface import Strategy
from jessight.strategy_scheduler import Scheduler

# TODO: Add implementation for this class


class RiskManager:
	def __init__(self, strategies: List[Strategy]):
		self.strategy_scheduler: Scheduler = Scheduler(strategies)
