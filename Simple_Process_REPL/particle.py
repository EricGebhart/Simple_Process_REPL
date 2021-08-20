#!/bin/python

import os
import subprocess
import logging
import time
import Simple_Process_REPL.subcmd as s
import Simple_Process_REPL.appstate as A
import Simple_Process_REPL.utils as u

logger = logging.getLogger()


yaml = u.dump_pkg_yaml("Simple_Process_REPL", "particle.yaml")
spr = u.load_pkg_resource("Simple_Process_REPL", "particle.spr")

# format and fill in as you wish.
HelpText = """
particle: - A particle.io device interface.  -

Interact with particle boards.  list, identify, claim, flash, test, etc.

Particle uses these parts of the Application state

%s

Particle Defines This SPR code.

%s





Particle defines /device as the location for the working device by default.
using 'with /device' will give predictable results.

Some functions do use timeouts and dialogs, putting
'/config/dialogs' in your 'with' stack will resolve any default values needed.

    with /config/timeout
    with /config/dialogs
    with /device

A 'with_init' function is provided which will do this.

When working with a Particle.io board, the first step is to 'get'
the id and device. There are many commands here which need the usb device
or the device id.  With that, the basic commands for the process we have
been intending would be;

'start, setup, claim, testit, flash, and archive_log'.

The 'continue to next' and 'device failed' dialog windows are built in to
the interactive loop of SPR. Any additional prompts, such as 'dialog-start' or
'dialog-test' can be added to the process  with their commands. If a more
interactive process is desired.

When working with a Particle.io board, the first step is to 'get'
the id and device. There are many commands here which need the usb device
or the device id. So the first step is always a `get`.

It is also useful to do `list` to see what devices are there.

A 'get' will retrieve the id, path and name of the currently connected
device and put them at the current 'with', which is possibly /device.

After that, it is possible to continue working with that device
to update it, set it's setup bit, flash it, handshake with it etc.

If a repeatable process is desired, simply create one by defining more
complex commands.


""" % (
    yaml,
    spr,
)


def help():
    """Additional SPR specific Help for the Particle Module."""
    print(HelpText)


def archive_log(id):
    "Move the current logfile to one named after the current value of id."
    A.archive_log("%s.log" % id)


def do_pcmd_w_timeout(cmd, timeout):
    """loop over a command for a timeout period. For commands
    that return failure quickly. Didn't work out for 'particle serial list',
    because it returns 0 no matter what happens."""
    start = time.time()
    while True:
        command = s.mk_cmd(cmd, prefix="particle")
        res = subprocess.run(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        print(res)
        logger.debug(res)
        if res.returncode == 0:
            break

        if time.time() - start >= timeout:
            logger.warning("%s: timed out" % " ".join(command))
            break

        time.sleep(1)

    # print(res.stdout)
    logger.info(res.stdout.decode("utf-8"))
    return res.stdout.decode("utf-8")


def get_w_timeout(timeout):
    """
    loop over list_usb() for a timeout period. Extract
    the usb device, board name, and the device id if possible.
    This is actually nice behavior because it gives a chance to
    replug your particle board. And this is the first step to
    any set of operations on a device.
    returns path,name and id.
    """
    start = time.time()
    while True:
        stdout = list_usb()

        # USB, id
        if stdout.split(" ")[0] != "No":
            device_line = stdout.split("\n")[1]
            devices = device_line.split(" - ")
            return {path: devices[0], name: devices[1], id: devices[2]}

        if time.time() - start >= timeout:
            logger.error("Getting USB and device ID timed out")
            raise Exception("Getting USB and device ID timed out.")

        time.sleep(1)

    return stdout


def do_pcmd(cmd):
    """run a particle command, read and return it's output."""
    return s.do_cmd(s.mk_cmd(cmd, prefix="particle"))


# this doesn't actually work because particle returns 0
# no matter what happens.
def list_usb_w_timeout(timeout):
    "list the particle devices connected to usb."
    return do_pcmd_w_timeout("serial list", timeout)


def list_usb():
    "list the particle devices connected to usb."
    return do_pcmd("serial list")


def inspect():
    "Inspect the particle device"
    return do_pcmd("serial inspect")


def login():
    "Login to particle cloud from the cli prompt"
    return os.system("particle cloud login")


def logout():
    "Logout of particle cloud, clean up tokens."
    return os.system("particle cloud logout")


def get_usb_and_id():
    """
    Does a particle list and retrieves the usb device and device id
    Returns: usb, id
    """
    devices = list_usb()
    # USB, id
    return [devices.split(" - ")[2], devices.split()[0]]


def identify():
    """
    Get the identity of the particle board,
    send it to the log. (listen then identify)
    """
    logger.info("Identify: Start listening")
    listen()
    try:
        identify = do_pcmd("identify")
    except Exception as e:
        logger.error("Unable to Identify the particle board.")
        logger.error(e)
        raise (e)
    else:
        return identify


def doctor():
    """Run particle doctor. (list usb, dfu mode then -> doctor)"""
    list_usb()
    dfu_mode()
    return do_pcmd("-v doctor")


def _doctor():
    """Run particle doctor. (just doctor)"""
    return do_pcmd("-v doctor")


def listen():
    """Start listening."""
    do_pcmd("usb start-listening")
    logger.info("Listening")


def update():
    """Update the device OS. ie. dfu, update."""
    logger.info("Updating device")
    dfu_mode()
    return do_pcmd("update")


def set_setup_bit():
    """Mark the setup bit done."""
    do_pcmd("usb setup-done")
    logger.info("Set: Setup-done")


# no command product add...
# particle help product add --> gives nothing.
def add(id):
    """Register/claim device with 'particle device add'"""
    logger.info("Registering device:")
    # particle product add $product_id $device_id
    do_pcmd("device add {}".format(id))


def product_add(product, id):
    """Associate device with a product 'particle product device add'
    Associate the device with a product.
    The default product is in config/particle.
    id would be in /device by default.

    Use 'with /config/particle
         with /device.'

    or another place where 'id' is set"""
    logger.info("Registering device:")
    do_pcmd("product device add %s %s" % (product, id))


def claim(id):
    """Cloud claim device with 'particle cloud claim'"""
    logger.info("Claiming device:")
    # particle product add $product_id $device_id
    do_pcmd("cloud claim {}".format(id))


def release(id):
    """Release the claim on a device"""
    do_pcmd("device remove {}".format(id))


def cloud_status(id):
    """Check the cloud-status of the device."""
    do_pcmd("usb cloud-status {}".format(id))


def reset_usb(id):
    """Reset the device on the usb."""
    do_pcmd("usb reset {}".format(id))


def name(id, name):
    """Name/Rename a device"""
    do_pcmd("device rename %s %s" % (id, name))


def flash(image):
    """flash an image. (dfu, flash --usb)"""
    logger.info("Flashing device with: %s" % image)
    if os.path.exists(image):
        dfu_mode()
        # do_pcmd('flash ––usb {}'.format(image))
        foo = os.popen("particle flash --usb %s" % image).read()
        logger.debug(foo)
    else:
        logger.error("Image %s to flash does not exist." % image)


def dfu_mode():
    """Put USB device in dfu mode."""
    do_pcmd("usb dfu")


def get_usb_and_id(timeout):
    """
    Retrieve and set the USB device, the board name,  and the device id.
    Uses 'particle serial list' in a timeout loop. This is required
    for most things. Wait and handshake, use the usb device,
    and the id is needed by many things.

    Sets path, name and id in current 'with'
    Use 'with /device' or another location where you would like the results.
    """
    # it's strange, if we add timeout to the args, and use with, we can
    # remove the explicit get-in-config.
    path, name, id = get_w_timeout(timeout)
    A._set_in({"path": path, "name": name, "id": id})
