import pkgutil
import traceback
import readline
import logging
import regex as re
import os
import atexit
import code
from inspect import signature, _empty
from Simple_Process_REPL.appstate import load_pkg_yaml

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


Root = {}
all_symbols = []  # for the readline completer.
stypes = ["fptr", "voidfptr", "partial", "dolist", "namespace"]
Current_NS = "/"
NS = Root

logger = logging.getLogger()


def root_symbols(symbols, specials):
    """add symbols to the symbol table as a namespace."""
    global Root
    append_specials(append_symbols(Root, symbols), specials)
    # print(Root.keys())


def append_funcs(st, module, funclist):
    """Import a python module and add the function list to the given symbol table."""
    # get the SPR symbols and stuff from the module.
    lib = __import__(module, globals(), locals(), funclist, 0)

    # logger.info("Append Funcs: %s %d" % (funclist, len(funclist)))
    for fname in list(funclist):
        if type(fname) is not str:
            logger.info("Not str: %s" % str(fname))
            return
        else:
            f = getattr(lib, fname)

        # figure out if it's a var args [a*], or an [a b c*] varargs.
        # and how many args. Just to be nice and check later.
        # also stash the parameters in case do_fptrs() wants to get fancy.
        signature, nargs, vargs, def_index = get_fsig(f)

        name = fname.replace("_", "-")  # cause I don't like hitting shift.

        st[name] = dict(
            fn=f,
            doc=f.__doc__,
            signature=signature,
            nargs=nargs,
            vargs=vargs,
            def_index=def_index,
            stype="fptr",
        )

    return st


def merge_ns_states():
    """Loop through the namespaces and merge their _SPR_AS_ trees into one
    big dict tree."""
    global Root
    res = {}
    for k, v in sorted(Root.items()):
        if isstype(v, "namespace"):

            lib = __import__(v["name"], globals(), locals(), ["_SPR_AS_"], 0)
            _AS_ = getattr(lib, "_SPR_AS_", None)
            if _AS_ is not None:
                # Note: 3.9, also destructive, so no overlap between modules.
                res |= _AS_
    return res


def import_lib(module, *funclist):
    """import functions from a python module into the current namespace."""
    global NS
    append_funcs(NS["symbols"], module, *funclist)
    import_lib_spr(module)


def is_blank_line(line):
    """test if text is blank or not."""
    return re.match(r"^[\s]*$", line)


def load(reader):
    """Load a text reader (hopefully an spr file) into the interpreter."""
    txt = ""
    for line in reader:
        if len(line) == 0 or is_blank_line(line):
            if len(txt) > 0:
                eval_cmd(txt)
                txt = ""
        else:
            # get rid of newlines so the interpreter
            # sees a continuous line.
            txt += re.sub("\n", " ", line)


def import_lib_spr(module):
    """Look for an spr file with the same name in the module and load it if found."""
    root, name = module.split(".")
    sprname = name + ".spr"
    yname = name + ".yaml"
    logger.info("import spr %s: %s" % (root, sprname))
    try:
        init = pkgutil.get_data(root, sprname).decode("utf-8").split("\n")
        load(init)
    except Exception:
        pass

    try:
        load_pkg_yaml(module, yname)
    except Exception:
        pass


def create_namespace(name, docstr, module, *funclist):
    global Root
    logger.info("Creating Namespace: %s from Python module: %s" % (name, module))
    # logger.info(*funclist)
    ns = {
        "symbols": append_funcs({}, module, *funclist),
        "doc": docstr,
        "name": module,
        "funclist": funclist,
        "stype": "namespace",
    }
    Root[name] = ns
    in_ns(name)
    import_lib_spr(module)


def ns():
    """Which namespace are we in?"""
    global Current_NS
    global NS
    ns = NS
    if Current_NS == "/":
        print("\nNamepace: %s\n SPR Root Namespace.\n\n" % Current_NS)
    else:
        print(
            "\nNamespace: %s\n   Module: %s\n    %s\n\n"
            % (Current_NS, ns["name"], ns["doc"])
        )


def in_ns(ns=None):
    """Change into a namespace Only one level of depth of Namespaces for now."""
    global Root
    global NS
    global Current_NS
    # logger.info("Root: %s" % Root.keys())

    # logger.info("%s" % Root[ns])
    # for k in Root[ns].keys():
    #     try:
    #         logger.debug("%s" % Root[ns][k].keys())
    #     except Exception:
    #         pass

    if ns is None or ns == "/":
        Current_NS = "/"
        NS = Root
    else:
        Current_NS = ns
        NS = Root[ns]
    logger.info("In Namespace: %s" % Current_NS)


def append_symbols(st, slist):
    """
    Given a list of symbols add them to the symbol table.
    each symbol should be in the form of
    ['name', function | str, 'help string']
    """
    for name, function, helptext in slist:
        if isinstance(function, str):
            stype = "dolist"
        else:
            stype = "voidfptr"
        st[name] = dict(fn=function, doc=helptext, stype=stype)
    return st


def find_first_parameter_with_default(parameters):
    """find the index of the first parameter with a default value."""
    res = 0
    count = 0
    for k in parameters.keys():
        # logger.info(parameters[k])
        count += 1
        if parameters[k].default == _empty:
            continue
        else:
            res = count
            break
    return res


def get_fsig(f):
    sig = signature(f)
    parameters = sig.parameters
    nargs = len(parameters)
    varargs = False
    def_index = 0
    if nargs > 0:
        last_arg_key = list(sig.parameters.keys())[nargs - 1]
        last_arg_kind = parameters[last_arg_key].kind.name
        varargs = last_arg_kind in ["VAR_POSITIONAL", "VAR_KEYWORD"]
        def_index = find_first_parameter_with_default(parameters)
    return str(sig), nargs, varargs, def_index


def append_specials(st, slist):
    """Given a symbol table and a list of specials append them to the
    symbol table. each symbol should be in the form of
    ['name', function | str, nargs, 'help string']
    """
    for name, function, nargs, helptext in slist:
        sig, nargs, vargs, def_index = get_fsig(function)
        st[name] = dict(
            fn=function,
            signature=sig,
            nargs=nargs,
            vargs=vargs,
            def_index=def_index,
            doc=helptext,
            stype="fptr",
        )
    return st


def def_symbol(name, helpstr, commandstr):
    """define a new symbol which is a 'dolist' of other symbols.
    def myhelp 'helptext' help log help bcqr"""
    _def_symbol(name, helpstr, commandstr, stype="dolist")


def def_partial(name, helpstr, commandstr):
    """define a new function from an fptr function which has some
    of it's arguments filled in.

    partial get-bar-code-from 'helptxt' set-in-from barQR value from:

    will create a new function get-bar-code-from that takes a value vector
    just like set-in-from would. Because it is."""
    _def_symbol(name, helpstr, commandstr, stype="partial")


def _def_symbol(name, helpstr, commandstr, stype="dolist"):
    """Define a new symbol in the symbol table of the current namespace."""
    global NS
    logging.info(
        "Define: %s/%s, %s, %s, %s" % (Current_NS, name, commandstr, helpstr, stype)
    )
    s = dict(fn=commandstr, doc=helpstr, stype=stype)
    if NS == Root:
        NS[name] = s
    else:
        NS["symbols"][name] = s


def get_ns(s):
    global Root
    namespace = None
    name = s
    ns = None
    if s.find("/") >= 0:
        ns, name = s.split("/")
        namespace = Root.get(ns)
    return name, namespace


def _get_symbol(s):
    "Quietly, Try to get a symbol's definition."
    global Root
    logger.debug("Getting Symbol: %s" % s)
    n = None
    namespace = None
    # does start with a namespace?
    # This means that / means name space path...
    # traceback.print_stack() # getting called from atom. too much!

    n, namespace = get_ns(s)
    # logger.info("n and n: %s %s" % (n, namespace))
    if namespace is not None:
        symbol = namespace["symbols"].get(n)
    else:
        symbol = Root[s]

    logger.debug("Got Symbol: %s" % symbol)

    return symbol


def get_symbol(s):
    "Try to get a symbol's definition."
    try:
        symbol = _get_symbol(s)
    except Exception:
        logger.error("Unkown Symbol: %s" % s)
        symbol = None
    return symbol


def isstype(v, s):
    if not isinstance(s, list):
        return v["stype"] == s
    else:
        return v["stype"] in s


def all_fptr_help(st):
    """Print help for a python function."""
    for k, v in sorted(st.items()):
        if v["stype"] not in ["fptr", "voidfptr"]:
            continue
        fptr_help(k, v)


def fptr_help(k, v):
    """Format an fptr symbol's help."""
    if "signature" in v.keys():
        sig = "%s%s" % (k, v["signature"])
    else:
        sig = k
    print("\n%-20s" % sig)
    print("----------------\n%s" % v["doc"])


def all_dolist_help(st):
    """give the doc and source for all the compound symbols."""
    if len(st.items()) > 0:
        for k, v in sorted(st.items()):
            dolist_help(k, v)


def dolist_help(k, v):
    """Format an dolist symbol's help."""
    if isstype(v, "dolist") or isstype(v, "partial"):
        print("\n {0[0]:20}\n--------------\n{0[1]}".format([k, v["doc"]]))
        print("    Source: [%s]" % v["fn"])


def namespace_help(key, ns):
    """Format an namespace symbol's help."""
    print("\n\nNamespace: %s\n   Module: %s\n    %s\n\n" % (key, ns["name"], ns["doc"]))
    all_fptr_help(ns["symbols"])
    all_dolist_help(ns["symbols"])


def list_namespace(ns=Root):
    """List the non namespace stuff in the Root namespace."""
    print("\n Root Namespace: ")
    for k, v in sorted(Root.items()):
        if not isstype(v, "namespace"):
            print("   %s" % k)


def list_namespace_tree():
    """List the namespaces and all of their symbols """
    list_namespace()
    print("\n")
    for k, v in sorted(Root.items()):
        if isstype(v, "namespace"):
            print(
                "\n%-10s %15s:\n---------------------------\n%s"
                % (k, v["name"], v["doc"])
            )
            for j, v in sorted(v["symbols"].items()):
                print("   %s" % j)


def list_namespaces(ns=None):
    """List the name spaces"""
    # So that the signature shows up nicely in the doc.
    if ns is None:
        ns = Root
    for k, v in sorted(ns.items()):
        if isstype(v, "namespace"):
            print(
                "\n%-10s %20s: \n---------------------------------------------\n%s"
                % (k, v["name"], v["doc"])
            )


def helpful_cmds():
    """Print a list of helpful commands"""
    print("Helpful Commands: ls-ns, ns-tree, help <ns>, as/showin, def, help as")


def help(args=None):
    """Help for everything."""
    global Root
    print("\nSPR Help\n=============================================")
    sym = args
    helpful_cmds()
    if args is None:  # or len(args) == 0:
        all_fptr_help(Root)
        all_dolist_help(Root)
        print("=============================================")
        helpful_cmds()
        # list_namespaces()

    else:
        # for sym in args:
        # logger.info("Sym in args: " % (sym, args))
        s = _get_symbol(sym)
        if isstype(s, "namespace"):
            namespace_help(sym, s)
        if isstype(s, "dolist"):
            dolist_help(sym, s)
        if isstype(s, ["fptr", "partial", "voidfptr"]):
            fptr_help(sym, s)


def all_symbol_names():
    """Return a list of all symbol names. for readline, prompt completion."""
    res = []
    res.extend(list(Root.keys()))
    for k, v in sorted(Root.items()):
        if isstype(v, "namespace"):
            res.extend(v["symbols"].keys())

    return res


def isa_fptr(cmd):
    "Quietly determine if a symbol is a fptr with args"
    try:
        sym = _get_symbol(cmd)
        if not isstype(sym, "fptr"):
            sym = None
    except Exception:
        return None
    else:
        return sym


def get_specials_with_narg(st, nargs):
    """Get a list of specials which have number of args defined."""
    swn = []
    for k, v in st.items():
        if isstype(v, "fptr") and v["nargs"] == nargs:
            swn.append(k)
    return swn


# I think this function is too complicated. could be simpler. but it is
# working at the moment.
def do_fptrs(commands):
    """Call the fptr functions with their argument lists.
    Validates the number of arguments if possible. nargs=-1 is varible args.
    returns true if it was a special, false if not, even if it fails.

    This get's the first shot. if the first token isn't an fptr, then it goes
    on to be evaluated elsewhere.
    """
    command = commands[0]
    fptr = isa_fptr(command)

    # logging.debug("do specials: %s" % command)
    # logging.debug("do specials: %s" % commands)
    # logging.debug("do specials: %s" % str(fptr))

    if fptr is None:
        return False

    # logging.info("keys: %s" % str(special.keys()))
    # # logging.debug("nargs: %s" % str(special['nargs']))

    # logger.info("DO_FPTR %s" % fptr)
    fn = fptr["fn"]
    fnargs = fptr["nargs"]
    vargs = fptr["vargs"]
    def_index = fptr["def_index"]
    # sig = fptr["signature"]
    nargs = len(commands) - 1

    # logger.info("Fptr: %s\nNargs: %d\nVargs: %d\nSig: %s" % (fptr, nargs, vargs, sig))
    # "Command: %s - %s %s\n argcount: %d prms: %d varargs: %d"
    # % (command, func, sig, fnargs, nargs, vargs)

    if command == "def" or command == "partial":
        commandstr = " ".join(commands[3:])
        fn(commands[1], commands[2], commandstr)
        return True

    if vargs and nargs == 0:
        # logger.info("vargs and nargs=0.func() %s" % fn)
        fn()
        # logger.info("After no args func()")

    elif vargs:
        if fnargs == 1:
            # logger.info("vargs 1 %s" % commands[1:])
            fn(commands[1:])
        if fnargs == 2:
            fn(commands[1], commands[2:])
        if fnargs == 3:
            fn(commands[1], commands[2], commands[3:])
        if fnargs == 4:
            fn(commands[1], commands[2], commands[3], commands[4:])
        if fnargs == 5:
            fn(commands[1], commands[2], commands[3], commands[4], commands[5:])

        return True

    elif nargs <= fnargs and nargs >= def_index - 1:

        # commands with 4 arguments.
        if nargs == 4:
            fn(commands[1], commands[2], commands[3], commands[4])

        # commands with 3 arguments.
        elif nargs == 3:
            fn(commands[1], commands[2], commands[3])

        # commands with 2 arguments.
        elif nargs == 2:
            fn(commands[1], commands[2])

        # commands with 1 argument.
        elif nargs == 1:
            fn(commands[1])

        elif nargs == 0:
            fn()

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
                # A parameter less function in the Root symbol table
                # if valid_command_ck(token):
                return token
            # else:
            #    raise SyntaxError("Unknown command %s" % token)


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
    "Execute a function in the symbol table."
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
    """Execute a list from the symbol table.
    It's either a command with arguments or
    a list of commands.
    """
    logger.debug("eval list: %s" % commands)

    # if it's a partial expand it.
    first_sym = _get_symbol(commands[0])

    if isstype(first_sym, "partial"):
        logger.debug("Partial: %s --> %s" % (commands[0], commands))
        eval_list(parse(first_sym["fn"]) + commands[1:])
        return

    if do_fptrs(commands) is False:
        for cmd in commands:
            eval_symbol(cmd)


def eval_cmd(commandstr):
    """Evaluate a commandstr."""
    eval_list(parse(commandstr))


def eval_cmds(commands):
    """Evaluate a commandstr."""
    for c in commands:
        eval_list(parse(c))


def repl_message():
    """Give a welcome message."""
    print("Welcome to the REPL.")
    print("Type 'help' for help and 'quit' to exit.")


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


def repl(prompt="SPR:> ", init=None):
    """
    An input loop. nothing fancy. It does have history and
    completion at least.
    """

    all_symbols = all_symbol_names()
    readline.parse_and_bind("tab: complete")
    readline.set_completer(make_completer(all_symbols))
    HistoryConsole()

    if init is not None:
        eval_cmds(init)

    repl_message()

    while True:
        try:
            line = input(prompt)
            if len(line):
                eval_list(parse(line))
        except Exception as e:
            logger.error(e)
