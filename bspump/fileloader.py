import json


def load_json_file(fname):

	if fname.endswith(".gz"):
		import gzip
		f = gzip.open(fname, 'rb')

	elif fname.endswith(".bz2"):
		import bz2
		f = bz2.open(fname, 'rb')

	elif fname.endswith(".xz") or fname.endswith(".lzma"):
		import lzma
		f = lzma.open(fname, 'rb')

	else:
		f = open(fname, 'rb')

	jdata = json.loads(f.read().decode('utf-8'))
	f.close()
	return jdata
