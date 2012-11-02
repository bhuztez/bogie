from __future__ import print_function

import sys


class ArgumentError(Exception):
    pass


def store(option, argv, ctx, arg):
    if arg is None:
        arg, argv = argv[0], argv[1:]

    ctx.args[option.dest] = arg
    return argv


def store_const(option, argv, ctx, arg):
    ctx.args[option.dest] = option.const
    return argv


def help(option, argv, ctx, arg):
    print_help(ctx.options, file=sys.stdout)
    quit()


class Option(object):

    def __init__(self, short, long=None, action=store, dest=None, required=False, const=None, help=None):
        if long is None and short.startswith('--'):
            short, long = None, short

        self.short, self.long = short, long

        opt_strings = []

        if short is not None:
            opt_strings.append(short)

        if long is not None:
            opt_strings.append(long)

        self.opt_strings = opt_strings
        self.dest = dest
        self.action = action
        self.required = required
        self.const=const
        self.help = help

    def find_option(self, ctx, opt_string):
        if opt_string in self.opt_strings:
            ctx.seen[self] = None, opt_string
            return self

    def is_missing(self, ctx):
        if self.required:
            if self not in ctx.seen:
                return self

    def consume(self, argv, ctx, arg):
        return self.action(self, argv, ctx, arg)


class OptionGroup(object):

    def __init__(self, title, options, required=False):
        self.title = title
        self.options = options
        self.required = required

    def find_option(self, ctx, opt_string):
        for opt in self.options:
            option = opt.find_option(ctx, opt_string)
            if option is not None:
                ctx.seen[self] = option, opt_string
                return option

    def is_missing(self, ctx):
        if self.required and self not in ctx.seen:
            return self

        for opt in self.options:
            missing = opt.is_missing(ctx)
            if missing is not None:
                return missing


class MutexOptionGroup(OptionGroup):

    def find_option(self, ctx, opt_string):
        seen_opt, seen_opt_string = ctx.seen.get(self, (None, None))

        for opt in self.options:
            option = opt.find_option(ctx, opt_string)

            if option is None:
                continue

            if seen_opt is None:
                ctx.seen[self] = opt, opt_string
                return option

            if opt != seen_opt:
                raise ArgumentError("arguments conflict with each other: %s, %s" % (seen_opt_string, opt_string))

            return option


class ConditionalOptionGroup(OptionGroup):

    def __init__(self, title, condition, options):
        super(ConditionalOptionGroup, self).__init__(title, options)
        self.condition = condition

    def find_option(self, ctx, opt_string):
        if self.condition(ctx):
            return super(ConditionalOptionGroup, self).find_option(ctx, opt_string)

    def is_missing(self, ctx):
        if self.condition(ctx):
            return super(ConditionalOptionGroup, self).is_missing(ctx)


class ParserContext(object):

    def __init__(self, options):
        self.options = options
        self.seen = {}
        self.args = {}


def print_help(option, file):
    print(option.title, file=file)

    for opt in option.options:
        if isinstance(opt, Option):
            if opt.short is None:
                short = '   '
            else:
                short = opt.short + ','

            long = '{0:<17s}'.format(opt.long)
            print('  {0} {1} {2}'.format(short, long, opt.help or ''), file=file)

    for opt in option.options:
        if isinstance(opt, OptionGroup):
            print(file=file)
            print_help(opt, file=file)


def consume_argv(ctx, argv):
    if not argv:
        return

    arg_string = argv[0]

    if arg_string and arg_string[0] == '-' and len(arg_string) > 1:
        if arg_string[1] == '-':
            if '=' in arg_string:
                opt_string, arg = arg_string.split('=', 1)
            else:
                opt_string, arg = arg_string, None
        else:
            opt_string = arg_string[:2]
            arg = arg_string[2:] or None

        opt = ctx.options.find_option(ctx, opt_string)

        if opt is not None:
            return consume_argv(ctx, opt.consume(argv[1:], ctx, arg))

    raise ArgumentError("unrecognized argument: %s" % (arg_string))


PROTOCOL_OPTIONS = MutexOptionGroup(
    "Protocol Options:",
    [ Option("--http", dest="protocol", action=store_const, const="http",
             help="HTTP"),
      Option("--fcgi", dest="protocol", action=store_const, const="fcgi",
             help="FastCGI protocol"),
      Option("--scgi", dest="protocol", action=store_const, const="scgi",
             help="SCGI protocol"),
      Option("--uwsgi", dest="protocol", action=store_const, const="uwsgi",
             help="uWSGI protocol"),
      Option("--ajp", dest="protocol", action=store_const, const="ajp",
             help="Apache JServ Protocol"),
      Option("--hmux", dest="protocol", action=store_const, const="hmux",
             help="HMUX protocol") ]) # XXX: SPDY

HTTP_OPTIONS = ConditionalOptionGroup(
    "HTTP Options:",
    lambda ctx: ctx.args.get("protocol", None) == 'http',
    [ Option("--origin", dest="origin-server", action=store_const, const=True,
             help="origin server talks directly to client") ])

WORKER_OPTIONS = MutexOptionGroup(
    "Worker Options:",
    [ Option("--develop", dest="worker", action=store_const, const="develop",
             help="development worker"),
      Option("--prefork", dest="worker", action=store_const, const="prefork",
             help="prefork worker") ])

APPLICATION_OPTIONS = MutexOptionGroup(
    "Application Options:",
    [ Option("--demo", dest="application", action=store_const, const="wsgiref.simple_server.demo_app",
             help="wsgiref.simple_server.demo_app"),
      Option("--app", dest="application", action=store,
             help="name of application module or function"),
      Option("--file", dest="file", action=store,
             help="name of application file")])

OPTIONS = OptionGroup(
    "Usage: bogie [options]",
    [ Option("-l", "--listen", dest="socket", action=store,
             help="listen on socket"),
      PROTOCOL_OPTIONS,
      HTTP_OPTIONS,
      WORKER_OPTIONS,
      APPLICATION_OPTIONS,
      Option("-h", "--help", action=help,
             help="show this help message and exit"),])

DEFAULTS = {
    "protocol": "http",
    "worker": "develop",
    "application": "wsgiref.simple_server.demo_app",
    "socket": "tcp:8000"
}

def config_from_argv(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    ctx = ParserContext(OPTIONS)

    try:
        consume_argv(ctx, argv)
    except ArgumentError as e:
        print('ERROR:', e, file=sys.stderr)
        exit(1)

    args = ctx.args

    for k,v in DEFAULTS.items():
        args.setdefault(k,v)

    return args
