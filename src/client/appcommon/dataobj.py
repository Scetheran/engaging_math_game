class DataObject(object):
    def __init__(self, **fields):
        self.__dict__.update(fields)
        self._fields = set()
        for k in fields.keys():
            self._fields.add(k)

    def fields(self):
        return self._fields
