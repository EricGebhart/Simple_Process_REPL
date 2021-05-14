import logging
import sys


"""
This is a mess. Nothing is really working properly. Nothing is going
to the log file, and the simpler code just doesn't work. For sure,
to get logging for everything, do not give a name to getLogger so
the root logger will come back.

I'm not really sure why start_logging()
doesn't work but setup_logger() does.

So more work to do here.

We are at least getting log info to stdout all the way
down into the particle.py code.

"""

message_fmt = "[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s"

stdout_format = "%(message)s"

# message_fmt = '[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s'
# message_fmt = '[%(levelname)s] %(name)s %(asctime)s - %(message)s'
message_fmt = "[%(name)s] %(asctime)s - %(message)s"


def validate_loglevel(loglevel):
    nloglevel = getattr(logging, loglevel.upper(), None)
    if not isinstance(nloglevel, int):
        raise ValueError("Invalid log level: %s" % nloglevel)
    return nloglevel


# this one was not working but maybe it will now. I'd like
# to study it.
def start_logging(loglevel):
    """Start up logging with 2 handlers. One for the logfile and
    on for stdout. Set the log level the same to all loggers."""

    nloglevel = validate_loglevel(loglevel)

    # file_handler = logging.FileHandler(logfile)
    stdout_handler = logging.StreamHandler(sys.stdout)
    handlers = [stdout_handler]
    logger = logging.getLogger()

    logging.basicConfig(
        encoding="utf-8", format=message_fmt, level=nloglevel, handlers=handlers
    )

    return logger()


def set_level(logger, lvl):
    "Set the level for the logger."
    logger.setLevel(validate_loglevel(lvl))


def log_lvl(lvl):
    """Change the logging level."""
    set_level(logging.getLogger(), lvl)


def add_file_handler(logger, loglevel, filename):
    """
    Takes a logger, a string loglevel, and a filename,
    to create and add a file handler to a logger.
    """

    nloglevel = validate_loglevel(loglevel)
    formatter = logging.Formatter(message_fmt)
    fh = logging.FileHandler(filename, mode="w", encoding="utf-8")
    # if we set these, then changing the root level has no effect.
    # fh.setLevel(nloglevel)
    fh.setFormatter(formatter)
    logger.addHandler(fh)


def setup_logger():
    """"setup a root level logger with the stdout handler"""
    log = logging.getLogger()
    out_hdlr = logging.StreamHandler(sys.stdout)
    out_hdlr.setFormatter(logging.Formatter(stdout_format))
    # out_hdlr.setLevel(logging.INFO)
    log.addHandler(out_hdlr)
    log.setLevel(logging.INFO)

    log.info("logger setup to info")

    return log


info = logging.info
warning = logging.warning
error = logging.error
critical = logging.critical
debug = logging.debug
level = log_lvl

# format and fill in as you wish.
HelpText = """
log: - This is the builtin logging of SPR -

Control the logging level and send messages to the log.
"""


def help():
    """Additional SPR specific Help for the logs Module."""
    print(HelpText)
