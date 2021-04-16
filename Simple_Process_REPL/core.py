import pkgutil
import Simple_Process_REPL.dialog_cli as D
import Simple_Process_REPL.bar_qr as bq
from sys import exit
import logging
import Simple_Process_REPL.logs as logs
from Simple_Process_REPL.options import create_parser
import os
from platform import system as platform
import Simple_Process_REPL.repl as r

import regex as re
import serial
import subprocess
import time
import yaml


"""
The main functionality here is to manage options and configurations and
logging, as well as define some functions which provide the necessary
functionality we need to define a sparse middle layer between the
REPL/interpreter and the interface layer to the Application.


This file defines the symbol table for the interpreter,
initializes the application, and then runs in the requested manner.

The symbols defined here are of a generic application nature.
save and load configurations, show variables, get help, all
the sorts of commands that can live here.

This layer does maintain a dictionary of state called AS,
It integrates the state map as given by the application.
functions are provided for easy access to everything the
application's function layer needs.

Aside from the functions declared here, and in the
application main.py, functionality is defined by interpreted lists
of symbols which live in the YAML config file. They can also be
coded here, but that is only really necessary if new functionality
is desired.

The repl allows for the creation of new function/commands interactively.
Those functions can then be saved as part of the configuration or separately.

The process to be run automatically should be a function in the symbol table
By default, or if not found, the 'hello' function is used.
The autoexec attribute in the configuration names the command(s) to run when
running in a loop or one time with no commands.
"""


# Application state, which will contain merged data from the application layer.
AS = {
    "device": {"id": "", "name": "", "path": "", "serial_number": "", "last_id": ""},
    "BarQR-code": {
        "src": []
        "value": ""
        "QR_code":{"code": None "filename": ""}
        "barcode":{"code": None "filename": ""}}
    "config": {},
    "args": {},
    "wifi-connected": False,
    "defaults": {
        "config_file": "SPR-config.yaml",
        "loglevel": "info",
        "logfile": "SPR.log",
    },
    "platform": platform(),
}


def reset_device():
    "Start fresh with empty device values."
    new_device = {}
    id = get_in_device("id")

    for k, v in AS["device"]:
        new_device[k] = ""

    new_device["last_id"] = id
    AS["device"] = new_device


def set(d):
    """
    merge in a new dict, like the device dictionary, into
    the Application state.
    """
    global AS
    AS |= d


def set_in(keys):
    """Takes a list of keys ending with the value to assign
    into the Application State dictionary tree."""
    global AS
    AS |= make_dict(keys)


def make_dict(keys):
    """Create a dictionary tree with a value from a list.
    ie. make_dict(["foo", "bar", value]) => {foo: {bar: value}}
    """
    d = {}
    v = None
    for x in keys.reverse():
        if v is None:
            v = x
        else:
            d[x] = v
            v = d
    return d


def get_in(dict_tree, keys):
    """
    Retrieve a value from a dictionary tree, using a key list
    Returns:
       The value found at the given key path, or `None` if
       any of the keys in the path is not found.
    """

    logger.debug(keys)
    try:
        for key in keys:
            logger.debug("key %s" % key)
            dict_tree = dict_tree[key]

        return dict_tree

    except KeyError:
        return None


# could have been a partial.
def get_in_config(keys):
    "Get stuff from the config, takes a list of keys."
    return get_in(AS["config"], keys)


def get_in_device(key):
    "Get to the device info, easier to read."
    return get_in(AS["device"], [key])


def islinux():
    """Check if the platform is linux."""
    return "Linux" == AS["platform"]


def input_string_to(msg, keys):
    """Dialog to get a string and set it in the Application state with a value vector."""
    v = keys + input_string("msg")
    set_in(v)


def input_string_to_v(v):
    """varargs version of input_string_to which takes a vector,
    the first entry should be a string which will be displayed in the dialog window."""
    input_string_to(v[0], v[1:])


def input_sn():
    """Dialog to get a serial number and set it on the device."""
    input_string_to("Enter a serial Number", ["device", "serial_number"])


BarCodeType = "barcode"
QRCodeType = "QR_code"

def set_bcqr_code_from(keys):
    v = get_in(AS, keys)
    set_bcqr_code(keys, v)


def set_bcqr_code(keys, v):
    set-in(["BarQR-code", "src", keys])
    set-in(["BarQR-code", "value", v])


def get_bcqr(codetype=BarCodeType):
    "Get a bar code for the current barQR value."
    try:
        v = get_in(AS, ["barQR", "value"])
        if codetype == BarCodeType:
                code = bq.create_bar_code(bq.serial_num_2_barcode(v))])
        elif codetype == QRCodeType:
                code = q.create_qr_code(bq.serial_num_2_qrcode(v))])

        set_in(["barQR", codetype, "code", code])
        set_in(["barQR", codetype, "saved" ""]))

    except Exception as e:
        print(e)


def save_bcqr(codetype=BarCodeType):
    "Save the codetype, 'barcode/QR_code', for the current barQR value to it's png file"
    sn = get_in(AS, ["barQR", "value"])
    code = get_in(AS, ["barQR", codetype, "code"])
    fn = bq.get_bc_filename(sn)
    bq.save_bar_code(code, fn)
    set_in(["barQR", codetype, "saved", fn]))


def print_bcqr(codetype=BarCodeType):
    """save the current barcode for the serial number"""
    cmd_name, print_command = print_command_radio()
    fn = get_in(AS, ["device", codetype, "saved"])
    command = print_command % fn
    logger.info("Printing %s %s to %s" % (codetype, fn, cmd_name))
    os.system(command)

def print_file(name):
    """Given a name, prompt for the printer and print the file."""
    cmd_name, print_command = print_command_radio()
    command = print_command % name
    logger.info("Printing file %s to %s" % (name, cmd_name))
    os.system(command)


def print_file_from(keys):
    """Given a value vector, print the filename value held there."""
    print_file(get_in(AS, keys))


def BC_or_QR():
    label_type = bq.dialog_BC_or_QR()
    if label_type == "Bar Code":
       return BarCodeType
    elif label_type == "QR Code":
       return QRCodeType


def print_codes():
    """Ask for a number, then print some number of bar or qr codes.
    See the `serial_number` section of the configuration."""

    input_string_to("Enter a code to print", ["barQR", "value"])
    codetype = BC_or_QR()
    get_bcqr(codetype)
    save_bcqr(codetype)
    fn = get_in(AS, ["barQR", codetype, "saved", fn]))

    cmd_name, print_command = print_command_radio()
    count = input_count("How many to Print ?")
    command = print_command % fn

    if ynbox(
        "You are ready to print %d %s label(s) of %s to %s?" %
            (count, label, sn, cmd_name)):

        command = print_command % fn
        for i in range(0, count):
            os.system(command)



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


def check_connection():
    "Check the wifi connection with Network manager"
    if islinux():
        logger.debug("check connection!")
        res = do_cmd(["nmcli", "device"])
        logger.debug(res)
        if len(re.findall("connected", res)):
            AS["wifi-connected"] = True
        else:
            AS["wifi-connected"] = False
            return False
        return True
    return False


def get_SSIDS():
    # get first column.
    cmd = ["nmcli", "connection", "show"]
    res = do_cmd(cmd)
    ssids = []
    for line in res.split("\n"):
        ssids.append(line.split(" ")[0])

    return ssids


def connect_SSID(ssid):
    """Connect the wifi to the SSID given."""
    cmd = ["nmcli", "device", "wifi", "connect", ssid]
    res = do_cmd(cmd)
    logger.info(res)


def connect_wifi():
    """
    Connect the wifi, get the SSID's, give a selection dialog to choose,
    then connect to the chosen SSID. Only implemented for linux for use
    with network manager.
    """
    if islinux():
        if not check_connection():
            ssids = get_SSIDS()
            menuitems = []
            for ssid in ssids:
                menuitems.append([ssid, ssid])
            ssid = select_choice("Choose an SSID to Connect.", menuitems)
            if ssid is not None:
                logger.info("Connecting to %s" % ssid)
                connect_SSID(ssid)


def confirm_tunnel():
    "Confirm the ssh tunnel is established"
    pass


def create_tunnel(pem_file, server):
    "Create an ssh tunnel."
    pass


def connect_tunnel():
    "Connect to an ssh tunnel"
    pass


def sendlog():
    "Send the log somewhere."
    pass


def pause_a_sec():
    "sleep for configured number of some # of seconds."
    time.sleep(get_in_config(["waiting", "pause_time"]))


def wait_for_file(path, timeout):
    """
    look for a file at path for the given timeout period.
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
    return wait_for_file(get_in_device("path"), get_in_config(["waiting", "timeout"]))


def do_qqc(line):
    do_qqc_regex = get_in_config(["test", "do_qqc_regex"])
    if do_qqc_regex:
        return re.match(do_qqc_regex, line)
    return False


def test_line_fails(line):
    fail_regex = get_in_config(["test", "fail_regex"])
    result = False
    if re.match(fail_regex, line):
        result = True
        logger.error("Test failed with: %s" % line)
    return result


def test_done(line):
    done_regex = get_in_config(["test", "done_regex"])
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
    init_string = get_in_config(["test", "start_string"])
    response_string = get_in_config(["test", "response_string"])
    do_qqc_func = get_in_config(["test", "do_qqc_func"])
    baudrate = get_in_config(["serial", "baudrate"])
    usb_device = get_in_device("path")

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


def showall():
    "Show everything we have in our configuration and state."
    logger.info(yaml.dump(AS))


def showin(keys):
    """Show a sub-tree in the Application State"""
    logger.info(yaml.dump(get_in(AS, keys)))


def show():
    "Show the Device data in the application state."
    showin(["device"])


def archive_log(new_name):
    "Move/rename the current logfile to the filename given."
    os.rename(get_in_config(["files", "logfile"]), new_name)


def sync_functions():
    "Sync user functions from the interpreter to the config."
    funcs = r.get_user_functions()
    AS["config"]["exec"]["functions"] = funcs


def hello():
    "Just in case we don't know what to do."
    msg = """You have received this message because your autoexec attribute is
    set to 'hello' or None, or can't be found. Maybe make some new commands
    to create some processes. When you get a command you want to run
    automatically set autoexec exec/autoexec in the config file to it's name.
    Here are the commands the interpreter currently recognizes."""
    print(msg)
    D.msgcli(get_in_config(["dialogs", "continue"]))
    help()
    D.msgcli(get_in_config(["dialogs", "continue"]))


def application_help():
    """Print help as defined by the function set in ['exec', 'help']
    in the config. This is a help function as defined by the
    application layer, which is specific to the functionality
    that we are interfacing with.
    """
    r.eval_cmd(get_in_config(["exec", "help"]))


def help():
    "Everyone needs a little help now and then."
    print(
        """Internal command help.\n
            These are the defined symbols for this REPL. Symbols
            may be listed to execute them in order.\n"""
    )

    application_help()

    r.funcptr_help()

    r.specials_help()

    r.compound_help()

    print("\n\n")


def eval_default_process():
    "Run the autoexec process"
    autoexec = get_in_config(["autoexec"])
    if autoexec is not None:
        try:
            r.eval_cmd(autoexec)
        except Exception as e:
            logger.error(e)
            raise Exception(e)
    else:
        hello()


# define all the symbols for the things we want to do.
_symbols = [
    ["hello", hello, "Hello message."],
    # beginning of local functions.
    ["wifi", connect_wifi, "Connect to wifi using nmtui if not connected."],
    ["connect_tunnel", connect_tunnel, "Connect through an ssh tunnel."],
    ["create_tunnel", create_tunnel, "Create an ssh tunnel."],
    ["reset-device", reset_device, "Reset the application state with an empty device."],
    ["wait", wait, "Wait for the usb device to come back."],
    ["show", show, "showin device, something something."],
    ["show-all", showall, "show everything we know currently."],
    [
        "handshake",
        handshake,
        "Look for the test start string, send the response, catch results.",
    ],
    ["pause", pause_a_sec, ("Pause/Sleep for 'pause_time' seconds")],
    ["run", eval_default_process, "Run the default process command."],
    [
        "sync-funcs",
        sync_functions,
        "Copy the functions from the REPL into the state, automatic w/save.",
    ],
    # dialog functions
    ["dialog-start", D.dialog_start, "Dialog, for ready to start ?"],
    ["dialog-test", D.dialog_test, "Dialog, ready to test ?"],
    ["dialog-flash", D.dialog_flash, "Dialog, ready to flash ?"],
    ["dialog-failed", D.dialog_failed, "Dialog, ready to flash ?"],
    ["dialog-finish", D.dialog_finish, "Dialog, Unplug, power off."],
    ["cli-start", D.cli_start, "Dialog, for ready to start ?"],
    ["cli-test", D.cli_test, "Dialog, ready to test ?"],
    ["cli-flash", D.cli_flash, "Dialog, ready to flash ?"],
    ["cli-failed", D.cli_failed, "Dialog, ready to flash ?"],
    ["cli-finish", D.cli_finish, "Dialog, Turn out the lights, Unplug, power off."],

    ["print-codes", print_codes, "Dialog to take a number, and print any number of barcodes or QR codes."],

    ["help", help, "Repl help, list symbols and their help."],
    ["quit", exit, "Quit"],
]


def load_functions():
    """Give the functions from the configuration to the repl.
    by adding them to the symbol table."""
    # add in the user functions from the config file.

    # fns = get_in_config(['exec', 'functions'])
    # print(yaml.dump(fns))

    fns = get_in_config(["exec", "functions"])
    if fns is not None:
        for k, v in fns.items():
            r.add_symbol(k, v["fn"], v["doc"])


def save_yaml_file(filename, dictionary):
    "Write a dictionary as yaml to a file"
    with open(filename, "w") as f:
        yaml.dump(dictionary, f)


def load_yaml_file(filename):
    "load a dictionary from a yaml file"
    if os.path.isfile(filename):
        logger.info("Loading Configuration: %s" % filename)
        with open(filename) as f:
            someyaml = yaml.load(f, Loader=yaml.SafeLoader)
        return someyaml


def load_defaults(state_init, pkgname=None, yamlname=None):
    global AS

    AS["config"] |= load_base_config()
    AS |= state_init
    if pkgname is None:
        return AS
    AS["config"] |= load_pkg_config(pkgname, yamlname)
    return AS


# import pkg_resources
def load_pkg_config(pkgname, yamlname):
    """load a configuration file from a package."""
    logger.info("Loading Configuration: %s: %s" % (pkgname, yamlname))
    return yaml.load(pkgutil.get_data(pkgname, yamlname), Loader=yaml.SafeLoader)
    # f = pkg_resources.resource_filename(pkgname, yamlname)
    # print(f)
    # print(load_yaml_file(f))
    # return load_yaml_file(f)


def load_base_config():
    """load the default configuration."""
    return load_pkg_config(__name__, "SPR-defaults.yaml")


def save_config(filename):
    "Sync the functions from the interpreter and save the configuration."
    sync_functions()
    save_yaml_file(filename, AS["config"])


def load_config(filename):
    """load a yaml file into the application's
    configuration dictionary.
    """
    AS["config"] = load_yaml_file(filename)


def log_lvl(lvl):
    """Change the logging level."""
    logs.set_level(logging.getLogger(), lvl)


# Name, function, number of args, help string
# Commands we want in the repl which can take arguments.
_specials = [
    ["save-config", save_config, 1, "Save the configuration; save-config filename"],
    ["load-config", load_config, 1, "Load a configuration; save-config filename"],
    ["msgbox", D.msgbox, 1, 'Give a dialog message box; msgbox "some message"'],
    [
        "msgcli",
        D.msgcli,
        1,
        'Give a message to continue at the command line; msgbox "some message"',
    ],
    [
        "loglvl",
        log_lvl,
        1,
        "Change the logging level; loglvl <debug|info|warning|error|critical>",
    ],
    ["log_info", logging.info, 1, 'Send a messag to logging; log_info "some message"'],
    [
        "log_debug",
        logging.debug,
        1,
        'Send a debug message to logging log_debug "some debug message"',
    ],
    [
        "showin",
        showin,
        -1,
        "Show the value in the Application state; showin config files",
    ],
    [
        "set-in",
        set_in,
        -1,
        "Set a value vector in the application state; setin foo bar 10",
    ],
    [
        "input-string-to",
        input_string_to,
        -1,
        'prompt for an input and set it to the value vector; input_string_to "some msg" "device" "serial_number"',
    ],
    [
        "set-bcqr-from",
        set_bcqr_from,
        -1,
        'Set the BarQR value to the value at the value vector given; set-bcqr-from device serial_number',
    ],
    ["get-bcqr", get_bcqr, 1, 'load a barcode or QR code for the current value; get-bcqr "barcode"]',
    ["save-bcqr", save_bcqr, 1, 'save the current barcode or QR code to a file; save-bcqr "barcode"]',
    ["print-bcqr", save_bcqr, 1, 'print the current barcode or QR code file; print-bcqr "barcode"]',
    ["print-file", print_file, 1, "Print a file; print-file foo.txt"],
    ["print-file-from", print_file_from, -1,
     "Print a file using the string stored at the value vector; print-file-from barQR QR_code saved"],
    ["rm-file", os.remove, 1, "Remove a file; rm-file foo.txt"],
    ["_archive-log", archive_log, 1, "Archive the logfile."],
    ["sleep", time.sleep, 1, "Sleep for specified seconds; sleep 5"],
    ["sh", do_shell, -1, "Run a shell command; sh ls -l"],
]


# endless loop with dialog next y/n.
def interactive_loop():
    """Execute the autoexec command in an interactive
    loop which reports failures and prompts to do another.
    """
    interactive = AS["args"]["interactive"]
    while interactive is True:
        try:
            do_one()
            if continue_to_next_dialog():
                interactive = False
        except Exception as e:
            logger.error(e)
            if continue_to_next_dialog():
                interactive = False
        reset_device()


def do_one():
    """Execute the default process one time, with fail and finish dialogs"""
    try:
        eval_default_process()
        D.dialog_finish()

    except Exception as e:
        logger.error("Device Failed")
        logger.error(e)
        D.dialog_failed()
        D.dialog_finish()


def do_something():
    """
    Maybe start the REPL,
    or Run the autoexec in a loop,
    or Run the autoexec once,
    or Run commands given on the cli.
    """

    commands = " ".join(AS["args"]["commands"])

    # Run the repl.
    if AS["args"]["repl"]:
        r.repl(get_in_config(["REPL", "prompt"]))

    # if there aren't any commands on the cli
    # do the auto exec in a loop or once.
    elif len(commands) == 0:
        if AS["args"]["interactive"] is True:
            interactive_loop()
        else:
            do_one()

    # run the commands given on the cli.
    else:
        logger.info("Attempting to do this: %s", commands)
        r.eval_cmd(commands)


logger = logs.setup_logger()


def merge_state(state_dict):
    """
    Merge the application's State dictionary with
    the defaults as needed.
    """
    global AS

    # python 3.9 syntax to merge two dictionaries.
    # Load the base configuration
    AS["config"] |= load_base_config()

    # Merge the application state
    AS |= state_dict


def get_parser():
    """
    Create a parser with some defaults and return it so the app can
    add parameters, groups, etc.
    """
    global AS

    return create_parser(AS["defaults"])


def init(symbols, specials, parser):
    """
    Parse the cli parameters,
    load the default config or the configuration given,
    start logging,
    initialize the symbol tables for the interpreter.
    Finally, run in whatever mode we were told.
    """
    global AS

    if parser is None:
        parser = get_parser()

    AS["args"] = vars(parser.parse_args())

    if get_in(AS, ["args" "config_file"]):
        y = load_yaml_file(AS["args"]["config_file"])
        if y is not None:
            AS["config"] |= y
    elif get_in(AS, ["defaults", "config_file"]):
        y = load_yaml_file(get_in(AS, ["defaults", "config_file"]))
        if y is not None:
            AS["config"] |= y

    # print(get_in_config(["files", "loglevel"]))

    logs.add_file_handler(
        logger,
        get_in_config(["files", "loglevel"]),
        get_in_config(["files", "logfile"]),
    )

    logger.info("Hello there, ready to go.")

    load_functions()

    r.init(_symbols, _specials)
    r.init(symbols, specials)

    do_something()
