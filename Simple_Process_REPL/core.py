from sys import exit
import os
import time
import logging
import Simple_Process_REPL.logs as logs
import Simple_Process_REPL.repl as r

import Simple_Process_REPL.appstate as A
import Simple_Process_REPL.device as device
import Simple_Process_REPL.subcmd as S
import Simple_Process_REPL.dialog_cli as D
import Simple_Process_REPL.network as N
import Simple_Process_REPL.bar_qr as bq

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


# define all the symbols for the things we want to do.
_symbols = [
    ["hello", D.hello, "Hello message."],
    # beginning of local functions.
    ["wifi", N.connect_wifi, "Connect to wifi using nmtui if not connected."],
    ["connect_tunnel", N.connect_tunnel, "Connect through an ssh tunnel."],
    ["create_tunnel", N.create_tunnel, "Create an ssh tunnel."],
    [
        "reset-device",
        A.reset_device,
        "Reset the application state with an empty device.",
    ],
    ["wait", device.wait, "Wait for the usb device to come back."],
    [
        "handshake",
        device.handshake,
        "Look for the test start string, send the response, catch results.",
    ],
    ["pause", device.pause_a_sec, ("Pause/Sleep for 'pause_time' seconds")],
    ["run", A.eval_default_process, "Run the default process command."],
    [
        "sync-funcs",
        A.sync_functions,
        "Copy the functions from the REPL into the state, automatic w/save.",
    ],
    # dialog functions
    ["dialog-start", D.dialog_start, "Dialog, for ready to start ?"],
    ["dialog-test", D.dialog_test, "Dialog, ready to test ?"],
    ["dialog-flash", D.dialog_flash, "Dialog, ready to flash ?"],
    ["dialog-failed", D.dialog_failed, "Dialog, ready to flash ?"],
    ["dialog-finish", D.dialog_finish, "Dialog, Unplug, power off."],
    ["cli-start", D.cli_start, "Dialog, for ready to start ?"],
    ["cli-test", D.cli_test, "Dialog, ready to test ?"],
    ["cli-flash", D.cli_flash, "Dialog, ready to flash ?"],
    ["cli-failed", D.cli_failed, "Dialog, ready to flash ?"],
    ["cli-finish", D.cli_finish, "Dialog, Turn out the lights, Unplug, power off."],
    [
        "save-bcqr",
        D.save_bcqr,
        "Dialog to print the current barQR value as a QR code or barcode.",
    ],
    [
        "print-bcqr",
        D.print_bcqr,
        "Dialog to print the current barQR value as a QR code or barcode.",
    ],
    ["help", D.help, "Repl help, list symbols and their help."],
    ["quit", exit, "Quit"],
]

# Name, function, number of args, help string
# Commands we want in the repl which can take arguments.
_specials = [
    ["save-config", A.save_config, 1, "Save the configuration; save-config filename"],
    ["load-config", A.load_config, 1, "Load a configuration; save-config filename"],
    ["msgbox", D.msgbox, 1, 'Give a dialog message box; msgbox "some message"'],
    [
        "msgcli",
        D.msgcli,
        1,
        'Give a message to continue at the command line; msgbox "some message"',
    ],
    [
        "loglvl",
        logs.log_lvl,
        1,
        "Change the logging level; loglvl <debug|info|warning|error|critical>",
    ],
    ["log_info", logging.info, 1, 'Send a messag to logging; log_info "some message"'],
    [
        "log_debug",
        logging.debug,
        1,
        'Send a debug message to logging log_debug "some debug message"',
    ],
    [
        "showin",
        A.showin,
        -1,
        "Show the value in the Application state; showin config files",
    ],
    [
        "set-in",
        A.set_in,
        -1,
        "Set a value vector in the application state; setin foo bar 10",
    ],
    [
        "input-string-to",
        D.input_string_to,
        -1,
        'prompt for an input and set it to the value vector; input_string_to "some msg" "device" "serial_number"',
    ],
    [
        "input-count-to",
        D.input_count_to,
        -1,
        'prompt for an integer input and set it to the value vector; input_count_to "some msg" "device" "serial_number"',
    ],
    [
        "set-bcqr-from",
        bq.set_bcqr_from,
        -1,
        "Set the barQR value to the value at the value vector given; set-bcqr-from device serial_number",
    ],
    [
        "get-bcqr",
        bq.get_bcqr,
        1,
        "load a barcode or QR code for the current value; get-bcqr barcode",
    ],
    [
        "save-bcqr",
        bq.save_bcqr,
        1,
        "save the current barcode or QR code to a file; save-bcqr barcode",
    ],
    [
        "print-bcqr",
        bq.print_bcqr,
        1,
        "print the current barcode or QR code file; print-bcqr barcode",
    ],
    ["print-file", D.print_file, 1, "Print a file; print-file foo.txt"],
    [
        "print-file-loop",
        D.print_file_loop,
        1,
        "Print a file more than once; print-file-loop foo.txt",
    ],
    [
        "print-file-from",
        D.print_file_from,
        -1,
        "Print a file using the string stored at the value vector; print-file-from barQR QR_code saved",
    ],
    [
        "print-file-loop-from",
        D.print_file_loop_from,
        -1,
        "Print a file more than once, using the string stored at the value vector; print-file-loop-from barQR QR_code saved",
    ],
    ["rm-file", os.remove, 1, "Remove a file; rm-file foo.txt"],
    ["_archive-log", A.archive_log, 1, "Archive the logfile."],
    ["sleep", time.sleep, 1, "Sleep for specified seconds; sleep 5"],
    ["sh", S.do_shell, -1, "Run a shell command; sh ls -l"],
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
            r.eval_cmd(commands)

        D.dialog_finish()

    except Exception as e:
        logger.error("Device Failed")
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

    commands = " ".join(A.get_in(["args", "commands"]))

    # Run the repl.
    if A.get_in(["args", "repl"]):
        r.repl(A.get_in_config(["REPL", "prompt"]))

    # if there aren't any commands on the cli
    # do the auto exec in a loop or once.
    elif len(commands) == 0:
        if A.get_in(["args", "interactive"]) is True:
            interactive_loop()
        else:
            do_one()

    # run the commands given on the cli.
    else:
        logger.info("Attempting to do this: %s", commands)
        if A.get_in(["args", "interactive"]) is True:
            interactive_loop(commands)
        else:
            r.eval_cmd(commands)


logger = logs.setup_logger()


def init(symbols, specials, parser):
    """
    Parse the cli parameters,
    load the default config or the configuration given,
    start logging,
    initialize the symbol tables for the interpreter.
    Finally, run in whatever mode we were told.
    """
    A.init(parser)

    logs.add_file_handler(
        logger,
        A.get_in_config(["files", "loglevel"]),
        A.get_in_config(["files", "logfile"]),
    )

    logger.info("Hello there, ready to go.")

    A.load_functions()

    r.init(_symbols, _specials)
    r.init(symbols, specials)

    do_something()
