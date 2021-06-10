import pkgutil

# import logging
import Simple_Process_REPL.logs as logs
import Simple_Process_REPL.repl as r
import Simple_Process_REPL.appstate as A

import Simple_Process_REPL.dialog as D

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


# endless loop with dialog next y/n.
def interactive_loop(commands=None):
    """Execute the autoexec command in an interactive
    loop which reports failures and prompts to do another.
    """
    interactive = A.get_in(["args", "interactive"])
    while interactive is True:
        try:
            do_one(commands)
            if D.continue_to_next():
                interactive = False
        except Exception as e:
            logger.error(e)
            if D.continue_to_next():
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

        D.finish()

    except Exception as e:
        logger.error("Process Failed")
        logger.error(e)
        D.failed()
        D.finish()


def do_something():
    """
    Get the startup and shutdown hooks from the config.
    load :
        core.spr
        startup hook
        Load/run a file if given on the cli with -f

    Maybe:
      Start the REPL and run the commands given on the cli.
      Loop over something, the cli commands or the autoexec.
      Do something one time. the cli commands or the autoexec,
    """

    try:
        r.load(pkgutil.get_data(__name__, "core.spr").decode("utf-8").split("\n"))
    except Exception as e:
        logger.error(e)

    commands = A.get_in(["args", "commands"])

    # Each of these should be a list of commands to execute.
    startup_hook = A.get_in(["config", "exec", "hooks", "startup"])

    logger.debug("startup hook: %s", startup_hook)

    if startup_hook:
        r.eval_cmds(startup_hook)

    # Load a file if we got one.
    sprfile = A.get_in(["args", "file"])

    if sprfile:
        try:
            r.load_file(sprfile)
        except Exception as e:
            logger.error(e)

    # Maybe Run the repl.
    if A.get_in(["args", "repl"]):
        r.repl(A.get_in_config(["REPL", "prompt"]), None)

    # or run in a loop
    elif A.get_in(["args", "interactive"]) is True:
        interactive_loop(commands)

    else:
        do_one(commands)


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
    A._set_({"_Root_": r.Root})
    # Need to revisit. Be nice if it worked.
    # A._set_({"_Current_NS_": r.Current_NS})

    # Add fundamental commands to the root level of the interpreter.
    r._import_(
        "Simple_Process_REPL.repl",
        [
            "ns",
            "ls",
            "ns_tree",
            "_help_",
            "_pyhelp_",
            "_def_",
            "_def_path",
            "_import_",
            "partial",
            "in_ns",
            "namespace",
            "load_file",
            "_quit_",
            "eval",
            "_set_sig_map",
        ],
    )

    # define all the symbols for the things we want to do.
    # r.root_symbols(_symbols, _specials)
    r.root_symbols(symbols, specials)

    do_something()
