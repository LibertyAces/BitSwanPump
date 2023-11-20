from ..abc.processor import Processor


class FlattenDictProcessor(Processor):
	"""
	Description: ....

			Inspired by https://github.com/amirziai/flatten

		Example:

		"person": {
			"details": {
				"first_name": "John",
				"last_name": "Doe"
			},
			"address": {
				"country": "GB",
				"city": "London",
				"postal_code": "WC2N 5DU"
			}
		}

		Gets converted to:

		{
			"person.details.first_name": "John",
			"person.details.last_name": "Doe",
			"person.address.country": "GB",
			"person.address.city": "London",
			"person.address.postal_code": "WC2N 5DU"
		}


	"""
	ConfigDefaults = {
		'separator': '.'
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		self.Separator = self.Config['separator']


	def _construct_key(self, previous_key, new_key):
		"""
		Description:

		:return: new_key

		|

		"""
		if previous_key:
			return u"{}{}{}".format(previous_key, self.Separator, new_key)
		else:
			return new_key


	def flatten(self, nested_dict):
		"""
		Description:

		:return: flattened_dict

		|

		"""

		flattened_dict = dict()

		def _flatten(object_, key):

			if not object_:
				flattened_dict[key] = object_

			# Dictionary
			elif isinstance(object_, dict):
				for object_key in object_:
					_flatten(
						object_[object_key],
						self._construct_key(
							key,
							object_key))
			# Anything else
			else:
				flattened_dict[key] = object_

		_flatten(nested_dict, None)
		return flattened_dict


	def process(self, context, event):
		"""
		Description:

		:return: event

		|

		"""
		event = self.flatten(event)
		return event
