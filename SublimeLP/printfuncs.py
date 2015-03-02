import os

import sublime
import sublime_plugin

from .printing.lp import PrintSystemLP
from .util import SettingsAdapter


def _get_synax(view):
    syntax_file = view.settings().get('syntax')
    return os.path.splitext(os.path.basename(syntax_file))[0]


def _get_options(view):
    return SettingsAdapter([
        sublime.load_settings('SublimeLP-{}'.format(_get_synax(view))),
        sublime.load_settings('SublimeLP.sublime-settings'),
    ])


class PrintUsingDefaultPrinterCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        content = self.view.substr(sublime.Region(0, self.view.size()))
        options = _get_options(self.view)

        # instantiate printing system
        ps = PrintSystemLP()
        ps.opts['lp'] = options.pop('lp_args')
        ps.opts['lpstat'] = options.pop('lpstat_args')

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
