PEW - Python Env Wrapper (née Invewrapper)
==========================================

[![PyPi version](https://pypip.in/v/pew/badge.png)](https://crate.io/packages/pew/)
[![Build Status](https://travis-ci.org/berdario/invewrapper.png)](https://travis-ci.org/berdario/invewrapper)

**For new users coming from virtualenvwrapper and pre-0.1.6 users: after some users' suggestions, and after deeming not very useful to replicate 1to1 virtualenvwrapper's commands, now all the commands are subcommands of the pew command, or can used by prefixing "pew-"**

Python Env Wrapper (also called Invewrapper) is a set of tools to manage multiple [virtual environments](http://pypi.python.org/pypi/virtualenv). The tools can create, delete and copy your environments, using a single command to switch to them wherever you are, while keeping them in a single (configurable) location.

Invewrapper makes it easier to work on more than one project at a time without introducing conflicts in their dependencies. It is written in pure python and leverages [inve](https://gist.github.com/datagrok/2199506): the idea/alternative implementation of a better activate script.

The advantage is that invewrapper doesn't hook into a shell, but is only a set of commands that is thus completely shell-agnostic:

It works on bash, zsh, fish, powershell, etc.

Another side effect is that its code is much shorter and (hopefully) easier to understand than [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/)'s (the project upon which this is based). How many Python programmers know at a glance what does `"${out_args[@]-}"` do? or `eval "envname=\$$#"`?

* Part of the conciseness of invewrapper is thanks to inve itself: "shelling out" let us avoid to keep track of the previous environment variable values, and to create a deactivate script.

* Part is thanks to Python libraries, like argparse.

* Part is thanks to the stricter Python error handling.

* Part is thanks to some [differences](#differences-from-virtualenvwrapper).

* Part is also probably due to my objectionable taste for code layout :)

Installation
------------

`pip install pew`

See the [troubleshooting](#troubleshooting) section, if needed.

Usage
-----

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

Command Reference
-----------------

### new ###

Create a new environment, in the WORKON_HOME.

`usage: pew-new [-hd] [-p PYTHON] [-i PACKAGES] [-a PROJECT] [-r REQUIREMENTS] envname`

The new environment is automatically activated after being initialized.

The `-a` option can be used to associate an existing project directory with the new environment.

The `-i` option can be used to install one or more packages (by repeating the option) after the environment is created.

The `-r` option can be used to specify a text file listing packages to be installed. The argument value is passed to `pip -r` to be installed.

### workon ###

List or change working virtual environments.

`usage: pew-workon [environment_name]`

If no `environment_name` is given the list of available environments is printed to stdout.

### mktmpenv ###

Create a temporary virtualenv.

`usage: pew-mktmpenv [-h] [-p PYTHON] [-i PACKAGES] [-a PROJECT] [-r REQUIREMENTS]`

### ls ###

List all of the environments.

`usage: pew-ls [-h] [-b | -l]`

### show ###

`usage: pew-show [env]`

### inall ###

Run a command in each virtualenv.

`usage: pew-inall [command]`

### in ###

Run a command in the given virtualenv.

`usage: pew-in [env] [command]`

### rm ###

Remove one or more environments, from the WORKON_HOME.

`usage: pew-rm envs [envs ...]`

You have to exit from the environment you want to remove.

### cp ###

Duplicate an existing virtualenv environment. The source can be an environment managed by virtualenvwrapper or an external environment created elsewhere.

Copying virtual environments is not well supported. Each virtualenv has path information hard-coded into it, and there may be cases where the copy code does not know to update a particular file. Use with caution.

`usage: pew-cp [-hd] source [targetenvname]`

Target environment name is required for WORKON_HOME duplications. However, target environment name can be ommited for importing external environments. If omitted, the new environment is given the same name as the original.

### sitepackages_dir ###

Returns the location of the currently active's site-packages

### lssitepackages ###

Equivalent to `ls $(sitepackages_dir)`.

### add ###

Adds the specified directories to the Python path for the currently-active virtualenv.

`usage: pew-add [-h] [-d] dirs [dirs ...]`

Sometimes it is desirable to share installed packages that are not in the system `site-packages` directory and which should not be installed in each virtualenv. One possible solution is to symlink the source into the environment `site-packages` directory, but it is also easy to add extra directories to the PYTHONPATH by including them in a `.pth` file inside `site-packages` using `add2virtualenv`.

The `-d` flag removes previously added directiories.

The directory names are added to a path file named `_virtualenv_path_extensions.pth` inside the site-packages directory for the environment.

### toggleglobalsitepackages ###

Controls whether the active virtualenv will access the packages in the global Python `site-packages` directory.

`usage: pew-toggleglobalsitepackages [-q]`


### mkproject ###

Create a new virtualenv in the `WORKON_HOME` and project directory in `PROJECT_HOME`.

`usage: pew-mkproject [-hd] [-p PYTHON] [-i PACKAGES] [-a PROJECT] [-r REQUIREMENTS] [-t TEMPLATES] [-l] envname`

The template option may be repeated to have several templates used to create a new project. The templates are applied in the order named on the command line. All other options are passed to `pew-new` to create a virtual environment with the same name as the project.

A template is simply an executable to be found in `WORKON_HOME`, it will be called with the name of the project, and the project directory as first and second argument, respectively. A `template_django` script is given as example inside the `invewrapper` package.

### setproject ###

Bind an existing virtualenv to an existing project.

`usage: pew-setproject [virtualenv_path] [project_path]`

When no arguments are given, the current virtualenv and current directory are assumed.

Configuration
-------------

You can customize invewrapper's virtualenvs directory location, with the `$XDG_DATA_HOME` or `$WORKON_HOME` environment variables, and the locations of new projects created with mkproject by setting `$PROJECT_HOME` (otherwise, the current directory will be selected)


Troubleshooting
---------------

### The environment seems to not be activated ###

If you've defined in your shell rc file, to export a PATH location that might shadow the executables needed by invewrapper (or your project), you might find that when getting into the environment, they will still be at the head of the PATH.

There're multiple way to overcome this issue:

* Move your export statements into the profile (`.bash_profile` and `.zprofile` for bash and zsh respectively, or in fish wrap your statements in a `if status --is-login` block ) and set up your terminal emulator to launch your shell as a login shell
* Change your exports to put the new location at the tail, instead of the head of the PATH, e.g.: `export PATH=${PATH}:/usr/bin`
* Change the files your OS provide to setup the base environment (it might come useful to look into /etc/paths.d /etc/profile and [environment.plist](http://stackoverflow.com/a/8421952/293735))


### Other issues ###

Congratulations! You found a bug, please [let me know](https://github.com/berdario/invewrapper/issues/new) :)

Running Tests
-------------

invewrapper's test suite is a straight port of virtualenvwrapper's, dropping test related to things absent in invewrapper and converting the scripts to use commands "echoed inside the workon commands" (almost surely there was a better approach, but I wasn't sure how to integrate it with shunit asserts, and I didn't want to rewrite all the tests as well); This means that they're slightly uglier and they spew out more unimportant output when running.

The test suite for invewrapper uses [shunit2](http://shunit2.googlecode.com/) and [tox](http://codespeak.net/tox). The shunit2 source is included in the `tests` directory, but tox must be installed separately (`pip install tox`).

To run individual test scripts, run from the top level directory of the repository a command like:

`tox tests/test_cd.sh`

To run tests under a single version of Python, specify the appropriate environment when running tox:

`tox -e py27`

Combine the two modes to run specific tests with a single version of Python:

`tox -e py27 tests/test_cd.sh`

Add new tests by modifying an existing file or creating new script in the tests directory.


Differences from Virtualenvwrapper
----------------------------------

### workon opens a new shell prompt ###

I don't think there's any shortcoming to workon on another environment without exiting from the previous, and I've done it myself some times while developing, you'll probably want to keep it in mind and remember to exit properly each time... After all you just need to press Ctrl+D.

Another consequence is that the prompt won't be updated... but this can be easily fixed by using the `$VIRTUAL_ENV` variable.

To get a blue-colored name at the start of your prompt:

#### bash prompt ####

`PS1="\[\033[01;34m\]\$(basename '$VIRTUAL_ENV')\e[0m$PS1"`

#### zsh prompt ####

Add this at the beginning of your `PS1`

`%{$fg_bold[blue]%}$(basename "$VIRTUAL_ENV")`

#### fish prompt ####

`set -g __fish_prompt_venv (set_color --bold -b blue white) (basename "$VIRTUAL_ENV") "$__fish_prompt_normal "`

and then echo `__fish_prompt_venv` in the `fish_prompt` function.

#### powershell prompt ####

Add this to a prompt function:

`Write-Host -NoNewLine -f blue ([System.IO.Path]::GetFileName($env:VIRTUAL_ENV))`

### there're no cd* commands ###

Due to the fact that the commands cannot change the environment from which they've been called, the `cdvirtualenv`, `cdsitepackages` and `cdproject` are missing.

They can be simply implemented like:

`cd $VIRTUAL_ENV` for `cdvirtualenv`

`cd $(sitepackages_dir)` for `cdsitepackages`

`cd $(cat $VIRTUAL_ENV/.project)` for `cdproject`

Just like in the inve idea, an invewrapper command that returns a string of commands to be sourced could be created, and by putting it in your .bashrc/.zshrc/config.fish these aliases/command creations could be automated.

### due to argparse, not every argument order is supported ###

If in doubt, for the commands that use argparse, just run them with the `--help` flag, e.g.:

`pew new --help`

### no hooks (for now) ###

Adding hooks for installing some packages on each new virtualenv creation is quite easy, but I couldn't find some comprehensive hook examples, and virtualenvwrapper's hook implementation lets the hook return a script to be sourced.

This could be handled by (instead of getting back a script to be sourced) getting back an environment/list of key-values to be applied when invoking inve.

But to handle just the simple case, using the existing virtualenvwrapper's infrastructure (which relied on stevedore) seemed like overkill, and given that the most interesting virtualenvwrapper's extensions have been merged to the trunk at the end, and that I never used virtualenvwrapper's hook first hand, I decided to skip them, at least for now.

### lots of VIRTUALENVWRAPPER* env variables aren't used ###

Some of those, like VIRTUALENVWRAPPER_VIRTUALENV, just defaulted to virtualenv itself and never got any use inside virtualenvwrapper, and I couldn't find someone that made use for it in the wild... so, given that external commands can still be overridden (e.g. by changing the PATH) I chose to leave them out.

### the commands don't have the same exact name ###

Since `0.1.6`

Thanks
------

Thanks to Michael F. Lamb for his thought provoking gist

Thanks to Dough Hellman for his virtualenvwrapper code and for the tests and of his documentation that I got to reuse extensively

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
