import logging
import itertools
import json
import os

import win32evtlog
import win32evtlogutil

import asyncio

from ..abc.source import Source

#

L = logging.getLogger(__name__)

#


class WinEventSource(Source):
	"""
	WinEventSource periodically reads Windows Events from the specified server and event type.
	"""

	ConfigDefaults = {
		"server": "localhost",  # Where the obtain Windows Events from
		"event_type": "System",  # Specify the type of Windows Events to load
		"last_value_storage": "/data/winevent_last_value_storage.json",  # Last value storage

		# The number of events after which the main method enters the idle
		# state to allow other operations to perform their tasks
		"buffer_size": 1024,  # Events to be read at once
		"event_block_size": 1000,
		"event_idle_time": 0.01,  # The time for which the main method enters the idle state (see above)
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)

		# Read configuration options
		self.Server = self.Config["server"]
		self.EventType = self.Config["event_type"]
		self.BufferSize = self.Config["buffer_size"]
		self.WinHandler = win32evtlog.OpenEventLog(self.Server, self.EventType)
		self.WinFlags = win32evtlog.EVENTLOG_FORWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ

		# Load last offset, timestamp etc. from file storage
		self.LastOffset = 0
		self.FirstRun = True
		self.LastTimestamp = None
		self.LastEventID = None
		self.LastRecordNumber = None
		self.LastValueStorage = self.Config["last_value_storage"]
		if os.path.exists(self.LastValueStorage) and not os.path.isdir(self.LastValueStorage):
			with open(self.LastValueStorage, "r") as last_value_file:
				last_value_dict = json.loads(last_value_file.read())
				self.LastOffset = last_value_dict.get("last_offset", 0)
				self.LastTimestamp = last_value_dict.get("last_timestamp")
				self.LastEventID = last_value_dict.get("last_event_id")
				self.LastRecordNumber = last_value_dict.get("last_record_number")

		# Subscribe to tick and exit
		app.PubSub.subscribe("Application.tick/60!", self._on_tick)
		app.PubSub.subscribe("Application.exit!", self._on_tick)

		# For event simulation
		self.EventCounter = 0
		self.EventBlockSize = int(self.Config["event_block_size"])
		self.EventIdleTime = float(self.Config["event_idle_time"])

	async def _on_tick(self, event_name):
		# Save the last value into persistent storage
		if self.LastOffset is not None:
			with open(self.LastValueStorage, "w") as last_value_file:
				last_value_file.write(json.dumps({
					"last_offset": self.LastOffset,
					"last_timestamp": self.LastTimestamp,
					"last_event_id": self.LastEventID,
					"last_record_number": self.LastRecordNumber,
				}))

	async def main(self):
		while True:
			events = win32evtlog.ReadEventLog(self.WinHandler, self.WinFlags, self.LastOffset, self.BufferSize)
			if events:
				for event in events:
					# Skip duplicities using rollover
					# This snippet is needed when the pump is restarted,
					# so only first run is considered
					if self.FirstRun and self.LastTimestamp is not None:
						timestamp = int(event.TimeGenerated.timestamp())
						if timestamp < self.LastTimestamp:
							continue
						elif timestamp == self.LastTimestamp:
							if self.LastEventID == event.EventID and self.LastRecordNumber == event.RecordNumber:
								self.FirstRun = False
							continue
						else:
							self.FirstRun = False
					# Obtain the event in readable format
					parsed_event = self.parse_windows_event(event)
					if len(parsed_event["data"]) == 0:
						continue
					# Process and store the event as last value
					await self.process(parsed_event, context={})
					self.LastOffset += 1
					self.LastTimestamp = parsed_event["timeGenerated"]
					self.LastEventID = parsed_event["eventID"]
					self.LastRecordNumber = parsed_event["recordNumber"]
					# Simulate event
					await self._simulate_event()

	def parse_windows_event(self, event):
		"""
		http://timgolden.me.uk/pywin32-docs/PyEventLogRecord.html
		:param event: Windows Event
		:return:
		"""

		return {
			"reserved": event.Reserved,
			"recordNumber": event.RecordNumber,
			"timeGenerated": int(event.TimeGenerated.timestamp()),
			"timeWritten": int(event.TimeWritten.timestamp()),
			"eventID": event.EventID,
			"eventType": event.EventType,
			"eventCategory": event.EventCategory,
			"reservedFlags": event.ReservedFlags,
			"closingRecordNumber": event.ClosingRecordNumber,
			"sourceName": event.SourceName,
			"stringInserts": event.StringInserts,
			"sid": str(event.Sid),
			"data": win32evtlogutil.SafeFormatMessage(event, self.EventType),
			"computerName": event.ComputerName,
		}

	async def _simulate_event(self):
		'''
		The _simulate_event method should be called in main method after a message has been processed.

		It ensures that all other asynchronous events receive enough time to perform their tasks.
		Otherwise, the application loop is blocked by a file reader and no other activity makes a progress.
		'''

		self.EventCounter += 1
		if self.EventCounter % self.EventBlockSize == 0:
			await asyncio.sleep(self.EventIdleTime)
			await self.Pipeline.ready()
			self.EventCounter = 0
