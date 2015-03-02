LPrint
======

LPrint is a fairly flexible printing system for Sublime Text 3. It uses
lp/lpstat to print and can filter documents through any number of programs
before printing.


How do I print?
---------------
TBD (add keyboard shortcuts)


How do I select a different printer?
------------------------------------
TBD (add menu entries)


How do I make the output less ugly?
-----------------------------------

See the `How it works`_-section for details; you need to select a filter.
LPrint's defaults are chosen to maximize the chance you'll get a printout once
you hit print, not to produce pretty results.




How it works
------------

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
