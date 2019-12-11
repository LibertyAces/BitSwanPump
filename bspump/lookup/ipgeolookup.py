import logging
import csv
import ipaddress

from bspump.abc.lookup import DictionaryLookup

###

L = logging.getLogger(__name__)

###


class IPGeoLookup(DictionaryLookup):
	'''
This lookup performs transformation of IP address into a geographical location.
It uses a file database from ip2location.com.
Lookup provides locations both in ipv4 and ipv6 formats.
NOTICE: IPv6 database includes also all IPv4 locations, see "ipv4mapped" config. option.

Free versions: IP2LOCATION-LITE-DB5.IPV6.CSV and IP2LOCATION-LITE-DB5.IPV4.CSV
For better precision visit https://lite.ip2location.com to buy a commercial version of database.

Usage: specify in configuration the path to the database in csv format.
'''


	ConfigDefaults = {
		'path': '',
		'ipv4mapped': 'no',  # IPv4-mapped IPv6 address (enables to use IPv6 lookups for IPv4 addresses)
	}

	def __init__(self, app, id=None, config=None):
		super().__init__(app, id=id, config=config)
		self.TreeRoot = None
		self.Locations = {}
		if self.Config['ipv4mapped'].lower() == 'yes':
			self.IP4Mapped = True
		else:
			self.IP4Mapped = False


	async def load(self):
		fname = self.Config['path']
		if fname == '':
			return

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
					d = {'lat': None, 'lon': None}
				else:
					d = {'lat': lat, 'lon': lon}

				if line[2] != '-':
					d['country'] = line[2]
				if line[4] != '-':
					d['region'] = line[4]
				if line[5] != '-':
					d['city'] = line[5]

				self.Locations[ip_int_address_start] = d
				self.Locations[ip_int_address_end] = d

		self.TreeRoot = self.sorted_array_to_bst(array)
		del array
		L.debug("IPGeoLookup {} was successfully created".format(self.Id))
		return True

	def set(self, tree):
		self.TreeRoot = tree

	# REST

	def rest_get(self):
		rest = super().rest_get()
		rest["TreeRoot"] = self.TreeRoot
		rest["Locations"] = self.Locations
		rest["IP4Mapped"] = self.IP4Mapped
		return rest

	def sorted_array_to_bst(self, arr):
		if not arr:
			return None

		mid = int(len(arr) / 2)
		root = Node(arr[mid])
		root.left = self.sorted_array_to_bst(arr[:mid])
		root.right = self.sorted_array_to_bst(arr[mid + 1:])
		return root


	def search(self, value):
		root = self.TreeRoot
		while True:
			if root.data == value:
				return root.data

			if root.data > value:

				left = root.left
				if left is None:
					return root.data
				else:
					root = left
			if root.data < value:
				right = root.right
				if right is None:
					return root.data
				else:
					root = right


	def lookup_location_ipv4(self, address):
		if self.TreeRoot is None:
			# L.warning("Cannot enrich the location")
			return None

		address_int = int(ipaddress.IPv4Address(address))

		if self.IP4Mapped:
			# https://blog.ip2location.com/knowledge-base/ipv4-mapped-ipv6-address/
			# 191.239.213.197 -> ::ffff:191.239.213.197
			address_int += 281470681743360

		value = self.search(address_int)
		return self.Locations.get(value)


	def lookup_location_ipv6(self, address):
		if self.TreeRoot is None:
			# L.warning("Cannot enrich the location")
			return None

		address_int = int(ipaddress.IPv6Address(address))

		value = self.search(address_int)
		return self.Locations.get(value)

	def lookup_location(self, address):
		if '.' in address:
			return self.lookup_location_ipv4(address)
		elif ':' in address:
			return self.lookup_location_ipv6(address)
		else:
			raise ValueError("Invalid IPv4/IPv6 format")


class Node:
	def __init__(self, d):
		self.data = d
		self.left = None
		self.right = None
