import pkgutil
import os
import logging
import yaml

logger = logging.getLogger()

# yaml = A.load_pkg_yaml("Simple_Process_REPL", "appstate.yaml")

# # format and fill in as you wish.
# HelpText = (
#     """
# utils: - SPR's utils, yaml and stuff.  -

# Everything needed to load, save, copy, set, and merge data.
# Yaml files and merging etc.

# Loading of files from python modules.

# """
#     % yaml
# )


# def help():
#     print(HelpText)


def merge(a, b, path=None, update=True):
    """Non destructive merge of dictionary trees.
    walk the trees and move the stuff as needed, don't wack
    anything unless explicitly asked to.

    Like setting something to None.

    nice solution from stack overflow, non-destructive merge.
    http://stackoverflow.com/questions/7204805/python-dictionaries-of-dictionaries-merge
    """
    # if b is None or len(b) == 0:
    # raise Exception("Cannot Merge empty trees.")

    if path is None:
        path = []

    if isinstance(b, str):
        a = b

    if isinstance(b, dict):
        for key in b:
            try:
                if key in a:
                    if isinstance(a[key], dict) and isinstance(b[key], dict):
                        merge(a[key], b[key], path + [str(key)])
                    elif a[key] == b[key]:
                        pass  # same leaf value
                    elif isinstance(a[key], list) and isinstance(b[key], list):
                        for idx, val in enumerate(b[key]):
                            if len(a[key]):
                                a[key][idx] = merge(
                                    a[key][idx],
                                    b[key][idx],
                                    path + [str(key), str(idx)],
                                    update=update,
                                )
                            else:
                                a[key] = b[key]

                    elif update:
                        a[key] = b[key]
                    else:
                        raise Exception(
                            "Conflict at %s with %s" % ("/".join(path), str(key))
                        )
                else:
                    a[key] = b[key]

            except Exception as e:
                logger.error("Failed to merge data")
                logger.error(e)
                logger.error("Problem at %s with %s" % ("/".join(path), str(key)))
                raise Exception("Failed Data Tree Merge.")

    return a


def make_dict(keys):
    """Create a dictionary tree from a list, a value vector with value.
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


def save_yaml_file(filename, dictionary):
    "Write a dictionary as yaml to a file"
    with open(filename, "w") as f:
        yaml.dump(dictionary, f)


def load_yaml_file(filename):
    "load a dictionary from a yaml file"
    someyaml = None
    if os.path.isfile(filename):
        logger.info("Loading YAML: %s" % filename)
        with open(filename) as f:
            someyaml = yaml.load(f, Loader=yaml.SafeLoader)
    return someyaml


def load_pkg_resource(package, filename):
    """Load a file from a python package, and return it."""
    return pkgutil.get_data(package, filename).decode("utf-8")


def load_pkg_yaml(package, yamlname):
    """load a configuration file from a package."""
    try:
        someyaml = yaml.load(
            load_pkg_resource(package, yamlname), Loader=yaml.SafeLoader
        )
    except FileNotFoundError:
        return
    except Exception as e:
        print(e)
        return

    logger.info("Loaded YAML from Module: %s: %s" % (package, yamlname))
    return someyaml


def dump_pkg_yaml(package, yamlname):
    """load a yaml file from a python package and dump it."""
    return yaml.dump(load_pkg_yaml(package, yamlname))
