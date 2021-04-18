import os
from dialog import Dialog
import logging

import regex as re
import Simple_Process_REPL.repl as r
import Simple_Process_REPL.appstate as A
import Simple_Process_REPL.bar_qr as bq

logger = logging.getLogger()

# set up the dialog interface
d = Dialog(dialog="dialog")
inputbox = d.inputbox


def application_help():
    """Print help as defined by the function set in ['exec', 'help']
    in the config. This is a help function as defined by the
    application layer, which is specific to the functionality
    that we are interfacing with.
    """
    r.eval_cmd(A.get_in_config(["exec", "help"]))


def myhelp():
    "Everyone needs a little help now and then."
    print(
        """Internal command help.\n
            These are the defined symbols for this REPL. Symbols
            may be listed to execute them in order.\n"""
    )

    application_help()

    r.funcptr_help()

    r.specials_help()

    r.compound_help()

    print("\n\n")


def hello():
    "Just in case we don't know what to do."
    msgcli(A.get_in_config(["dialogs", "hellomsg"]))
    myhelp()
    msgcli(A.get_in_config(["dialogs", "continue"]))


def _input_string_to(msg, keys):
    """Dialog to get a string and set it in the Application state with a value vector."""
    v = keys + d.input_string("msg")
    A.set_in(v)


def input_string_to(v):
    """varargs version of _input_string_to which takes a vector,
    the first entry should be a string which will be displayed in the dialog window.
    The rest will be used as the value vector to set in the Application state."""
    _input_string_to(v[0], v[1:])


def dialog_print_command(fname):
    """Dialog to ask which print command to use."""
    cmd_name, print_command = print_command_menu()
    command = print_command % fname
    return 1, cmd_name, command


def dialog_print_loop(fname):
    """Dialog to ask which print command to use and how many times to print it."""
    cmd_name, command = dialog_print_command(fname)
    count = D.input_count("How many to Print ?")
    return cmd_name, command, count


def msgbox(msg):
    "Display a simple message box, enter to continue."
    d.msgbox(
        msg,
        title=A.get_in_config(["dialogs", "title"]),
        height=10,
        width=50,
    )
    os.system("clear")


def ynbox(msg):
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
    p_p_cmds = A.get_in_config("print_commands", A.get_in(["platform"]))

    rlist = tuple([(key, "") for key, cmd in p_p_cmds])
    choice = select_choice("Which print command to use ?", rlist)
    return choice, p_p_cmds[choice]


def print_file(fn):
    cmd_name, print_command = print_command_menu()
    command = print_command % fn
    os.system(command)


def BC_or_QR_menu():
    return D.select_choice(
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
    fn = bq.save_bcqr()
    print_file_loop(fn)


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
            msgbox("count must be an integer")
            continue
        break
    return res


# has nothing to do with printing really.... Just the messages. -- Refactor.
def _print_file(cmd_name, command, count):
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
    _print_file(dialog_print_command(fname))


def print_file_loop(fname):
    """Print a filename A number of times with a series of dialog prompts."""
    _print_file(dialog_print_loop(fname))


def print_file_from(keys):
    """Given a value vector, print the filename value held there."""
    print_file(A.get_in(keys))


def print_file_loop_from(keys):
    """Given a value vector, print the filename value held there, how ever many times they say."""
    print_file_loop(A.get_in(keys))


def continue_to_next():
    "cli version of continue to next."
    if re.match("^[yY]?$", input(A.get_in_config(["dialogs", "continue_to_next"]))):
        return True
    raise Exception("Answer was No")


def msgcli(msg):
    """Display a message on the cli and wait for input."""
    print(msg)
    input("Press any key to continue;")


def continue_to_next_dialog():
    "Do another one? Dialog. returns True/False"
    if not ynbox(A.get_in_config(["dialogs", "start_again"])):
        logger.info("exiting")
        return False
    return True


def cli_failed():
    """cli: Process failed."""
    msgcli(A.get_in_config(["dialogs", "device_failed"]))


def dialog_failed():
    """dialog: Process failed."""
    msgbox(A.get_in_config(["dialogs", "device_failed"]))


# So we have a parameter less functions for all of these.


def dialog_start():
    """dialog: Plugin a board and start a process."""
    msgbox(A.get_in_config(["dialogs", "plugin_start"]))


def dialog_finish():
    """dialog: unplug and shutdown a board at the end of a process."""
    msgbox(A.get_in_config(["dialogs", "process_finish"]))


def dialog_test():
    """dialog: Ready to test?"""
    msgbox(A.get_in_config(["dialogs", "ready_to_test"]))


def dialog_flash():
    """dialog: Ready to flash?"""
    msgbox(A.get_in_config(["dialogs", "ready_to_flash"]))


# So we have parameter less functions for all of these.
def cli_start():
    """cli: Plugin a board and start a process."""
    msgcli(A.get_in_config(["dialogs", "plugin_start"]))


def cli_finish():
    """cli: unplug and shutdown a board at the end of a process."""
    msgcli(A.get_in_config(["dialogs", "process_finish"]))


def cli_test():
    """cli: Ready to test?"""
    msgcli(A.get_in_config(["dialogs", "ready_to_test"]))


def cli_flash():
    """cli: Ready to flash?"""
    msgcli(A.get_in_config(["dialogs", "ready_to_flash"]))
