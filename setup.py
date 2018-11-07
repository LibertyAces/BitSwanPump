from setuptools import setup
from setuptools import find_packages

setup(
	name='bspump',
	version='18.05-alpha1',
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
		'requests',
	],
	scripts=[
		'utils/bselastic'
	]
)

