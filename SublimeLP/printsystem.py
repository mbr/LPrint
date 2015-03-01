from contextlib import contextmanager
from functools import wraps
import subprocess


class PrintSystemError(Exception):
    pass


class PrintSystem(object):
    pass


@contextmanager
def error_wrap():
    try:
        yield
    except OSError as e:
        raise PrintSystemError('OSError: {}'.format(e))
    except subprocess.CalledProcessError as e:
        raise PrintSystemError('{} failed ({}): {}'.format(
            e.cmd, e.returncode, e.output
        ))


def wrap_errors(f):
    @wraps(f)
    def _(*args, **kwargs):
        with error_wrap():
            return f(*args, **kwargs)

    return _


class CmdOptsMixin(object):
    def __init__(self):
        self.cmds = {}
        self.opts = {}

    def build_args(self, cmd, *extra_args):
        args = [self.cmds.get(cmd, cmd)]
        args.extend(self.opts.get(cmd, []))
        args.extend(extra_args)
        return args


class PrintSystemLP(CmdOptsMixin):
    def __init__(self):
        super(PrintSystemLP, self).__init__()
        self.cmds['lp'] = 'lp'
        self.cmds['lpstat'] = 'lpstat'

    def get_all_printers(self):
        printers = []
        with error_wrap():
            buf = subprocess.check_output(self.build_args('lpstat', '-a'))

        for line in buf.splitlines():
            printer_name = line.split()[0].strip()
            if not printer_name:
                continue

            printers.append(PrinterLP(self, printer_name))

        return printers

    def get_default_printer(self):
        with error_wrap():
            buf = subprocess.check_output(self.build_args('lpstat', '-d'))
        if b':' not in buf:
            return None

        name = buf.split(b':')[-1].strip()

        return PrinterLP(self, name)

    def get_printer(self, name):
        return PrinterLP(self, name)

    def _opts_to_args(self, title=None, options=None,):
        args = []

        if title is not None:
            args.extend(['-t', title])

        if options is None:
            return args

        if options.copies is not None:
            args.extend(['-n', str(options.copies)])

        if options.priority is not None:
            args.extend(['-q', str(options.priority)])

        if options.media is not None:
            args.extend(['-o', 'media={}'.format(options.media)])

        if options.landscape is not None:
            args.append('-o')
            args.append('landscape' if options.landscape else 'portrait')

        if options.duplex is not None:
            args.append('-o')

            if options.duplex == 'long-edge':
                args.append('sides=two-sided-long-edge')
            elif options.duplex == 'short-edge':
                args.append('sides=two-sided-short-edge')
            elif options.duplex == 'one-sided':
                args.append('sides=one-sided')
            else:
                raise ValueError('Invalid duplex value: {}'.format(
                    options.duplex)
                )

        if options.chars_per_inch is not None:
            cpi, lpi = options.chars_per_inch

            if cpi:
                args.extend(['-o', 'cpi={}'.format(cpi)])
            if lpi:
                args.extend(['-o', 'lpi={}'.format(lpi)])

        if options.margins is not None:
            for idx, name in enumerate(('top', 'right', 'bottom', 'left')):
                val = options.margins[idx]

                if val is not None:
                    args.extend(['-o', 'page-{}={}'.format(name, val)])

        return args


class PrinterLP(object):
    def __init__(self, ps, name):
        self.ps = ps
        self.name = name

    def print_raw(self, data, title=None, options=None):
        with error_wrap():
            args = self.ps.build_args(
                'lp', '-d', self.name, *self.ps._opts_to_args(title, options)
            )

            proc = subprocess.Popen(
                args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )

            stdout, _ = proc.communicate(data)
            if proc.returncode != 0:
                raise subprocess.CalledProcessError(
                    proc.returncode, proc.args, stdout
                )

    def print_ps(self, data, title=None, options=None):
        self.print_raw(data, title, options)

    def print_pdf(self, data, title=None, options=None):
        self.print_raw(data, title, options)

    def __repr__(self):
        return '<Printer {!r}>'.format(self.name)


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


if __name__ == '__main__':
    ps = PrintSystemLP()

    print(ps.get_all_printers())
    print(ps.get_default_printer())

    pos = PrintOptions(
        duplex='long-edge',
        copies=1,
        media='a4',
        landscape=True,
    )

    ps.get_printer('PDF').print_raw(b'hello, world', title='HELLOWORLD',
                                    options=pos)
