from printing import PrintOptions
from printing.lp import PrintSystemLP
from printing.filter import CommandFilter, DocumentPrinter


class EnscriptFilter(CommandFilter):
    output_format = 'ps'

    def __init__(self, encoding='latin1'):
        super(EnscriptFilter, self).__init__()
        self.encoding = encoding

    def __call__(self, text):
        proc = self._popen(
            ['enscript', '-p', '-', '-X', self.encoding],
        )

        return self._communicate(proc, text.encode(self.encoding))


if __name__ == '__main__':
    ps = PrintSystemLP()

    print(ps.get_all_printers())
    print(ps.get_default_printer())

    pos = PrintOptions(
        duplex='long-edge',
        copies=1,
        media='a4',
    )

    doc = u'hellö, wörld!'
    dp = DocumentPrinter(ps.get_printer('PDF'))
    dp.filters.append(EnscriptFilter())

    dp.print_doc(doc, title=u'printtest', options=pos)
