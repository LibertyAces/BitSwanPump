from .processor import ProcessorBase

class Generator(ProcessorBase):
	"""
    Example of use:

.. code:: python

    class GeneratingProcessor(bspump.Generator):

        def process(self, context, event):

            def generate(items):
                for item in items:
                    yield item

            return generate(event.items)
    """
	pass
