from pathlib import Path
pkgroot = Path(__file__).parent.absolute()
projroot = pkgroot.parent
from evn import *
from evn import dev, doc, format
# from evn.print import *
# from evn.decontain import *
from evn.cli import CLI

from icecream import ic as ic
ic.configureOutput(includeContext=True, prefix="🍦")
import builtins
builtins.ic = ic  # make ic available globally
