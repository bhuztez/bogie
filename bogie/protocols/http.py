from __future__ import absolute_import

try:
    from urllib.parse import unquote_to_bytes

    def unquote(bytestring):
        return unquote_to_bytes(bytestring).decode('latin-1')

    def tostr(s):
        return str(s, 'iso-8859-1', 'strict')

except ImportError:
    from urllib import unquote

    tostr = str

import socket

from ..handler import WSGIHandler


MAXLINE = 65536
LWS = b"\t "
CRLF = b"\r\n"
HTTP_DEFAULT_SERVER_PORT = '80'

class LineTooLong(Exception):
    pass

class InvalidHeader(Exception):
    pass

class ConnectionHandler(object):

    def __init__(self):
        pass

    def __repr__(self):
        return 'HTTP'

    def _parse_headerlines(self, stdin):
        while True:
            headerline = stdin.readline(MAXLINE+2).rstrip(CRLF)
            if len(headerline) > MAXLINE:
                raise LineTooLong

            if len(headerline) == 0:
                break

            if headerline[0] in LWS:
                yield None, headerline[1:]
                continue

            name, value = headerline.split(b':', 1)
            yield name, value.strip(LWS)


    def _parse_headers(self, stdin):
        last_header = None

        for name,value in self._parse_headerlines(stdin):
            if name is not None:
                if last_header:
                    yield last_header

                last_header = name, value
            elif last_header:
                last_header = last_header[0], last_header[1] + b'\n ' + value
            else:
                raise InvalidHeader

        if last_header:
            yield last_header


    def parse_request(self, stdin):
        requestline = stdin.readline(MAXLINE+2).rstrip(CRLF)
        if len(requestline) > MAXLINE:
            raise LineTooLong

        method, uri, protocol = requestline.split(b" ", 3)

        headers = {}
        for name, value in self._parse_headers(stdin):
            header = headers.get(name, None)
            if header is None:
                headers[name] = value
            else:
                headers[name] = header + b', ' + value

        if b'?' in uri:
            path, query = uri.split(b'?',1)
        else:
            path, query = uri, b''

        environ = {}

        for key, value in headers.items():
            key = tostr(key).upper().strip().replace('-', '_')
            if key not in ['CONTENT_LENGTH', 'CONTENT_TYPE']:
                key = 'HTTP_' + key

            environ[key] = tostr(value.strip())

        environ['REQUEST_METHOD'] = tostr(method)
        environ['PATH_INFO'] = unquote(path)
        environ['QUERY_STRING'] = unquote(query)
        environ['SERVER_PROTOCOL'] = tostr(protocol)
        environ['SCRIPT_NAME'] = ''
        return environ


    def handle(self, conn, addr, server):
        stdin = conn.makefile("rb")
        stdout = conn.makefile("wb")


        # TODO: HTTP/1.1 keep alive
        # while True:

        try:
            # TODO log request
            environ = self.parse_request(stdin)

            # SERVER_NAME, SERVER_PORT
            if conn.family in (socket.AF_INET, socket.AF_INET6):
                environ['HTTP_REMOTE_ADDR'] = addr[0]
                environ['HTTP_REMOTE_PORT'] = str(addr[1])

            handler = WSGIHandler(environ, stdin, stdout)
            handler.run(server.application)
        finally:
            stdin.close()
            stdout.close()
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
