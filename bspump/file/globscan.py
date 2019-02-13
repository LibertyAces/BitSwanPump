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
		result = subprocess.run(['lsof', fname], stdout=subprocess.PIPE)
		return len(result.stdout) != 0


def _glob_scan(path, exclude='', include=''):
	if path is None: return None
	if path == "": return None

	filelist = glob.glob(path, recursive=True)
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


def _file_check(path, file_count):
	

	if path is None: return
	if path == "": return

	filelist = glob.glob(path, recursive=True)
	file_count["all_files"] += len(filelist)

	for file in filelist:
		if file.endswith('-locked'): 
			file_count["locked"] += 1
		if fname.endswith('-failed'):
			file_count["failed"] += 1
		if fname.endswith('-processed'):
			file_count["processed"] += 1
		if not os.path.isfile(fname): 
			file_count["all_files"] -= 1
			continue
		
		file_count["unprocessed"] += 1

