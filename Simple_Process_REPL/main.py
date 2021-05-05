import Simple_Process_REPL.core as r
import Simple_Process_REPL.appstate as A

"""
The purpose of this module is to Serve as a liaison between the
Interpreter/REPL and the Application interface layer. This is where
you will add functionalities which you wish to use in your processes.

The Repl module requires two symbol tables, and a dictionary of
defaults, as well as any stateful data the application would like to keep.
In this case it is the _device_ dictionary below.

The symbol table of these functions is defined and passed to
to the repl core module which is reponsible for similar things
as well as parsing the command line, setting up logging, and
executing the process as desired.

The symbol tables could be automated with the use of import. But I have
tried to keep a minimum of magic here. Symbol tables are clear and obvious.
"""

# This is a map which is merged with the application state map.
# Defaults are used by the cli where appropriate.
# device is our particle board, we need it's id, and the
# the path of it's device, ie. /dev/ttyUSB..., The board
# name is boron, photon, whatever. and the last_id just
# in case we need it.

MyState = {}
MyState = A.load_defaults(MyState)

symbols = []
specials = []

# get the default parser for the application and add to it if needed.
parser = None
# parser = r.get_parser()
# parser.add_argument("-f", "--foo", action="store_true", help="set foo")


def init():
    """
    Call into the interpreter/repl with our stuff,
    This starts everything up.
    """
    r.init(symbols, specials, parser)
