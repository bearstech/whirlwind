class AbstractStore(object):

    def fetch(self, path, startTime, endTime):
        # return datalib.TimeSeries
        raise NotImplemented()



class Store(AbstractStore):

    def __init__(self, drive, memory):
        pass


class WhisperStore(AbstractStore):
    pass


class CarbonStore(AbstractStore):
    pass
