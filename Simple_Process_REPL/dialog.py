import os
from dialog import Dialog
import logging
import traceback

import regex as re
import Simple_Process_REPL.repl as r
import Simple_Process_REPL.appstate as A
import Simple_Process_REPL.bar_qr as bq
import Simple_Process_REPL.utils as u

logger = logging.getLogger()

# set up the dialog interface
d = Dialog(dialog="dialog")
inputbox = d.inputbox

yaml = u.dump_pkg_yaml("Simple_Process_REPL", "dialog.yaml")
# format and fill in as you wish.
HelpText = (
    """
dialog: An interface to the python dialog library.

This module provides dialog windows for various purposes.

There is currently no stateful data.

    %s

dialog is an old curses library written in C used for simple dialogs.
"""
    % yaml
)


def help():
    print(HelpText)


def hello():
    "Just in case we don't know what to do."
    msg(A.get_in_config(["dialogs", "hellomsg"]))


def input_string(msg):
    """Get a string input"""
    code, res = inputbox(
        msg,
        title=A.get_in_config(["dialogs", "title"]),
        height=10,
        width=50,
    )
    return res


def input_count(msg):
    """Give an input dialog that insists on an integer input.
    A range box could work, but seemed cumbersome."""
    while True:
        code, res = inputbox(
            msg,
            title=A.get_in_config(["dialogs", "title"]),
            height=10,
            width=50,
        )
        try:
            res = int(res)
        except Exception:
            msg("count must be an integer")
            continue
        break
    return res


def _input_count_to(msg, keys):
    """Dialog to get a string and set it in the Application state with a value vector."""
    v = keys + [input_count(msg)]
    A.set_in(v)


def _input_string_to(msg, keys):
    """Dialog to get a string and set it in the Application state with a value vector."""
    v = keys + [input_string(msg)]
    A.set_in(v)


def input_string_to(v):
    """varargs version of _input_string_to which takes a vector,
    the first entry should be a string which will be displayed in the dialog window.
    The rest will be used as the value vector to set in the Application state."""
    _input_string_to(v[0], v[1:])


def input_count_to(v):
    """varargs version of _input_count_to which takes a vector,
    the first entry should be a string which will be displayed in the dialog window.
    The rest will be used as the value vector to set in the Application state."""
    _input_count_to(v[0], v[1:])


def dialog_print(fname):
    """Dialog to ask which print command to use."""
    cmd_name, print_command = print_command_menu()
    command = print_command % fname
    return cmd_name, command


def dialog_print_loop(fname):
    """Dialog to ask which print command to use and how many times to print it."""
    cmd_name, command = dialog_print(fname)
    count = input_count("How many to Print ?")
    return cmd_name, command, count


def msg(text):
    "Display a simple message box, enter to continue."
    d.msgbox(
        text,
        title=A.get_in_config(["dialogs", "title"]),
        height=10,
        width=50,
    )
    os.system("clear")


def yes_no(msg):
    "Display a yesno dialog, return True or False."
    response = d.yesno(
        msg,
        title=A.get_in_config(["dialogs", "title"]),
        height=10,
        width=50,
    )
    os.system("clear")
    if response == "ok":
        return True
    else:
        return False


def radiolist(msg, choices):
    (code, tag) = d.radiolist(
        msg,
        width=50,
        title=A.get_in_config(["dialogs", "title"]),
        choices=choices,
    )
    return tag


def select_choice(msg, choices):
    logger.info("select choice: %s", choices)
    code, choice = d.menu(
        msg,
        title=A.get_in_config(["dialogs", "title"]),
        choices=choices,
        height=50,
        width=50,
    )
    os.system("clear")
    return choice


def print_command_menu():
    """Give a menu of possible print commands for the current platform"""
    p_dict = A.get_in_config(["print_commands", A.get_in(["platform"])])
    p_p_cmds = list(p_dict.items())

    rlist = [(key, "") for key, cmd in p_p_cmds]
    choice = select_choice("Which print command to use ?", rlist)
    return choice, p_dict[choice]


def BC_or_QR_menu():
    return select_choice(
        "Which would you like to print?",
        [
            ("Bar Code", ""),
            ("QR Code", ""),
        ],
    )


def BC_or_QR():
    """Dialog for Bar code or QR, normalized to Codetype."""
    label_type = BC_or_QR_menu()
    if label_type == "Bar Code":
        return BarCodeType
    elif label_type == "QR Code":
        return QRCodeType


def save_bcqr():
    """Ask which; Barcode or Qr code, then generate and save the png,
    return the filename."""
    codetype = BC_or_QR()
    bq.get_bcqr(codetype)
    return bq.save_bcqr(codetype)


def print_bcqr():
    """Dialogs to generate, save, and print any number of the current barQR
    value as a bar or QR code."""
    fn = bq.print_bcqr()
    print_file_loop(fn)


# has nothing to do with printing really.... Just the messages. -- Refactor.
def _print_file(fname, cmd_name, command, count=1):
    """Internal use. Display print messages and loop or not over a system command."""
    if count > 1:
        logger.info("Printing file %s, %d times, to %s" % (fname, count, cmd_name))
    else:
        logger.info("Printing file %s to %s" % (fname, cmd_name))

    if count > 1 and ynbox(
        "You are ready to print %d times to %s?" % (count, cmd_name)
    ):
        for i in range(0, count):
            os.system(command)
    else:
        os.system(command)


def print_file(fname):
    """Print a filename with a series of dialog prompts."""
    name, cmd = dialog_print(fname)
    _print_file(fname, name, cmd, 1)


def print_file_loop(fname):
    """Print a filename A number of times with a series of dialog prompts."""
    name, cmd, count = dialog_print_loop(fname)
    _print_file(fname, name, cmd, count)


def print_file_from(*keys):
    """Given a value vector, print the filename value held there."""
    print_file(A.get_in(keys[0]))


def print_file_loop_from(*keys):
    """Given a value vector, print the filename value held there, how ever many times they say."""
    print_file_loop(A.get_in(keys[0]))


def continue_to_next():
    "Do another one? Dialog. returns True/False"
    if yes_no(A.get_in_config(["dialogs", "start_again"])):
        logger.info("exiting")
        return False
    return True


def failed():
    """dialog: Process failed."""
    msg(A.get_in_config(["dialogs", "process_failed"]))


def start():
    """dialog: Plugin a board and start a process."""
    msg(A.get_in_config(["dialogs", "plugin_start"]))


def finish():
    """dialog: unplug and shutdown a board at the end of a process."""
    msg(A.get_in_config(["dialogs", "process_finish"]))


def test():
    """dialog: Ready to test?"""
    msg(A.get_in_config(["dialogs", "ready_to_test"]))


def flash():
    """dialog: Ready to flash?"""
    msg(A.get_in_config(["dialogs", "ready_to_flash"]))
