import curses
from .cli import main

curses.wrapper(main)
