LPrint
======

LPrint is a fairly flexible printing system for Sublime Text 3. It uses
lp/lpstat to print and can filter documents through any number of programs
before printing.


How do I print?
---------------
Two commands are available for printing: ``Print Document`` and ``Quick
Print``. The former allows you to print the current document on a printer of
your choice, while ``Quick Print`` will use the default printer.

The following hotkeys are available by default:

* alt+shift+p:  ``Print Document``
* alt+shift+o:  ``Quick Print``
* alt+shift+s:  ``Select Printer`` (Select printer selection below).

You can also print from the menu, using ``File -> Print Document``.


How do I select a different printer?
------------------------------------
Use the ``Select Printer`` command. The selected printed will be used whenever
you use ``Quick Print`` and preselected on ``Print Document``.

This is also available via the menu: ``Preferences -> Select Printer``.


How do I make the output less ugly?
-----------------------------------

You need to select a better filter. LPrint's defaults are chosen to maximize
the chance you'll get a printout once you hit print, not to produce pretty
results.


How do I configure other options?
---------------------------------

LPrint uses its own settings (see ``Preferences -> Package Settings ->
LPrint``), by editing your user settings you can override these. For example,
if you want to use ``enscript`` (needs to be installed) as your default
filter, you can set it up as follows::

    "filter_chain": ["Enscript"]

All text slated for printing will first be run through the ``EnscriptFilter``
and then passed on to CUPS as postscript.

All filters have their own quirks due to the underlying utilities (for
example, ``enscript`` does not support utf8 while ``paps`` does, the latter
does not do syntax highlighting and so on).

Other configurable settings like paper size, number of copies, duplex can be
configured normally, have a look at the default settings file for a list of
options.


How does it work?
-----------------

lp
~~

``lp`` is usually found on Unix systems, as part of CUPS. LPrint is developed
primarily on Linux, it could work on OS X as well - if it breaks, send patches
(https://github.com/mbr/LPrint).


filters
~~~~~~~

LPrint uses filters to produce printable output. A filter is given a specific
type of input and produces an output that may or may not be suitable for
printing.

The simplest filter is the ``UTF8``-filter. It will take a string of text
(i.e. the buffer to be printed) and output UTF8-encoded "binary" text. Since
this can be passed to ``lp``, it is the default, as it reliably produces a
printable output (albeit of the ugly kind).
