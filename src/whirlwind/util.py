import imp
import socket
import errno
from os.path import splitext, basename
try:
    import cPickle as pickle
    USING_CPICKLE = True
except:
    import pickle
    USING_CPICKLE = False
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


def find_escaped_pattern_fields(pattern_string):
    pattern_parts = pattern_string.split('.')
    for index, part in enumerate(pattern_parts):
        if is_escaped_pattern(part):
            yield index


def is_escaped_pattern(s):
    for symbol in '*?[{':
        i = s.find(symbol)
        if i > 0:
            if s[i - 1] == '\\':
                return True
    return False


def is_local_interface(host):
    if ':' in host:
        host = host.split(':', 1)[0]

    for port in xrange(1025, 65535):
        try:
            sock = socket.socket()
            sock.bind((host, port))
            sock.close()

        except socket.error, e:
            if e.args[0] == errno.EADDRNOTAVAIL:
                return False
            else:
                continue

        else:
            return True

    raise Exception("Failed all attempts at binding to interface %s, last exception was %s" % (host, e))


def is_pattern(s):
    return '*' in s or '?' in s or '[' in s or '{' in s


def load_module(module_path, member=None):
    module_name = splitext(basename(module_path))[0]
    module_file = open(module_path, 'U')
    description = ('.py', 'U', imp.PY_SOURCE)
    module = imp.load_module(module_name, module_file, module_path, description)
    if member:
        return getattr(module, member)
    else:
        return module


# This whole song & dance is due to pickle being insecure
# The SafeUnpickler classes were largely derived from
# http://nadiana.com/python-pickle-insecure
# This code also lives in carbon.util
if USING_CPICKLE:
    class SafeUnpickler(object):
        PICKLE_SAFE = {
            'copy_reg': set(['_reconstructor']),
            '__builtin__': set(['object']),
            'graphite.intervals': set(['Interval', 'IntervalSet']),
        }

        @classmethod
        def find_class(cls, module, name):
            if not module in cls.PICKLE_SAFE:
                raise pickle.UnpicklingError('Attempting to unpickle unsafe module %s' % module)
            __import__(module)
            mod = sys.modules[module]
            if not name in cls.PICKLE_SAFE[module]:
                raise pickle.UnpicklingError('Attempting to unpickle unsafe class %s' % name)
            return getattr(mod, name)

        @classmethod
        def loads(cls, pickle_string):
            pickle_obj = pickle.Unpickler(StringIO(pickle_string))
            pickle_obj.find_global = cls.find_class
            return pickle_obj.load()

else:
    class SafeUnpickler(pickle.Unpickler):
        PICKLE_SAFE = {
            'copy_reg': set(['_reconstructor']),
            '__builtin__': set(['object']),
            'graphite.intervals': set(['Interval', 'IntervalSet']),
        }

        def find_class(self, module, name):
            if not module in self.PICKLE_SAFE:
                raise pickle.UnpicklingError('Attempting to unpickle unsafe module %s' % module)
            __import__(module)
            mod = sys.modules[module]
            if not name in self.PICKLE_SAFE[module]:
                raise pickle.UnpicklingError('Attempting to unpickle unsafe class %s' % name)
            return getattr(mod, name)

        @classmethod
        def loads(cls, pickle_string):
            return cls(StringIO(pickle_string)).load()

unpickle = SafeUnpickler
