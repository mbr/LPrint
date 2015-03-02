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


class SelectPrinterCommand(sublime_plugin.WindowCommand):
    def run(self):
        settings = sublime.load_settings(PLUGIN_CONFIG_FILE)
        ps = _get_print_system(settings)

        printers = ps.get_all_printers()

        def select_printer(idx):
            if idx == -1:
                return

            printer = printers[idx]
            settings.set('printer', printer.name.decode('utf8'))
            sublime.save_settings(PLUGIN_CONFIG_FILE)

        self.window.show_quick_panel(
            [p.name.decode('utf8') for p in printers], select_printer
        )


class PrintUsingDefaultPrinterCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        content = self.view.substr(sublime.Region(0, self.view.size()))
        options = _get_options(self.view)

        # instantiate printing system
        ps = _get_print_system(options)

        printer_name = options.pop('printer')
        if printer_name is None:
            printer = ps.get_default_printer()
        else:
            printer = ps.get_printer(printer_name)

        title = (self.view.name() or self.view.file_name() or
                 'Buffer {}'.format(self.view.buffer_id()))
        options['title'] = title
        sublime.status_message('Printing ({}): {}'.format(printer.name, title))

        printer.print_raw(content.encode('utf8'), options)
