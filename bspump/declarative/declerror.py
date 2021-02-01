

class DeclarationError(RuntimeError):

	def __init__(self, original_exception, location=None):
		"""
		:param original_exception: message
		:param location: used by expressions
		"""

		self.OriginalException = original_exception
		self.Location = location
		super().__init__(original_exception)

	def __str__(self):
		if self.Location is None:
			return super().__str__()
		else:
			return "{}\n{}".format(
				self.OriginalException, self.Location
			)
