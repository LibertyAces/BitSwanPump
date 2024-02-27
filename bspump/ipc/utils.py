import re
import socket

def parse_address(address):
	"""
	The function `parse_address` takes an address string and returns a tuple containing the appropriate
	socket family and address.
	
	:param address: The `address` parameter is a string representing either a UNIX socket address or an
	IP address with a port number

	Examples:
	* "0.0.0.0 8080"
	* "0.0.0.0:8080" (this format is nice to YAML)
	* ":: 8080"
	* ":::8080"  (this format is nice to YAML)
	* "*:8080"
	* "8080"
	* "/tmp/unix.sock"

	:return: The function `parse_address` returns a tuple containing the address family (either
	`socket.AF_UNIX` or `socket.AF_INET`) and the address itself (either a string for UNIX addresses or
	a tuple of `(address, port)` for IP addresses).
	"""
	address = address.strip()

	# UNIX address starts with `/` or '.'
	if address.startswith('/') or address.startswith('.'):
		return (socket.AF_UNIX, address)

	portrm = re.search(r"^(.*)[\s:](\d+)$", address)
	if portrm is None:
		portrm = re.search(r"^(\d+)$", address)
		if portrm is None:
			# It is a UNIX address
			return (socket.AF_UNIX, address)
		else:
			# An user issued just a port
			return (socket.AF_INET, (None, int(portrm.group(1))))

	if portrm.group(1) == '*':
		return (socket.AF_INET, (None, int(portrm.group(2))))
	else:
		return (socket.AF_INET, (portrm.group(1), int(portrm.group(2))))
