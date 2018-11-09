import logging
import csv
import ipaddress

from bspump.abc.lookup import DictionaryLookup

###

L = logging.getLogger(__name__)

###

'''This lookup contains locations with precision to city.
	For better precision visit https://lite.ip2location.com 
	to buy a better version of database.
	Usage: specify in configuration the path to the database in csv format.
	Lookup provides locations both in ipv4 and ipv6 formats'''

class IPGeoLookup(DictionaryLookup):


	ConfigDefaults = {
		'path': '',
	}

	def __init__(self, app, lookup_id, config=None):
		super().__init__(app, lookup_id=lookup_id, config=config)
		self.TreeRoot = None
		self.Locations = {}


	async def load(self):
		fname = self.Config['path']
		with open(fname, 'r') as f:
			array = []
			
			for line in csv.reader(f, delimiter=","):
				ip_int_address_start = int(line[0])
				ip_int_address_end = int(line[1])
				array.append(ip_int_address_start)
				array.append(ip_int_address_end)
				lat = float(line[6])
				lon = float(line[7])

				if (lat == 0.0) or (lon == 0.0):
					d = {'lat' : None, 'lon' : None}
				else:
					d = {'lat' : lat, 'lon' : lon}

				self.Locations[ip_int_address_start] = d
				self.Locations[ip_int_address_end] = d

		self.TreeRoot = self.sorted_array_to_bst(array)
		return True

	def set(self, tree):
		self.TreeRoot = tree


	def sorted_array_to_bst(self, arr): 
		if not arr: 
			return None

		mid = int(len(arr) / 2)
		root = Node(arr[mid]) 
		root.left = self.sorted_array_to_bst(arr[:mid]) 
		root.right = self.sorted_array_to_bst(arr[mid+1:]) 
		return root 


	def search(self, value):
		root = self.TreeRoot
		while True:
			if root.data == value:
				return root.data
			
			if root.data > value:

				l = root.left
				if l is None:
					return root.data
				else:
					root = l
			if root.data < value:
				r = root.right
				if r is None:
					return root.data
				else:
					root = r


	def lookup_location_ipv4(self, address):
		
		#check if correct address
		if len(address.split(".")) != 4:
			raise ValueError("This IP-address is not in ipv4 format")

		address_int = int(ipaddress.IPv4Address(address))
		value = self.search(address_int)
		location = self.Locations.get(value)
		return location


	def lookup_location_ipv6(self, address):
		
		#check if correct address
		if len(address.split(":")) not in [7, 8]:
			raise ValueError("This IP-address is not in ipv6 format")

		address_int = int(ipaddress.IPv6Address(address))
		value = self.search(address_int)
		location = self.Locations.get(value)
		return location
	

class Node: 
	def __init__(self, d): 
		self.data = d 
		self.left = None
		self.right = None
