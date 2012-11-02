from __future__ import absolute_import


import socket


class BaseSocketDescription(object):

    def _get_socket(self):
        raise NotImplementedError

    def listen(self, backlog=socket.SOMAXCONN):
        s = self._get_socket()
        s.listen(backlog)
        return s


class InetSocketDescription(BaseSocketDescription):

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def _get_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        return s

    def __repr__(self):
        return "<socket at %s:%d>"%(self.host, self.port)


class UnixSocketDescription(BaseSocketDescription):

    def __init__(self, path):
        self.path = path

    def _get_socket(self):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.bind(self.path)
        return s

    def __repr__(self):
        return "<socket at '%s'>"%(self.path,)


class FromFDSocketDescription(BaseSocketDescription):

    def __init__(self, fd):
        self.fd = fd

    def _get_socket(self):
        s = socket.fromfd(fd)
        return s

    def __repr__(self):
        return "<socket from fd:%d>"%(self.fd,)


def SocketDescription(description):
    parts = description.split(':', 1)

    if len(parts) == 1:
        return InetSocketDescription('127.0.0.1', int(parts[0]))
    else:
        host, port = parts

        if host == "unix":
            return UnixSocketDescription(int(port))
        elif host == "fromfd":
            return FromFDSocketDescription(int(port))

        # XXX: how about 0177.0.0.0x01
        return InetSocketDescription(host, int(port))

