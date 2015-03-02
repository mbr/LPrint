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


How do I configure syntax-specific settings?
--------------------------------------------

Configuring the print-system per syntax is useful because it allows setting up
filters solely for a single filetype. An example is setting up RST2PDF for
restructed Text files.

The quickest way to edit these is opening a file with the syntax you want
special options for and use ``Preferences -> Package Settings -> LPrint ->
Settings - Current Filetype``. Here is a useful example::

    "filter_chain": ["RST2PDF"]

Added to the restructuredText syntax-specific settings file this will result in
nicely rendered output (make sure to install ``rst2pdf`` though). You can print
this file to try it out now!


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


What filters are available?
---------------------------

UTF8
~~~~

The UTF8Filter is the most basic filter, it will encode your unicode text into
UTF8, making it possible to ship it directly to lp.


Enscript
~~~~~~~~

Calls `enscript` with a range of options. Enscript is finnicky about fonts and
many default configurations do not include support TrueType fonts, which often
make up the majority of fonts on a system. If your printed pages are all empty,
try changing ``font_family`` to ``Courier`` and ``font_size`` to 10.


PAPS
~~~~

An alternative to Enscript. Does not support syntax highlighting (at least not
at this moment), but uses utf8 natively and handles fonts like you would
expect.

You should have ``paps`` installed before using this.


RST2PDF
~~~~~~~

Runs your document through ``rst2pdf``. Should be activated using
Syntax-specific configuration options (see `How do I configure syntax-specific
settings?`_).

Install ``rst2pdf`` before using.
