class UnchangeableCapitalException(Exception):
    """Exception raised for objects with fixed capital.

    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message="restricted to update capital"):
        self.message = message
        super().__init__(self.message)
