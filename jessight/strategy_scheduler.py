import logging
from typing import List

from jessight.strategy_interface import Strategy

# TODO: Add implementation for this class


class Scheduler:
	# TODO: Add logger to this class
	def __init__(self, strategies: List[Strategy]):
		log = logging.LoggerAdapter(
			logging.getLogger(),
			{"strategy": {"strategies": map(lambda indicator: indicator.name(), strategies)}},
		)
		log.info("Initializing strategy scheduler")

		self.strategies: List[Strategy] = strategies
