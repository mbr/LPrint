class PrintSystem(object):
    def get_all_printers(self):
        pass

    def get_default_printer(self):
        pass

    def get_printer(self):
        pass


class Printer(object):
    name = None

    def print_raw(self, title=None, options=None):
        pass

    def print_ps(self, data, title=None, options=None):
        self.print_raw(data, title, options)

    def print_pdf(self, data, title=None, options=None):
        self.print_raw(data, title, options)

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


class PrintOptions(object):
    def __init__(self, **kwargs):
        super(PrintOptions, self).__init__()
        for k, v in kwargs.items():
            setattr(self, k, v)

    duplex = None          # possible values: 'long-edge', 'short-edge',
                           # 'one-sided'
    copies = None          # integer
    priority = None        # range 0-100
    media = None           # a4, letter, legal or others
    landscape = None       # False means portrait
    chars_per_inch = None  # characters per inch/line, should be a tuple
    margins = (None,       # top (in pt)
               None,       # right
               None,       # left
               None,)      # bottom
