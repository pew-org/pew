#! /usr/bin/env python

from setuptools import setup

long_desc = '''Python Env Wrapper is a set of tools to manage multiple virtual environments. The tools can create, delete and copy your environments, using a single command to switch to them wherever you are, while keeping them in a single (configurable) location.

Pew makes it easier to work on more than one project at a time without introducing conflicts in their dependencies. It is written in pure python and leverages inve: the idea/alternative implementation of a better activate script.

The advantage is that pew doesn't hook into a shell, but is only a set of commands that is thus completely shell-agnostic:

It works on bash, zsh, fish, powershell, etc.

For the documentation, you might want to read here:
https://github.com/berdario/pew#usage'''


setup(
    name='pew',
    version='0.1.14',
    description='tool to manage multiple virtualenvs written in pure python, '
    'a virtualenvwrapper rewrite',
    long_description=long_desc,
    author='Dario Bertini',
    author_email='berdario+pypi@gmail.com',
    url='https://github.com/berdario/pew',
    license='MIT License',
    packages=['pew'],
    install_requires=[
        'virtualenv>=1.11', 'virtualenv-clone>=0.2.5', 'setuptools>=0.8'
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
        'console_scripts':
        ["pew-{0} = pew.pew:{0}_cmd".format(cmd[:-4])
         for cmd in ('new_cmd', 'rm_cmd', 'show_cmd', 'ls_cmd', 'workon_cmd',
                     'add_cmd', 'sitepackages_dir_cmd', 'lssitepackages_cmd',
                     'toggleglobalsitepackages_cmd', 'cp_cmd',
                     'setproject_cmd', 'mkproject_cmd', 'mktmpenv_cmd',
                     'wipeenv_cmd', 'inall_cmd', 'in_cmd', 'restore_cmd',
                     'version_cmd')] +
        ['pew = pew.pew:pew']},
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Environment :: Console']
)
