import subprocess

from . import PrintSystem, Printer, CmdOptsMixin
from .exc import error_wrap


class PrintSystemLP(PrintSystem, CmdOptsMixin):
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

    def _opts_to_args(self, options={}):
        args = []

        if options.get('title', None) is not None:
            args.extend(['-t', options['title']])

        if options.get('copies', None) is not None:
            args.extend(['-n', str(options['copies'])])

        if options.get('priority', None) is not None:
            args.extend(['-q', str(options['priority'])])

        if options.get('media', None) is not None:
            args.extend(['-o', 'media={}'.format(options['media'])])

        if options.get('landscape', None) is not None:
            args.append('-o')
            args.append('landscape' if options['landscape'] else 'portrait')

        if options.get('duplex', None) is not None:
            args.append('-o')

            if options['duplex'] == 'long-edge':
                args.append('sides=two-sided-long-edge')
            elif options['duplex'] == 'short-edge':
                args.append('sides=two-sided-short-edge')
            elif options['duplex'] == 'one-sided':
                args.append('sides=one-sided')
            else:
                raise ValueError('Invalid duplex value: {}'.format(
                    options['duplex'])
                )

        # For simplicity we assume 10 Pitch (== CPI) at font size 10 and
        # keep the 10/6 ratio that's the default of lp
        # nothing we can do about font-familiy
        if options.get('font_size', None) is not None:
            cpi = 10 * (10.0/options['font_size'])
            lpi = cpi * 6 / 10.0
            args.extend(['-o', 'cpi={}'.format(cpi),
                         '-o', 'lpi={}'.format(lpi)])

        for side in ('top', 'right', 'bottom', 'left'):
            m = 'margin_' + side
            if options.get(m, None) is not None:
                args.extend(['-o', 'page-{}={}'.format(side, options[m])])

        return args


class PrinterLP(Printer):
    def __init__(self, ps, name):
        self.ps = ps
        self.name = name

    def print_raw(self, data, options={}):
        with error_wrap():
            args = self.ps.build_args(
                'lp', '-d', self.name, *self.ps._opts_to_args(options)
            )

            print('lp args:', args)

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
