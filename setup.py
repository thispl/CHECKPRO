# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in checkpro/__init__.py
from checkpro import __version__ as version

setup(
	name='checkpro',
	version=version,
	description='check list',
	author='saru',
	author_email='sarumathy.d@groupteampro.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
