from itertools import chain
import os
import shutil

from pew._utils import invoke_pew as invoke


def test_restore(workon_home, env1):
    # Break the test virtualenv by deleting all setuptools-related files and
    # directories.
    setuptools_patterns = ['lib*/**/setuptools*', 'Lib/**/setuptools*']
    to_be_deleted = set(chain(*((workon_home / 'env1').glob(pat) for pat in setuptools_patterns)))
    for file_path in to_be_deleted:
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except FileNotFoundError:
            # NOTE: The to_be_deleted list can contain multiple links to the
            # same file so the file could already be deleted.
            pass
    # Importing setuptools in the broken test virtualenv should fail.
    result = invoke('in', 'env1', 'python', '-c', 'import setuptools')
    assert 'ModuleNotFoundError' in result.err
    # Re-create the test virtualenv.
    invoke('restore', 'env1')
    # Importing setuptools in the re-created test virtualenv should not fail.
    result = invoke('in', 'env1', 'python', '-c', 'import setuptools')
    assert 'Error' not in result.err
