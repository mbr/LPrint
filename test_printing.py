from printing.lp import PrintSystemLP
from printing.lib import *
from printing.filter import DocumentPrinter


if __name__ == '__main__':
    ps = PrintSystemLP()

    print(ps.get_all_printers())
    print(ps.get_default_printer())

    pos = {
        'duplex': 'long-edge',
        'copies': 1,
        'media': 'a4',
        'font_family': 'Times',
        'font_size': 28,
        'margin_left': 0,
        'margin_right': 0,
        'text_columns': 2,
        'landscape': True,
        'header': True,
        'title': 'JOBTEST',
    }

    doc = open('sample.rst', 'rb').read().decode('utf8')
    dp = DocumentPrinter(ps.get_printer('PDF'))
    dp.filters.append(PAPSFilter())

    dp.print_doc(doc, options=pos)
