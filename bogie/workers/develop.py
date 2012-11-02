from __future__ import absolute_import

import os
import select

from . import base


class WSGIServer(base.WSGIServer):

    def handle(self, socket):
        select.select([socket], [], [])

        pid = os.fork()
        if pid:
            os.waitpid(pid, 0)
        else:
            super(WSGIServer, self).handle(socket)
            quit()
