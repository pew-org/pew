#! /usr/bin/env python

from __future__ import print_function

import os
import sys
import argparse
import shutil
import contextlib
import locale
from subprocess import check_call, check_output
from glob import glob

locale.setlocale(locale.LC_ALL, '')

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


def deploy_inve(target):
	# temporary workaround: I plan to remove it when virtualenv's PR #247
	# will be completed
	if not os.path.exists(target):
		shutil.copy(source_inve, target)


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
		os.environ['VIRTUALENV_DISTRIBUTE'] = 'true'
		check_call(["virtualenv", args.envname] + args.rest)
		with chdir(args.envname):
			if args.project:
				with open('.project', 'w') as dotproject:
					dotproject.write(args.project)
			
	deploy_inve(get_inve(args.envname))
	
	inve = get_inve(args.envname)
	
	if args.requirements:
		invoke(inve, 'pip', 'install', '-r', expandpath(args.requirements))
	
	if args.packages:
		invoke(inve, 'pip', 'install', *args.packages)
	
	invoke(inve)


def rmvirtualenv_cmd():
	if len(sys.argv) < 2:
		sys.exit("Please specify an environment")
	
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
			sys.exit('showvirtualenv [env]')


def lsvirtualenv(verbose):
	envs = [env.split(os.path.sep)[-3] for env in
			glob(os.path.join(workon_home, '*', env_bin_dir, 'python'))]
	for env in envs:
		deploy_inve(get_inve(env))

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
		sys.exit("ERROR: Environment '{0}' does not exist. Create it with \
'mkvirtualenv {0}'.".format(env))
	else:
		inve = get_inve(env)
		invoke(inve)


def sitepackages_dir():
	if 'VIRTUAL_ENV' not in os.environ:
		sys.exit('ERROR: no virtualenv active')
	else:
		site = check_output(['python', '-c', 'import distutils; \
print(distutils.sysconfig.get_python_lib())'])
		return site.decode(locale.getlocale()[1]).strip()


def add2virtualenv_cmd():
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', dest='remove', action='store_true')
	parser.add_argument('dirs', nargs='+')
	args = parser.parse_args()
	
	extra_paths = os.path.join(sitepackages_dir(), '_virtualenv_path_extension.pth')
	new_paths = [os.path.abspath(d) + "\n" for d in args.dirs]
	if not os.path.exists(extra_paths):
		with open(extra_paths, 'w') as extra:
			extra.write('''import sys; sys.__plen = len(sys.path)
import sys; new=sys.path[sys.__plen:]; del sys.path[sys.__plen:]; p=getattr(sys,'__egginsert',0); sys.path[p:p]=new; sys.__egginsert = p+len(new)
''')

	def rewrite(f):
		with open(extra_paths, 'r+') as extra:
			to_write = f(extra.readlines())
			extra.seek(0)
			extra.truncate()
			extra.writelines(to_write)

	if args.remove:
		rewrite(lambda lines: [line for line in lines if line not in new_paths])
	else:
		rewrite(lambda lines: lines[0:1] + new_paths + lines[1:])


def sitepackages_dir_cmd():
	print(sitepackages_dir())


def lssitepackages_cmd():
	site = sitepackages_dir()
	print(*os.listdir(site))
	extra_paths = os.path.join(site, '_virtualenv_path_extension.pth')
	if os.path.exists(extra_paths):
		print('from _virtualenv_path_extension.pth:')
		with open(extra_paths) as extra:
			print(''.join(extra.readlines()))
