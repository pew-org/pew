Pew - Python Env Wrapper
========================

[![PyPi version](http://img.shields.io/pypi/v/pew.svg)](https://pypi.python.org/pypi/pew)
[![Build Status](https://travis-ci.org/berdario/pew.png)](https://travis-ci.org/berdario/pew)
[![Build status](https://ci.appveyor.com/api/projects/status/xxe096txh1fuqfag/branch/master?svg=true)](https://ci.appveyor.com/project/berdario/pew/branch/master)
[![PyPi](https://img.shields.io/pypi/format/pew.svg)](https://pypi.python.org/pypi/pew/)

[![Pull Request stats](http://www.issuestats.com/github/berdario/pew/badge/pr?style=flat-square)](http://www.issuestats.com/github/berdario/pew)
[![Issue stats](http://www.issuestats.com/github/berdario/pew/badge/issue?style=flat-square)](http://www.issuestats.com/github/berdario/pew)

Python Env Wrapper is a set of commands to manage multiple [virtual environments](http://pypi.python.org/pypi/virtualenv). Pew can create, delete and copy your environments, using a single command to switch to them wherever you are, while keeping them in a single (configurable) location.

Virtualenvs makes it easier to work on more than one project at a time without introducing conflicts in their dependencies.

Pew is completely shell-agnostic and thus works on bash, zsh, fish, powershell, etc.

Installation
------------

_Pew and its dependencies rely on a couple of features of pip/setuptools which might not be available on old versions. In case your distribution doesn't ship with one recent enough, you'll probably want to run `pip install --upgrade pip` before the installation._

If you cannot upgrade the version of setuptools on your system, and one of the packages listed below is of no use to you, I suggest to use [`pipsi`](https://pypi.python.org/pypi/pipsi) rather than plain `pip`


`pipsi install pew`

See the [troubleshooting](#troubleshooting) section, if needed.

There are also some packages, more or less up-to-date:

### Arch linux

For Archlinux, there's an [AUR package](https://aur.archlinux.org/packages/python-pew/)


Usage
-----

### Which SHELL is Pew going to use?

Ok, Pew is shell-agnostic, but how is your shell going to be selected?

Look for the `SHELL` environment variable: on most unix-like systems it's already defined in a login shell, and you can verify it with commands like:

    env | grep SHELL

or

    python3 -c 'import os;print(os.environ.get("SHELL","No shell defined"))'

Since that variable is not commonly used on Windows, we're defaulting to `powershell` over there. In all other cases we default instead to `sh`.

If `CMDER_ROOT` is defined this will select Cmder (a custom configuration of `cmd.exe`). Custom selection for even more shells might be added in the future.

### Windows/Cygwin notes

A python installed from the normal `.exe` file [behaves differently](https://github.com/berdario/pew/issues/80#issuecomment-168279648) from a python installed inside Cygwin. For this reason if you want to use Pew inside a Cygwin shell, you should use a Cygwin python, and if you want to use it inside Powershell, you should use your normal Python install, and avoid a Cygwin one.

Common workflow
---------------

You can create a new virtualenv, with a non-default python and specifying some packages to be installed in it, like this:

    ~> pew new --python=pypy -i django myproject
    Running virtualenv with interpreter /home/dario/Applications/bin/pypy
    New pypy executable in myproject/bin/pypy
    Installing distribute..................................................................
    .......................................................................................
    ..................................................................done.
    Installing pip................done.
    Downloading/unpacking django
    Downloading Django-1.5.1.tar.gz (8.0MB):
    8.0MB downloaded
    Running setup.py egg_info for package django

    warning: no previously-included files matching '__pycache__' found under directory '*'
    warning: no previously-included files matching '*.py[co]' found under directory '*'
    Installing collected packages: django
    [SNIP]
    Successfully installed django Cleaning up...
    Launching subshell in virtual environment. Type 'exit' or 'Ctrl+D' to return.

Once inside, you can check the current python version, list the packages present in its python's site-packages directory, and install additional packages like this:

    myproject ~> python -V
    Python 2.7.3 (b9c3566aa017, May 09 2013, 09:09:14)
    [PyPy 2.0.0 with GCC 4.6.3]
    myproject ~> pew lssitepackages
    distribute-0.6.34-py2.7.egg Django-1.5.1-py2.7.egg-info setuptools.pth pip-1.3.1-py2.7.egg
    easy-install.pth django
    myproject ~> pip install pdbpp
    Downloading/unpacking pdbpp
    [SNIP]
    Successfully installed pdbpp fancycompleter wmctrl pygments pyrepl
    Cleaning up...
    myproject ~> pip freeze
    Django==1.5.1
    Pygments==1.6
    cffi==0.6
    distribute==0.6.34
    fancycompleter==0.4
    pdbpp==0.7.2
    pyrepl==0.8.4
    wmctrl==0.1
    wsgiref==0.1.2
    myproject ~> ^D

You can also specify a requirements file, to be passed on to pip, and activate another virtualenv with workon:

    ~> pew new -r ~/Projects/topaz/requirements.txt topaz
    New python executable in topaz/bin/python
    [SNIP]
    Successfully installed rply pytest invoke requests py
    Cleaning up...
    Launching subshell in virtual environment. Type 'exit' or 'Ctrl+D' to return.
    topaz ~> ^D

    ~> pew workon myproject
    Launching subshell in virtual environment. Type 'exit' or 'Ctrl+D' to return.
    myproject ~>

Since 0.1.16, Pew integrates Pythonz, which allows you to easily install a new python version (only on linux and macosx):

    ~> pew install 2.6.1 --type pypy
    WARNING: Linux binaries are dynamically linked, as is usual, and thus might not be usable due to the sad story of linux binary    compatibility,  check the PyPy website for more information
    Downloading pypy-2.6.1-linux64.tar.bz2 as /home/dario/.pythonz/dists/pypy-2.6.1-linux64.tar.bz2
    ########################################################################## 100%
    Extracting pypy-2.6.1-linux64.tar.bz2 into /home/dario/.pythonz/build/PyPy-2.6.1
    Installing PyPy-2.6.1 into /home/dario/.pythonz/pythons/PyPy-2.6.1

    Installed PyPy-2.6.1 successfully.
    ~> pew new --python=$(pythonz locate 2.6.1 --type pypy) latest_pypy
    Running virtualenv with interpreter /home/dario/.pythonz/pythons/PyPy-2.6.1/bin/python
    New pypy executable in latest_pypy/bin/python
    Also creating executable in latest_pypy/bin/pypy
    Installing setuptools, pip, wheel...done.
    Launching subshell in virtual environment. Type 'exit' or 'Ctrl+D' to return.
    latest_pypy ~> python -V
    Python 2.7.10 (f3ad1e1e1d62, Aug 28 2015, 10:45:29)
    [PyPy 2.6.1 with GCC 4.8.4]


Command Reference
-----------------

When invoked without arguments `pew` will output the list of all commands with each one's description

### new ###

Create a new environment, in the WORKON_HOME.

`usage: pew new [-hd] [-p PYTHON] [-i PACKAGES] [-a PROJECT] [-r REQUIREMENTS] envname`

The new environment is automatically activated after being initialized.

The `-a` option can be used to associate an existing project directory with the new environment.

The `-i` option can be used to install one or more packages (by repeating the option) after the environment is created.

The `-r` option can be used to specify a text file listing packages to be installed. The argument value is passed to `pip -r` to be installed.

### workon ###

List or change working virtual environments.

`usage: pew workon [environment_name]`

If no `environment_name` is given the list of available environments is printed to stdout.

### mktmpenv ###

Create a temporary virtualenv.

`usage: pew mktmpenv [-h] [-p PYTHON] [-i PACKAGES] [-a PROJECT] [-r REQUIREMENTS]`

### ls ###

List all of the environments.

`usage: pew ls [-h] [-b | -l]`

The `--long` options will print each virtualenv side-by-side with its Python version and the contents of its site-packages

### show ###

`usage: pew show [env]`

### inall ###

Run a command in each virtualenv.

`usage: pew inall [command]`

### in ###

Run a command in the given virtualenv.

`usage: pew in [env] [command]`

### rm ###

Remove one or more environments, from the WORKON_HOME.

`usage: pew rm envs [envs ...]`

You have to exit from the environment you want to remove.

### install ###
Use Pythonz to download and build a Python vm

`usage: pew install [options] version`

To install Python3.5.0

`pew install 3.5.0`

To install Pypy:

`pew install 2.6.1 --type pypy`

### list_pythons ###
List the pythons installed by Pythonz

`usage: pew list_pythons [options]`

You can list all the Pythons available to install with `-a` or `--all-versions`

### locate_python ###
Locate the path for the python version installed by Pythonz

`usage: pew locate_python [options] version`

### cp ###

Duplicate an existing virtualenv environment. The source can be an environment managed by virtualenvwrapper or an external environment created elsewhere.

_Copying virtual environments is not well supported. Each virtualenv has path information hard-coded into it, and there may be cases where the copy code does not know to update a particular file. Use with caution._

`usage: pew cp [-hd] source [targetenvname]`

Target environment name is required for WORKON_HOME duplications. However, target environment name can be omitted for importing external environments. If omitted, the new environment is given the same name as the original.

### sitepackages_dir ###

Returns the location of the currently active's site-packages

### lssitepackages ###

Equivalent to `ls $(sitepackages_dir)`.

### add ###

Adds the specified directories to the Python path for the currently-active virtualenv.

`usage: pew add [-h] [-d] dirs [dirs ...]`

Sometimes it is desirable to share installed packages that are not in the system `site-packages` directory and which should not be installed in each virtualenv. One possible solution is to symlink the source into the environment `site-packages` directory, but it is also easy to add extra directories to the PYTHONPATH by including them in a `.pth` file inside `site-packages` using `pew add`.

The `-d` flag removes previously added directiories.

The directory names are added to a path file named `_virtualenv_path_extensions.pth` inside the site-packages directory for the environment.

### toggleglobalsitepackages ###

Controls whether the active virtualenv will access the packages in the global Python `site-packages` directory.

`usage: pew toggleglobalsitepackages [-q]`


### mkproject ###

Create a new virtualenv in the `WORKON_HOME` and project directory in `PROJECT_HOME`.

`usage: pew mkproject [-hd] [-p PYTHON] [-i PACKAGES] [-a PROJECT] [-r REQUIREMENTS] [-t TEMPLATES] [-l] envname`

The template option may be repeated to have several templates used to create a new project. The templates are applied in the order named on the command line. All other options are passed to `pew new` to create a virtual environment with the same name as the project.

A template is simply an executable to be found in `WORKON_HOME`, it will be called with the name of the project, and the project directory as first and second argument, respectively. A `template_django` script is given as an example inside the `pew` package.

### setproject ###

Bind an existing virtualenv to an existing project.

`usage: pew setproject [virtualenv_path] [project_path]`

When no arguments are given, the current virtualenv and current directory are assumed.

### restore ###

Try to restore a broken virtualenv by reinstalling the same python
version on top of it

`usage: pew restore env`

### rename ###

Rename a virtualenv (by copying it over to the new name, and deleting the old one)

`usage: pew rename source target`

### wipeenv ###

Remove all installed packages from the current (or supplied) env.

`usage: pew wipeenv [env]`

### shell_config ###

Prints the path for the current $SHELL helper file

`usage: pew shell_config`



Configuration
-------------

You can customize pew's virtualenvs directory location, with the `$XDG_DATA_HOME` or `$WORKON_HOME` environment variables, and the locations of new projects created with mkproject by setting `$PROJECT_HOME` (otherwise, the current directory will be selected).


Troubleshooting
---------------

### The environment doesn't seem to be activated ###

If you've defined in your shell rc file to export a PATH location that might shadow the executables needed by pew (or your project), you might find that when getting into the environment, they will still be at the head of the PATH.

There're multiple way to overcome this issue:

* Move your export statements into the profile (`.bash_profile` and `.zprofile` for bash and zsh respectively, or in fish wrap your statements in a `if status --is-login` block ) and set up your terminal emulator to launch your shell as a login shell
* Change your exports to put the new location at the tail, instead of the head of the PATH, e.g.: `export PATH=${PATH}:/usr/bin`
* Change the files your OS provides to setup the base environment (it might be useful to look into `/etc/paths.d`, `/etc/profile`, and [environment.plist](http://stackoverflow.com/a/8421952/293735))

If you're running the `zsh` configuration tool `prezto`, and/or you're on MacOSX, [you might want to read this](https://github.com/thoughtbot/dotfiles/pull/426#issue-109716011) (it's about another project for handling dotfiles, but the misconfiguration described is quite similar to one witnessed on other OSX/prezto systems).


### pkg_resources.DistributionNotFound: virtualenv ###

This might happen after a Python update, especially on MacOSX, upgrading `setuptools` might fix that (you should need superuser permissions to do it)

`easy_install -U setuptools`

or

`pip install --upgrade setuptools`

### Other issues ###

Congratulations! You found a bug, please [let me know](https://github.com/berdario/pew/issues/new) :)

Running Tests
-------------

The test suite for `pew` uses [tox](http://codespeak.net/tox). Most tests are actually integration tests that will fork shells, create virtualenvs and in some cases even download python packages from Pypi. The whole test suite takes around 1 minute to run on a single interpreter.

With every commit and pull request, the test suite is run over all supported interpreters on travis-ci (for unix-like) and appveyor (for windows).

To run individual test scripts, run from the top level directory of the repository a command like:

`tox tests/test_setproject.py`

To run tests under a single version of Python, specify the appropriate environment when running `tox`:

`tox -e py27`

Combine the two modes to run specific tests with a single version of Python:

`tox -e py27 tests/test_setproject.py`

You can also filter them:

`tox -e py34 -- -k workon`

Add new tests by modifying an existing file or creating new script in the tests directory.


Display the environment name in the terminal prompt
---------------------------------------------------

### bash/zsh ###

The first run setup should take care of this for you.

You can do it manually by appending to your `.bashrc`/`.zshrc`

`source $(pew shell_config)`

#### fish ####

Just like for bash/zsh, but since fish uses a `fish_prompt` function and not a `PS1` environment variable, the setup will only make available to you a fish function `pew_prompt`. Just use its output in the `fish_prompt` function.

#### powershell prompt ####

Add this to a prompt function:

`Write-Host -NoNewLine -f blue ([System.IO.Path]::GetFileName($env:VIRTUAL_ENV))`

### no hooks (for now) ###

(There's currently a Pull Request open for it)

Adding hooks for installing some packages on each new virtualenv creation is quite easy, but I couldn't find some comprehensive hook examples, and virtualenvwrapper's hook implementation lets the hook return a script to be sourced.

This could be handled by (instead of getting back a script to be sourced) getting back an environment/list of key-values to be applied when invoking inve.

But to handle just the simple case, using the existing virtualenvwrapper's infrastructure (which relied on stevedore) seemed like overkill, and given that the most interesting virtualenvwrapper's extensions have been merged to the trunk at the end, and that I never used virtualenvwrapper's hook first hand, I decided to skip them, at least for now.


Thanks
------

Everyone who submitted patches/PR, as of September 2015:

- José Luis Lafuente
- Arthur Vuillard
- Jakub Stasiak
- Ryan Hiebert
- Michael Hofer
- Daniel Harding
- Timothy Corbett-Clark
- Simon Junod
- Robin
- Matei Trușcă
- Lucas Cimon


Thanks also to Michael F. Lamb for his thought provoking gist and to Doug Hellman for virtualenvwrapper

Rationale
---------

Pew is written in pure python and leverages [inve](https://gist.github.com/datagrok/2199506): the idea for a better activate script.

Pew was originally a rewrite of virtualenvwrapper, the advantage is that pew doesn't hook into a shell, but is only a set of commands, thus completely shell-agnostic:

It works on bash, zsh, fish, powershell, etc.

Thanks to using Python libraries and setuptools for dependency management, to Python stricter error handling and the fact that "shelling out" let us avoid keeping track of the previous environment variable values, pew code is much shorter and easier to understand than [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/)'s. How many Python programmers know at a glance what does `"${out_args[@]-}"` do? Or `eval "envname=\$$#"`? Or [all other bash quirks](http://mywiki.wooledge.org/BashPitfalls) for that matter?

License
-------

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
