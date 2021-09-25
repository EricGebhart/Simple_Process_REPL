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

With the new 'with' functionality and the results stack, a lot of this
could maybe go away.  _msg, _yes_no, _menu are closer to the bare dialog
functions to see how that works out.  dialog uses **kwargs, so I could just
send in the whole flattened with stack when it gets called in do_fptrs.



"""
    % yaml
)


def help():
    print(HelpText)


def hello(hellomsg):
    "Just in case we don't know what to do."
    msg(hellomsg)


def input_string(input_please, title, height=10, width=50):
    """Get a string input"""
    code, res = inputbox(
        input_please,
        title=title,
        height=height,
        width=width,
    )
    return res


def input_count(input_please, title, height=10, width=50):
    """Give an input dialog that insists on an integer input.
    A range box could work, but seemed cumbersome."""
    while True:
        code, res = inputbox(
            input_please,
            title=title,
            height=height,
            width=width,
        )
        try:
            res = int(res)
        except Exception:
            logger.info("count must be an integer")
            continue
        break
    return res


def _inputbox(input_please, title, height=10, width=50):
    """Get a string input"""
    code, res = inputbox(
        input_please,
        title=title,
        height=height,
        width=width,
    )

    if code == "cancel":
        res = code

    return res


def _input_string(
    input_please,
    title,
    input_regex=None,
    input_is_correct=None,
    input_must=None,
    height=10,
    width=50,
):
    """
    Give an input dialog which will check the entered value against
    a regular expression. If no regex is given, this function
    behaves the same as input_string.

    message - The request to input something.
    input_regex - the regex to match the input.
    title - usually the application title for all dialogs.
    input_is_correct - question to ask, if result matches regex.
    input_must - message to say what it must match.
    height - height of dialog.
    width - width of dialog.

    Allows for the elimination of the confirmation
    dialog and setting of confirmation and error messages.

    If the result matches the regular expression,
    and a 'correct' message is provided,
    Then there will be a confirmation dialog provided.

    If incorrect, the message provided by input_must
    is displayed along with the regular expression which failed.

    An example of yaml to hold a regex.
    This one is for 8 digits.
    regex : '^\d{8}$'

    """
    if input_regex is None:
        return _inputbox(input_please, title, height, width)

    while True:
        res = _inputbox(input_please, title, height, width)

        if res == "cancel":
            break

        if re.match(input_regex, res):
            if input_is_correct is not None:
                yno_msg = "%s : %s" % (input_is_correct, res)
                if yes_no(yno_msg, title):
                    break
            else:
                break
        else:
            if input_must is not None:
                msg("%s : %s" % (input_must, input_regex), title)
            else:
                break

    return res


def msg(msg, title, height=10, width=50):
    """Display a simple message box, with either
    the msg or the text located at msg if it begins with a /..
    """
    if msg is not None:
        d.msgbox(
            msg,
            title=title,
            height=height,
            width=width,
        )


def yes_no(yn_msg, title, height=10, width=50):
    """Display a yesno dialog,
    return True if ok or False."
    """
    response = d.yesno(
        yn_msg,
        title=title,
        height=height,
        width=width,
    )
    if response == "ok":
        return True
    else:
        return False


def radiolist(radio_msg, title, choices, height=50, width=50):
    """
    Give a radio list from a dictionary of choices.
    """
    choice_tuples = list(choices.items())

    code, value = d.radiolist(
        msg,
        title=title,
        choices=choice_tuples,
        height=50,
        width=50,
    )
    return [code, value, choices[value]]


def menu(menu_msg, title, choices, height=50, width=50):
    """
    Give a menu using a dictionary of key values to make the choice tuples.
    """

    # choice_tuples = []
    # logger.info("choices: %s" % choices)
    # for k, v in choices.items():
    #     choice_tuples += tuple(k, v)

    choice_tuples = list(choices.items())

    code, value = d.menu(
        menu_msg,
        title=title,
        choices=choice_tuples,
        height=height,
        width=width,
    )

    return [code, value, choices[value]]


def yno_fail(yn_fail_msg, title):
    """Ask a yes no question, raise an exception
    to fail if the answer is no.
    """

    if yn_fail_msg is not None and not yes_no(yn_fail_msg, title):
        raise Exception("Failure: %s No!" % yn_fail_msg)
