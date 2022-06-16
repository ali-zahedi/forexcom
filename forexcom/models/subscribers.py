class Listener:
    def __init__(self, name, sub_key):
        self._name = name
        self._sub_key = sub_key
        self._last_index = 0
        self._listener = {}

    @staticmethod
    def _get_index(index):
        return f'{index}'

    @property
    def name(self):
        return self._name

    @property
    def sub_key(self):
        return self._sub_key

    @property
    def listeners(self):
        return self._listener.values()

    def add(self, listener):
        self._last_index += 1
        index = self._get_index(self._last_index)
        self._listener[index] = listener
        return index

    def remove(self, index):
        if index in self._listener:
            del self._listener[index]


class Subscriber:
    splitter = '*_*'

    def __init__(self):
        self._subscriber = {}

    def join_index(self, name, index):
        return f'{name}{self.splitter}{index}'

    def split_index(self, index):
        sp = index.split(self.splitter)

        if len(sp) != 2:
            raise ValueError(f"{index} index is wrong")
        return sp[0], sp[1]

    def add_subscriber(self, name, sub_key):
        if self.exists(name):
            raise ValueError(f"{name} does exists before.")
        lis = Listener(name, sub_key)
        self._subscriber[lis.name] = lis

    def remove_subscriber(self, name):
        if self.exists(name):
            del self._subscriber[name]

    def add_listener(self, name, listener):
        if not self.exists(name):
            raise ValueError(f"{name} subscriber does not exists.")
        index = self._subscriber[name].add(listener)
        return self.join_index(name, index)

    def remove_listener(self, index):
        name, index = self.split_index(index)
        if self.exists(name):
            self._subscriber[name].remove(index)

    def exists(self, name):
        return name in self._subscriber

    def get_listeners(self, name):
        return self._subscriber[name].listeners if self.exists(name) else []

    def get_sub_key(self, name):
        return self._subscriber[name].sub_key if self.exists(name) else ''

    @property
    def sub_keys(self):
        return map(lambda x: self._subscriber[x].sub_key, self._subscriber.keys())
