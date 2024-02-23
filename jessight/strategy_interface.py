from abc import ABC, abstractmethod

# TODO: Add more relevant methods what should exist in all strategies
# TODO: Add type hints for every method


class Strategy(ABC):

	@abstractmethod
	def before(self):
		pass

	@abstractmethod
	def after(self):
		pass

	@abstractmethod
	def update_position(self):
		pass

	@abstractmethod
	def should_cancel_entry(self):
		pass

	@abstractmethod
	def should_long(self):
		pass

	@abstractmethod
	def should_short(self):
		pass

	@abstractmethod
	def go_long(self):
		pass

	@abstractmethod
	def go_short(self):
		pass

