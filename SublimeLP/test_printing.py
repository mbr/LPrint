from printing import DEFAULT_OPTIONS
from printing.lp import PrintSystemLP
from printing.filter import CommandFilter, DocumentPrinter


class EnscriptFilter(CommandFilter):
    output_format = 'ps'

    def __init__(self, encoding='latin1'):
        super(EnscriptFilter, self).__init__()
        self.encoding = encoding

    def __call__(self, text, options):
        proc = self._popen(
            ['enscript', '-p', '-', '-X', self.encoding],
        )

        return self._communicate(proc, text.encode(self.encoding)), options


class PAPSFilter(CommandFilter):
    output_format = 'ps'

    def __call__(self, text, options):
        args = ['paps']

        proc = self._popen(args)

        return self._communicate(proc, text.encode('utf8')), options


if __name__ == '__main__':
    ps = PrintSystemLP()

    print(ps.get_all_printers())
    print(ps.get_default_printer())

    pos = DEFAULT_OPTIONS.copy()
    pos.update({
        'duplex': 'long-edge',
        'copies': 1,
        'media': 'a4',
    })

    doc = u'hellö, wörld!'
    dp = DocumentPrinter(ps.get_printer('PDF'))
    dp.filters.append(PAPSFilter())

    dp.print_doc(doc, title=u'printtest', options=pos)
