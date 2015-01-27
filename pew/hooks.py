import os.path

from importlib.machinery import SOURCE_SUFFIXES, SourceFileLoader
from pathlib import Path

class _Hook(object):
    def __init__(self):
        self._registry = []

    def register(self, priority=float('inf')):
        def combinator(f):
            self._registry.append((priority, f))
            return f

        return combinator

    def call(self, *args, **kwargs):
        for _, f in sorted(self._registry, key=lambda x: x[0]):
            f(*args, **kwargs)

def _import_path(path):
    str_path = str(path)
    # use the first component of the filename and use that as module name
    name = 'pew.hooks.{}'.format(os.path.basename(str_path).split('.')[0])
    loader = SourceFileLoader(name, str_path)
    return loader.load_module()

def import_hooks(file_or_dir):
    for suffix in SOURCE_SUFFIXES:
        path = str(file_or_dir) + suffix
        if os.path.exists(path):
            _import_path(path)
            return

    if os.path.isdir(str(file_or_dir)):
        for suffix in SOURCE_SUFFIXES:
            for path in file_or_dir.glob('**/*' + suffix):
                _import_path(path)

# hooks exposed for downstream
# FIXME: document purpose of each hook
preactivate_hook = _Hook()
postactivate_hook = _Hook()
