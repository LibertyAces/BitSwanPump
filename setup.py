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
		['git', 'describe', '--abbrev=7', '--tags', '--dirty=+dirty', '--always'], cwd=module_dir)
	version = version.decode('utf-8').strip()
	if version[:1] == 'v':
		version = version[1:]

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
	description='BSPump is a real-time stream processor for Python 3.6+',
	long_description=open('README.rst').read(),
	url='https://github.com/LibertyAces/BitSwanPump',
	author='TeskaLabs Ltd',
	author_email='info@teskalabs.com',
	license='BSD License',
	platforms='any',
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: 3.7',
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
		'aiokafka>=0.6.0',
		'aiozk>=0.25.0',
		'aiosmtplib>=1.1.3',
		'fastavro>=0.23.5',
		'google-api-python-client>=1.7.10',
		'numpy>=1.19.0',
		'pika>=1.1.0',
		'pymysql>=0.9.2,<=0.9.2',  # aiomysql 0.0.20 requires PyMySQL<=0.9.2
		'aiomysql>=0.0.20',
		'mysql-replication>=0.21',
		'pytz>=2020.1',
		'netaddr>=0.7.20',
		'pyyaml>=5.3.1',
		'pymongo>=3.10.1',
		'motor>=2.1.0',
		'mongoquery>=1.3.6',
		'pywinrm>=0.4.1',
		'pyarrow>=0.13.0',  # `pip install pyarrow` fails on Apline Linux, official bspump alpine images do not include pyarrow
		'pandas>=0.24.2',  # pandas is required in bstelco
		'xxhash>=1.4.4',
	],
	scripts=[
		'utils/bselastic',
		'utils/bskibana',
	],
	cmdclass={
		'build_py': custom_build_py,
	},
)