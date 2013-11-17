#! /usr/bin/env python

from setuptools import setup
import invewrapper

long_desc = '''Python Env Wrapper (also called Invewrapper) is a set of tools to manage multiple virtual environments. The tools can create, delete and copy your environments, using a single command to switch to them wherever you are, while keeping them in a single (configurable) location.

Invewrapper makes it easier to work on more than one project at a time without introducing conflicts in their dependencies. It is written in pure python and leverages inve: the idea/alternative implementation of a better activate script.

The advantage is that invewrapper doesn't hook into a shell, but is only a set of commands that is thus completely shell-agnostic:

It works on bash, zsh, fish, powershell, etc.

For the documentation, you might want to read here:
https://github.com/berdario/invewrapper#usage'''

setup(
	name='pew',
	version='0.1.7',
	description='tools to manage multiple virtualenvs written in pure python, '
		'a virtualenvwrapper rewrite',
	long_description=long_desc,
	author='Dario Bertini',
	author_email='berdario+pypi@gmail.com',
	url='https://github.com/berdario/invewrapper',
	license='MIT License',
	packages=['invewrapper'],
	install_requires=['virtualenv', 'virtualenv-clone'],
	dependency_links=
		['https://github.com/berdario/virtualenv-clone/tarball/c302ca84e524cb22f88c834cccb23dd410cced97#egg=virtualenv-clone'],
	package_data={'': ['inve']},  # XXX
	entry_points={
		'console_scripts':
			["pew-{0} = invewrapper.invewrapper:{0}_cmd".format(cmd[:-4])
			for cmd in dir(invewrapper.invewrapper) if cmd.endswith("_cmd")] +
			['pew = invewrapper.invewrapper:pew']},
	classifiers=[
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 3',
		'Intended Audience :: Developers',
		'Environment :: Console']
)
