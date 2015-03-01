import re

from printing.filter import CommandFilter


class EnscriptFilter(CommandFilter):
    output_format = 'ps'

    def __call__(self, text, options):
        encoding = options.pop('print_encoding', 'latin1')

        args = ['enscript', '-p', '-', '-X', encoding]

        if not options.pop('header', False):
            args.append('--no-header', '')

        args.extend(['--title', options.pop('title', 'Enscript_Print_Job')])

        args.extend(['--font', '{}@{}'.format(
            options.pop('font_family', 'Courier'),
            options.pop('font_size', 10),
        )])

        if options.pop('landscape', False):
            args.append('--landscape')
        else:
            args.append('--portrait')

        args.extend(['--media', options.pop('media', 'a4')])

        args.append('--margins')
        args.append('{}:{}:{}:{}'.format(
            options.pop('margin_left', ''),
            options.pop('margin_right', ''),
            options.pop('margin_top', ''),
            options.pop('margin_bottom', ''),
        ))

        proc = self._popen(args)

        return self._communicate(proc, text.encode(encoding)), options


class PAPSFilter(CommandFilter):
    output_format = 'ps'
    _title_re = re.compile(b'%%Title: stdin')
    _unsafe_re = re.compile(b'[^0-9A-Za-z-_.]')

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
        ps = self._communicate(proc, text.encode('utf8'))

        # fix title
        safe_title = self._unsafe_re.sub(
            b'', options.pop('title', 'PAPS Print Job').encode('utf8')
        )
        ps_new = self._title_re.sub(
            b'%%Title: ' + safe_title, ps, count=1
        )
        return ps_new, options


class RST2PDFFilter(CommandFilter):
    output_format = 'pdf'

    def __call__(self, text, options):
        args = ['rst2pdf', '-o', '-']

        proc = self._popen(args)
        return self._communicate(proc, text.encode('utf8')), options
