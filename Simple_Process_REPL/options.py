import argparse
import textwrap

help_prefix = textwrap.dedent(
    """\
        The Simple Process REPL is intended to make it easy
        to define Serialized Processes. It manages the CLI, configuration,
        logging and help, as well as providing multiple ways of running
        the process.

        Define your own processes to interact with anything you like.

        Run interactively in a REPL, run the autoexec once, or in a loop, or
        just run a command from the cli.

        This program is based on a REPL/interpreter. Everything it does
        is defined with it's YAML config file.

        New commands can be defined in the configuration files, and any
        command can be specified to run automatically. The foundational
        commands are python functions. Secondary commands are simply
        lists of other commands, so that more complex processes can be
        created from smaller ones.

        By default the autoexec is set to a 'hello' function.

        Configuration:
        There is a default config file as well as a config file
        option. The default configuration is loaded just before parsing
        the cli. If the config file option is given, it will then be
        loaded on top of the default, and the cli will be re-parsed with
        the new defaults from both configuration files. So all options on
        the command line will win, but also receive their proper defaults.

        After parsing it is possible to load another configuration file.
        It is possible that this should be rearranged. First the
        defaults, then the optional configuration, then reparse with
        the new defaults from both configurations.

        Help:  There are two different help commands available. This one,
        -h, and the internal command, 'help' which gives help for all
        commands available to create processes from. ie. 'spra -h',
        'spra --help', or for the internals, 'spra help'.

        This script assumes there will only be one particle board
        connected at a time. Device detection and targeting would be a
        problem otherwise.

        Interactive mode will loop continually in order to configure
        multiple boards with dialogs. There is a minimized interaction
        mode which prompts only for boards, reporting success or fail,
        for each.

       Each step can also be  manually from the command line.
       Some builtins are:

       * connect wifi
       * python Dialogs
       * cli prompts
       * inspection of state
       * shell commands

       Interactive mode will loop continually with dialogs.
       The default, with no options, is to do everything once in order,
       for one process.
       """
)


help_suffix = textwrap.dedent(
    """\
       Commands can be given after the options in any sequence. Each
       command will run in the order given. Any errors will cause the
       sequence to abort.
        """
)


def define_help_text(prefix, suffix):
    """Add application specific help text"""
    global help_prefix
    global help_suffix

    help_prefix = prefix + "\n" + help_prefix
    help_suffix = suffix + "\n" + help_suffix


def get_argp():
    """Get an argument parser."""
    return argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=help_prefix,
        epilog=help_suffix,
    )


def create_parser(defaults):
    """Create argument parser."""
    parser = get_argp()

    parser.add_argument(
        "--config-file",
        dest="config_file",
        help="Yaml configuration file to load.",
        type=argparse.FileType(mode="r"),
    )

    parser.add_argument(
        "-f",
        "--file",
        dest="file",
        help="File name of spr code to execute",
        action="store",
    )

    parser.add_argument(
        "--logfile",
        default=defaults["logfile"],
        action="store",
        help="logfile to use",
    )

    parser.add_argument(
        "-r",
        "--repl",
        action="store_true",
        help="Start a REPL",
    )

    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Loop, like Awk, do the autoexec or the cli commands in a loop.",
    )

    parser.add_argument("commands", nargs="*")

    return parser


def parse_cli(defaults):
    """parse the command line, provide a dictionary for the defaults."""
    return create_parser(defaults).parse_args()
