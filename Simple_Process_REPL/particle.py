#!/bin/python

import os
import subprocess
import logging
import time
import Simple_Process_REPL.subcmd as s

logger = logging.getLogger()


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
    """
    start = time.time()
    while True:
        stdout = list_usb()

        # USB, id
        if stdout.split(" ")[0] != "No":
            device_line = stdout.split("\n")[1]
            devices = device_line.split(" - ")
            return [devices[0], devices[1], devices[2]]

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
    """Run particle doctor. (list, dfu, doctor)"""
    list_usb()
    dfu_mode()
    return do_pcmd("-v doctor")


def _doctor():
    """Run particle doctor. (doctor)"""
    return do_pcmd("-v doctor")


def listen():
    """Start listening."""
    do_pcmd("usb start-listening")
    logger.info("Listening")


def update():
    """ Update the device OS. ie. dfu, update."""
    logger.info("Updating device")
    dfu_mode()
    return do_pcmd("update")


def set_setup_bit():
    """Mark the setup bit done."""
    do_pcmd("usb setup-done")
    logger.info("Set: Setup-done")


# no command product add...
# particle help product add --> gives nothing.
def add(device_id):
    """Register/claim device with 'particle device add'"""
    logger.info("Registering device:")
    # particle product add $product_id $device_id
    do_pcmd("device add {}".format(device_id))


def product_add(product, device_id):
    """Associate device with a product 'particle product device add'"""
    logger.info("Registering device:")
    do_pcmd("product device add %s %s" % (product, device_id))


def claim(device_id):
    """Cloud claim device with 'particle cloud claim'"""
    logger.info("Claiming device:")
    # particle product add $product_id $device_id
    do_pcmd("cloud claim {}".format(device_id))


def release(device_id):
    """Release the claim on a device"""
    do_pcmd("device remove {}".format(device_id))


def cloud_status(device_id):
    """Check the cloud-status of the device."""
    do_pcmd("usb cloud-status {}".format(device_id))


def reset_usb(device_id):
    """Reset the device on the usb."""
    do_pcmd("usb reset {}".format(device_id))


def name(device_id, n):
    """Name/Rename a device"""
    do_pcmd("device rename %s %s" % (device_id, n))


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
