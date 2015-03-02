class SettingsAdapter(object):
    """Wraps multiple sublime settings in a dict-like interface.

    Settings are consulted in order. Any removal of keys is tracked as well.
    """
    def __init__(self, settings=[]):
        self.settings = settings
        self.popped = set()
        self.added = {}

    def copy(self):
        cp = SettingsAdapter(self.settings)
        cp.added = self.added.copy()
        cp.popped = self.popped[:]

        return cp

    def __setitem__(self, key, value):
        self.added[key] = value
        self.popped.discard(key)

    def __getitem__(self, key):
        return self.get(key)

    def __contains__(self, key):
        try:
            self.get(key)
            return True
        except KeyError:
            return False

    def get(self, key, *args):
        assert len(args) < 2  # one optional arg

        if key not in self.popped:
            if key in self.added:
                return self.added[key]

            for s in self.settings:
                if s.has(key):
                    return s.get(key)

        if len(args) > 0:
            return args[0]

        raise KeyError(key)

    def pop(self, *args):
        val = self.get(*args)
        self.popped.add(args[0])

        return val
