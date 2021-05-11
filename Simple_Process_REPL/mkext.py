# Create a python project for an SPR extension module.
# import Simple_Process_REPL.appstate as A
import os
import pkgutil
import regex as re
import logging

logger = logging.getLogger()

root = "make-ext"


def get_pkg_file(fname):
    return pkgutil.get_data("Simple_Process_REPL", fname)


def insert_name(name, lines):
    """Look through a list of lines looking for %s formats. if found,
    format it with the name."""
    res = []
    for line in lines.split("\n"):
        if re.findall("%s", line):
            line = line % name
        res += [line + "\n"]
    return res


def write_lines_2_file(fname, lines):
    """Open a file and write the lines to it."""
    with open(fname, "w") as f:
        f.writelines(lines)
    f.close()


def new_spr_extension_project(pathname):
    """Create a Python project to create an SPR extension module.
    This creates a skeleton python project that is
    compatible with pip.

    It includes everything needed to create a new extension
    module that can be installed with pip and imported by SPR.
    """

    setup = get_pkg_file("setup.txt").decode("utf-8")
    py = get_pkg_file("python.txt").decode("utf-8")
    spr = get_pkg_file("spr.txt").decode("utf-8")
    yaml = get_pkg_file("yaml.txt").decode("utf-8")
    readme = get_pkg_file("readme.txt").decode("utf-8")

    logger.info("Creating Python Project: %s" % pathname)

    if os.path.exists(pathname):
        logger.error("Path: %s, exists" % pathname)
        return
    else:
        os.mkdir(pathname)

    name = os.path.split(pathname)[1]
    module_path = os.path.join(pathname, name)

    os.mkdir(module_path)

    if setup:
        write_lines_2_file(os.path.join(pathname, "setup.py"), insert_name(name, setup))

    if readme:
        write_lines_2_file(
            os.path.join(pathname, "README.md"), insert_name(name, readme)
        )

    write_lines_2_file(
        os.path.join(module_path, "__init__.py"), ['__version__ = "0.0.1"']
    )

    if py:
        write_lines_2_file(os.path.join(module_path, "core.py"), insert_name(name, py))

    if spr:
        write_lines_2_file(
            os.path.join(module_path, "core.spr"), insert_name(name, spr)
        )
    if yaml:
        write_lines_2_file(
            os.path.join(module_path, "core.yaml"), insert_name(name, yaml)
        )
