import time
import logging
import numpy as np

import asab

from .analyzer import Analyzer

###

L = logging.getLogger(__name__)

###


class SessionAnalyzer(Analyzer):
	
	'''
	sa_configuration = {'label0':{'column_formats':['c1', 'c2'], 'column_names':['col1', 'col12']}}
	if you need to create just one session matrix, name the label somehow and specify column_fomats/names. 
	you can access it by self.SessionAggregation without the label 
	'''


	def __init__(self, app, pipeline, sa_configuration, sessions=None, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		if sessions is None:
			self._create_session_aggregations(app, pipeline, sa_configuration)	
		else:
			if sessions == {}:
				raise RuntimeError("sessions cannot be an empty dictionary")
			
			self.SessionAggregations = sessions
		
		self.LabelDefault = list(self.SessionAggregations.values())[0]
		self.SessionAggregation = self.SessionAggregations[self.LabelDefault]
		

	def _create_session_aggregations(self, app, pipeline, sa_configuration):
		self.SessionAggregations = {}
		for label in sa_configuration.keys():
			self.SessionAggregations[label] = SessionAggregation(
				app,
				pipeline,
				column_formats=sa_configuration[label]['column_formats'],
				column_names=sa_configuration[label]['column_names'],
			)


		

	
	
	





	

