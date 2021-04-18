import pkgutil
from platform import system as platform
from Simple_Process_REPL.options import create_parser
import os
import logging
import Simple_Process_REPL.repl as r
from Simple_Process_REPL.dialog_cli import hello
import yaml

logger = logging.getLogger()

# Application state, which will contain merged data from the application layer.
AS = {
    "device": {"id": "", "name": "", "path": "", "serial_number": "", "last_id": ""},
    "barQR": {
        "src": [],
        "value": "",
        "QR_code": {"code": None, "filename": ""},
        "barcode": {"code": None, "filename": ""},
    },
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
    AS = merge(AS, make_dict(keys))


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


def load_configs():
    global AS
    cli_config = get_in(["args", "config_file"])
    defaults = get_in(["defaults", "config_file"])
    if cli_config is not None:
        y = load_yaml_file(cli_config)
        if y is not None:
            AS["config"] |= y
    elif defaults is not None:
        y = load_yaml_file(defaults)
        if y is not None:
            AS["config"] |= y


def init(parser):
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
