#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from shutil import rmtree
from setuptools import setup, Command

long_desc = '''Python Env Wrapper is a set of commands to manage multiple [virtual environments](http://pypi.python.org/pypi/virtualenv). Pew can create, delete and copy your environments, using a single command to switch to them wherever you are, while keeping them in a single (configurable) location.

Virtualenvs makes it easier to work on more than one project at a time without introducing conflicts in their dependencies.

Pew is completely shell-agnostic and thus works on bash, zsh, fish, powershell, etc.

For the documentation, you might want to read here:
https://github.com/berdario/pew#usage'''

here = os.path.abspath(os.path.dirname(__file__))
VERSION = '1.2.0'

AUTHOR = os.environ.get('DEBFULLNAME', 'Dario Bertini')
EMAIL = os.environ.get('DEBEMAIL', 'berdario+pypi@gmail.com')

class DebCommand(Command):
    """Support for setup.py deb"""

    description = 'Build and publish the .deb package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'deb_dist'))
        except FileNotFoundError:
            pass
        self.status(u'Creating debian mainfest…')
        os.system('{0} setup.py --command-packages=stdeb.command sdist_dsc -z artful --package3=pew --depends3=python3-virtualenv-clone'.format(sys.executable))

        self.status(u'Building .deb…')
        os.chdir('deb_dist/pew-{0}'.format(VERSION))
        os.system('dpkg-buildpackage -rfakeroot -uc -us')

setup(
    name='pew',
    version=VERSION,
    description='tool to manage multiple virtualenvs written in pure python',
    long_description=long_desc,
    author=AUTHOR,
    author_email=EMAIL,
    url='https://github.com/berdario/pew',
    license='MIT License',
    packages=['pew'],
    install_requires=[
        'virtualenv>=1.11', 'virtualenv-clone>=0.2.5', 'setuptools>=17.1'
    ],
    extras_require={
        ':python_version=="2.6"': [
            'argparse', 'pathlib', 'backports.shutil_get_terminal_size', 'shutilwhich'
        ],
        ':python_version=="2.7"': [
            'pathlib', 'backports.shutil_get_terminal_size', 'shutilwhich'
        ],
        ':python_version=="3.2"': [
            'pathlib', 'backports.shutil_get_terminal_size', 'shutilwhich'
        ],
        ':python_version=="3.3"': [
            'pathlib'
        ],
        ':sys_platform=="win32"': [
            'shellingham'
        ],
        'pythonz': [
            'pythonz-bd>=1.10.2'
        ]
    },
    include_package_data=True,
    zip_safe=False,
    cmdclass={
        'deb': DebCommand
    },
    entry_points={
        'console_scripts': ['pew = pew.pew:pew']},
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Environment :: Console']
)
