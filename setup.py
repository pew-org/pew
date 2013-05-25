#! /usr/bin/env python

from setuptools import setup
import invewrapper

try:
    with open('README.md') as readme:
        long_desc = readme.read()
except IOError:
    long_desc = ''

setup(
	name='invewrapper',
	version='0.1.3',
	description='tools to manage multiple virtualenv written in pure python',
	long_description=long_desc,
	keywords='virtualenvwrapper',
	author='Dario Bertini',
	author_email='berdario+pypi@gmail.com',
	url='https://github.com/berdario/invewrapper',
	license='MIT License',
	packages=['invewrapper'],
	install_requires=['virtualenv', 'virtualenv-clone'],
	package_data={'': ['inve']},  # XXX
	entry_points={
		'console_scripts':
			["{0} = invewrapper.invewrapper:{0}_cmd".format(cmd[:-4])
			for cmd in dir(invewrapper.invewrapper) if cmd.endswith("_cmd")]},
	classifiers=[
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 3',
		'Intended Audience :: Developers',
		'Environment :: Console']
)
