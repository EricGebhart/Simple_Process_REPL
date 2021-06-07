import os
from dialog import Dialog
import logging

import regex as re
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


def _input_string(msg, regex=None, correct=None, must=None, confirmation=True):
    """
    Give an input dialog which will check the entered value against
    a regular expression.

    Allows for the elimination of the confirmation
    dialog and setting of confirmation and error messages.

    If the result matches the regular expression,
    and a 'correct' message is provided,
    Then there will be a confirmation dialog provided.

    If incorrect, the message provided by must or in
    /config/dialogs/must is displayed along with the regular
    expression which failed.

    An example of yaml to hold a regex.
    This one is for 8 digits.
    regex : r"^\d{8}$"

    """
    if regex is None:
        return input_string(msg)

    if must is None:
        must = (A.get_in_config(["dialogs", "must"]),)

    if correct is None:
        correct = A.get_in_config(["dialogs", "correct"])

    while True:
        res = input_string(msg)
        if re.match(regex, res):
            if confirmation:
                yno_msg = "%s : %s" % (correct, res)
                if yes_no(yno_msg):
                    break
            else:
                break
        else:
            if must is not None:
                msg("%s : %s" % ("must", regex))

    return res


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


def msg(msg):
    """Display a simple message box, with either
    the msg or the text located at msg if it begins with a /..
    """
    if msg[0] == "/":
        msg = A.get(msg)

    d.msgbox(
        msg,
        title=A.get_in_config(["dialogs", "title"]),
        height=10,
        width=50,
    )
    os.system("clear")


def yes_no(msg):
    """Display a yesno dialog,
    If msg is a path, use the contents of path.

    return True or False."
    """

    if msg[0] == "/":
        msg = A.get(msg)

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
    if msg[0] == "/":
        msg = A.get(msg)

    (code, tag) = d.radiolist(
        msg,
        width=50,
        title=A.get_in_config(["dialogs", "title"]),
        choices=choices,
    )
    return tag


def select_choice(msg, choices):
    if msg[0] == "/":
        msg = A.get(msg)

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


def print_file(filename):
    """Print a filename with a series of dialog prompts."""
    name, cmd = dialog_print(filename)
    _print_file(filename, name, cmd, 1)


def print_file_loop(filename):
    """Print a filename A number of times with a series of dialog prompts."""
    name, cmd, count = dialog_print_loop(filename)
    _print_file(filename, name, cmd, count)


def continue_to_next():
    "Do another one? Dialog. returns True/False"
    if yes_no(A.get_in_config(["dialogs", "start_again"])):
        logger.info("exiting")
        return False
    return True
