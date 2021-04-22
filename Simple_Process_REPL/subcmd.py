import Simple_Process_REPL.appstate as A
import subprocess
import logging

logger = logging.getLogger()
AS = A.AS


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


def do_shell(commands, shell=True):
    do_cmd(commands)


# Commands we want in the repl which can take arguments.
symbols = [
    ["ls", "sh ls -l", "Run a shell command; ls"],
]

specials = [
    ["sh", do_shell, -1, "Run a shell command; sh ls -l"],
]

helptext = """"Shell stuff. Do a sub process. hope it works."""


def subcmd():
    return {
        "name": "subcmd",
        "symbols": symbols,
        "specials": specials,
        "doc": helptext,
        "state": None,
    }
