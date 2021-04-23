import pkgutil
from platform import system as platform
from Simple_Process_REPL.options import create_parser
import Simple_Process_REPL.logs as logs
import os
import time
import logging
import Simple_Process_REPL.repl as r
from Simple_Process_REPL.dialog_cli import hello
import yaml

logger = logging.getLogger()

# Application state, which will contain merged data from the application layer.
AS = {
    "config": {},
    "args": {},
    "defaults": {
        "config_file": "SPR-config.yaml",
        "loglevel": "info",
        "logfile": "SPR.log",
    },
    "platform": platform(),
    "Libs": [],
    "_symbols_": [],
}


def set(d):
    """
    merge in a new dict, like the device dictionary, into
    the Application state.
    """
    global AS
    AS = merge(AS, d)


def set_in(keys):
    """Takes a list of keys ending with the value to assign
    into the Application State dictionary tree."""
    global AS
    AS = merge(AS, make_dict(keys))


def set_in_from(keys):
    """Takes 2 lists of keys separated with 'from:' the value to assign
    into the Application State and where to get it from."""
    global AS
    set_keys = []
    from_keys = []
    dest = set_keys
    for k in keys:
        if k == "from:":
            dest = from_keys
            continue
        dest += [k]

    set_keys += [get_in(from_keys)]
    set_in(set_keys)


def merge(a, b, path=None, update=True):
    """nice solution from stack overflow, non-destructive merge.
    http://stackoverflow.com/questions/7204805/python-dictionaries-of-dictionaries-merge
    """
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            elif isinstance(a[key], list) and isinstance(b[key], list):
                for idx, val in enumerate(b[key]):
                    a[key][idx] = merge(
                        a[key][idx],
                        b[key][idx],
                        path + [str(key), str(idx)],
                        update=update,
                    )
            elif update:
                a[key] = b[key]
            else:
                raise Exception("Conflict at %s" % ".".join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a


def make_dict(keys):
    """Create a dictionary tree with a value from a list.
    ie. make_dict(["foo", "bar", value]) => {foo: {bar: value}}
    """
    d = {}
    v = None
    for x in reversed(keys):
        if v is None:
            v = x
        else:
            d = {x: v}
            v = d
    return v


def get_in(keys):
    """Get something out of the Application state."""
    return _get_in(AS, keys)


def _get_in(dict_tree, keys):
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
    return _get_in(AS["config"], keys)


def get_in_device(key):
    "Get to the device info, easier to read."
    return _get_in(AS["device"], [key])


def showin(keys):
    """Show a sub-tree in the Application State"""
    logger.info(yaml.dump(get_in(keys)))


def archive_log(new_name):
    "Move/rename the current logfile to the filename given."
    os.rename(get_in_config(["files", "logfile"]), new_name)


def sync_functions():
    "Sync user functions from the interpreter to the config."
    funcs = r.get_user_functions()
    AS["config"]["exec"]["functions"] = funcs


def islinux():
    """Check if the platform is linux."""
    return "Linux" == AS["platform"]


def reset_device():
    "Start fresh with empty device values."
    new_device = {}
    id = get_in_device("id")

    for k, v in AS["device"]:
        new_device[k] = ""

    new_device["last_id"] = id
    AS["device"] = new_device


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


def load_functions():
    """Give the functions from the configuration to the repl.
    by adding them to the symbol table."""
    # add in the user functions from the config file.

    # fns = get_in_config(['exec', 'functions'])
    # print(yaml.dump(fns))

    fns = get_in_config(["exec", "functions"])
    if fns is not None:
        for k, v in fns.items():
            r.def_symbol(k, v["doc"], v["fn"])


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

    AS["config"] = merge(AS["config"], load_base_config())
    # AS |= state_init  #### destructive...
    AS = merge(AS, state_init)
    if pkgname is None:
        return AS
    AS["config"] = merge(AS["config"], load_pkg_config(pkgname, yamlname))
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


def load_configs():
    global AS
    cli_config = get_in(["args", "config_file"])
    defaults = get_in(["defaults", "config_file"])
    if cli_config is not None:
        y = load_yaml_file(cli_config)
        if y is not None:
            AS["config"] = merge(AS["config"], y)
    elif defaults is not None:
        y = load_yaml_file(defaults)
        if y is not None:
            AS["config"] = merge(AS["config"], y)


def init(parser, logger):
    """
    Parse the cli parameters,
    load the default config or the configuration given,
    start logging,
    initialize the symbol tables for the interpreter.
    Finally, run in whatever mode we were told.
    """
    global AS

    if parser is None:
        parser = create_parser(get_in(["defaults"]))

    AS["args"] = vars(parser.parse_args())

    load_configs()

    logs.add_file_handler(
        logger,
        get_in_config(["files", "loglevel"]),
        get_in_config(["files", "logfile"]),
    )

    logger.info("Hello there, ready to go.")

    # load functions from the config into the interpreter.
    load_functions()


# define all the symbols for the things we want to do.
symbols = [
    [
        "reset-device",
        reset_device,
        "Reset the application state with an empty device.",
    ],
    ["run", eval_default_process, "Run the default process command."],
    [
        "sync-funcs",
        sync_functions,
        "Copy the functions from the REPL into the state, automatic w/save.",
    ],
    ["show", "as device", "Show the device information."],
]

# Name, function, number of args, help string
# Commands we want in the repl which can take arguments.
specials = [
    ["save-config", save_config, 1, "Save the configuration; save-config filename"],
    ["load-config", load_config, 1, "Load a configuration; save-config filename"],
    [
        "as",
        showin,
        -1,
        "Show the Application state data tree, or any subtree or value; as config files",
    ],
    # [
    #     "get-in",
    #     get_in,
    #     -1,
    #     "Get a value vector in the application state; get-in foo bar 10",
    # ],
    [
        "set-in",
        set_in,
        -1,
        "Set a value vector in the application state; set-in foo bar 10",
    ],
    [
        "set-in-from",
        set_in_from,
        -1,
        "Set a value vector in the application state from another value vector; set-in-from foo bar from: bar baz",
    ],
    ["_archive-log", archive_log, 1, "Archive the logfile."],
]

helptext = """Functions to set, get, copy, and show data in the Application State Data Structure."""


def appstate():
    return {
        "name": "appstate",
        "symbols": symbols,
        "specials": specials,
        "doc": helptext,
        "state": None,
    }
