import pathlib
import re
import subprocess

from setuptools import find_packages, setup
from setuptools.command.build_py import build_py

here = pathlib.Path(__file__).parent
if (here / '.git').exists():
	module_dir = (here / 'bspump')

	version = subprocess.check_output(
		['git', 'describe', '--abbrev=7', '--tags', '--dirty=+dirty', '--always'], cwd=module_dir)
	version = version.decode('utf-8').strip()
	if version[:1] == 'v':
		version = version[1:]

	build = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=module_dir)
	build = build.decode('utf-8').strip()

else:
	txt = (here / 'bspump' / '__version__.py').read_text('utf-8')
	version = re.findall(r"^__version__ = '([^']+)'\r?$", txt, re.M)[0]
	build = re.findall(r"^__build__ = '([^']+)'\r?$", txt, re.M)[0]


class custom_build_py(build_py):

	def run(self):
		super().run()

		version_file_name = pathlib.Path(self.build_lib, 'bspump/__version__.py')
		with open(version_file_name, 'w') as f:
			f.write("__version__ = '{}'\n".format(version))
			f.write("__build__ = '{}'\n".format(build))
			f.write("\n")
			f.write("__all__ = ['__version__', '__build__']")
			f.write("\n")


setup(
	name='bspump',
	version=version,
	description='BSPump is a real-time stream processor for Python 3.5+',
	long_description=open('README.rst').read(),
	url='https://github.com/TeskaLabs/bspump',
	author='TeskaLabs Ltd',
	author_email='info@teskalabs.com',
	license='BSD License',
	platforms='any',
	classifiers=[
		'Development Status :: 5 - Alpha',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: 3.7',
	],
	keywords='asyncio asab',
	packages=find_packages(),
	package_data={
		'bspump.web': [
			'static/*.html',
			'static/*.js'
		]
	},
	project_urls={
		'Source': 'https://github.com/TeskaLabs/bspump'
	},
	install_requires=[
		'aiohttp>=3.5.4',
		'aiokafka>=0.5.1',
		'aiomysql>=0.0.20',
		'aiosmtplib>=1.0.5',
		'asab>=18.12',
		'fastavro>=0.21.24',
		'mongoquery>=1.3.5',
		'mysql-replication>=0.19',
		'numpy>=1.16.3',
		'pandas>=0.24.2',
		'pika>=1.0.1',
		'pyarrow>=0.13.0',
		'requests>=2.21.0',
	],
	scripts=[
		'utils/bselastic'
	],
	cmdclass={
		'build_py': custom_build_py,
	},
)
