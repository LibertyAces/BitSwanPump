import os.path

from setuptools import setup
from setuptools import find_packages
from setuptools.command.build_py import build_py

import bspump


class custom_build_py(build_py):

	def run(self):
		super().run()

		# Install a proper __version__py, if needed.
		version_file_name = os.path.join(self.build_lib, 'bspump/__version__.py')
		with open(version_file_name, 'w') as f:
			f.write("__version__ = '''{}'''\n".format(bspump.__version__))
			f.write("__build__ = '''{}'''\n".format(bspump.__build__))
			f.write("\n")


setup(
	name='bspump',
	version=bspump.__version__,
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
		'requests', # for bselastic tool
	],
	scripts=[
		'utils/bselastic'
	],
	cmdclass={
		'build_py': custom_build_py,
	},
)
