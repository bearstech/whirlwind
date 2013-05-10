from . import Carbon

from tornado.ioloop import IOLoop

server = Carbon()
server.listen(2003)
IOLoop.instance().start()
