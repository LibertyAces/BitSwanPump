import glob
import os.path

def _glob_scan(path):
	if path is None: return None
	if path == "": return None

	filelist = glob.glob(path)
	filelist.sort()
	while len(filelist) > 0:
		fname = filelist.pop()
		if fname.endswith('-locked'): continue
		if fname.endswith('-processed'): continue
		if not os.path.isfile(fname): continue

		#TODO: Validate thru lsof ...

		return fname

	return None
