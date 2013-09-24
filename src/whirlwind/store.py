import os.path

class AbstractStore(object):

    def fetch(self, path, startTime, endTime):
        # return datalib.TimeSeries
        raise NotImplemented()


class Store(AbstractStore):
    """Consolidate values from a whisper store and carbon cache."""

    def __init__(self, drive, memory):
        pass


class WhisperStore(AbstractStore):

    def __init__(self, root_path):
        self.root_path = root_path

    def fetch(self, path, startTime, endTime):
        real_path = os.path.join(self.root_path, os.path.separator.join(path.split('.')))

class CarbonStore(AbstractStore):
    pass
