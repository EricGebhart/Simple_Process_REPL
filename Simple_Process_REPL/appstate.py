import pkgutil
from platform import system as platform
from Simple_Process_REPL.options import create_parser
import Simple_Process_REPL.logs as logs
import os
from uuid import uuid4
import logging
import Simple_Process_REPL.repl as r
import Simple_Process_REPL.utils as u
from Simple_Process_REPL.dialog import hello
import yaml

logger = logging.getLogger()

# format and fill in as you wish.
HelpText = """
appstate: - Manage SPR's yaml datastore.  -

Everything needed to load, save, copy, set, and merge data
in the yaml datastore. Yaml files and merging etc.

Appstate is the Yaml Datastore.

When writing python code to interact with SPR the appstate functions
get_in, set_in, get_in_config, and get_in_device are of primary
use.

Within SPR code, show, set, and set-from are of primary use.

"""

#  this  is where  we  will look for the path to the with stack.
WITH_PATH = "/_with_path_"


def help():
    """Additional SPR help For the appstate Module."""
    print(HelpText)


# yaml datastore, which will contain merged data from the application layer.
AS = {
    "config": {},
    "__gensyms__": {},
    "args": {"commands": {}},
    "defaults": {
        "config_file": "PBRConfig.yaml",
        "loglevel": "info",
        "logfile": "PBR.log",
    },
    "platform": "",
    "with_depth": -1,
    "_with_path_": "/_with_",
    "_with_": [],
}


def gensym(prefix="__G__"):
    """Create a unique symbol"""
    return prefix + str(uuid4())


def setgensym(value, prefix=None):
    """Create and set a gensym in __gensyms__, returning it's name"""
    if prefix is not None:
        gs = gensym(prefix)
    else:
        gs = gensym()

    # logger.inf("merge: %s" % root)
    gv = ["__gensyms__", gs] + value
    d = u.make_dict(gv)

    # logger.info(d)
    u.merge(AS, d)
    return gs


def getgensym(sym):
    """Convenience function to get a gensym's value."""
    path = ["__gensyms__", sym]
    return get_in(path)


def get_with_path():
    """Return the  path  to the current with  stack."""
    path = get_in(_get_vv_from_path(WITH_PATH))
    return path


def get_with_stack():
    """Return  the entire with stack."""
    return get_in(_get_vv_from_path(get_with_path()))


def show_with():
    """Show the with stack as a series of yaml trees, Omitting '/'."""
    for path in get_with_stack():
        if not path == "/":
            show(path)


def last_with():
    """Return the current 'With' path."""
    with_stack = get_with_stack()
    if len(with_stack) == 0:
        return "/"
    else:
        return nth(-1, with_stack)


def last_with_vv():
    """Return the current 'With' Vector."""
    path = last_with()
    if path == "/":
        return []
    else:
        return _get_vv_from_path(path)


def _push_with(path):
    """push a path onto the current with stack.
    Tries to resolve where the current with stack is and pushes path to it.
    Equivalent to 'push ~/_with_path_ /some/path' in SPR."""
    wp = get_with_path()
    if isinstance(path, list):
        _set_in(" ", get_with_path())
        _set_in(path, get_with_path())
    else:
        push(wp, path)


def _pop_with(path):
    """pop a path off of the current with stack.
    Equivalent to 'pop ~/_with_path_' in SPR."""
    pop(get_with_path())


def _ls_with():
    path = last_with()
    print(path)
    print("-------------------------")
    if path[0] == "/":
        if len(path) == 1:
            keys = get_keys_in()
        else:
            vv = path[1:].split("/")
            keys = get_keys_in(*vv)

    if keys:
        for k in keys:
            print("    %-30s" % k)
    else:
        print("   Is Empty.")


def _with(wpath=None, wcommand=None, destpath=None):
    """
    Show the current 'With' path or if a path is given,
    Push a datastore path onto the 'with' stack.

    if wpath is a list, that list will replace the current with stack
    in it's entirety.

    If it is not yet there, it will appear when someone sets something.

    If a command is given, execute the command and pop.
    if a destination is given pop the last result to that path.
    """
    #    logger.info("_with %s" % path)
    #    logger.info("_stack %s" % with_stack)

    if not isinstance(wpath, list):

        if wpath is None:
            _ls_with()
            return

        if wpath[0] != "/":
            wpath = "/" + wpath

        vv = _get_vv_from_path(wpath)
        set_in(vv + [{}])

    _push_with(wpath)

    # if there is a command, either
    # pop the result to the path or pushed with. before popping.
    # if destination starts with a . it is taken to mean the
    # the with from which this with was launched.
    # not sure this is a good idea.
    #
    if wcommand:
        r.eval_cmd(wcommand)
        if destpath is not None:
            if destpath[0] == ".":
                g = gensym()
                pop("results", g)
                _pop_with()
                set(destpath, g)
            else:
                pop("results", destpath)
        else:
            _pop_with()
    else:
        try:
            _ls_with()
        except Exception:
            pass


def _full_with_path(path):
    """Takes a path and prepends the with path."""
    withpath = last_with()

    if withpath != "/" and path[0] != "/":
        path = "/" + path
    return withpath + path


def get_in_with(path):
    vv = last_with_vv() + _get_vv_from_path(path)
    return get_in(vv)


def select_keys(m, keys):
    """Given a map and list of keys,
    return a map of with those keys from the map.
    """
    d = {}
    # logger.info("select-keys: %s, %s" % (keys, m))
    try:
        for k in keys:
            if m.__contains__(k):
                d[k] = m[k]
    except Exception as e:
        logger.info(e)
        pass
    # logger.info("select-keys: %s" % d)
    return d


def flat_with():
    """Print the flattened with in YAML."""
    print(yaml.dump(flatten_with(), Dumper=NoAliasDumper))


def get_in_stack(symbol):
    """Get a value from the with stack. Returns the value
    or none."""
    return flatten_with().get(symbol, None)


def _get(symbol_or_path):
    """Get  a path  or symbol value from somewhere.

    / means its a full path.
    . means local to the current with
    nothing means to look in the with stack for resolution.
    """
    if symbol_or_path[0] == "/" or symbol_or_path[0] == ".":
        return get(symbol_or_path)
    else:
        return get_in_stack(symbol_or_path)


def flatten_with():
    """Go through the with stack and flatten it,
    Only go to the depth set by /with_depth.

    If < 0 will go all the way to the layer above /.

    A simple method for variable resolution with scope.
    returns a map of the flattened with values.
    """
    depth = get_in(["with_depth"])
    fd = {}
    i = 0
    with_stack = get_with_stack()
    for w in with_stack[1:]:
        d = get_in(_get_vv_from_path(w))
        fd |= d

        if depth >= 0 and i == depth:
            break
        i += 1

    return fd


def select_with(keys):
    """Given a list of keys,
    return a map of with those keys from the with map.
    """
    # used to be get_with()
    return select_keys(flatten_with(), keys)


def get_with():
    """Return the current with map."""
    return get_in(last_with_vv())


def _set_(d):
    """Merge in a new dict, like the device dictionary, into
    the yaml datastore.
    """
    global AS
    AS = u.merge(AS, d)


def _set_in(value, path=None):
    """Set a value at path or with-path if path is None."""
    set_in(resolve_path(path) + [value])


def set_in(*keys):
    """Takes a list of keys ending with the value to assign
    into the Yaml Datastore dictionary tree."""
    global AS
    AS = u.merge(AS, u.make_dict(*keys))


def _get_vv_from_path(path):
    if path is None:
        return ["_Root_"]
    if path[0] == "/":
        path = path[1:]
    return path.split("/")


def get_from_path(path):
    vv = _get_vv_from_path(path)
    return get_in(vv)


def clear_path(path):
    """clear the value at path."""
    global AS
    set_keys = get_vv(path)
    set_keys += [""]
    AS = u.merge(AS, u.make_dict(set_keys))


def pop(path, destination=None):
    """if the path is a list , pop the last value,
    if it is not a list, clear it.
    If destination is set, place the value popped there.
    """
    if path[0] != "/":
        value = get_in_with(path)
    else:
        value = get_from_path(path)

    if value is None:
        logger.info("Pop: %s not found, no thing to pop." % path)
        return

    if isinstance(value, list):
        if len(value):
            v = value.pop()
        else:
            v = None

    else:
        clear_path(path)
        v = value

    if destination is not None and v is not None:
        if destination[0] == ".":
            destination = last_with()

        set(destination, v)


def push(set_path, fromv):
    """Takes a path or path symbol and a value
    or 2 paths.

    Honors 'with'.

    Values beginning with / will be
    treated a path, otherwise as a symbol/value.

    pushes the value onto the list at set_path.
    """
    global AS

    # set_keys = _get_vv_from_path(_full_with_path(set_path)[1:])
    set_keys = _get_vv_from_path(set_path)
    val = get_fromv(fromv)

    # get the thing at the path. hopefully it's a list.
    try:
        if set_path[0] == "/":
            dest = get(set_path)
            set_keys = _get_vv_from_path(set_path)
        else:
            dest = get_in_with(set_path)
            set_keys = _get_vv_from_path(_full_with_path(set_path)[1:])
    except Exception:
        dest = None

    if not isinstance(val, list):
        val = [val]

    # pushing a list appends it, I don't know if I like that.
    if dest:
        if not (isinstance(dest, list) or isinstance(dest, dict)):
            dest = [dest]
            dest += val
        else:
            # do it directly
            dest += val
    else:
        dest = val

    set_keys += [dest]
    AS = u.merge(AS, u.make_dict(set_keys))


def swap(path):
    """If the path is a list , swap the last 2 values.
    Otherwise do nothing.
    """
    if path is None or len(path) == 0:
        return

    logger.info("swapping %s" % path)

    if path[0] != "/":
        value = get_in_with(path)
    else:
        value = get_from_path(path)

    if isinstance(value, list):
        last = value.pop()
        newlast = value.pop()
        value += [last]
        value += [newlast]


def nth(nth, path):
    """If the path is a list , return the nth value.
    Otherwise do nothing.
    """
    if path is None or len(path) == 0:
        return "Not found"

    if isinstance(path, list) or isinstance(path, str):
        if len(path) >= nth:
            v = path[nth]
            return v

    return "Not found"


def rest(path):
    """If the path is a list or string, return all but the first value."""
    if path is None or len(path) == 0:
        return "Not found"

    if isinstance(path, list) or isinstance(path, str):
        v = path[1:]
        return v

    return "Not found"


def reverse(path):
    """If the path is a list or string, return all but the first value."""
    if path is None or len(path) == 0:
        return "Not found"

    if isinstance(path, str) or isinstance(path, list):
        v = path[::-1]
        return v

    return "Not found"


def dedup(path):
    """If the path is a list remove duplicates, first wins."""
    res = []

    if isinstance(path, list):
        for item in path:
            if item not in res:
                res.append(item)
    return res


# This seems weird to me. Less so now that most of it is a comment.
def get_fromv(fromv):
    """Get the value from there, if it's a there.
    If its raw value is a list, then it's a string from the parser.
    if it's a path, then get the value."""
    if isinstance(fromv, int) or isinstance(fromv, float):
        fromv = fromv

    # elif isinstance(fromv, str):
    #     # path = r.isa_path(fromv)
    #     # if path
    #     #     fromv = _get_vv_from_path(path)
    #     # else:

    # if fromv[0] == "/":
    #     fromv = get_from_path(fromv[1:])

    # elif fromv[0] == ".":
    #     vv = _get_vv_from_path(fromv[1:])
    #     fromv = get_in(last_with_vv() + vv)

    # haven't found the reason this was here yet.
    # elif isinstance(fromv, list):
    #     res = None
    #     for x in fromv:
    #         if res is None:
    #             res = str(x)
    #         else:
    #             res = res + " " + str(x)
    #             fromv = res
    if isinstance(fromv, list):
        fromv = fromv.copy()

    # elif fromv and len(fromv) == 1:
    #    fromv = fromv  # [0]

    # logger.info("fromv: %s" % fromv)
    return fromv


def get_vv(set_path):
    """return the value vector for a path."""
    set_keys = _get_vv_from_path(set_path)
    path = r.isa_path(set_path)
    if path:
        set_keys = _get_vv_from_path(path)
    else:
        set_keys = _get_vv_from_path(set_path)

    return set_keys


def resolve_path(path):
    """get the vv for path even if it's empty."""
    if path is None:
        set_keys = last_with_vv()

    elif path[0] == "/":
        set_keys = get_vv(path)

    elif path[0] == ".":
        set_keys = last_with_vv()

    elif path[0] != "/":
        path = _full_with_path(path)
        set_keys = get_vv(path)

    return set_keys


def set(set_path, fromv):
    """Takes a path or path symbol and a value
    or 2 paths.

    Set path can be absolute, or relative to the with.
    If set_path does not begin with / then it
    will be searched from the 'with' root.

    If '.' The source will be merged directly into the current with.

    Values beginning with / will be
    treated as a path, otherwise as a symbol/value.
    """
    global AS

    # with local and absolute paths.
    set_keys = resolve_path(set_path)

    # if isinstance(fromv, str):
    fromv = get_fromv(fromv)

    set_keys += [fromv]

    AS = u.merge(AS, u.make_dict(set_keys))


def get(path):
    """Get a data value from a path in the datastore.
    Without a leading / the path is considered relative
    to the current 'with' path.
    """

    if path[0] != "/":
        vv = _get_vv_from_path(path[1:])
        vv = last_with_vv() + vv

    elif path[0] == ".":
        vv = _get_vv_from_path(path[1:])
        vv = last_with_vv() + vv

    else:
        vv = _get_vv_from_path(path)

    return get_in(vv)


def get_in(keys):
    """Get something out of the yaml datastore."""
    global AS
    return _get_in(AS, keys)


def get_keys_in(*keys):
    """Get just a list of keys from the thing at the value vector."""
    thing = get_in(keys)
    if isinstance(thing, list):
        return thing
    elif thing:
        return thing.keys()
    return None


def get_vals_in(path, *keys):
    """Get a list of values from a value vector in the yaml datastore.
    Vector should be a vector of keys, and keys should be a list of keys. :-/

    this, that, it = get_vals_in(["foo", "bar"], ["this" "that" "it"]).

    This is of primary use in the creation '-with' commands.
    """
    res = []
    d = get_from_path(path)
    for k in keys[0]:
        try:
            res += [d[k]]
        except Exception:
            res += [None]
    return res


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


def show(pathname=None):
    """Show a sub-tree in the Yaml Datastore with a path.

    If no path is given, the current _with_ is shown. if
    the current _with_ is '/', it is listed instead of
    shown, as showing that is rarely what we would want.

    If you really want to 'show' the entire tree it has to
    be explicit.  `show /`

    example: show /device

    This will display the yaml datastore tree from the device node on.
    """
    qqc = None

    # point at with if we got Nothing.
    if pathname is None:
        pathname = last_with()
        # We really don't want to 'show' that on accident.
        if pathname == "/":
            pathname = None
            _ls_with()

    if pathname == "/":
        # remove _Root_ from showing unless asked.
        qqc = AS | {"_Root_": None}

    elif pathname:
        logger.info(pathname)
        # so we don't have to type the first / in the path.
        if pathname[0] == "/":
            pathname = pathname[1:]
        vv = pathname.split("/")
        qqc = get_in(vv)

    if qqc:
        try:
            logger.info(yaml.dump(qqc, Dumper=NoAliasDumper))
        except Exception as e:
            logger.error(e)
            logger.info(str(qqc))


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


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


def yaml_load(y):
    """Safely load some yaml and return it as a list."""
    try:
        d = yaml.load(y, Loader=yaml.SafeLoader)
    except Exception as e:
        logger.error("Yaml load failed.")
        logger.error(y)
        logger.error(e)
        d = None
        raise Exception(e)
    return [d]


def merge_yaml_with(y):
    """Merge a yaml data structure into the yaml datastore."""
    root = last_with_vv()
    try:
        d = [yaml.load(y, Loader=yaml.SafeLoader)]
    except Exception as e:
        logger.error("Yaml load/merge failed.")
        logger.error(y)
        logger.error(e)
        raise Exception(e)
        return

    # logger.info("merge: %s" % root)
    d = u.make_dict(root + d)

    # logger.info(d)
    u.merge(AS, d)


# These should probably honor the current with.
def merge_yaml(y):
    """Merge a yaml data structure into the yaml datastore."""
    logger.debug("Merge yaml-\n %s" % y)
    u.merge(AS, yaml.load(y, Loader=yaml.SafeLoader))


def load(yaml_file):
    """Load a yaml file into the yaml datastore, merging at /."""
    merge_yaml(u.load_yaml_file(yaml_file))


def load_functions():
    """Give the functions from the configuration to the repl.
    by adding them to the symbol table."""
    # add in the user functions from the config file.

    fns = get_in_config(["exec", "functions"])

    if fns is not None:
        for k, v in fns.items():
            r.def_symbol(k, v["doc"], v["fn"])


def load_defaults(state_init, pkgname=None, yamlname=None):
    global AS

    bc = load_base_config()

    if bc is not None and len(bc):
        AS["config"] = u.merge(AS["config"], bc)
        # AS |= state_init  #### destructive...
    AS = u.merge(AS, state_init)
    if pkgname is None:
        return AS
    AS["config"] = u.merge(AS["config"], u.load_pkg_yaml(pkgname, yamlname))
    return AS


def merge_pkg_yaml(package, yamlname):
    """load a yaml file from a package into the yaml datastore."""
    global AS
    AS = u.merge(AS, u.load_pkg_yaml(package, yamlname))


def load_base_config():
    """load the default configuration."""
    return u.load_pkg_yaml(__name__, "SPR-defaults.yaml")


def load_pkg_resource_to(package, filename, *keys):
    """load a python package resource file and place the contents
    at the value vector given.

    example: load-pkg-resource-to Simple_Process_REPL README.md readme md

    Will place the contents of the README.md file into the value vector
    readme/md.
    """
    res = u.load_pkg_resource(package, filename)
    set_in(keys[0] + [res])


def load_pkg_resource(package, filename):
    """load a python package resource file.
    Find a resource file in a python module
    and return it.
    """
    return u.load_pkg_resource(package, filename)


def load_pkg_resource_with(path):
    """load a python package resource file
    using the values found in 'package' and 'filename' located at
    the path.

    The contents will be placed into 'contents' at the path given.

    For this example there is a structure in the yaml datastore which
    looks like this. In this case the value vector is simply 'readme'.
    Contents is included for clarity, but will be created if not there.

    readme:
         package: "Simple_Process_REPL"
         filename: "README.md"
         content: ""

    example: load-pkg-resource-with readme

    Will place the contents of the README.md file into the value vector
    readme/md.

    In SPR:

    with readme
    '
    package: Simple_Process_REPL
    filename: README.md


    load-pkg-resources-with readme

    """
    pkgname, filename = get_vals_in(path, ["package", "filename"])
    res = u.load_pkg_resource(pkgname, filename)
    keys = _get_vv_from_path(path)
    set_in(keys + ["content", res])


def _format(string, *args):
    """Python format function"""
    return format(string % args)


def save(path, filename):
    "Save some part of the data store as a yaml file."
    u.save_yaml_file(filename, get_from_path(path))


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

    _with("/")

    load_configs()

    logs.add_file_handler(
        logger,
        get_in_config(["files", "loglevel"]),
        get_in_config(["files", "logfile"]),
    )
    set_in(["platform", platform()])

    # load functions from the config into the interpreter.
    load_functions()
