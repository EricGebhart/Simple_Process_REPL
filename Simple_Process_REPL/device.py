import os
import regex as re
import serial
import time
import logging
import Simple_Process_REPL.repl as r
import Simple_Process_REPL.appstate as A

logger = logging.getLogger()


def pause():
    "Sleep for configured number of some # of seconds."
    time.sleep(A.get_in_config(["waiting", "pause_time"]))


def wait_for_file(path, timeout):
    """
    Look for a file at path for the given timeout period.
    returns True or False, works for /dev/ttyUSB...
    """
    start = time.time()
    print("Waiting for Path:", path)
    while not os.path.exists(path):
        if time.time() - start >= timeout:
            return False
    return True


def wait():
    """wait for our device to appear."""
    return wait_for_file(
        A.get_in_device("path"), A.get_in_config(["waiting", "timeout"])
    )


def do_qqc(line):
    do_qqc_regex = A.get_in_config(["test", "do_qqc_regex"])
    if do_qqc_regex:
        return re.match(do_qqc_regex, line)
    return False


def test_line_fails(line):
    fail_regex = A.get_in_config(["test", "fail_regex"])
    result = False
    if re.match(fail_regex, line):
        result = True
        logger.error("Test failed with: %s" % line)
    return result


def test_done(line):
    done_regex = A.get_in_config(["test", "done_regex"])
    result = False
    if re.match(done_regex, line):
        result = True
        logger.info("Test finished with: %s" % line)
    return result


def handshake():
    """
    Handshake with the device after test flash.
    All parameters are set in the configuration.
    Wait for start string, respond with response string.
    Look for fail_regex, done_regex, and do_qqc_regex.
    If fail, raise exception.
    if done, exit quietly with true.
    if do_qqc, then call function and send return to the
    serial device.
    """
    init_string = A.get_in_config(["test", "start_string"])
    response_string = A.get_in_config(["test", "response_string"])
    do_qqc_func = A.get_in_config(["test", "do_qqc_func"])
    baudrate = A.get_in_config(["serial", "baudrate"])
    usb_device = A.get_in_device("path")

    _handshake(usb_device, baudrate, init_string, response_string, do_qqc_func)


def _handshake(usb_device, baudrate, init_string, response_string, do_qqc_func):
    """
    Handshake with the device after test flash.
    All parameters are set in the configuration.
    Wait for start string, respond with response string.
    Look for fail_regex, done_regex, and do_qqc_regex.
    If fail, raise exception.
    if done, exit quietly with true.
    if do_qqc, then call function and send return to the
    serial device.
    """

    result = False  # start with failure, until we get the handshake.

    logger.info("Wait for string: %s" % init_string)
    # timout=None makes this a blocking call that waits.
    with serial.Serial(usb_device, baudrate, timeout=None) as ser:
        got_string = ser.read(size=len(init_string)).decode("utf-8")
        logger.info("Caught: %s" % got_string)

        # send the response and then wait for test results.
        if got_string == init_string:
            logger.info("Sending Response: %s" % response_string)
            ser.write(bytes(response_string, "utf-8"))

            # so far so good, get ready to fail.
            result = True
            logger.info("Waiting for test results.")

            while True:
                line = ser.readline().decode("utf-8")
                logging.info(line)

                if test_line_fails(line):
                    result = False
                    # break
                    ser.close()
                    raise Exception("Fail: %s" % line)

                if do_qqc_func is not None and do_qqc(line):
                    func = r.get_symbol(do_qqc_func)["fn"]
                    response = bytes(func() + "\n", "utf-8")
                    ser.write(response)

                if test_done(line):
                    break

            ser.close()
    return result
