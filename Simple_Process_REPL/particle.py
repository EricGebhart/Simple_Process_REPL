#!/bin/python

import os
import subprocess
import logging
import time
import Simple_Process_REPL.subcmd as s
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

    with /config/device/waiting
    with /config/device/serial
    with /config/device/handshake
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


# def archive_log(id):
#     "Move the current logfile to one named after the current value of id."
#     A.archive_log("%s.log" % id)


def do_pcmd(cmd, timeout=None):
    """run a particle command, read and return it's output. timeout is the amount
    of time given for the command to return before killing it and raising an exception.
    """
    return s.do_cmd(s.mk_cmd(cmd, prefix="particle"), timeout=timeout)


def do_id_pcmd(cmd, id, timeout=None):
    """Do particle command with an id. Convenience for creating
    more interface functions without writing python code, and still
    get the id signature variable we want to automatically fill."""
    # particle product add $product_id $device_id
    do_pcmd(cmd + " " + id, timeout=timeout)


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
        stdout = do_pcmd("list usb")

        # USB, id
        if stdout.split(" ")[0] != "No":
            device_line = stdout.split("\n")[1]
            devices = device_line.split(" - ")
            return {"path": devices[0], "name": devices[1], "id": devices[2]}

        if time.time() - start >= timeout:
            logger.error("Getting USB and device ID timed out")
            raise Exception("Getting USB and device ID timed out.")

        time.sleep(1)

    return stdout


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


def name(name, id):
    """Name/Rename a device"""
    do_pcmd("device rename %s %s" % (id, name))


def flash(image):
    """flash an image. (dfu, flash --usb)"""
    logger.info("Flashing device with: %s" % image)
    if os.path.exists(image):
        do_pcmd("usb dfu")
        # do_pcmd('flash ––usb {}'.format(image))
        foo = os.popen("particle flash --usb %s" % image).read()
        logger.debug(foo)
    else:
        logger.error("Image %s to flash does not exist." % image)
