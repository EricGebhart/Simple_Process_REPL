from sys import exit

# import logging
import Simple_Process_REPL.logs as logs
import Simple_Process_REPL.repl as r
import Simple_Process_REPL.appstate as A

# from Simple_Process_REPL.device import device
# from Simple_Process_REPL.subcmd import subcmd
import Simple_Process_REPL.dialog_cli as D

# from Simple_Process_REPL.network import network
# from Simple_Process_REPL.bar_qr import bar_qr

"""
This file defines the symbol table for the interpreter,
initializes the application, and then runs in the requested manner.

The repl allows for the creation of new function/commands interactively.
Those functions can then be saved as part of the configuration or separately.

The process to be run automatically should be a function in the symbol table
By default, or if not found, the 'hello' function is used.
The autoexec attribute in the configuration names the command(s) to run when
running in a loop or one time with no commands.
"""

logger = logs.setup_logger()

Libs = []


# define all the symbols for the things we want to do.
_symbols = [
    ["ls-ns", r.list_namespaces, "list namespaces."],
    ["ns-tree", r.list_namespace_tree, "list the namespaces and their symbols."],
    ["quit", exit, "Quit"],
]

# Name, function, number of args, help string
# Commands we want in the repl which can take arguments.
_specials = [
    [
        "help",
        r.help,
        -1,
        "Get help for all, or a namespace or function; help <name>",
    ],
    [
        "def",
        r.def_symbol,
        -1,
        "Define a new function; def <name> 'helpstr' <list of commands>",
    ],
    [
        "import",
        r.import_lib,
        -1,
        "Import a python library into the current namespace.; import spam.ham ham eggs",
    ],
    [
        "partial",
        r.def_partial,
        -1,
        "Define a new partial function; def <name> 'helpstr' <list of partial command>",
    ],
    [
        "in-ns",
        r.in_ns,
        1,
        "change to a different namespace or '/'; in-ns <namespace>",
    ],
    [
        "namespace",
        r.create_namespace,
        -1,
        "Create a Namespace and import some python into it; namespace spam spam.ham ham eggs.",
    ],
]


# endless loop with dialog next y/n.
def interactive_loop(commands=None):
    """Execute the autoexec command in an interactive
    loop which reports failures and prompts to do another.
    """
    interactive = A.get_in(["args", "interactive"])
    while interactive is True:
        try:
            do_one(commands)
            if D.continue_to_next_dialog():
                interactive = False
        except Exception as e:
            logger.error(e)
            if D.continue_to_next_dialog():
                interactive = False
        A.reset_device()


def do_one(commands=None):
    """Execute the default process or the cli commands one time,
    with fail and finish dialogs"""
    try:
        if commands is None:
            A.eval_default_process()
        else:
            r.eval_cmds(commands)

        D.dialog_finish()

    except Exception as e:
        logger.error("Process Failed")
        logger.error(e)
        D.dialog_failed()
        D.dialog_finish()


def do_something():
    """
    Maybe start the REPL,
    or Run the autoexec in a loop,
    or Run the autoexec once,
    or Run commands given on the cli.
    """

    commands = A.get_in(["args", "commands"])

    # Each of these should be a list of commands to execute.
    startup_hook = []
    shutdown_hook = []
    startup_hook = A.get_in(["config", "exec", "hooks", "startup"])
    shutdown_hook = A.get_in(["config", "exec", "hooks", "startup"])

    if len(commands) > 0:
        startup_hook += [" ".join(commands)]

    logger.debug("startup hook: %s", startup_hook)

    # Run the repl.
    if A.get_in(["args", "repl"]):
        r.repl(A.get_in_config(["REPL", "prompt"]), startup_hook)

    if A.get_in(["args", "interactive"]) is True:
        interactive_loop(startup_hook)
    else:
        r.eval_cmds(startup_hook)

    r.eval_cmds(shutdown_hook)


def init(symbols, specials, parser):
    """
    Parse the cli parameters,
    load the default config or the configuration given,
    start logging,
    initialize the symbol tables for the interpreter.
    Finally, run in whatever mode we were told.
    """
    A.init(parser, logger)
    # make the symbol table available in the App State.
    A.set({"_Root_": r.Root})

    # Add fundamental commands to the root level of the interpreter.
    r.root_symbols(_symbols, _specials)
    r.root_symbols(symbols, specials)

    do_something()
