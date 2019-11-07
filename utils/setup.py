import pathlib
import re
import subprocess

from setuptools import find_packages, setup
from setuptools.command.build_py import build_py

here = pathlib.Path(__file__).parent.parent
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
	name='bspump-utils',
	version=version,
	description='BSPump utils for ElasticSearch and Kibana. Tiny subset of BSPump',
	long_description=open('README.rst').read(),
	url='https://github.com/LibertyAces/BitSwanPump',
	author='Liberty Aces Ltd',
	author_email='info@libertyaces.com',
	license='BSD-3-Clause',
	platforms='any',
	classifiers=[
		'Development Status :: 3 - Alpha',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: 3.7',
	],
	keywords='asyncio asab bspump',
	packages=find_packages(here / "utils"),
	project_urls={
		'Source': 'https://github.com/LibertyAces/BitSwanPump'
	},
	install_requires=[
		'Jinja2>=2.10.1,<3.0',
		'requests>=2.21.0,<3.0',
	],
	scripts=[
		'bselastic',
		'bskibana',
	],
	cmdclass={
		'build_py': custom_build_py,
	},
)
