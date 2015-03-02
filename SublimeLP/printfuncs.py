import os
import subprocess

import sublime
import sublime_plugin

from .printing.lp import PrintSystemLP


def _get_synax(view):
    syntax_file = view.settings().get('syntax')
    return os.path.splitext(os.path.basename(syntax_file))[0]


def _get_options(view):
    return SettingsAdapter([
        sublime.load_settings('SublimeLP-{}'.format(_get_synax(view))),
        sublime.load_settings('SublimeLP.sublime-settings'),
    ])


class SettingsAdapter(object):
    """Wraps multiple sublime settings in a dict-like interface.

    Settings are consulted in order. Any removal of keys is tracked as well.
    """
    def __init__(self, settings=[]):
        self.settings = settings
        self.popped = set()
        self.added = {}

    def copy(self):
        cp = SettingsAdapter(self.settings)
        cp.added = self.added.copy()
        cp.popped = self.popped[:]

        return cp

    def __setitem__(self, key, value):
        self.added[key] = value
        self.popped.discard(key)

    def __getitem__(self, key):
        return self.get(key)

    def __contains__(self, key):
        try:
            self.get(key)
            return True
        except KeyError:
            return False

    def get(self, key, *args):
        assert len(args) < 2  # one optional arg

        if key not in self.popped:
            if key in self.added:
                return self.added[key]

            for s in self.settings:
                if s.has(key):
                    return s.get(key)

        if len(args) > 0:
            return args[0]

        raise KeyError(key)

    def pop(self, *args):
        val = self.get(*args)
        self.popped.add(args[0])

        return val


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
