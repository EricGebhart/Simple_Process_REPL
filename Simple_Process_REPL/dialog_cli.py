import os
from dialog import Dialog
import Simple_Process_REPL.repl as r
import logging

logger = logging.getLogger()

# set up the dialog interface
d = Dialog(dialog="dialog")
inputbox = d.inputbox


def msgbox(msg):
    "Display a simple message box, enter to continue."
    d.msgbox(
        msg,
        title=r.get_in_config(["dialogs", "title"]),
        height=10,
        width=50,
    )
    os.system("clear")


def ynbox(msg):
    "Display a yesno dialog, return True or False."
    response = d.yesno(
        msg,
        title=r.get_in_config(["dialogs", "title"]),
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
        title=r.get_in_config(["dialogs", "title"]),
        choices=choices,
    )
    return tag


def select_choice(msg, choices):
    logger.info("select choice: %s", choices)
    code, choice = d.menu(
        msg,
        title=r.get_in_config(["dialogs", "title"]),
        choices=choices,
        height=50,
        width=50,
    )
    os.system("clear")
    return choice


def print_command_radio():
    """Give a radio list of possible print commands for the current platform"""
    p_p_cmds = r.get_in_config("print_commands", AS["platform"])

    rlist = tuple([(key, "", 0) for key, cmd in p_p_cmds])
    choice = radiolist("Which print command to use ?", rlist)
    return choice, p_p_cmds[choice]


def dialog_print_file(fn):
    cmd_name, print_command = print_command_radio()
    command = print_command % fn
    os.system(command)


def input_string(msg):
    """Get a string input"""
    code, res = inputbox(
        msg,
        title=r.get_in_config(["dialogs", "title"]),
        height=10,
        width=50,
    )
    return res


def input_count(msg):
    """Give an input dialog that insists on an integer input.
    A range box could work, but seemed cumbersome."""
    while True:
        code, res = inputbox(msg, title=Title, height=10, width=50)
        try:
            res = int(res)
        except Exception:
            msgbox("count must be an integer")
            continue
        break
    return res


def continue_to_next():
    "cli version of continue to next."
    if re.match("^[yY]?$", input(r.get_in_config(["dialogs", "continue_to_next"]))):
        return True
    raise Exception("Answer was No")


def msgcli(msg):
    """Display a message on the cli and wait for input."""
    print(msg)
    input("Press any key to continue;")


def continue_to_next_dialog():
    "Do another one? Dialog. returns True/False"
    if not ynbox(r.get_in_config(["dialogs", "start_again"])):
        logger.info("exiting")
        return False
    return True


def cli_failed():
    """cli: Process failed."""
    msgcli(r.get_in_config(["dialogs", "device_failed"]))


def dialog_failed():
    """dialog: Process failed."""
    msgbox(r.get_in_config(["dialogs", "device_failed"]))


# So we have a parameter less functions for all of these.


def dialog_start():
    """dialog: Plugin a board and start a process."""
    msgbox(r.get_in_config(["dialogs", "plugin_start"]))


def dialog_finish():
    """dialog: unplug and shutdown a board at the end of a process."""
    msgbox(r.get_in_config(["dialogs", "process_finish"]))


def dialog_test():
    """dialog: Ready to test?"""
    msgbox(r.get_in_config(["dialogs", "ready_to_test"]))


def dialog_flash():
    """dialog: Ready to flash?"""
    msgbox(r.get_in_config(["dialogs", "ready_to_flash"]))


# So we have parameter less functions for all of these.
def cli_start():
    """cli: Plugin a board and start a process."""
    msgcli(r.get_in_config(["dialogs", "plugin_start"]))


def cli_finish():
    """cli: unplug and shutdown a board at the end of a process."""
    msgcli(r.get_in_config(["dialogs", "process_finish"]))


def cli_test():
    """cli: Ready to test?"""
    msgcli(r.get_in_config(["dialogs", "ready_to_test"]))


def cli_flash():
    """cli: Ready to flash?"""
    msgcli(r.get_in_config(["dialogs", "ready_to_flash"]))
