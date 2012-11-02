from __future__ import absolute_import

import io
import unittest
import functools

from .protocols import http



class HTTPTestCase(unittest.TestCase):

    def test_header_parse(self):
        buffer = io.BytesIO(b"""
GET / HTTP/1.1
Host: localhost

""".lstrip().replace(b'\n', b'\r\n'))
        handler = http.ConnectionHandler()
        env = handler.parse_request(buffer)

        self.assertEqual(env['REQUEST_METHOD'], 'GET')
        self.assertEqual(env['PATH_INFO'], '/')
        self.assertEqual(env['QUERY_STRING'], '')
        self.assertEqual(env['SERVER_PROTOCOL'], 'HTTP/1.1')
        self.assertEqual(env['HTTP_HOST'], 'localhost')


    def test_line_continuation(self):
        buffer = io.BytesIO(b"""
GET / HTTP/1.1
Line: a
 b
""".lstrip().replace(b'\n', b'\r\n'))
        handler = http.ConnectionHandler()
        env = handler.parse_request(buffer)

        self.assertEqual(env['HTTP_LINE'], 'a\n b')


    def test_multi_header(self):
        buffer = io.BytesIO(b"""
GET / HTTP/1.1
Cookie: a
Cookie: b

""".lstrip().replace(b'\n', b'\r\n'))
        handler = http.ConnectionHandler()
        env = handler.parse_request(buffer)

        self.assertEqual(env["HTTP_COOKIE"], 'a, b')


    def test_whitespace(self):
        buffer = io.BytesIO(b"""
GET / HTTP/1.1
Host: localhost\t\t\t\t

""".lstrip().replace(b'\n', b'\r\n'))
        handler = http.ConnectionHandler()
        env = handler.parse_request(buffer)

        self.assertEqual(env['HTTP_HOST'], 'localhost')




if __name__ == '__main__':
    unittest.main()

