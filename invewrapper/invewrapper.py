#! /usr/bin/env python

from __future__ import print_function

import os
import sys
import argparse
import shutil
import contextlib
from subprocess import check_call, check_output
from glob import glob

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


source_inve = os.path.join(os.path.dirname(__file__), 'inve')


def get_inve(env):
	return os.path.join(workon_home, env, env_bin_dir, 'inve')


def invoke(inve, *args):
	if sys.platform == 'win32' and not args:
		check_call(['python', inve, 'powershell'])
	else:
		check_call(('python', inve) + args)


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
			shutil.copy(source_inve, env_bin_dir)
	
	inve = get_inve(args.envname)
	
	if args.requirements:
		invoke(inve, 'pip', 'install', '-r', expandpath(args.requirements))
	
	if args.packages:
		invoke(inve, 'pip', 'install', *args.packages)
	
	invoke(inve)


def rmvirtualenv_cmd():
	if len(sys.argv) < 2:
		print("Please specify an environment", file=sys.stderr)
		return
	
	with chdir(workon_home):
		for env in sys.argv[1:]:
			env = os.path.join(workon_home, env)
			if os.environ.get('VIRTUAL_ENV') == env:
				print("ERROR: You cannot remove the active environment \
	(%s)." % env, file=sys.stderr)
				break
			try:
				shutil.rmtree(env)
			except OSError as e:
				print("Error while trying to remove the {} env: \
\n{}".format(env, e.strerror), file=sys.stderr)


def showvirtualenv(env):
	print(env)


def showvirtualenv_cmd():
	try:
		showvirtualenv(sys.argv[1])
	except IndexError:
		if 'VIRTUAL_ENV' in os.environ:
			showvirtualenv(os.path.basename(os.environ['VIRTUAL_ENV']))
		else:
			print('showvirtualenv [env]', file=sys.stderr)


def lsvirtualenv(verbose):
	envs = [env.split(os.path.sep)[-3] for env in
			glob(os.path.join(workon_home, '*', env_bin_dir, 'inve'))]
	# I'm checking the presence of inve, this will skip environments
	# not created with invewrapper, but this is for the best, since you
	# wouldn't be able to load them
	if not verbose:
		print(' '.join(envs))
	else:
		for env in envs:
			showvirtualenv(env)


def lsvirtualenv_cmd():
	parser = argparse.ArgumentParser()
	p_group = parser.add_mutually_exclusive_group()
	p_group.add_argument('-b', '--brief', action='store_false')
	p_group.add_argument('-l', '--long', action='store_true')
	args = parser.parse_args()
	lsvirtualenv(args.long)


def workon_cmd():
	try:
		env = sys.argv[1]
	except IndexError:
		lsvirtualenv(False)
		return
	
	env_path = os.path.join(workon_home, env)
	if not os.path.exists(env_path):
		print("ERROR: Environment '{0}' does not exist. Create it with \
'mkvirtualenv {0}'.".format(env), file=sys.stderr)
		return
	else:
		inve = get_inve(env)
		invoke(inve)


def add2virtualenv_cmd():
	NotImplemented


def lssitepackages_cmd():
	if 'VIRTUAL_ENV' not in os.environ:
		print('ERROR: no virtualenv active', file=sys.stderr)
	else:
		site = check_output(['python', '-c', 'import distutils; \
print(distutils.sysconfig.get_python_lib())']).strip()
		print(' '.join(os.listdir(site)))
		extra_paths = os.path.join(site, '_virtualenv_path_extension.pth')
		if os.path.exists(extra_paths):
			print('from _virtualenv_path_extension.pth:')
			with open(extra_paths) as extra:
				print(''.join(extra.readlines()))
