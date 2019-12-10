import fnmatch
import glob
import logging
import os.path
import platform
import subprocess

#

L = logging.getLogger(__file__)

#


if platform.system() == "Windows":
	def _is_file_open(fname):
		# TODO: Provide implementation of _is_file_open() for Windows
		return False
else:
	def _is_file_open(fname):
		result = subprocess.run(['lsof', fname], stdout=subprocess.PIPE)
		return len(result.stdout) != 0


def _glob_scan(path, gauge, loop, exclude='', include=''):
	if path is None:
		return None
	if path == "":
		return None

	filelist = glob.glob(path, recursive=True)
	filelist.sort()

	filelist_to_check = []
	filelist_to_check.extend(filelist)

	# also check the whole folder meanwhile
	loop.call_soon(_file_check, filelist_to_check, gauge)

	while len(filelist) > 0:
		fname = filelist.pop(0)
		if any([
			fname.endswith('-locked'),
			fname.endswith('-failed'),
			fname.endswith('-processed'),
			not os.path.isfile(fname),
		]):
			continue

		if exclude != "":
			if fnmatch.fnmatch(fname, exclude):
				continue
		if include != "":
			if not fnmatch.fnmatch(fname, include):
				continue

		if _is_file_open(fname):
			continue

		return fname

	return None


def _file_check(filelist, gauge):

	file_count = {
		"processed": 0,
		"unprocessed": 0,
		"failed": 0,
		"locked": 0,
		"all_files": 0
	}

	file_count["all_files"] += len(filelist)
	for file in filelist:
		if file.endswith('-locked'):
			file_count["locked"] += 1
			continue
		if file.endswith('-failed'):
			file_count["failed"] += 1
			continue
		if file.endswith('-processed'):
			file_count["processed"] += 1
			continue

		file_count["unprocessed"] += 1


	gauge.set("processed", file_count["processed"])
	gauge.set("failed", file_count["failed"])
	gauge.set("locked", file_count["locked"])
	gauge.set("unprocessed", file_count["unprocessed"])
	gauge.set("all_files", file_count["all_files"])
