#! /usr/bin/env python

from setuptools import setup

long_desc = '''Python Env Wrapper is a set of commands to manage multiple [virtual environments](http://pypi.python.org/pypi/virtualenv). Pew can create, delete and copy your environments, using a single command to switch to them wherever you are, while keeping them in a single (configurable) location.

Virtualenvs makes it easier to work on more than one project at a time without introducing conflicts in their dependencies.

Pew is completely shell-agnostic and thus works on bash, zsh, fish, powershell, etc.

For the documentation, you might want to read here:
https://github.com/berdario/pew#usage'''


setup(
    name='pew',
    version='0.1.17',
    description='tool to manage multiple virtualenvs written in pure python',
    long_description=long_desc,
    author='Dario Bertini',
    author_email='berdario+pypi@gmail.com',
    url='https://github.com/berdario/pew',
    license='MIT License',
    packages=['pew'],
    install_requires=[
        'virtualenv>=1.11', 'virtualenv-clone>=0.2.5', 'setuptools>=17.1', 'pythonz-bd>=1.10.2'
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
        ':python_version=="3.3"': ['pathlib'],
    },
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': ['pew = pew.pew:pew']},
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Environment :: Console']
)
