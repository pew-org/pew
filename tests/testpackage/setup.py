# Test package for virtualenvwrapper tests
from setuptools import setup

version = '1.0'

setup(
    name='testpackage',
    version=version,
    description="Fake package",
    author="Ingeniweb",
    author_email='thomas.desvenain@gmail.com',
    url='http://pypi.python.org/pypi/testpackage/',
    scripts=['testscript.py']
    )
