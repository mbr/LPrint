"""Exercise command error reporting without Sublime or a print server."""

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch


class CommandTests(unittest.TestCase):
    """Check synchronous and deferred print-system failures at the UI boundary."""

    @classmethod
    def setUpClass(cls):
        """Load the plugin with stand-ins for Sublime's command base classes."""
        root = Path(__file__).resolve().parents[1]
        spec = importlib.util.spec_from_file_location(
            "_lprint_commands",
            root / "LPrint.py",
            submodule_search_locations=[str(root)],
        )
        cls.plugin = importlib.util.module_from_spec(spec)
        modules = patch.dict(
            sys.modules,
            {
                spec.name: cls.plugin,
                "sublime": MagicMock(),
                "sublime_plugin": SimpleNamespace(
                    WindowCommand=object, TextCommand=object
                ),
            },
        )
        modules.start()
        cls.addClassCleanup(modules.stop)
        spec.loader.exec_module(cls.plugin)

    def setUp(self):
        """Provide isolated settings, editor state, and subprocess stand-ins."""
        self.settings = {
            "lp_args": [],
            "lpstat_args": [],
            "printer": "printer",
            "filter_chain": ["UTF8"],
        }
        self.sublime = self.enterContext(patch.object(self.plugin, "sublime"))
        self.sublime.load_settings.return_value = self.settings
        self.enterContext(
            patch.object(
                self.plugin,
                "_get_options",
                side_effect=lambda view: self.settings.copy(),
            )
        )
        self.check_output = self.enterContext(patch.object(subprocess, "check_output"))
        self.check_output.return_value = b"printer accepting requests\n"
        self.popen = self.enterContext(patch.object(subprocess, "Popen"))
        self.popen.return_value.communicate.return_value = (b"", None)
        self.popen.return_value.returncode = 0
        self.window = MagicMock()
        self.view = MagicMock()
        self.view.window.return_value = self.window
        self.view.substr.return_value = "Printable text: \u00e9"
        self.view.name.return_value = "Document"

    def run_command(self, command_type):
        """Invoke a command with its expected editor context."""
        command = command_type()
        command.window = self.window
        command.view = self.view
        if command_type is self.plugin.SelectPrinterCommand:
            command.run()
        else:
            command.run(None)

    def print_document(self, command_type):
        """Print, selecting a named printer only after the command has returned."""
        self.run_command(command_type)
        if command_type is self.plugin.PrintDocumentCommand:
            callback = self.window.show_quick_panel.call_args.args[1]
            callback(1)

    def test_discovery_failures_show_one_error(self):
        """Report missing or failing lpstat for each command."""
        self.settings["printer"] = None
        for command in (
            self.plugin.SelectPrinterCommand,
            self.plugin.PrintDocumentCommand,
            self.plugin.QuickPrintCommand,
        ):
            for failure in (
                FileNotFoundError(2, "No such file or directory", "lpstat"),
                subprocess.CalledProcessError(1, ["lpstat"], b"unavailable"),
            ):
                with self.subTest(command=command.__name__, failure=failure):
                    self.sublime.error_message.reset_mock()
                    self.check_output.side_effect = failure
                    self.run_command(command)
                    self.sublime.error_message.assert_called_once()
                    message = self.sublime.error_message.call_args.args[0]
                    self.assertTrue(message.startswith("LPrint: "))
                    self.assertIn("lpstat", message)
                    self.window.show_quick_panel.assert_not_called()
                    self.popen.assert_not_called()

    def test_submission_failures_show_one_error(self):
        """Report missing or failing lp in direct and deferred printing paths."""
        for command in (
            self.plugin.PrintDocumentCommand,
            self.plugin.QuickPrintCommand,
        ):
            for missing in (True, False):
                with self.subTest(command=command.__name__, missing=missing):
                    self.sublime.error_message.reset_mock()
                    self.popen.side_effect = (
                        FileNotFoundError(2, "No such file or directory", "lp")
                        if missing
                        else None
                    )
                    self.popen.return_value.returncode = 1
                    self.popen.return_value.args = ["lp", "-d", "printer"]
                    self.popen.return_value.communicate.return_value = (
                        b"rejected",
                        None,
                    )
                    self.print_document(command)
                    self.sublime.error_message.assert_called_once()
                    message = self.sublime.error_message.call_args.args[0]
                    self.assertTrue(message.startswith("LPrint: "))
                    self.assertIn("lp", message)
                    if not missing:
                        self.assertIn("rejected", message)

    def test_successful_printing_has_no_error(self):
        """Preserve UTF-8 submission through both printing commands."""
        for command in (
            self.plugin.PrintDocumentCommand,
            self.plugin.QuickPrintCommand,
        ):
            with self.subTest(command=command.__name__):
                self.popen.reset_mock()
                self.print_document(command)
                self.popen.assert_called_once()
                self.popen.return_value.communicate.assert_called_once_with(
                    self.view.substr.return_value.encode("utf8"),
                )
                self.sublime.error_message.assert_not_called()


if __name__ == "__main__":
    unittest.main()
