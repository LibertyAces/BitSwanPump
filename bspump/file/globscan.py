import glob
import os.path
import subprocess
import platform
import fnmatch


if platform.system() == "Windows":
	def _is_file_open(fname):
		#TODO: Provide implementation of _is_file_open() for Windows
		return False
else:
	def _is_file_open(fname):
		return False
		result = subprocess.run(['lsof', fname], stdout=subprocess.PIPE)
		return len(result.stdout) != 0


def _glob_scan(path, exclude='', include=''):
	if path is None: return None
	if path == "": return None

	filelist = glob.glob(path)
	filelist.sort()
	while len(filelist) > 0:
		fname = filelist.pop()
		if fname.endswith('-locked'): continue
		if fname.endswith('-failed'): continue
		if fname.endswith('-processed'): continue
		if not os.path.isfile(fname): continue

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
