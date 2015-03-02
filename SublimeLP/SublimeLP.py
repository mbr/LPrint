import os

import sublime
import sublime_plugin

from .printing.lp import PrintSystemLP
from .util import SettingsAdapter


PLUGIN_CONFIG_FILE = 'SublimeLP.sublime-settings'
SYNTAX_CONFIG_FILE = 'SublimeLP-{}'


def _get_synax(view):
    syntax_file = view.settings().get('syntax')
    return os.path.splitext(os.path.basename(syntax_file))[0]


def _get_options(view=None):
    options = SettingsAdapter(
        [sublime.load_settings(PLUGIN_CONFIG_FILE)]
    )

    if view is not None:
        fn = SYNTAX_CONFIG_FILE.format(_get_synax(view))
        options.settings.insert(0, sublime.load_settings(fn))

    return options


def _get_print_system(settings):
    ps = PrintSystemLP()
    ps.opts['lp'] = settings.get('lp_args')
    ps.opts['lpstat'] = settings.get('lpstat_args')

    return ps


def show_printer_select(window, ps, on_selected, add_default=True,
                        message=None, current=False):
    printers = ps.get_all_printers()

    def select_printer(idx):
        if idx == -1:
            return

        if add_default:
            if idx == 0:
                printer = None
            else:
                printer = printers[idx-1]
        else:
            printer = printers[idx]

        on_selected(printer)

    printer_list = [p.name for p in printers]
    selected_index = -1

    if add_default:
        printer_list.insert(0, '(None, use print system default)')
        if current is not False and current is None:
            selected_index = 0

    if current:
        selected_index = printer_list.index(current)

    if message:
        sublime.status_message(message)
    window.show_quick_panel(
        printer_list, select_printer,
        selected_index=selected_index,
    )


class SelectPrinterCommand(sublime_plugin.WindowCommand):
    def run(self):
        settings = sublime.load_settings(PLUGIN_CONFIG_FILE)
        ps = _get_print_system(settings)

        def set_active_printer(printer):
            if printer is None:
                settings.set('printer', None)
                sublime.status_message('Now using system default printer.')
            else:
                settings.set('printer', printer.name)
                sublime.status_message('Now using printer: {}'.format(
                    printer.name
                ))
            sublime.save_settings(PLUGIN_CONFIG_FILE)

        show_printer_select(
            self.window, ps, set_active_printer,
            message='Select the new default printer',
            current=settings.get('printer')
        )


class PrintDocumentCommand(sublime_plugin.TextCommand):
    printer = 'ask'

    def run(self, edit):
        options = _get_options(self.view)

        # instantiate printing system
        ps = _get_print_system(options)

        if self.printer == 'ask':
            show_printer_select(
                self.view.window(), ps, lambda p: self._do_print(p, options),
                message='Select destination printer',
                current=options.get('printer')
            )
        elif self.printer == 'default':
            pname = options.pop('printer')
            if pname is None:
                self._do_print(ps.get_default_printer(), options)
            else:
                self._do_print(ps.get_printer(pname), options)

    def _do_print(self, printer, options):
        content = self.view.substr(sublime.Region(0, self.view.size()))
        title = (self.view.name() or self.view.file_name() or
                 'Buffer {}'.format(self.view.buffer_id()))
        options['title'] = title
        sublime.status_message('Printing ({}): {}'.format(printer.name, title))

        printer.print_raw(content.encode('utf8'), options)


class QuickPrintCommand(PrintDocumentCommand):
    printer = 'default'
