import pathlib
import re

from setuptools import find_packages
from setuptools import setup

here = pathlib.Path(__file__).parent
txt = (here / 'asab' / '__init__.py').read_text('utf-8')
try:
	version = re.findall(r"^__version__ = '([^']+)'\r?$", txt, re.M)[0]
except IndexError:
	raise RuntimeError('Unable to determine version.')


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
		'requests', # for bselastic tool
	],
	scripts=[
		'utils/bselastic'
	],
)
