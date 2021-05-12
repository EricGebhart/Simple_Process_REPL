import logging
import regex as re
import Simple_Process_REPL.appstate as A
import Simple_Process_REPL.utils as u

logger = logging.getLogger()

yaml = u.dump_pkg_yaml("Simple_Process_REPL", "dialog.yaml")

HelpText = (
    """
cli: An interface to the commandline using python input().

This module provides a few cli prompts, and messages.
it is a partial match to the interface presented in the dialog module.

There is currently no stateful data, although that should change.

The cli uses the same parts of the configuration as the dialog module.

%s

"""
    % yaml
)


def help():
    print(HelpText)


def hello():
    "Just in case we don't know what to do."
    msg(A.get_in_config(["dialogs", "hellomsg"]))


def radiolist(msg, choices):
    pass


def select_choice(msg, choices):
    pass
    # return choice


def print_command_menu():
    """Give a menu of possible print commands for the current platform"""
    p_dict = A.get_in_config(["print_commands", A.get_in(["platform"])])
    p_p_cmds = list(p_dict.items())

    rlist = [(key, "") for key, cmd in p_p_cmds]
    choice = select_choice("Which print command to use ?", rlist)
    return choice, p_dict[choice]


def yes_no(message):
    "Yes or No message, returns True or False."
    if re.match("^[yY]?$", input(message)):
        return True
    return False


def continue_to_next():
    "Continue to next. raise exception if not Y/y."
    if yes_no(A.get_in_config(["dialogs", "continue_to_next"])):
        return True
    raise Exception("Answer was No")


def msg(msg):
    """Display a message on the cli and wait for input."""
    print(msg)
    input("Press any key to continue;")


def failed():
    """cli: Process failed."""
    msg(A.get_in_config(["dialogs", "device_failed"]))


# So we have parameter less functions for all of these.
def start():
    """cli: Plugin a board and start a process."""
    msg(A.get_in_config(["dialogs", "plugin_start"]))


def finish():
    """cli: unplug and shutdown a board at the end of a process."""
    msg(A.get_in_config(["dialogs", "process_finish"]))


def test():
    """cli: Ready to test?"""
    msg(A.get_in_config(["dialogs", "ready_to_test"]))


def flash():
    """cli: Ready to flash?"""
    msg(A.get_in_config(["dialogs", "ready_to_flash"]))
