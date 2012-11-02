from __future__ import absolute_import

import select


class WSGIServer(object):

    def __init__(self, application, handler):
        self.application = application
        self.handler = handler

    def handle(self, socket):
        conn, addr = socket.accept()

        # if self.verify_request:
        #     if not self.verify_request(conn, addr):
        #         conn.shutdown()
        #         conn.close()
        #         # TODO: log
        #         return

        self.handler.handle(conn, addr, self)

    def serve(self, socket):
        while True:
            self.handle(socket)
