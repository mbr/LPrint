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

        if options.pop('landscape', False):
            args.append('--landscape')

        cols = options.pop('text_columns', None)
        if cols is not None:
            args.append('--columns={}'.format(cols))

        args.extend(['--font', '{}, {}'.format(
            options.pop('font_family', 'Monospace'),
            options.pop('font_size', 12))])

        if options.pop('rtl', None):
            args.append('--rtl')

        args.extend(['--paper', options.pop('media', 'A4')])

        for side in ('top', 'right', 'bottom', 'left'):
            m = 'margin_' + side
            args.extend(['--{}-margin'.format(side), str(options.pop(m, 36))])

        if options.pop('header', False):
            args.append('--header')

        proc = self._popen(args)
        return self._communicate(proc, text.encode('utf8')), options


if __name__ == '__main__':
    ps = PrintSystemLP()

    print(ps.get_all_printers())
    print(ps.get_default_printer())

    pos = {
        'duplex': 'long-edge',
        'copies': 1,
        'media': 'a4',
        'font_family': 'Times New Roman',
        'font_size': 28,
        'margin_left': 0,
        'text_columns': 2,
        'landscape': True,
    }

    doc = u'hellö, wörld! ' * 50
    dp = DocumentPrinter(ps.get_printer('PDF'))
    dp.filters.append(PAPSFilter())

    dp.print_doc(doc, title=u'printtest', options=pos)
