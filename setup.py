#! /usr/bin/env python

from setuptools import setup
import invewrapper

setup(
	name='invewrapper',
	version='0.1',
	description='tools to manage multiple virtualenv written in pure python',
	keywords=[],
	author='Dario Bertini',
	author_email='berdario+pypi@gmail.com',
	url='https://github.com/berdario/invewrapper',
	license='MIT License',
	py_modules=['invewrapper'],
	install_requires=['virtualenv'],
	data_files=[('', ['inve'])],  # XXX
	entry_points={
		'console_scripts':
			["{0} = invewrapper:{0}_cmd".format(cmd[:-4])
			for cmd in dir(invewrapper) if cmd.endswith("_cmd")]}
)
