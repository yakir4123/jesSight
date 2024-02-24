import logging

from jessight.strategy_scheduler import Scheduler

# TODO: Add implementation for this class
# TODO: All prints should be changed to logger


class RiskManager:
	def __init__(self, capital: float, strategy_scheduler: Scheduler):
		log = logging.LoggerAdapter(logging.getLogger(), {"total_capital": capital})
		log.info("Initializing risk manager")

		self.capital = capital
		self.strategy_scheduler: Scheduler = strategy_scheduler
