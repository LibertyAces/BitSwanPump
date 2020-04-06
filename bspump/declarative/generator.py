import inspect

import bspump

from .builder import ExpressionBuilder


class DeclarativeGenerator(bspump.Generator):
	"""
	Example of usage:

		---
		pipeline_id: AnalyticsUserPipeline
		generator: |
			--- !DICT
			with: !EVENT
			add:
				user_password_info:
					!LOOKUP
					lookup: UserPasswordLookup (synchronous/asynchronous lookup)
					key:
						!ITEM
						with: !EVENT
						item: user
	"""

	@classmethod
	def construct(cls, app, pipeline, definition: dict):
		_id = definition.get("id")
		config = definition.get("config")
		declaration = definition.get("declaration")
		return cls(app, pipeline, declaration=declaration, id=_id, config=config)

	@staticmethod
	async def _process_futures_in_dict(_dict):
		for field, value in _dict.items():
			if inspect.iscoroutine(value):
				_dict[field] = await value
		return _dict

	def __init__(self, app, pipeline, declaration, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		builder = ExpressionBuilder(app)
		self.Expression = builder.parse(declaration)

	async def generate(self, context, event, depth):
		self.Pipeline.inject(
			await self._process_futures_in_dict(context),
			await self._process_futures_in_dict(self.Expression(context, event)),
			depth
		)
