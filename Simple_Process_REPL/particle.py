#!/bin/python

import os
import subprocess
import logging
import time
import Simple_Process_REPL.subcmd as s
import Simple_Process_REPL.utils as u

logger = logging.getLogger()


# yaml = u.dump_pkg_yaml("Simple_Process_REPL", "particle.yaml")
# spr = u.load_pkg_resource("Simple_Process_REPL", "particle.spr")

# format and fill in as you wish.
HelpText = """
particle: - A particle.io device interface.  -

Interact with particle boards.  list, identify, claim, flash, test, etc.

This is just a thin, interface to the particle-cli from particle.io.
Most of it is defined within spr. There are only handful of python
functions for convenience or to address special situations.

Use `show /config/particle` to see configuration settings.

Assuming this was put in the pb namespace, `pb/init-with` will set up the
_with stack_.
After doing `pb/init-with` use `as/flat-with` to see everything that
these particle functions might be using.

Particle defines /device as the location for the working device by default.

Some functions do use timeouts and dialogs, putting
'/config/dialogs' in your 'with' stack will resolve any default values needed.

    with /config/device/waiting
    with /config/device/serial
    with /config/device/handshake
    with /config/dialogs
    with /device

After the with stack is set up, then it's time to play.
When working with a Particle.io board, the first step is to 'get'
the id and device. There are many commands here which need the usb device
or the device id.  With that, the basic commands for the process we have
been intending would be;

'start, setup, claim, test, flash, and archive_log'.

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
"""


def help():
    """Additional SPR specific Help for the Particle Module."""
    print(HelpText)


# def archive_log(id):
#     "Move the current logfile to one named after the current value of id."
#     A.archive_log("%s.log" % id)


def cmd(cmd, timeout=None):
    """Execute a Particle cli command."""
    return s.do_cli_cmd(cmd, external_cli_prefix="particle", timeout=timeout)


def id_cmd(cmd, id, timeout=None):
    """Do particle command with an id. Convenience for creating
    more interface functions without writing python code, and still
    get the id signature variable we want to automatically fill."""
    # particle product add $product_id $device_id
    s.do_cli_cmd(cmd + " " + id, external_cli_prefix="particle", timeout=timeout)


def get_w_timeout(timeout):
    """
    loop over list_usb() for a timeout period. Extract
    the usb device, board name, and the device id if possible.
    This is actually nice behavior because it gives a chance to
    re-plug your particle board. And this is the first step to
    any set of operations on a device.
    returns path,type and id.
    """
    start = time.time()
    while True:
        stdout = cmd("serial list")

        # USB, id
        if stdout.split(" ")[0] != "No":
            device_line = stdout.split("\n")[1]
            devices = device_line.split(" - ")
            return {"path": devices[0], "type": devices[1], "id": devices[2]}

        if time.time() - start >= timeout:
            logger.error("Getting USB and device ID timed out")
            raise Exception("Getting USB and device ID timed out.")

        # time.sleep(1)

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
    cmd("product device add %s %s" % (product, id))


def name(name, id):
    """Name/Rename a device"""
    cmd("device rename %s %s" % (id, name))


def flash(image):
    """flash an image. (dfu, flash --usb)"""
    logger.info("Flashing device with: %s" % image)
    if os.path.exists(image):
        cmd("usb dfu")
        # do_pcmd('flash ––usb {}'.format(image))
        foo = os.popen("particle flash --usb %s" % image).read()
        logger.debug(foo)
    else:
        logger.error("Image %s to flash does not exist." % image)
