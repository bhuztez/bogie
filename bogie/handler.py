from __future__ import absolute_import

import sys
from wsgiref.handlers import BaseHandler


class WSGIHandler(BaseHandler):
    os_environ = {}

    # wsgi.multiprocess, wsgi.multithread, wsgi.run_once, wsgi.url_scheme
    def __init__(self, environ, stdin, stdout, stderr=sys.stderr):
        self.base_env = environ
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

        self._write = self.stdout.write
        self._flush = self.stdout.flush

    def get_stdin(self):
        return self.stdin

    def get_stderr(self):
        return self.stderr

    def add_cgi_vars(self):
        self.environ.update(self.base_env)


    

