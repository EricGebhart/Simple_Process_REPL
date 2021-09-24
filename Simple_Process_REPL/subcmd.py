import subprocess
import os
import time
import logging

logger = logging.getLogger()

# format and fill in as you wish.
HelpText = """
Subcmd: - SPR's subprocess interface, ie. shell.  -

Use the sub process command library to execute system commands.

Roughly equivalent, but not, to python's os.system().
There are reasons to use one or the other.

https://docs.python.org/3/library/subprocess.html

"""


def help():
    """Additional SPR specific Help for the App State Module."""
    print(HelpText)


def rm(filename):
    """remove file at path."""
    os.remove(filename)


def environ():
    """Show the shell environment"""
    logger.info(os.environ)


def sleep(s):
    """Sleep for x seconds"""
    time.sleep(s)


def mk_cmd(cmd, prefix=""):
    """
    Put together a command list for subprocess.run.
    simplistic, split on spaces to make the list of command pieces.
    """
    if prefix:
        command = [prefix]
    else:
        command = []
    command.extend(cmd.split(" "))
    logger.debug(command)
    return command


def do_cmd(command, shell=False, timeout=None):
    """run a sub command, read and return it's output."""
    doit = command
    if shell is True:

        for thing in command:
            doit + " " + str(thing)
            # command = " ".join(command)

    logging.debug("do_cmd, Timeout: %s\n%s" % (timeout, command))

    res = subprocess.run(
        doit,
        shell=shell,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        timeout=timeout,
    )

    stderr = res.stderr.decode("utf-8")
    stdout = res.stdout.decode("utf-8")

    logger.debug("Return Code: %d" % res.returncode)
    logger.info(stdout)
    logger.error(stderr)

    if res.returncode:
        raise Exception("stdout: %s\n stderr: %s\n" % (stdout, stderr))

    return stdout


def do(*commands):
    """A varargs wrapper for do_cmd using subprocess to run shell commands."""
    do_cmd(*commands)


def do_cli_cmd(cmd, timeout=None, external_cli_prefix=None):
    """run a command, adding the prefix before execution.
    read and return it's output.
    timeout is the amount of time given for the command to
    return before killing it and raising an exception.
    """
    return do_cmd(mk_cmd(cmd, prefix=external_cli_prefix), timeout=timeout)


def do_cli_cmd_w_timeout(cmd, timeout, external_cli_prefix=None):
    """loop over a command for a timeout period. For commands
    that return failure quickly.
    Note, this is not the same meaning of timeout elsewhere.
    It is similar.. This is for things that are too quick, and
    also for things that hang. It's the too quick situation that
    is being addressed here.  It really has not worked out yet.
    so it's here in theory that it could be useful.

    Didn't work out for 'particle serial list',
    because it returns 0 no matter what happens."""
    start = time.time()
    while True:
        command = mk_cmd(cmd, prefix=external_cli_prefix)
        res = subprocess.run(
            command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, timeout=timeout
        )

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


def loop_cmd(command, count=1):
    """Loop over a shell command using os.system."""
    for i in range(0, count - 1):
        os.system(command)
    else:
        os.system(command)
