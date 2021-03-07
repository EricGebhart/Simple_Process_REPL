import readline
import logging
import regex as re
import os
import atexit
import code

# The same configuration can be stored as instructions in a file read
# by the library with a single call. If myreadline.rc contains:
# # Turn on tab completion
# tab: complete
# # Use vi editing mode instead of emacs
# set editing-mode vi
# the file can be read with read_init_file():

# another alternative.
# Use the tab key for completion
# readline.parse_and_bind('tab: complete')

try:
    readline.read_init_file("spr-readline.rc")
except Exception:
    readline.parse_and_bind("tab: complete")

"""
This is a repl/interpreter with almost no syntax.
It currently recognizes words, strings and numbers.

The symbol tables are defined by the user.  To start,
symbols which point to functions should be added to the symbol
table.  From there, new symbols can be made by listing symbols
together.  This is a poor mans lisp with no parentheses.

There are two symbol tables. One is a table of what could
be considered keywords to invoke functions, or lists of keywords
which ultimately invoke functions.

The other is a table of special symbols which take parameters.
specials are functions which take arguments. Since we really have
no syntax this is a difficulty. Specials operate on the entire
command line and cannot be listed together like the normal
symbols can. Finding a special consists of looking up the first
word in the command, if found the special is evaluated with
parameters given. If the command is not a special, it is passed
on to be evaluated by normal symbol processing.

The two specials defined here are 'def' and 'set'. def allows
the creation of a new symbol in the symbol table, interactively
from the repl.  ie. 'def some-new-command 'help string' some list
of known symbols'

In the user space, save and load a configuration file is at least recommended
so that a configuration can be saved or loaded from the repl.

The symbol table is the lookup table for any functions you wish
to use in the repl, or in evaluating process strings.

A symbol is one of two things.
1. A function which will take no arguments or they are
provided in the symbol definition.  Arguments are not rebound.
2. A string of symbols.

It is possible to expose any functionality you wish, with these
limitations.

 Example:
 import repl as r
 symbols = [
     ['wifi', connect_wifi, 'Connect to wifi using nmtui if not connected.']
     ['list', P.list_usb,   'List the particle boards connected to USB.']
     ['start', 'wifi list', 'Connect wifi and list the boards.']
 ]
 r.init_symbol_table(symbols)

The specials table exists because it's handy to do things that take arguments.
like loading or saving a config file or defining a new symbol.
The normal symbols cannot be mixed with the special symbols, although
it should be possible to create a symbol which invokes a special in
a static argument manner.

If the number of args is -1 that indicates a varargs function and
the number of args will not be validated.

    ['name', function, nargs, 'helpstr']

    ['def', def_symbol, -1,
     "Define a new function; def <name> 'helpstr' <list of commands>"]

"""


# The regular symbols.
symbol_table = {}
# Special forms.
specials = {}
all_symbols = []  # for the readline completer.

logger = logging.getLogger()  # not working here????


def init(symbols, specials):
    init_symbol_table(symbols)
    init_specials_table(specials)


def init_symbol_table(symbol_list):
    """
    Given a list of symbols add them to the symbol table.
    each symbol should be in the form of
    ['name', function | str, 'help string']
    """
    for symbol in symbol_list:
        add_symbol(*symbol)


def add_symbol(name, function, helptext):
    """
    Add symbols to the repl symbol table,
    their function or list of commands and a help string
    """
    symbol_table[name] = dict(fn=function, doc=helptext)


def init_specials_table(symbol_list):
    """
    Given a list of specials add them to the specials table.
    each symbol should be in the form of
    ['name', function | str, 'help string']
    """

    for symbol in symbol_list:
        add_special(*symbol)


def add_special(name, function, nargs, helptext):
    """
    Add special symbols to the repls special symbol table,
    their function, number of arguments and a help string
    """
    specials[name] = dict(fn=function, nargs=nargs, doc=helptext)


def def_symbol(name, helpstr, commandstr):
    """Define a new symbol in the symbol table."""
    logging.info("define symbol: %s, %s, %s" % (name, commandstr, helpstr))
    add_symbol(name, commandstr, helpstr)


# Initialize the specials table with the repl's def symbol, so
# that the user will be able to define new symbols inside the repl.
init_specials_table(
    [
        [
            "def",
            def_symbol,
            -1,
            "Define a new function; def <name> 'helpstr' <list of commands>",
        ]
    ]
)


def get_special(s):
    "Try to get a special symbol's definition."
    logger.debug("Getting Special: %s" % s)
    symbol = specials.get(s)
    if symbol is None:
        logger.error("Invalid Command: %s" % s)
    return symbol


def get_symbol(s):
    "Try to get a symbol's definition."
    logger.debug("Getting Symbol: %s" % s)
    symbol = symbol_table.get(s)
    if symbol is None:
        logger.error("Invalid Command: %s" % s)
    return symbol


def symb_help(symbol_table):
    "return a list of symbols and their help text."
    res = []
    for key, val in sorted(symbol_table.items()):
        res.append([key, val["doc"]])
    return res


def get_user_functions():
    "return a list of user defined functions so they can be saved"
    res = {}
    for k, v in sorted(symbol_table.items()):
        if isinstance(v["fn"], str):
            res[k] = v
    return res


def get_non_user_functions():
    "return a list of user defined functions so they can be saved"
    res = {}
    for k, v in sorted(symbol_table.items()):
        if not isinstance(v["fn"], str):
            res[k] = v
    return res


def help_specials():
    """Return a list of the special symbols along with their help."""
    return symb_help(specials)


def help_symbols():
    """Return a list of the symbols along with their help."""
    return symb_help(symbol_table)


def funcptr_help():
    print("""These symbols are the basic parameter free functions.\n""")
    for k, v in get_non_user_functions().items():
        fn = v["fn"]
        print("    {0[0]:20} --- {0[1]}".format([k, v["doc"]]))
        try:
            print("              %s-doc: %s" % (fn.__name__, fn.__doc__))
        except Exception:
            print("              doc: %s" % (fn.__doc__))


def specials_help():
    print("\n\nSpecials are symbols which take parameters.\n")
    for doc in help_specials():
        print("    {0[0]:20} --- {0[1]}".format(doc))


def compound_help():
    """give the doc and source for all the compound symbols."""
    print("\n\nHere are the symbols which are defined in the configuration.\n")
    for k, v in sorted(get_user_functions().items()):
        print("    {0[0]:20} --- {0[1]}".format([k, v["doc"]]))
        print("             Source: [%s]" % v["fn"])


def all_symbol_names():
    """Return a list of all symbol names."""
    res = []
    res = list(specials.keys())
    res.extend(list(symbol_table.keys()))
    return res


def isa_special(cmd):
    "Quietly determine if a symbol is a special"
    try:
        sym = specials.get(cmd)
    except Exception:
        return None
    else:
        return sym


def isa_symbol(cmd):
    "Quietly determine if a symbol is symbol"
    try:
        sym = symbol_table.get(cmd)
    except Exception:
        return None
    else:
        return sym


def valid_command_ck(cmd):
    "Quietly validate a command is either a symbol or a special"
    try:
        isa_symbol(cmd)
    except Exception:
        try:
            isa_special(cmd)
        except Exception:
            return False
        else:
            return True
    else:
        return True


def get_specials_with_narg(nargs):
    """Get a list of specials which have number of args defined."""
    swn = []
    for k, v in specials.items():
        if v["nargs"] == nargs:
            swn.append(k)
    return swn


def do_specials(commands):
    """Call the special functions with their argument lists.
    Validates the number of arguments if possible. nargs=-1 is varible args.
    returns true if it was a special, false if not, even if it fails.
    """
    command = commands[0]
    special = isa_special(command)

    # logging.debug("do specials: %s" % command)
    # logging.debug("do specials: %s" % commands)
    # logging.debug("do specials: %s" % str(special))
    # # logging.debug("keys: %s" % str(special.keys()))
    # # logging.debug("nargs: %s" % str(special['nargs']))

    if special is not None:
        spfunc = special["fn"]
        spnargs = special["nargs"]
        nargs = len(commands[1:])

        if spnargs != -1 and spnargs != nargs:
            msg = "Command %s takes %d arguments" % (command, spnargs)
            raise SyntaxError(msg)

        else:
            # commands with 3 arguments, sort-of.
            # def actually takes variable args. which turns into 3 args.
            if command == "def":
                commandstr = " ".join(commands[3:])
                spfunc(commands[1], commands[2], commandstr)

            # commands with var args. ;-) they get a list to deal with.
            elif command in get_specials_with_narg(-1):
                spfunc(commands[1:])

            # commands with 2 arguments.
            elif command in get_specials_with_narg(2):
                spfunc(commands[1], commands[2])

            # commands with 1 argument.
            elif command in get_specials_with_narg(1):
                spfunc(commands[1])
    else:
        return False
    return True


def atom(token):
    'Numbers become numbers; "..." string; otherwise Symbol/cmd.'
    if token[0] == '"':
        # to get rid of the quotes, but that doesn't serve us.
        # return token[1:-1].encode('utf_8').decode('unicode_escape')
        return token.encode("utf_8").decode("unicode_escape")
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            try:
                return complex(token.replace("i", "j", 1))
            except ValueError:
                # A parameter less function in the symbol_table
                if valid_command_ck(token):
                    return token
                else:
                    raise SyntaxError("Unknown command %s" % token)


def tokenize(line):
    "Return the next token, reading new text into line buffer if needed."
    tregex = r"""\s*("(?:[\\].|[^\\"])*"|[^\s(")]*)(.*)"""
    tokens = []
    while True:
        if line == "":
            break
        token, line = re.match(tregex, line).groups()
        if token != "":
            tokens.append(token)
    logging.debug("tokenize: %s" % tokens)
    return tokens


def read(tokens):
    "Read an expression and return a list of tokens to be evaluated."
    commands = []
    for token in tokens:
        commands.append(atom(token))
    logging.debug("read %s" % commands)
    return commands


def parse(commandstr):
    "Tokenize a command string and parse it."
    logging.debug("parse %s" % commandstr)
    return read(tokenize(commandstr))


def eval_symbol(s):
    "Execute a function in the symbol_table."
    logger.debug("eval symbol: %s" % s)
    symbol = get_symbol(s)

    if symbol is not None:
        function = symbol["fn"]

        # its a string of symbols.
        if isinstance(function, str):
            eval_list(parse(function))
        else:
            function()


def eval_list(commands):
    "Execute a list of commands from the symbol table"
    logger.debug("eval list: %s" % commands)
    if do_specials(commands) is False:
        for cmd in commands:
            eval_symbol(cmd)


def eval_cmd(commandstr):
    """Evaluate a commandstr."""
    eval_list(parse(commandstr))


def repl_message():
    """Give a welcome message."""
    print("Welcome to the REPL.")
    print("Type 'help' for help and 'quit' to exit.")
    print("Other useful commands are list, get, show, and show-all.")


def make_completer(vocabulary):
    def custom_complete(text, state):
        # None is returned for the end of the completion session.
        results = [x for x in vocabulary if x.startswith(text)] + [None]
        # A space is added to the completion since the Python readline doesn't
        # do this on its own. When a word is fully completed we want to mimic
        # the default readline library behavior of adding a space after it.
        return results[state] + " "

    return custom_complete


class HistoryConsole(code.InteractiveConsole):
    def __init__(
        self,
        locals=None,
        filename="<console>",
        histfile=os.path.expanduser("~/.spr-history"),
    ):
        code.InteractiveConsole.__init__(self, locals, filename)
        self.init_history(histfile)

    def init_history(self, histfile):
        readline.parse_and_bind("tab: complete")
        if hasattr(readline, "read_history_file"):
            try:
                readline.read_history_file(histfile)
            except FileNotFoundError:
                pass
            atexit.register(self.save_history, histfile)

    def save_history(self, histfile):
        readline.set_history_length(1000)
        readline.write_history_file(histfile)


def repl(prompt="SPR:> "):
    """
    An input loop. nothing fancy. It does have history and
    completion at least.
    """
    repl_message()

    all_symbols = all_symbol_names()
    readline.parse_and_bind("tab: complete")
    readline.set_completer(make_completer(all_symbols))
    HistoryConsole()

    while True:
        try:
            line = input("SPR:> ")
            if len(line):
                eval_list(parse(line))
        except Exception as e:
            logger.error(e)
