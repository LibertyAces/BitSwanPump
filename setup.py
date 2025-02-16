import pathlib
import re
import subprocess

from setuptools import find_packages, setup
from setuptools.command.build_py import build_py

here = pathlib.Path(__file__).parent
if (here / '.git').exists():
	# This branch is happening during build from git version
	module_dir = (here / 'bspump')

	version = subprocess.check_output(
		['git', 'describe', '--abbrev=7', '--tags', '--dirty=-dirty', '--always'], cwd=module_dir)
	version = version.decode('utf-8').strip()
	if version[:1] == 'v':
		version = version[1:]

	# PEP 440 requires that the PUBLIC version field does not contain hyphens or pluses.
	# https://peps.python.org/pep-0440/#semantic-versioning
	# The commit number, hash and the "dirty" string must be in the LOCAL version field,
	# separated from the public version by "+".
	# For example, "v22.06-rc6-291-g3021077-dirty" becomes "v22.06-rc6+291-g3021077-dirty".
	match = re.match(r"^(.+)-([0-9]+-g[0-9a-f]{7}(?:-dirty)?)$", version)
	if match is not None:
		version = "{}+{}".format(match[1], match[2])

	build = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=module_dir)
	build = build.decode('utf-8').strip()

else:
	# This is executed from packaged & distributed version
	txt = (here / 'bspump' / '__version__.py').read_text('utf-8')
	version = re.findall(r"^__version__ = '([^']+)'\r?$", txt, re.M)[0]
	build = re.findall(r"^__build__ = '([^']+)'\r?$", txt, re.M)[0]


class custom_build_py(build_py):

	def run(self):
		super().run()

		# This replace content of `__version__.py` in build folder
		version_file_name = pathlib.Path(self.build_lib, 'bspump/__version__.py')
		with open(version_file_name, 'w') as f:
			f.write("__version__ = '{}'\n".format(version))
			f.write("__build__ = '{}'\n".format(build))
			f.write("\n")


setup(
	name='bspump',
	version=version,
	description='BSPump is a real-time stream processor for Python 3',
	long_description=open('README.rst').read(),
	url='https://github.com/LibertyAces/BitSwanPump',
	author='TeskaLabs Ltd',
	author_email='info@teskalabs.com',
	license='BSD License',
	platforms='any',
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Programming Language :: Python :: 3.8',
		'Programming Language :: Python :: 3.9',
		'Programming Language :: Python :: 3.10',
		'Programming Language :: Python :: 3.11',
	],
	packages=find_packages(),
	package_data={
		'bspump.web': [
			'static/*.html',
			'static/*.js'
		]
	},
	project_urls={
		'Source': 'https://github.com/LibertyAces/BitSwanPump'
	},
	install_requires=[
		'asab>=20.7.28',
		'aiohttp>=3.6.2',
		'requests>=2.24.0',		
		'pytz>=2020.1',
		'netaddr>=0.7.20',
		'pyyaml>=5.4',
		'motor>=2.1.0',
		'mongoquery>=1.3.6',
		'pybind11>=2.6.1',
		'cysimdjson>=21.11',
		'xxhash>=1.4.4',
		'orjson',
	],
	extras_require={
		'ldap': 'python-ldap',
		'asn': 'pyasn1==0.4.8',  # version 0.5.0 is not compatible with pysnmp
		'kafka': 'confluent-kafka>=1.8.2',
		'zookeeper': 'aiozk>=0.25.0',
		'smtp': 'aiosmtplib>=1.1.3',
		'avro': 'fastavro>=0.23.5',
		'google': 'google-api-python-client>=1.7.10',
		'numpy': 'numpy>=1.19.0',
		'amqp': 'pika>=1.1.0',
		'mysql': [
			'pymysql>=0.9.2,<=0.9.2',  # aiomysql 0.0.20 requires PyMySQL<=0.9.2
			'aiomysql>=0.0.20',
			'mysql-replication>=0.21'
		],
		'mongo': [
			'pymongo>=3.10.1',
			'motor>=2.1.0',
			'mongoquery>=1.3.6',
		],
		'winrm': 'pywinrm>=0.4.1',
		'pandas': 'pandas>=0.24.2',
	},
	scripts=[
		'utils/bselastic',
		'utils/bskibana',
	],
	cmdclass={
		'build_py': custom_build_py,
	},
)
