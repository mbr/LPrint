import subprocess

import sublime
import sublime_plugin

from .printing.lp import PrintSystemLP


class SettingsAdapter(object):
    def __init__(self, settings):
        self.settings = settings
        self.popped = []
        self.added = {}

    def __setitem__(self, key, value):
        self.added[key] = value

    def __getitem__(self, key):
        return self.get(key)

    def __contains__(self, key):
        return self.settings.has(key)

    def get(self, key, *args):
        if key in self.popped:
            if len(args) < 1:
                raise KeyError(key)
            return args[0]

        if key in self.added:
            return self.added[key]

        return self.settings.get(key, *args)

    def pop(self, *args):
        val = self.get(*args)
        self.popped.append(args[0])

        return val


class PrintUsingDefaultPrinterCommand(sublime_plugin.TextCommand):
    def load_settings(self):
        return sublime.load_settings('SublimeLP.sublime-settings')

    def run_lp(self, lines, title):
        try:
            settings = self.settings

            lp_cmd = ['lp', '-t', title]

            def append_arg(cmd, arg, name):
                val = settings.get(name)
                if val is not None:
                    cmd.append(arg)
                    cmd.append(str(val))

            def append_flag(cmd, arg, name):
                val = settings.get(name)
                if val:
                    cmd.append(arg)

            def append_option(cmd, opt, name):
                val = settings.get(name)
                if val is not None:
                    cmd.append('-o')
                    cmd.append('{}={}'.format(opt, val))

            def append_option_flag(cmd, flag, name):
                val = settings.get(name)
                if val:
                    cmd.append('-o')
                    cmd.append(flag)

            # connection options
            append_flag(lp_cmd, '-E', 'stlp_force_encryption')
            append_arg(lp_cmd, '-U', 'stlp_username')
            append_arg(lp_cmd, '-h', 'stlp_host')
            append_flag(lp_cmd, '-m', 'stlp_send_email')

            # job options
            append_arg(lp_cmd, '-d', 'stlp_dest')
            append_arg(lp_cmd, '-n', 'stlp_copies')
            append_arg(lp_cmd, '-q', 'stlp_priority')

            # paper
            append_option(lp_cmd, 'media', 'stlp_media')
            append_option_flag(lp_cmd, 'landscape', 'stlp_landscape')

            duplex = settings.get('stlp_duplex')
            if duplex is True or duplex == 'long-edge':
                lp_cmd.extend(['-o', 'sides=two-sided-long-edge'])
            elif duplex is False or duplex == 'one-sided':
                lp_cmd.extend(['-o', 'one-sided'])
            elif duplex == 'short-edge':
                lp_cmd.extend(['-o', 'sides=two-sided-short-edge'])

            # text output
            append_option(lp_cmd, 'cpi', 'stlp_text_cols_per_inch')
            append_option(lp_cmd, 'lpi', 'stlp_text_lines_per_inch')
            append_option(lp_cmd, 'page-top', 'stlp_text_margin_top')
            append_option(lp_cmd, 'page-right', 'stlp_text_margin_right')
            append_option(lp_cmd, 'page-bottom', 'stlp_text_margin_bottom')
            append_option(lp_cmd, 'page-left', 'stlp_text_margin_left')

            print('lp command', lp_cmd)
            try:
                lp = self._open_cmd(lp_cmd)
                stdout, stderr = self._communicate(
                    lp, input=lines.encode('utf8'))
            except OSError as e:
                sublime.error_message(str(e))
            sublime.status_message('Print job sent')
        except subprocess.TimeoutExpired:
            sublime.error_message('Command timeout')

    def run(self, edit):
        content = self.view.substr(sublime.Region(0, self.view.size()))
        options = SettingsAdapter(self.load_settings())

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
        sublime.status_message('Printing {}'.format(title))

        printer.print_raw(content.encode('utf8'), options)
