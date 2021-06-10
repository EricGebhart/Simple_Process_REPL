import sys
import traceback
import pydoc
import pkgutil
import readline
import logging
import regex as re
import os
import atexit
import code
from sys import exit
from inspect import signature, _empty
from Simple_Process_REPL.appstate import (
    merge_yaml_with,
    merge_pkg_yaml,
    _full_with_path,
    select_with,
    push,
    get,
    _set_in,
    get_in,
    get_from_path,
    get_in_config,
    get_keys_in,
    show,
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
            # logger.info("Not str: %s" % str(fname))
            return
        else:
            f = getattr(lib, fname)

        # figure out if it's a var args [a*], or an [a b c*] varargs.
        # and how many args. Just to be nice and check later.
        # also stash the parameters in case do_fptrs() wants to get fancy.
        signature, nargs, vargs, def_index, parms, sigmap = get_fsig(f)

        name = fname.replace("_", "-")  # cause I don't like hitting shift.

        st[name] = dict(
            fn=f,
            doc=f.__doc__,
            signature=signature,
            pkeys=parms,
            sigmap=sigmap,
            nargs=nargs,
            vargs=vargs,
            def_index=def_index,
            stype="fptr",
        )

    return st


def is_blank_line(line):
    """test if text is blank or not."""
    return re.match(r"^[\s]*$", line)


def inline_yaml(lines):
    """take an iterator and read until the end or two blank lines are encountered.
    Attempt to merge the resulting yaml and merge it into to yaml datastore."""
    yaml = ""
    blank_count = 0

    logger.info("loading inline Yaml:")

    while True:

        try:
            line = lines.__next__()
            logger.info("%s" % line.rstrip())
        except Exception:
            break

        if len(line) == 0 or is_blank_line(line):
            blank_count += 1
        else:
            blank_count = 0

        if blank_count == 2:
            break

        yaml += line + "\n"

    merge_yaml_with(yaml)
    return lines


def load(reader):
    """Load a text reader (hopefully an spr file) into the interpreter."""
    txt = ""
    lines = reader.__iter__()
    line = True
    logger.info("loading SPR:")

    while True:

        try:
            line = lines.__next__()
        except Exception:
            break

        if line and line[0] == "#":
            continue

        if line.strip() == "'":
            inline_yaml(lines)
            txt = ""
            continue

        else:
            if len(line) == 0 or is_blank_line(line):
                if len(txt) > 0:
                    eval_cmd(txt)
                    txt = ""
            else:
                # get rid of newlines so the interpreter
                # sees a continuous line.
                logger.info("%s" % line)
                txt += re.sub("\n", " ", line)

    if len(txt) > 0:
        eval_cmd(txt)


def import_lib_spr(module):
    """Look for spr and yaml files within the python module which are
    named after the module. Load them in the current namespace if found."""
    if re.findall("\.", module):
        root, name = module.split(".")
    else:
        root = module
        name = module
    sprname = name + ".spr"
    yname = name + ".yaml"
    logger.info("\nImport spr %s: %s" % (root, sprname))

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
    """
    Create a name space with name. From the python module, import the functions listed.
    Will also import any spr or yaml files found within the module having the
    same name as the module. As per the import_lib_spr function.
    """
    global Root
    logger.info("\nCreating Namespace: %s from Python module: %s" % (name, module))
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
    """import functions from a python module into the current namespace.
    Then import the module's yaml and spr files if found.

    A complete python-SPR module 'foo' would have a foo.py, foo.spr,
    and possibly a foo.yaml.
    """
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
    """Change into a namespace."""
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
    Given a list of symbols, add them to the symbol table given.
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


def get_fsig_map(parameters):
    """Create a map of parameters with their default values."""
    res = {}
    count = 0
    for k in parameters.keys():
        count += 1
        p = parameters[k]
        v = p.default
        if v == _empty:
            v = None
        res[p.name] = v

    return res


def get_fsig(f):
    if not callable(f):
        return None, 0, False, 0, []

    sig = signature(f)
    parameters = sig.parameters
    nargs = len(parameters)
    pkeys = []
    sigmap = {}
    varargs = False
    def_index = 0
    if nargs > 0:
        pkeys = parameters.keys()
        sigmap = get_fsig_map(parameters)
        last_arg_key = list(pkeys)[nargs - 1]
        last_arg_kind = parameters[last_arg_key].kind.name
        varargs = last_arg_kind in ["VAR_POSITIONAL", "VAR_KEYWORD"]
        def_index = find_first_parameter_with_default(parameters)
    return str(sig), nargs, varargs, def_index, pkeys, sigmap


def append_specials(st, slist):
    """Given a symbol table and a list of specials append them to the
    symbol table. each symbol should be in the form of
    ['name', function | str, nargs, 'help string']
    """
    for name, function, nargs, helptext in slist:
        sig, nargs, vargs, def_index, parms, sigmap = get_fsig(function)
        if sig:
            st[name] = dict(
                fn=function,
                signature=sig,
                pkeys=parms,
                sigmap=sigmap,
                nargs=nargs,
                vargs=vargs,
                def_index=def_index,
                doc=helptext,
                stype="fptr",
            )


def _def_(name, helpstr, commandstr):
    """define a new symbol which is a 'dolist' of other symbols.
    example: def hello-world \"My help text\" ui/msg \"hello world\" """
    stype = "dolist"
    if commandstr[0] == "/":
        stype = "path"
    _def_symbol(name, helpstr, commandstr, stype=stype)


def _def_path(name, helpstr, commandstr):
    """define a new symbol which is a 'path' to another place.
    absolute path;
    example: def mybaz \"My baz path\" /foo/baz

    Relative path to with;
    def mybaz \"My baz path\" foo/baz"""
    stype = "path"

    # if commandstr[0] != "/":
    #     commandstr = _full_with_path(commandstr)

    _def_symbol(name, helpstr, commandstr, stype=stype)


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

    if isinstance(s, str):
        n, namespace = get_ns(s)
        # logger.info("n and n: %s %s" % (n, namespace))
        if namespace is not None:
            symbol = namespace["symbols"].get(n)
        elif Root[s]:
            symbol = Root[s]
        else:
            # get it from the appstate if we can.
            symbol = get(s)
    else:
        symbol = None

    logger.debug("Got Symbol: %s" % symbol)

    return symbol


def get_symbol(s):
    "Try to get a symbol's definition."
    try:
        symbol = _get_symbol(s)
    except Exception:
        symbol = None

    if symbol is None:
        logger.error("Unkown Symbol: %s" % s)

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
    print("\n%sSignature Map: %-40s" % (indention, v["sigmap"]))
    print("%s----------------\n%s%s" % (indention, indention, v["doc"]))


def all_dolist_help(st):
    """give the doc and source for all the compound symbols."""
    if len(st.items()) > 0:
        for k, v in sorted(st.items()):
            dolist_help(k, v)


def dolist_help(k, v):
    """Format an dolist symbol's help."""
    if isstype(v, "dolist") or isstype(v, "partial") or isstype(v, "path"):
        print("\n {0[0]:20}\n--------------\n{0[1]}".format([k, v["doc"]]))
        print("    Type: %s" % v["stype"])

    if isstype(v, "path"):
        print("    Path: [%s]\n" % v["fn"])

    if isstype(v, "fptr"):
        fptr_help(k, v)

    if isstype(v, "partial"):
        print("    Source: [%s]\n" % v["fn"])
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

    if isstype(symbol, "path"):
        print("   %-30s  Path -->  %-20s" % (sig, symbol["fn"]))

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


def help_summary():
    """help"""
    t = """Initially this was a simple alias to wrapped python functions. Such that
    functions would be called sequentially entirely for their side effects which
    would compound into a complete system.

    Start with a configuration and clean system, accumulate information and data,
    do whatever. do it again. or do it once, or do a part of it, etc.

    A different job/application only needs a different configuration file and maybe
    some spr code. Depending on the complexity, maybe an spr/python extension.

    There is an Application datastore which is built from yaml config files
    as well as by spr code within spr extensions.

    An spr extension is not always needed, but provides a mechanism for importing
    yaml data and spr code in conjunction of python code. An spr extension is a standard
    python/pip type module with spr and yaml included. A template project can be created
    with the `new_spr_extension_project` command.

    This language, if you can call it that, has almost no syntax. words, double quoted
    strings and numbers are it. It has no stack, no scope, no variables exactly.
    Because all of the data is initially yaml, There is the idea of paths to data,
    these look like unix paths. ie. /this/is/a/path/to/something.

    There is namespaces, but only one layer deep. Root, '/', has some basic commands,
    and the appstate module imported as 'as' has the rest of the most important commands.

    SPR does have a `with` stack, which can be pointed anywhere in the data store, and it
    understands yaml, so data manipulation within the datastore is very easy.

    The idea is to point at a place in the datastore tree, fill it with what you
    care about, let functions get their parameters from there and put their results
    on the results stack there. Move the results around as needed, push or pop a `with`,
    do another step, etc.  If anything fails, the process fails. Everything is logged.


    yaml can be entered like so.

    `'
     foo:
          bar: 10
          baz: 100
    `

    and will be merged into the application datastore at the location of the current
    `with`.

    as/-with foo
    '
    spam: Hello


    will put a spam entry into foo next to bar and baz.
    """
    print(t)


def helpful_cmds():
    """Print a list of helpful commands"""
    t = """
    The Simple Process REPL is a thin framework of configuration,
    datastore, and REPL.  It can import python modules and use them
    directly. Each module is usually associated with a namespace upon
    import.

    SPR's purpose is to make it easy to create simple application type processes
    which may interact with a user, other devices, or anything else.
    It should be simple to compose processes which are repeatable and consistent
    in behavior. It should also be easy to add new configuration options which can
    also be easily used and over-ridden.

    Python functions will bind to data in the `with` if they find what they want.

    Python functions are imported with namespace or import.
    Partial functions can be defined in spr code.
    Do List functions can be defined in spr code or in the configuration file.
    Datastore chunks can be defined in the configuration files, spr code, or in
    extension yaml files.



    Useful Commands: ls, help, pyhelp, show

    * `help` to get a summary.
    * `help /` to get help for the root namespace.
    * `help <ns>` to get help for a namespace.
    * `help <ns>/<function>` to get help for a function in a namespace.

    * `pyhelp <ns>` to get python help for a namespace.
    * `pyhelp <ns>/<function>` to get python help for a function in a namespace.

    * `ls` to list the contents of the Root, '/',  Namespace.
    * `ls <ns>` to see a summary of a namespace.

    / denotes a path into the application state datastore.
    * `ls /` to list the contents of the Root, '/',  of the application state.
    * `ls /path/to/something` to see a list of keys at that location in the Application State.

    * `show` to browse the Application State Data.
    * `show /path/to/something` to see the contents of the datastore tree at that location.

    By Convention;
    * `show <ns module>` to see the stateful data used by a namespace, if any.
    * `show config <ns module>` to see the configuration data used by the namespace

    * `browse-doc`  To read the README.md in your browser.
    * `view-doc`  To read the README.md in an HTML viewer - does not require internet.
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
        if isstype(s, ["dolist", "partial", "path"]):
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
        if isstype(s, "namespace"):
            pydoc.help(s["name"])
        if isstype(s, "partial"):
            n, s = get_parent_symbol(s)
            pydoc.help(s["fn"])
        if isstype(s, ["dolist", "path"]):
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


def isa_path(cmd):
    "Quietly determine if a symbol is a path"
    try:
        sym = _get_symbol(cmd)
        if not isstype(sym, "path"):
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


def _set_sig_map(symbol, path=None):
    """Get the signature map for a symbol/python function
    and set/merge it into the path given.

    If path is not specified, merges into the current with path.
    """
    fptr = isa_fptr(symbol)
    if fptr:
        sigmap = fptr["sigmap"]
        _set_in(sigmap, path)


def expand(commands):
    """Expand the arguments into their values as needed.
    So far this is just paths. With this, we have 'variables'.
    Path symbols expand to their value.

    Keeping it simple, one layer expansion, no recursion. It's enough
    to give dangerous power.
    """
    res = []
    for symbol in commands:
        path = isa_path(symbol)
        if path:
            logger.debug("Expand: %s" % path["fn"])
            v = get(path["fn"])
            if not isinstance(v, str):
                res += [v]
            else:
                res += v.split(" ")
        else:
            res += [symbol]

    logger.debug("Expand: %s" % res)
    return res


def resolve_vars(commands, start_index=1):
    """Big cheat, just gonna try to expand variables and see what happens.
    So yea, it works. Sorta. Too well. too much. Need a more real interpreter.
    on verra.
    """

    # if len(commands) > start_index:
    #     cmds = commands[:start_index]
    #     for symbol in commands[start_index:]:
    #         if isinstance(symbol, str):
    #             v = get(symbol)
    #             if v:
    #                 cmds += [v]
    #             cmds += [symbol]
    #         else:
    #             cmds += [symbol]
    #     commands = cmds

    return commands


# I think this function is too complicated. could be simpler. but it is
# working at the moment.
def do_fptrs(commands):
    """Call the fptr functions with their argument lists.
    Validates the number of arguments if possible. nargs=-1 is varible args.
    returns true if it was a special, false if not, even if it fails.

    This get's the first shot. if the first token isn't an fptr, then it goes
    on to be evaluated elsewhere.
    """

    result = None
    command = commands[0]

    # logging.debug("do fptrs: %s" % command)
    # logging.debug("do fptrs: %s" % command)
    # logging.debug("full: %s" % commands)
    # # logging.debug("fptr: %s" % str(fptr))

    fptr = isa_fptr(command)

    if fptr is None:
        return False

    # logging.info("keys: %s" % str(special.keys()))
    # # logging.debug("nargs: %s" % str(special['nargs']))

    # Such a mess. This needs to be fixed so it uses args and kwargs,
    #  goes hand in hand with making with work.

    # logger.info("DO_FPTR %s" % fptr)
    fn = fptr["fn"]
    fnargs = fptr["nargs"]
    vargs = fptr["vargs"]
    def_index = fptr["def_index"]
    sig = fptr["signature"]
    nargs = len(commands) - 1
    pkeys = fptr["pkeys"]

    # logger.info("do-fptrs: %d, %s" % (nargs, commands))

    # logger.info("args: %s" % args)

    # logger.info("Fptr: %s\nNargs: %d\nVargs: %d\nSig: %s" % (fptr, nargs, vargs, sig))
    # logger.info(
    #     "Command: %s - %s %s\n argcount: %d prms: %d varargs: %d"
    #     % (command, fn, sig, fnargs, nargs, vargs)
    # )

    # oy. je n'aime pas des exceptions
    if command == "-def-" or command == "partial":
        # commands = resolve_vars(commands, start_index=2)
        commandstr = " ".join(commands[3:])
        fn(commands[1], commands[2], commandstr)
        return True

    # oy. je n'aime pas des exceptions
    if command == "as/set":
        # noop ? - yes
        # commands = resolve_vars(commands, start_index=2)
        fn(commands[1], commands[2:])
        return True

    # noop ? - yes
    # commands = resolve_vars(commands, start_index=1)

    try:
        if fnargs == 0 and nargs == 0:
            result = fn()

        elif vargs:

            args = commands[1:fnargs]
            args += [commands[fnargs:]]
            result = fn(*args)

        # elif nargs <= fnargs and nargs >= def_index - 1:
        else:

            args = dict(zip(pkeys, commands[1:]))
            with_vars = select_with(list(pkeys)[nargs:])

            try:
                args = dict(zip(pkeys, commands[1:]))
                if with_vars and nargs < fnargs:
                    args.update(with_vars)

            except Exception as e:
                print(e)

            result = fn(**args)

            if result is not None:
                push("results", result)

    except Exception as e:
        logger.error(commands)
        print(e)
        # traceback.print_exception(*sys.exc_info())

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

    try:
        symbol = get_symbol(s)
        if symbol is not None:
            function = symbol["fn"]

            # its a string of symbols.
            if isinstance(function, str):
                eval_list(parse(function))
            else:
                function()
    except Exception:
        pass


def eval_list(commands):
    """Execute a list from the symbol table.
    It's either a partial, a command with
    arguments or a list of commands.
    """
    logger.debug("eval list: %s" % commands)

    # we have function pointers sort-of by having this here.
    # if you put a symbol name for something in the yaml
    # and a path symbol that points at it....
    commands = expand(commands[0:])

    # logger.info(commands)
    # if it's a partial expand it.
    first_sym = _get_symbol(commands[0])

    if first_sym is None:
        logger.error("Unkown Symbol: %s" % commands[0])
        return False

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
    """Evaluate a command list."""
    for c in commands:
        eval_list(parse(c))


def eval(path):
    """Evaluate a list of symbols, from a path, if what is held there is
    a string, then evaluate it.
    If it is a list evaluate each entry in turn.

    ```
    set mymessage cli/msg "hello there"

    eval mymessage
    ```

    An example using 'with' to construct a list of commands.

    ```
    with my/func/of/stuff

    '
    - cli/msg hello
    - cli/msg goodbye

    pop-with
    eval /my/func/of/stuff

    def myfunc "My function that does more than one thing." eval /my/func/of/stuff
    ```
    """
    v = get(path)
    if isinstance(v, list):
        eval_cmds(v)
    else:
        eval_cmd(v)


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
    logger.info("Loading SPR file: %s" % filename)
    with open(filename, "r") as reader:
        load(reader)


def _quit_():
    shutdown_hook = get_in(["config", "exec", "hooks", "shutdown"])
    if shutdown_hook:
        eval_cmds(shutdown_hook)
    exit()


def yaml_parse():
    yaml = ""
    while True:
        try:
            line = input("YAML...>")
            if len(line):
                yaml += line + "\n"
            else:
                break
        except Exception as e:
            logger.error(e)
    merge_yaml_with(yaml)
    return


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
            if line and line[0] == "#":
                continue
            if line == "'":
                yaml_parse()
            else:
                if len(line):
                    eval_list(parse(line))

        except Exception as e:
            print(e)
