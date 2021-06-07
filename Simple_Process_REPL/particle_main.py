import Simple_Process_REPL.appstate as A
import Simple_Process_REPL.utils as u
from Simple_Process_REPL.dialog import yes_no, inputbox, msg
import Simple_Process_REPL.particle as P
import regex as re
import logging
import os


"""
The purpose of this module is to Serve as a liaison between the
Interpreter/REPL and the device interface layer, the particle-cli,
which in this case is defined in particle.py
"""

# This is a map which is merged with the application state map.
# Defaults are used by the cli where appropriate.
# device is our particle board, we need it's id, and the
# the path of it's device, ie. /dev/ttyUSB..., The board
# name is boron, photon, whatever. and the last_id just
# in case we need it.

logger = logging.getLogger()

yaml = u.dump_pkg_yaml("Simple_Process_REPL", "particle_main.yaml")
spr = u.load_pkg_resource("Simple_Process_REPL", "particle_main.spr")

# format and fill in as you wish.
HelpText = """
particle: - A particle.io device interface.  -

Interact with particle boards.  list, identify, claim, flash, test, etc.

Particle uses these parts of the Application state

%s

Particle Defines This SPR code.

%s

When working with a Particle.io board, the first step is to 'get'
the id and device. There are many commands here which need the usb device
or the device id. So the first step is always a `get`

A 'get' will populate the device in the Application
state with the currently connected device.

After that, it is possible to continue working with that device
to update it, set it's setup bit, flash it, handshake with it etc.

If a repeatable process is desired, simply create one by defining more
complex commands.

Working  in the REPL with particle boards is much nicer than the particle-cli.

""" % (
    yaml,
    spr,
)


def help():
    """Additional SPR specific Help for the Particle Module."""
    print(HelpText)


def see_images():
    """Ask if the test images are seen, fail if not."""
    yno_msg = A.get_in_config(["dialogs", "images_seen"])
    if not yes_no(yno_msg):
        raise Exception("Failure: Test images not Seen.")


def input_serial():
    """
    Function called by test handshake, Asks if images are seen,
    then presents a dialog loop to receive an 8 digit serial number
    to be returned back to the handshake and sent to the device.
    """
    see_images()

    msg = A.get_in_config(["dialogs", "input_serial"])
    while True:
        code, res = inputbox(
            msg, title=A.get_in_config(["dialogs", "title"]), height=10, width=50
        )
        if re.match(r"^\d{8}$", res):
            yno_msg = "%s : %s" % (
                A.get_in_config(["dialogs", "serial_is_correct"]),
                res,
            )
            if yes_no(yno_msg):
                break
        else:
            msg(A.get_in_config(["dialogs", "serial_must"]))

            os.system("clear")
            logger.info("Serial Number Entered is: %s" % res)
            A.set_in(["device", "serial", res])
        return res


def flash_image():
    "Flash the flash image"
    P.flash(A.get_in_config(["particle", "images", "flash"]))


def flash_tinker():
    "Flash the tinker image"
    P.flash(A.get_in_config(["particle", "images", "tinker"]))


def flash_test():
    "Flash the test image"
    P.flash(A.get_in_config(["particle", "images", "test"]))


def product_add():
    """ product device add product id - associate the device wit a product"""
    P.product_add(A.get_in_config(["particle", "product"]), A.get_in_device("id"))


def claim():
    "Claim the device, cloud claim"
    P.claim(A.get_in_device("id"))


def add():
    "Claim the device, device add"
    P.add(A.get_in_device("id"))


def release():
    "Release the claim on a device."
    P.release(A.get_in_device("id"))


def name(name):
    """Name/Rename the current device."""
    P.name(A.get_in_device("id"), name)


def name_from(varpath):
    """Name/Rename the device from a variable in the Application state."""
    n = A.get_in(varpath)
    logger.info("Naming device: %s" % n)
    name(n)


def cloud_status():
    "Check to see if the device is connected to the cloud"
    P.cloud_status(A.get_in_device("id"))


def reset_usb():
    "Reset the usb device."
    P.reset_usb(A.get_in_device("id"))


def list_usb_w_timeout():
    "Do a serial list repeatedly for timeout period"
    P.list_usb_w_timeout(A.get_in_config(["waiting", "timeout"]))


def get_usb_and_id():
    """
    Retrieve and set the USB device, the board name,  and the device id.
    Uses 'particle serial list' in a timeout loop. This is required
    for most things. Wait and handshake, use the usb device,
    and the id is needed by many things.
    """
    # PB['usb_device'], PB['device_id'] = P.get_usb_and_id()
    path, name, id = P.get_w_timeout(A.get_in_config(["waiting", "timeout"]))
    A._set_({"device": {"path": path, "name": name, "id": id}})


def wait_for_plist():
    """Wait for particle serial list to succeed with timeout, doesn't
    really work."""
    # we don't care about the results, just to wait.
    P.get_w_timeout(A.get_in_config(["waiting", "timeout"]))


def archive_log():
    "Move the current logfile to one named after the current device."
    archive_log("%s.log" % A.get_in_device("id"))


def do_pcmd(cmds):
    """Call the particle cli, with something."""
    P.do_pcmd(" ".join(cmds))


def particle_help():
    """A function to provide additional Application specific help."""
    print(
        """\n\n Particle Process help:\n
Particle help can be accessed directly at any time with the 'particle-help'
command.\n
When working with a Particle.io board, the first step is to 'get'
the id and device. There are many commands here which need the usb device
or the device id.  With that, the basic commands for the process we have
been intending would be;

'start, setup, claim, testit, flash, and archive_log'.

Note that 'start', 'setup', and 'testit', are user defined commands which are
actually lists of other commands. These are defined in the configuration
file.  Help lists the source for these commands.
'start' is actually; 'dialog-start get wait identify'

The 'continue to next' and 'device failed' dialog windows are built in to
the interactive loop. Any additional prompts, such as 'dialog-start' or
'dialog-test' can be added to the process  with their commands.
and prompt texts are defined in the configuration, which can be
seen with 'show config'.

When a process is deemed good, the autoexec can be set to it, and that
will be what runs automatically, in the process loop, or as a oneshot,
if no commands are given on the cli.\n\n """
    )


# nicer names in this name space. not pretty, but easy.
dfu = P.dfu_mode
listen = P.listen
list = P.list_usb
identify = P.identify
inspect = P.inspect
login = P.login
logout = P.logout
update = P.update
setup_done = P.set_setup_bit
_doctor = P.doctor
_flash = P.flash
pcmd = P.do_pcmd
