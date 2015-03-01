from printing import PrintOptions
from printing.lp import PrintSystemLP


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
