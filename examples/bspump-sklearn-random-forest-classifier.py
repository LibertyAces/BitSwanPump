import logging
import time

import bspump
import bspump.common
import bspump.file
import bspump.trigger
import bspump.analyzer
import bspump.model

import re
import requests
import numpy as np
import pandas as pd
import pickle
import datetime
import json

import socket
import urllib.request
import pythonwhois as pw

##


L = logging.getLogger(__name__)


##


class MyApplication(bspump.BSPumpApplication):
	def __init__(self):
		super().__init__()
		svc = self.get_service("bspump.PumpService")
		svc.add_pipeline(MyPipeline(self, "MyPipeline"))



class MyPipeline(bspump.Pipeline):
	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)

		model = MyRFModel(self, id='MyModel', config={'path_model': 'examples/classification/MBDomainsModel.pkl', 
												'path_parameters': 'examples/classification/MBLabelEncoder.pkl'})
		self.build(
			bspump.file.FileLineSource(app, self, config={'path': 'examples/classification/named.log', 'post':'move'}
				).on(bspump.trigger.OpportunisticTrigger(app)),
			NamedParser(app, self),
			MyMBDomainClassifier(app, self, model),
			bspump.common.PPrintSink(app, self)
		)


class NamedParser(bspump.Processor):
	ConfigDefaults = {
		'encoding': 'utf-8',
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		self._encoding = self.Config['encoding']

	def process(self, context, event):
		event = event.decode(self._encoding).replace("\n", "").replace("\r", "").replace("  ", " ")

		pattern = re.compile(r"^(\S+.\S+)\squeries:\s(\w+):\s\w+\s(\S+)\s(\S+)\s\S+\squery:\s(\S+)\s\w+\s(\w+).+$")

		event_split = pattern.match(event)

		parsed_event = {}

		parsed_event['timestamp'] = int((datetime.datetime.strptime(event_split[1], '%d-%B-%Y %H:%M:%S.%f')).timestamp())
		parsed_event['severity'] = event_split[2]
		parsed_event['object_id'] = event_split[3]
		parsed_event['sourceAddress'] = event_split[4].split("#")[0]
		parsed_event['sourcePort'] = event_split[4].split("#")[1]
		parsed_event['dnsQuery'] = event_split[5]
		parsed_event['dnsRecordType'] = event_split[6]
		parsed_event['raw'] = event
		return parsed_event


class MyMBDomainClassifier(bspump.Processor):
	def __init__(self, app, pipeline, model, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Model = model


	def process(self, context, event):
		sample = self.Model.transform(event)
		if sample is None:
			return event
		
		predicted = self.Model.predict(sample)
		event.update(predicted)
		return event


class MyRFModel(bspump.model.Model):
	def __init__(self, app, id=None, config=None):
		super().__init__(app, id=id, config=config)
		self.load_model_from_file()
		self.load_parameters_from_file()


	def load_model_from_file(self):
		self.TrainedModel = pickle.load(open(self.PathModel, 'rb'))


	def load_parameters_from_file(self):
		self.Parameters = {}
		l_e = pickle.load(open(self.PathParameters, 'rb'))
		self.Parameters['serverPreproc'] = l_e[0]
		self.Parameters['charsetPreproc'] = l_e[1]
		self.Parameters['countryPreproc'] = l_e[2]


	def transform(self, sample):
		url = sample['dnsQuery']
		details = {}
		details['URL_LENGTH'] = len(url)
		details['NUMBER_SPECIAL_CHARACTERS'] = (len(url) - len(re.findall('[\w]', url)))
		try:
			response = urllib.request.urlopen('http://' + url + '/')
			details['SERVER'] = 'nginx'
			details['CHARSET'] = response.headers.get_content_charset()

			details['CONTENT_LENGTH'] = response.getheader('Content-Length') or 0.0

			ip = socket.gethostbyname(url)
			details['COUNTRY'] = 'US'

			details['WHOIS_REGDATE'] = 0.0
			details['WHOIS_UPDATED_DATE'] = 0.0

		except Exception as e:
			return None

		df = pd.DataFrame(details, index=[0])
		try:
			df['SERVER'] = df.SERVER.str.upper()
			df['SERVER'] = self.Parameters['serverPreproc'].transform(df.SERVER)

			df['CHARSET'] = df.CHARSET.str.upper()
			df['CHARSET'] = self.Parameters['charsetPreproc'].transform(df.CHARSET)

			df['COUNTRY'] = df.COUNTRY.str.upper()
			df['COUNTRY'] = self.Parameters['countryPreproc'].transform(df.COUNTRY)
		except Exception as e:
			return None


		df['WHOIS_REGDATE'] = pd.to_datetime(df.WHOIS_REGDATE, errors='coerce', utc=True)
		df['WHOIS_UPDATED_DATE'] = pd.to_datetime(df.WHOIS_UPDATED_DATE, errors='coerce', utc=True)
		df['WHOIS_UPDATED_DATE'] = (df['WHOIS_UPDATED_DATE'] - pd.to_datetime('1/1/1970', utc=True)) / np.timedelta64(1,'D')
		df['WHOIS_REGDATE'] = (df['WHOIS_REGDATE'] - pd.to_datetime('1/1/1970', utc=True)) / np.timedelta64(1,'D')

		df['WHOIS_REGDATE'].fillna(0.0, inplace=True)
		df['WHOIS_UPDATED_DATE'].fillna(0.0, inplace=True)

		sample = df.iloc[0].values
		sample = sample.reshape(-1, 1).transpose()
		return sample


	def predict(self, data):
		result = {}
		prediction = int(self.TrainedModel.predict(data))
		result['Result'] = 'malign' if prediction else 'benign'
		return result
	

if __name__ == '__main__':
	app = MyApplication()
	app.run()

