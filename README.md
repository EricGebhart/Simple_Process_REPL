# Simple Process REPL

    pip install Simple_Process_REPL
    
This is a stupid simple, highly configurable, application interface.

To create a new application copy main.py, import some libraries,
write some functions, fill in the symbol table and the special's table
as needed.  Create a 'Config.yaml' to your liking.

Instant application.


## Yet another application framework.

This is at it's heart a simple Read Eval Print Loop. It has 4 ways
of running, and it automatically manages Application state, yaml 
configuration files, the command line, and help.  Everything needed
for a particular application can be managed 
with a very lightweight module of functions..

Python dialog, with several standard messages and boxes are included, as is 
a yaml configuration, and an Application state which contains everything
known to the app.

Everything is extensible. Usually a few python functions
and a configuration file is all you will need to create a nicely versatile 
application.

While there is a Repl available, and commands can be added, combined
and remixed, they can also be run automatically. Either through the
autoexec setting, or by specifying commands on the command line.

The _-i_ option will cause the program to run in a loop doing 
whatever you told it to until you tell it to stop.

The _-r_ will give a repl.


### Getting Help

# Invoking.
Two different kinds of help are built in.
    * `python -m Simple_Process_REPL -h`
    * `python -m Simple_Process_REPL help`

Help with the symbols which are available for programming 
in the REPL is obtained with the help symbol/function.
 `python -m Simple_Process_REPL help` 

The easiest way to understand this is system is by using the REPL. 
It will show you how it works. `python -m Simple_Process_REPL -r` 
 
Then type _help_ and/or _showin_.

Once in the REPL at the prompt; __SPR:>,
_help_ shows all the commands known with their documentation. 


### A map of all things that matter 
is called AS - Application State. 

It is a merge of the Repl's Application state and the dictionary given by the core layer.

The command: **show-all** or **showin** in the REPL will give it to you in yaml.
**help** will give you the documentation for every command you can do, even the ones you just
created. Inside _repl_core.py_, **AS** is the name of the Application State structure. 
__AS['config']__ is the name of the loaded configuration. 
__AS['device']__ is the dictionary of device information.
The easiest way to access it is `showin device` or `showin config serial`
with `showin key1 key2,...` is the command to find sub-section or attributes in the REPL.
`showin config` , `showin defaults`, or just __showin__ which is the same as __show-all__.
`showin config files`  or `showin config files logfile`.

So, If you need something, a function we don't have, Add an actual function to core.py, and
put an entry in one of the symbol tables.

If it can be created from a combination of pieces then do it with a new symbol. 
It could be def'd in the REPL, once it worked correctly. Then _save config_, that will
sync the symbol tables between the interpreter and the config, then the config will save
with whatever you've got. If you 'know it', code the new functionality directly in the yaml.

The __save-config__ command automatically syncs your functions from the REPL before the save.

You can sync the symbols to your config at anytime with the __sync-funcs__ command.
However, you still must save the configuration you have in memory if you want to keep them.

Be warned, that def's in the REPL are ephemeral unless saved. make it up, throw it away, 
or save it. -- this is not a step. --


## Data and symbol driven

This program is actually a very simple interpreter with an interactive REPL. 
Everything you want to do must be a python function which is registered in the
interpreter's symbol table. From there, everything is composable from symbol/words
from the interpreter's symbol table, ie, your symbols. Those composed symbols can 
also be added to the interpreter's symbol table to create increasingly complex sets of processes, 
which are executed in order. These user functions can also be defined in the YAML config file.
which defaults to _'pbi-defaults.yaml'_

## A poor mans lisp

It has a really, really stupid parser. All it can do execute a list of symbols, or call
a special symbol with everything that follows. It does know the difference between
symbols, strings and numbers.

Basic symbol/functions should be functions done entirely for their side-effects.
They take no parameters and give no return. Special Symbols can take arguments.

At the lowest level, in core.py, the symbols/commands are directly connected to
python functions. But symbols/commands can also be lists of known symbols instead
of a function.  This allows for the creation of sub-groups which can be referenced by
other symbols.  There are no parentheses, only the ability to associate lists of
symbols with a new symbol.

    import repl as r
    symbols = [
        ['wifi',       connect_wifi,    'Connect to wifi using nmtui if not connected.']
        ['list',       P.list_usb,      'List the boards connected to USB.']
        ['start',      'wifi list',     'Connect wifi and list the boards.']
        ['identify',   P.identify,      'Try to identify a device.']
        ['domore',     'start identify', 'Start then identify']
        ['doevenmore', 'domore setup',   'Start identify and setup.']
    ]
    r.init_symbol_table(symbols)

The symbols _start_, _domore_ and _doevenmore_ can be defined in the YAML 
configuration file, it is not necessary to modify python code unless new 
functionality needs to be introduced.

## Special Symbols

The interpreter is not very bright and has no way of grouping things together which
makes it difficult to execute commands which take arguments. Specials are symbols 
at the beginning of a command which will eat the rest of the line, in attempt to
do what they are supposed to do.

To compensate the interpreter has the concept of special symbols, 
These are symbols which take arguments and can consume the entire REPL command. 

These are also pointers to python functions, but which take some arguments.
These go on a line by themselves since we have no way of knowing them unless the
line starts with them, and then the special gobbles up the rest of the line.

The REPL itself has a special symbol, __def__ which allows for the creation 
of a new symbol with the following syntax. 

    def <symbol> 'helpstr' symbol1 symbol2 symbol3...

It is possible to make compound commands of specials which can then be used in other compound
commands.  The specials are commands like _def_, _save-config_, _load-config_, _msgbox_, _msgcli_,
_loglvl_, _log-info_, _showin_, etc.  Many of them have no real use outside of the 
REPL/development environment.
    
Special symbols have an argument count which can be set. If positive the command will
be checked for compliance. Here is an example which
creates symbols for saving and loading configurations from a given filename.
These obviously must be the responsibility of the application, ie. core.py.

    specials = [
        "Commands we want in the repl which can take arguments."
        ['save-config', save-config, 1,
        "Save the configuration; save-config 'filename'"]

        ['load-config', load-config, 1,
        "Load a configuration; save-config 'filename'"]
    ]
    
Dialog windows are wrapped in individual python functions, but they could be a special
that takes an argument. The eval command in the repl will do the right thing if a
special is part of your process.

__Weird fact:__ You can put a completed specials command in the regular symbols table
and it will do the right thing. It's just going to be static with it's parameters.


## Configuration

The Simple Process REPL uses YAML for it's configuration files. 

Everything is specified there,
there is very little in common with the cli. If no config file is given, the default
will be loaded. The primary purpose of the cli is to designate the fashion you would 
like for the REPL to run. The default configuration file is _SPRConfig.yaml_.

All necessary defaults are set within the package with SPR-defaults.yaml.
When building an application, that application's defaults will be merged 
into the Simple_Process_REPL's default configuration before loading a locally defined
SPRConfig.yaml. Generally, an application will take this over, and have
a configuration of it's own instead. It is just a setting in the defaults.


## 4 modes of running

  * Run in a loop for doing a process over and over, 
  * Run the default process once, 
  * Run a list of command/symbols from the command line, 
  * As an interactive REPL 

  Running in the REPL allows for the preservation of state
  as well as introspection and the interactive manipulation of a board.
  It is possible to create new symbols/functions as well as saving and 
  loading of configurations and functions.

## The REPL

The REPL is very convenient as it saves state, and can be used to
interactively create/execute a process step by step. Symbols have a documentation
string associated with them. It is possible to get a list of symbols and
their help by typing `help` at the REPL prompt. The _doc_ strings for the 
functions, and the source code for compound functions are also included.

Everything is driven by the two symbol tables and the yaml config file. 
Additional functionality can be added by adding to the functions to symbol 
table in core.py. User functions, ie, lists of known symbols, can be defined
in the REPL or in the configuration file. With the limitation that
those functions are ultimately composed of known symbols as defined in _core.py_
If symbols are defined within the REPL, they should be saved or they will be lost upon exit.

## The default process
In the configuration there is an __autoexec__ attribute. This should be a symbol name or
list of symbol names to run as the default process. This is the process that will run when 
running cli in interactive loop mode, or when run once.
  
If symbols are given on the cli after the option then that list is executed once 
automatically instead of the symbol in autoexec.
## Symbols/Commands/functions

We've got three kinds.

 * Symbols which point at directly at parameter-less functions
 * Symbols which are lists of symbols, _compound commands_.
 * Symbols which are _special_ because they take parameters.

### symbol/functions.
These commands are just python functions, whatever it is they do.
Usually, manipulate the application state, and/or interact with something.

### Compound commands

Compound commands are commands defined outside of python code. They are strings which
can be parsed and evaluated by the REPL/interpreter.  The core functions tend to be
very specific, it is best to keep them simple. So that creating more complex process 
is a matter of creating compound commands. 

Compound commands can be built from other compound commands and even _special_ commands.
Compound commands can be defined in yaml, in python code, or interactively in the REPL.

## REPL: Features.

 * Builtins __help__
 * __show__, __showin__, and __show-all__ are quite handy.
 * REPL prompt: persistent history and tab completion. 
 * Symbols, Specials, and compound symbols are working as designed.
 * Seems to be handling exceptions and displaying good errors.
 * The __loglvl__ command can change the logging level interactively.
 * Defining a symbol of a special works. - Super cool.
    * `msgbox "Hello World"` 
    * `def mymsg "my special msg" msgbox "Hello World"`
    * That means it works in yaml too.
 * __log-info__ and __log-debug__ allow sending of arbitrary messages to the log.
 * __sh__ for running shell commands.

 
## Core: Everything generic in functionality

There are many symbols builtin which do 
special things. There is __wait__ which just waits for the usb device to come online 
with a timeout. There is pause which just sleeps for a few seconds, as set in the 
configuration. The wifi function checks the wifi with linux's network manager, and
uses _nmcli_ to create a connection if one does not exist. Functionality is easy 
to add with a new function and an entry in the symbol table.

This is where all of the basic functionality like dialogs, command prompts, 
saving and loading of configurations and in general looking around
and manipulating data etc.  handshaking, waiting, pausing etc.

There are a number of key features that are working.
   * dialogs - There is a pythondialog interface, and cli dialog interface. 
   * serial waiting, reading, and sending, 
   * wifi, - Uses network manager (nmcli) for linux. Non-functional on other platforms.
   * Waiting and handshaking are working. 
        * __wait__ looks for the actual usb device with a _timeout_.
        * __pause__ sleeps for _pause_time_. 
            Note: __wait__ for device is literally a poll to see if the device file exists.
            Once it appears there is some time before the udev rules make the file accessible
            by non-root users. A pause helps everything go smoothly. The next command will 
            actually have access to the device. So now I have a habit of following a __wait__ with
            a __pause__. 

        * __handshake__ does a blocking serial.read/readline for both the initial
        string, and the test results after. 

### Handshake function

This is a generic function in _core.py_.  It manages the interaction
with the test procedure. Everything _handshake_ does is defined in the
configuration. If anything fails, or doesn't match, an exception is 
raised and the device is considered failed.

Here are the steps that _handshake()_ does.

  * Wait for the _start_string_, match it.
  * Respond with the _response_string_.
  * Look in the output for: 
    * fail_regex, 
    * done_regex, 
    * do_qqc_regex.
  * If fail, raise an exception.
  * if done, exit quietly with true.
  * if do_qqc, then call the do_qqc_function 
  and send the return value to the serial device.
  qqc = quelque chose = something. It's a common .fr abbrev. :-)
  
  In our case, the do_qqc_function is input-serial,
  which prompts for a serial number, validates it,
  and returns it.  This function must be listed in
  the symbol table as that is where _handshake()_ will
  look for it. Makes it easy to test. _serial-input_ at the
  _pbi:>_ prompt.
      
    



