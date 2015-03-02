import subprocess


class DocumentPrinter(object):
    def __init__(self, printer, filters=[]):
        self.printer = printer
        self.filters = filters

    @property
    def name(self):
        return self.printer.name

    def print_doc(self, data, options={}):
        fmt = 'raw'
        options = options.copy()

        for f in self.filters:
            data, options = f(data, options)
            fmt = f.output_format

        return getattr(self.printer, 'print_{}'.format(fmt))(
            data, options
        )

    print_raw = print_doc


class DocumentFilter(object):
    output_format = 'raw'

    def __call__(self, data, options):
        return data, options


class CommandFilter(DocumentFilter):
    def _popen(self, *args, **kwargs):
        return subprocess.Popen(
            *args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            **kwargs
        )

    def _communicate(self, proc, *args, **kwargs):
        stdout, stderr = proc.communicate(*args, **kwargs)

        if proc.returncode != 0:
            raise subprocess.CalledProcessError(
                proc.returncode, proc.args, stderr
            )

        return stdout
