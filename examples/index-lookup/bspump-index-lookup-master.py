import logging
import numpy as np
import pandas

import bspump
import bspump.common
import bspump.elasticsearch
import bspump.file
import bspump.trigger
from lookup import MyIndexLookup

##

L = logging.getLogger(__name__)

##


class MasterApplication(bspump.BSPumpApplication):
	def __init__(self):
		super().__init__(web_listen="0.0.0.0:8080")

		svc = self.get_service("bspump.PumpService")
		
		self.Lookup = MyIndexLookup(self, id='MyLookup', config={'path':'cz.o2tv.db.as.cac.live.epg.results.csv', 'delimiter':';'})

		svc.add_lookup(self.Lookup)


if __name__ == '__main__':
	app = MasterApplication()
	app.run()
