import pkgutil
from platform import system as platform
from Simple_Process_REPL.options import create_parser
import Simple_Process_REPL.logs as logs
import os
import logging
import Simple_Process_REPL.repl as r
import Simple_Process_REPL.utils as u
from Simple_Process_REPL.dialog import hello
import yaml

logger = logging.getLogger()

# format and fill in as you wish.
HelpText = """
appstate: - Manage SPR's Application state.  -

Everything needed to load, save, copy, set, and merge data
in the Application state. Yaml files and merging etc.

Appstate is the Application State.

When writing python code to interact with SPR the appstate functions
get_in, set_in, get_in_config, and get_in_device are of primary
use.

Within SPR code, showin, set-in, and set-in-from are of primary use.

"""


def help():
    print(HelpText)


# Application state, which will contain merged data from the application layer.
AS = {
    "config": {},
    "args": {"commands": {}},
    "defaults": {
        "config_file": "PBRConfig.yaml",
        "loglevel": "info",
        "logfile": "PBR.log",
    },
    "platform": "",
}


def set(d):
    """
    merge in a new dict, like the device dictionary, into
    the Application state.
    """
    global AS
    AS = u.merge(AS, d)


def set_in(*keys):
    """Takes a list of keys ending with the value to assign
    into the Application State dictionary tree."""
    global AS
    AS = u.merge(AS, u.make_dict(*keys))


def set_in_from(*keys):
    """Takes 2 lists of keys separated with 'from:' the value to assign
    into the Application State and where to get it from."""
    global AS
    set_keys = []
    from_keys = []
    dest = set_keys
    for k in keys[0]:
        if k == "from:":
            dest = from_keys
            continue
        dest += [k]

    set_keys += [get_in(from_keys)]
    set_in(set_keys)


def get_in(keys):
    """Get something out of the Application state."""
    global AS
    return _get_in(AS, keys)


def _get_in(dict_tree, keys):
    """
    Retrieve a value from a dictionary tree, using a key list
    Returns:
       The value found at the given key path, or `None` if
       any of the keys in the path is not found.
    """

    # logger.info("_get_in")
    # logger.info(dict_tree.keys())
    # logger.info(keys)
    # logger.info("_get_in")

    try:
        for key in keys:
            # logger.info("key %s" % key)
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


def showin(*keys):
    """Show a sub-tree in the Application State"""
    if len(keys) == 0:
        # remove _Root_ from showing unless asked.
        qqc = AS | {"_Root_": None}
    else:
        qqc = get_in(*keys)
    logger.info(yaml.dump(qqc))


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


def merge_yaml(y):
    """Merge a yaml data structure into the Application state."""
    logger.info("Merge Yaml: %s:" % y)
    u.merge(AS, yaml.load(y, Loader=yaml.SafeLoader))


def load_functions():
    """Give the functions from the configuration to the repl.
    by adding them to the symbol table."""
    # add in the user functions from the config file.

    fns = get_in_config(["exec", "functions"])
    # logger.info(yaml.dump(fns))

    if fns is not None:
        for k, v in fns.items():
            r.def_symbol(k, v["doc"], v["fn"])


def load_defaults(state_init, pkgname=None, yamlname=None):
    global AS

    bc = load_base_config()
    if bc:
        AS["config"] = u.merge(AS["config"], bc)
        # AS |= state_init  #### destructive...
    AS = u.merge(AS, state_init)
    if pkgname is None:
        return AS
    AS["config"] = u.merge(AS["config"], u.load_pkg_yaml(pkgname, yamlname))
    return AS


def merge_pkg_yaml(pkgname, yamlname):
    """load a yaml file from a package into the application state."""
    global AS
    AS = u.merge(AS, u.load_pkg_yaml(pkgname, yamlname))


# import pkg_resources
def load_pkg_config(pkgname, yamlname):
    """load a configuration file from a package."""
    logger.info("Loading YAML from Module: %s: %s" % (pkgname, yamlname))
    try:
        some_yaml = yaml.load(
            pkgutil.get_data(pkgname, yamlname), Loader=yaml.SafeLoader
        )
    except FileNotFoundError:
        pass
    except Exception as e:
        print(e)
    return some_yaml


def load_base_config():
    """load the default configuration."""
    return load_pkg_config(__name__, "SPR-defaults.yaml")


def save_config(filename):
    "Sync the functions from the interpreter and save the configuration."
    sync_functions()
    u.save_yaml_file(filename, AS["config"])


def load_config(filename):
    """load a yaml file into the application's
    configuration dictionary.
    """
    AS["config"] = u.load_yaml_file(filename)


def load_configs():
    global AS
    cli_config = get_in(["args", "config_file"])
    defaults = get_in(["defaults", "config_file"])
    if cli_config is not None:
        y = u.load_yaml_file(cli_config)
        if y is not None:
            AS["config"] = u.merge(AS["config"], y)
    elif defaults is not None:
        y = u.load_yaml_file(defaults)
        if y is not None:
            AS["config"] = u.merge(AS["config"], y)


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
    set_in(["platform", platform()]),

    # load functions from the config into the interpreter.
    load_functions()
