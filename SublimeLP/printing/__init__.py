"""Available options:
    'duplex': None,          # possible values are 'long-edge', 'short-edge',
                             # 'one-sided'
    'copies': None,          # integer
    'priority': None,        # range 0-100
    'media': None,           # a4, letter, legal or others
    'landscape': False,
    'font_size': 12,
    'font_family': 'Courier New',
    'header': False,

    # in pt:
    'margin_top':
    'margin_right':
    'margin_bottom':
    'margin_left':
"""


class PrintSystem(object):
    def get_all_printers(self):
        pass

    def get_default_printer(self):
        pass

    def get_printer(self):
        pass


class Printer(object):
    name = None

    def print_raw(self, options={}):
        pass

    def print_ps(self, data, options={}):
        self.print_raw(data, options)

    def print_pdf(self, data, options={}):
        self.print_raw(data, options)

    def __repr__(self):
        return '<Printer {!r}>'.format(self.name)


class CmdOptsMixin(object):
    def __init__(self):
        self.cmds = {}
        self.opts = {}

    def build_args(self, cmd, *extra_args):
        args = [self.cmds.get(cmd, cmd)]
        args.extend(self.opts.get(cmd, []))
        args.extend(extra_args)
        return args
