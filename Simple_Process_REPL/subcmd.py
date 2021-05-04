import Simple_Process_REPL.appstate as A
import subprocess
import os
import time
import logging

logger = logging.getLogger()
AS = A.AS


def rm(filename):
    """remove file at path."""
    os.remove(filename)


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


def do_cmd(command, shell=False):
    """run a sub command, read and return it's output."""
    if shell is True:
        command = " ".join(command)

    logging.debug("do_cmd: %s" % command)

    res = subprocess.run(
        command, shell=shell, stderr=subprocess.PIPE, stdout=subprocess.PIPE
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
