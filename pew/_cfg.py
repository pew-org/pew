import collections
import pathlib


class Cfg(object):
    """Minimal parser for pyvenv.cfg.
    """
    def __init__(self, path):
        self._path = path
        self._data = collections.OrderedDict()
        with path.open(encoding='utf-8') as f:
            for line in f:
                key, _, value = line.partition('=')
                self._data[key.strip().lower()] = value.strip()

    @property
    def bindir(self):
        return pathlib.Path(self._data['home'])

    @property
    def include_system_sitepackages(self):
        return self._data['include-system-site-packages'] == 'true'

    @include_system_sitepackages.setter
    def include_system_sitepackages(self, value):
        value = {True: 'true', False: 'false'}[value]
        self._data['include-system-site-packages'] = value

    def save(self):
        with self._path.open('w', encoding='utf-8') as f:
            for k, v in self._data.items():
                f.write('{} = {}\n'.format(k, v))
