from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

authorizer = DummyAuthorizer()
authorizer.add_user('admin', 12345, './admin', perm='elradfmw')
authorizer.add_user('user', 1234, './usr', perm='elradfmw')

handler = FTPHandler
handler.authorizer = authorizer

server = FTPServer(('127.0.0.1', 1026), handler)
server.serve_forever()
