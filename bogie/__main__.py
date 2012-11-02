from __future__ import absolute_import

import sys

from .config import config_from_argv



if __name__ == '__main__':
    # from wsgiref.simple_server import demo_app

    # args = parser.parse_args(sys.argv[1:])
    # print args

    # sock = args.socket.listen()

    # server = args.server(demo_app, args.handler)

    # try:
    #     server.serve(sock)
    # finally:
    #     sock.close()


    print config_from_argv()
