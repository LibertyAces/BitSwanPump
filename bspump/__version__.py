# THIS-FILE-WILL-BE-REPLACED  !!! DO NOT CHANGE OR MODIFY THIS LINE!!
import os
import subprocess

# During `setup.py build_py`, this file is overwritten
# __version__ = '[git describe --abbrev=7 --tags --dirty=+dirty --always]
# __build__ = '[git rev-parse HEAD]'

# PEP 440 -- Version Identification and Dependency Specification
# https://www.python.org/dev/peps/pep-0440/

def _buid_version_info():
	module_dir = os.path.dirname(__file__)
	try:
		version = subprocess.check_output(['git', 'describe', '--abbrev=7', '--tags', '--dirty=+dirty', '--always'], cwd=module_dir)
		version = version.decode('utf-8').strip()
		if version[:1] == 'v':
			version = version[1:]
	except Exception:
		version = "???"

	try:
		build = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=module_dir)
		build = build.decode('utf-8').strip()
	except Exception:
		build = "???"

	return version, build

__all__ = ["__version__", "__build__"]
__version__, __build__ = _buid_version_info()
