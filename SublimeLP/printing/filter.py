import subprocess


class DocumentPrinter(object):
    def __init__(self, printer, filters=[]):
        self.printer = printer
        self.filters = filters

    def print_doc(self, data, title=None, options=None):
        fmt = 'raw'

        for f in self.filters:
            data = f(data)
            fmt = f.output_format

        return getattr(self.printer, 'print_{}'.format(fmt))(
            data, title, options
        )


class DocumentFilter(object):
    output_format = 'raw'

    def __call__(self, data):
        return data


class UTF8Filter(DocumentFilter):
    output_format = 'raw'

    def __call__(self, text):
        return text.encode('utf8')


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
