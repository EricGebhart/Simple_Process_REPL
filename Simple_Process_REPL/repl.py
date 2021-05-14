import pydoc
import pkgutil
import readline
import logging
import regex as re
import os
import atexit
import code
from inspect import signature, _empty
from Simple_Process_REPL.appstate import (
    merge_pkg_yaml,
    get_in,
    get_in_config,
    get_keys_in,
)
import Simple_Process_REPL.utils as u

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
"""


Root = {}
all_symbols = []  # for the readline completer.
stypes = ["fptr", "voidfptr", "partial", "dolist", "namespace"]
Current_NS = "/"
NS = Root

logger = logging.getLogger()

# yaml = u.load_pkg_yaml("Simple_Process_REPL", "bar_qr.yaml")

# # format and fill in as you wish.
# HelpText=("""
# bar-qr: - Bar and QR Code Scanning, generation, saving and printing.  -

# Recognized codetypes are either 'barcode' and 'QR-code'.

# Encode any value with preset prefix and suffixes as set in the configuration
# into a barcode or QR-code.

# Read a bar or QR code using the webcam. Currently keeps trying until it
# catches it or an escape key is pressed.

# Bar-qr uses this part of the Application state.

# %s

# When encoding the value is retrieved from bar-QR/value.
# When scanning with the webcam the resulting value will be placed in bar-QR/value.

# If working exclusively with bar or QR codes it may be beneficial to define
# partials for some functions, which always require a code type.

# """ % yaml)


# def help():
#     print(HelpText)


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


def is_blank_line(line):
    """test if text is blank or not."""
    return re.match(r"^[\s]*$", line)


def load(reader):
    """Load a text reader (hopefully an spr file) into the interpreter."""
    txt = ""
    for line in reader:
        logger.debug("loading SPR: ")
        logger.debug("%s" % line)
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
    if re.findall("\.", module):
        root, name = module.split(".")
    else:
        root = module
        name = module
    sprname = name + ".spr"
    yname = name + ".yaml"
    logger.info("Import spr %s: %s" % (root, sprname))

    try:
        init = pkgutil.get_data(root, sprname).decode("utf-8").split("\n")
        load(init)
    except Exception:
        pass

    try:
        merge_pkg_yaml(module, yname)
    except Exception:
        pass


def namespace(name, docstr, module, *funclist):
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


def _import_(module, *funclist):
    """import functions from a python module into the current namespace."""
    global NS
    if NS == Root:
        append_funcs(NS, module, *funclist)
    else:
        append_funcs(NS["symbols"], module, *funclist)

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
    if not callable(f):
        return None, 0, False, 0

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
        if sig:
            st[name] = dict(
                fn=function,
                signature=sig,
                nargs=nargs,
                vargs=vargs,
                def_index=def_index,
                doc=helptext,
                stype="fptr",
            )


def _def_(name, helpstr, commandstr):
    """define a new symbol which is a 'dolist' of other symbols.
    example: def hello-world \"My help text\" ui/msg \"hello world\" """
    _def_symbol(name, helpstr, commandstr, stype="dolist")


def partial(name, helpstr, commandstr):
    """define a new function from an fptr function which has some
    of it's arguments filled in.

    partial get-bar-code-from 'helptxt' set-in-from barQR value from:

    will create a new function get-bar-code-from that takes a value vector
    just like set-in-from would. Because it is."""
    _def_symbol(name, helpstr, commandstr, stype="partial")


def _def_symbol(name, helpstr, commandstr, stype="dolist"):
    """Define a new symbol in the symbol table of the current namespace."""
    global NS
    global Current_NS
    logging.debug(
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


def fptr_sig(k, v):
    if "signature" in v.keys():
        return "%s%s" % (k, v["signature"])
    else:
        return k


def fptr_help(k, v, indent=False):
    """Format an fptr symbol's help."""
    sig = fptr_sig(k, v)
    indention = ""
    if indent:
        indention = "    "

    print("\n%s%-20s" % (indention, sig))
    print("%s----------------\n%s%s" % (indention, indention, v["doc"]))


def all_dolist_help(st):
    """give the doc and source for all the compound symbols."""
    if len(st.items()) > 0:
        for k, v in sorted(st.items()):
            dolist_help(k, v)


def dolist_help(k, v):
    """Format an dolist symbol's help."""
    if isstype(v, "dolist") or isstype(v, "partial"):
        print("\n {0[0]:20}\n--------------\n{0[1]}".format([k, v["doc"]]))
        print("    Type: %s" % v["stype"])
        print("    Source: [%s]\n" % v["fn"])
    if isstype(v, "partial"):
        print("  --- Derived from: ---")
        func_name = v["fn"].split(" ")[0]
        s = _get_symbol(func_name)
        fptr_help(func_name, s, indent=True)


def namespace_help(key, ns):
    """Format an namespace symbol's help."""
    print("\n\nNamespace: %s\n   Module: %s\n    %s\n\n" % (key, ns["name"], ns["doc"]))
    try:
        eval_cmd("%s/help" % key)
    except Exception:
        pass
    all_fptr_help(ns["symbols"])
    all_dolist_help(ns["symbols"])


def list_namespace():
    """List the non namespace stuff in the Root namespace."""
    print("\n Root Namespace: ")
    for k, v in sorted(Root.items()):
        if not isstype(v, "namespace"):
            print("   %s" % k)


def ns_tree():
    """List the namespaces and all of their symbols """
    list_namespace()
    print("\n")
    for k, v in sorted(Root.items()):
        if isstype(v, "namespace"):
            printns(k, v)
            for j, z in sorted(v["symbols"].items()):
                print("   %s" % j)


def printns(k, v):
    print(
        "\n%-10s %20s: \n---------------------------------------------\n%s"
        % (k, v["name"], v["doc"])
    )


def printns_syms(ns):
    for k, symbol in sorted(ns["symbols"].items()):
        print_sym(k, symbol)


def get_parent_symbol(symbol):
    """get the symbol this symbol is derived from"""
    func_name = symbol["fn"].split(" ")[0]
    s = _get_symbol(func_name)
    return func_name, _get_symbol(func_name)


def print_sym(k, symbol):
    """Print a symbols signature."""
    sig = fptr_sig(k, symbol)

    if isstype(symbol, "namespace"):
        print("   %-15s -->  %-30s %-30s" % (sig, symbol["name"], symbol["doc"]))

    if isstype(symbol, "partial"):
        parent_name, parent = get_parent_symbol(symbol)
        print("   %-30s  Partial -->  %-20s" % (sig, fptr_sig(parent_name, parent)))

    if isstype(symbol, "dolist"):
        print("   %-30s  Do List -->  %-20s" % (sig, symbol["fn"]))

    if isstype(symbol, "fptr"):
        print("   %-30s" % sig)


def ls(ns=None):
    """
    List the name spaces, the contents of a namespace.
    Or the contents of the Application state at value vector given
    in the form of a pathname starting with a '/'

    ls - list all symbols in the root namespace.
    ls foo - list all the symbols in the foo namespace
    ls / - show the symbols tree in the root of the Application State
    ls /bar-QR - show the symbol tree from the /bar-QR node of the Application State
    ls /bar-QR/qrcode - show the symbol tree from the /bar-QR node of the Application State
    """
    if ns is None:
        ns = Root
        print("Namespaces:")
        for k, v in sorted(ns.items()):
            if isstype(v, "namespace"):
                print_sym(k, v)
                # printns(k, v)

        print("\nFunctions:")
        for k, v in sorted(ns.items()):
            if not isstype(v, "namespace"):
                print_sym(k, v)
    else:
        if ns[0] == "/":
            if len(ns) == 1:
                keys = get_keys_in()
            else:
                vv = ns[1:].split("/")
                keys = get_keys_in(*vv)

            for k in keys:
                print("    %-30s" % k)
        else:
            s = get_symbol(ns)
            if isstype(s, "namespace"):
                printns(ns, s)
                printns_syms(s)


def helpful_cmds():
    """Print a list of helpful commands"""
    t = """
    Useful Commands: ls, help, pyhelp, show

    If the prescribed coding patterns for SPR extensions are adhered to:
    * `ls` to list the contents of the Root, '/',  Namespace.
    * `ls /` to list the contents of the Root, '/',  of the Application state.
    * `ls <ns>` to see a summary of a namespace.
    * `ls /path/to/something` to see a list of keys at that location in the Application State.
    * `help` to get a summary.
    * `help /` to get help for the root namespace.
    * `help <ns>` to get help for a namespace.
    * `help <ns>/<function>` to get help for a function in the namespace.

    * `pyhelp <ns>` to get python help for a namespace.
    * `pyhelp <ns>/<function>` to get python help for a function in the namespace.

    * `showin <ns>` to see the Stateful Data used by the namespace.
    * `showin config <ns>` to see the configuration data used by the namespace

    * `browse-doc`  To read the README.md in your browser.
    * `view-doc`  To read the README.md in an HTML viewer.
    """
    print(t)


def _help_(args=None):
    """
    This is the SPR help, Additionally there is also the builtin
    python help which can be accessed with the pyhelp command.
    The two help systems show different information, all of which is
    quite useful.

    Help understands SPR symbols and their origins, so it can display
    different and additional information about SPR than the python help.

    Help can be used on namespaces and functions.  All of the following
    Will give help in more and more specific ways.

     * help
     * help /
     * help nw
     * help nw/connect-wifi

    """
    global Root
    application_help()
    sym = args
    print("\nSPR Help\n=============================================")
    if args is None:  # or len(args) == 0:
        helpful_cmds()
        print("=============================================")
        print("All Symbols in the Root / namespace")
        ls()
    elif args == "/":
        all_fptr_help(Root)
        all_dolist_help(Root)
        print("=============================================")

    else:
        # for sym in args:
        # logger.info("Sym in args: " % (sym, args))
        if sym[0] == "/":
            sym = sym[1:]
        s = _get_symbol(sym)
        if isstype(s, "namespace"):
            namespace_help(sym, s)
        if isstype(s, ["dolist", "partial"]):
            dolist_help(sym, s)
        if isstype(s, ["fptr", "voidfptr"]):
            fptr_help(sym, s)


def _pyhelp_(args=None):
    """
    This is the interactive python help, Additionally there is also the builtin
    SPR help which can be accessed with the help command.
    The two help systems show different information, all of which is
    quite useful.

    pyHelp understands Python modules and doc strings and can therefore
    provide nicely formated python level help for all SPR functionality.

    It does also know how to show the documentation for the underlying
    python functions which are used by SPR's partials.

    pyHelp can be used on namespaces and functions.  All of the following
    Will give help in more and more specific ways.

     * pyhelp
     * pyhelp nw
     * pyhelp nw/connect-wifi
    """

    global Root
    application_help()

    sym = args
    helpful_cmds()
    if args is None:  # or len(args) == 0:
        print("\nSPR Help\n=============================================")
        # all_fptr_help(Root)
        # all_dolist_help(Root)
        helpful_cmds()
        print("=============================================")
        print("All Symbols in the Root / namespace")
        ls()

    else:
        # for sym in args:
        # logger.info("Sym in args: " % (sym, args))
        s = _get_symbol(sym)
        logger.info("Sym : %s" % s)
        if isstype(s, "namespace"):
            pydoc.help(s["name"])
        if isstype(s, "partial"):
            n, s = get_parent_symbol(s)
            pydoc.help(s["fn"])
        if isstype(s, "dolist"):
            dolist_help(sym, s)
        if isstype(s, ["fptr", "voidfptr"]):
            pydoc.help(s["fn"])


def application_help():
    """Print help as defined by the function set in ['exec', 'help']
    in the config. This is a help function as defined by the
    application layer, which is specific to the functionality
    that we are interfacing with.
    """
    helpfn = get_in_config(["exec", "help"])
    if helpfn:
        eval_cmd(get_in_config(["exec", "help"]))


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

    # logging.debug("do fptrs: %s" % command)
    # logging.debug("full: %s" % commands)
    # logging.debug("fptr: %s" % str(fptr))

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

    # oy. je n'aime pas des exceptions
    if command == "-def-" or command == "partial":
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
    It's either a partial, a command with
    arguments or a list of commands.
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
    helpful_cmds()


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


def load_file(filename):
    """load an SPR file into the application."""
    with open(filename, "r") as reader:
        load(reader)


def _quit_():
    shutdown_hook = get_in(["config", "exec", "hooks", "shutdown"])
    if shutdown_hook:
        eval_cmds(shutdown_hook)
    exit()


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
            print("")
            line = input(prompt)
            if len(line):
                eval_list(parse(line))
        except Exception as e:
            logger.error(e)
