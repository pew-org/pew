#! /usr/bin/env python

from __future__ import print_function

import os
import sys
import argparse
import shutil
import contextlib
from subprocess import check_call


env_bin_dir = 'bin'
if sys.platform in ('win32', 'cygwin'):
	env_bin_dir = 'Scripts'


def expandpath(path):
	return os.path.normpath(os.path.expanduser(os.path.expandvars(path)))

workon_home = expandpath(os.environ.get('WORKON_HOME', '~/.virtualenvs'))
if not os.path.exists(workon_home):
	os.makedirs(workon_home)


@contextlib.contextmanager
def chdir(dirname):
	curdir = os.getcwd()
	try:
		os.chdir(dirname)
		yield
	finally:
		os.chdir(curdir)


source_inve = os.path.normpath(os.path.join(os.path.dirname(
	__file__), '../../../../bin/inve'))
# XXX don't know why, but setuptools puts inve inside bin/ instead of lib/
# even if it's not executable
if not os.path.exists(source_inve):
	source_inve = os.path.join(os.path.dirname(__file__), 'inve')


def get_inve(env):
	return os.path.join(workon_home, env, env_bin_dir, 'inve')


def mkvirtualenv_cmd():
	parser = argparse.ArgumentParser()
	parser.add_argument('-p', '--python')
	parser.add_argument('-i', action='append', dest='packages', help='Install a \
package after the environment is created. This option may be repeated.')
	parser.add_argument('-a', dest='project', help='Provide a full path to a \
project directory to associate with the new environment.')
	parser.add_argument('-r', dest='requirements', help='Provide a pip \
requirements file to install a base set of packages into the new environment.')
	parser.add_argument('envname')
	parser.add_argument('rest', nargs=argparse.REMAINDER)

	args = parser.parse_args()
	if args.python:
		args.rest = ["--python=%s" % args.python] + args.rest
	
	with chdir(workon_home):
		check_call(["virtualenv", args.envname] + args.rest)
		with chdir(args.envname):
			if args.project:
				with open('.project', 'w') as dotproject:
					dotproject.write(args.project)
			# temporary workaround: as soon as virtualenv's PR #247 will be
			# completed I'll remove it
			shutil.copy2(source_inve, env_bin_dir)
	
	inve = get_inve(args.envname)
	
	if args.requirements:
		check_call([inve, 'pip', 'install', '-r', expandpath(args.requirements)])
	
	if args.packages:
		check_call([inve, 'pip', 'install'] + args.packages)
	
	check_call([inve])


def workon_cmd():
	try:
		env = sys.argv[1]
	except IndexError:
		lsvirtualenv("-b")
		return
	
	env_path = os.path.join(workon_home, env)
	if not os.path.exists(env_path):
		print("ERROR: Environment '{0}' does not exist. Create it with \
'mkvirtualenv {0}'.".format(env), file=sys.stderr)
		return
	else:
		inve = get_inve(env)
		check_call([inve])
