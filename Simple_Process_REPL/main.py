import Simple_Process_REPL.core as r
import regex as re
import logging
import os


"""
The purpose of this module is to Serve as a liaison between the
Interpreter/REPL and the Application interface layer. This is where
you will add functionalities which you wish to use in your processes.

The Repl module requires two symbol tables, and a dictionary of
defaults, as well as any stateful data the application would like to keep.
In this case it is the _device_ dictionary below.

The symbol table of these functions is defined and passed to
to the repl core module which is reponsible for similar things
as well as parsing the command line, setting up logging, and
executing the process as desired.

The symbol tables could be automated with the use of import. But I have
tried to keep a minimum of magic here. Symbol tables are clear and obvious.
"""

# This is a map which is merged with the application state map.
# Defaults are used by the cli where appropriate.
# device is our particle board, we need it's id, and the
# the path of it's device, ie. /dev/ttyUSB..., The board
# name is boron, photon, whatever. and the last_id just
# in case we need it.

# It doesn't have to be a device, it can be anything you wish to
# keep the state of.  This map is integrated into the configuration
# structure after it is loaded.

MyState = {
    "device": {"id": "", "name": "", "path": "", "last_id": ""},
    "defaults": {
        "config_file": None,
        "loglevel": "info",
        "logfile": "SPR.log",
    },
}

# We don't really need anything, the defaults are fine.
MyState = {}
# If we have a config in our package we could load it here.
# The simple Process repl will load SPR-defaults first, then
# it will load the defaults for the application level package..

# Do this for your app's yaml, SPR will load it's defaults first.
# MyState |= r.load_defaults(__name__, "MY-defaults.yaml")

# If you don't have a default config to add...
MyState |= r.load_defaults()

logger = logging.getLogger()

# Hook Functions.  These first two are used by the handshake function
# which will look for patterns in the output of the device and
# do various actions.  The handshake function should be set
# to the value of "do_qqc_func" in the config.  Handshake will
# look for that name in the symbol table if it needs it.


def see_images():
    """Ask if the test images are seen, fail if not."""
    yno_msg = r.get_in_config(["dialogs", "images_seen"])
    if not r.ynbox(yno_msg):
        raise Exception("Failure: Test images not Seen.")


def input_serial():
    """
    Function called by test handshake, Asks if images are seen,
    then presents a dialog loop to receive an 8 digit serial number
    to be returned back to the handshake and sent to the device.
    """
    see_images()

    msg = r.get_in_config(["dialogs", "input_serial"])
    while True:
        code, res = r.inputbox(
            msg, title=r.get_in_config(["dialogs", "title"]), height=10, width=50
        )
        if re.match(r"^\d{8}$", res):
            yno_msg = "%s : %s" % (
                r.get_in_config(["dialogs", "serial_is_correct"]),
                res,
            )
            if r.ynbox(yno_msg):
                break
        else:
            r.msgbox(r.get_in_config(["dialogs", "serial_must"]))

    os.system("clear")
    logger.info("Serial Number Entered is: %s" % res)
    return res


# Regular Functions.  These are functions which are used
# purely for their side effects.  They take no arguments and
# and return nothing. Processes are, for the most part, made
# from these.


def print_config_val():
    "print a config value"
    print(r.get_in_config(["dialogs", "start"]))


def print_device_val():
    "Get a value out of the device structure."
    print(r.get_in_device("id"))


def set_device_vals():
    """
    An example to show how to set values in the device state.
    """
    name = "foo"
    path = "bar"
    id = "12345"
    r.set({"device": {"path": path, "name": name, "id": id}})
    r.show()


def archive_log():
    "Move the current logfile to one named after the current device."
    r.archive_log("%s.log" % r.get_in_device("id"))


def app_help():
    """A function to provide additional Application specific help.
    The name of this symbol should be set in the config for exec->help."""
    print(
        """\n\n MY NEW Process help:\n
Help can be accessed directly at any time with the 'help'
command.\n

...

When a process is deemed good, the autoexec can be set to it, and that
will be what runs automatically, in the process loop, or as a oneshot,
if no commands are given on the cli.\n\n """
    )


symbols = [
    ["print_config_val", print_config_val, "Example of using configuration variables."],
    ["print_device_val", print_device_val, "Example of using device values."],
    ["set_device_vals", set_device_vals, "Example of setting device values."],
    ["archive-log", archive_log, "Archive the log to the the device id."],
    ["input-serial", input_serial, "Dialog to receive an 8 digit serial number."],
    ["app_help", app_help, "Additional Application layer help."],
]


def MySpecial(x):
    print(x)


# Name, function, number of args, help string
# Commands we want in the repl which can take arguments.
# look in core.py for examples.
specials = [
    [
        "MySpecialCMD",
        MySpecial,
        1,
        "Takes one argument does something special.",
    ]
]

# get the default parser for the application and add to it if needed.
parser = None
# parser = r.get_parser()
# parser.add_argument("-f", "--foo", action="store_true", help="set foo")


def init():
    """
    Call into the interpreter/repl with our stuff,
    This starts everything up.
    """
    r.init(symbols, specials, parser)
