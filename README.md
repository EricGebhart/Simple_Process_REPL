# Simple Process REPL

    pip install Simple_Process_REPL
    
This is a stupid simple, configurable, application interface.

To start the REPL;

    SPR -r 

To create a new application copy main.py, import some libraries,
write some functions, fill in the symbol table and the special's table
as needed.  Create a _Config.yaml_ to your liking.

[The Particle Board REPL](https://github.com/ericgebhart/Particle_Board_REPL.git)
is an application built from the Simple_Process_REPL.


## Yet another application framework.

This is at it's heart a simple Read Eval Print Loop. It has 4 ways
of running, and it automatically manages Application state, yaml 
configuration files, the command line, dialogs, prompts, logging and help.  
Everything needed for a particular application can be done with a module of functions..

The cli is done with argparse is extendible from the application layer as needed.

Python dialog, with several standard messages and boxes are included, as is 
a yaml configuration, and an Application state which contains everything
known to the app.

Everything is extensible. Usually a few python functions
and a configuration file is all you will need to create a nicely versatile 
application.

While there is a Repl available, and commands can be added, combined
and remixed, they can also be run automatically through the
autoexec setting in the config.  The default autoexec is to provide help.

## Configuration

The Simple Process REPL uses YAML for it's configuration files. 

Everything is specified there,
there is very little in common with the cli. If no config file is given, the default
_SPR-config.yaml_ will be loaded if found. The primary purpose of the cli is to 
designate the fashion you would like for the REPL to run. 

All necessary defaults are set within the package with SPR-defaults.yaml.
When building an application, that application's defaults will be merged 
into the Simple_Process_REPL's default configuration before loading a locally defined
SPR-config.yaml. An application can over-ride the configuration file name with a setting
in the defaults section of the Application State.


## 4 modes of running

  * Run in a loop for doing a process over and over 
  * Run the default process once 
  * Run a list of command/symbols from the command line 
  * As an interactive REPL 
  
__In any case, if any step fails, the process will fail.__ 
if in interactive loop mode, _-i_, the continue dialog will catch the fail for the next
loop.

## The default process
In the configuration there is an __autoexec__ attribute. This should be a
symbol name or list of symbol names to run as the default process. This
is the process that will run when running cli in interactive loop mode,
or when run once.
  
If symbols are given on the cli after the option then that list is executed once 
automatically instead of the symbol in autoexec.

# Invoking.
Two different kinds of help are built in.
    * `SPR -h`
    * `SPR help`

Help with the symbols which are available for programming 
in the REPL is obtained with the help symbol/function.
 `SPR help` 

The easiest way to understand this is system is by using the REPL. 
It will show you how it works. `SPR -r` 
 
Then type _help_ and/or _showin_.

Once in the REPL at the prompt; __SPR:>,
_help_ shows all the commands known with their documentation. 

## Symbols/Commands/functions

There are three kinds.

 * Symbols which point at directly at parameter-less functions
 * Symbols which are lists of symbols, _compound commands_.
 * Symbols which are _special_ because they take parameters.

### symbol/functions.
These commands are just python functions, whatever it is they do.
Usually, manipulate the application state, and/or interact with something.

### Compound commands

Compound commands are commands defined outside of python code. They are strings which
can be parsed and evaluated by the REPL/interpreter.

Compound commands can be built from other compound commands and _special_ commands.
Compound commands can be defined in yaml, in python code, or interactively in the REPL.


## The REPL

The REPL is very convenient as it saves state, and can be used to
interactively create/execute a process step by step. 
`help` at the REPL prompt. 

 * Builtins __help__
 * __show__, __showin__, and __show-all__ are quite handy.
 * REPL prompt: persistent history and tab completion. 
 * The __loglvl__ command can change the logging level interactively.
 * Defining a symbol of a special works. - Super cool.
    * `msgbox "Hello World"` 
    * `def mymsg "my special msg" msgbox "Hello World"`
 * __log-info__ and __log-debug__ allow sending of arbitrary messages to the log.
 * __sh__ for running shell commands. - There are known bugs.

### Application State. 

```python
AS = {
    "config": {},
    "args": {},
    "defaults": {
        "config_file": "SPR-config.yaml",
        "loglevel": "info",
        "logfile": "SPR.log",
    },
    "device": {"id": "", "name": "", "path": ""},
    "wifi-connected": False,
    "platform": platform(),
}
```
 * configuration is the merged yaml configurations
 * args is the resolved command line
 * defaults is used by argparse to supply default options to the command line.
 * device is an imaginary device. Which we can wait for and handshake with.

The command: **show-all** or **showin** in the REPL will give it to you in yaml.
**help** will give you the documentation for every command you can do, even the ones you just created. 
The easiest way to access it is `showin device` or `showin config serial`
with `showin key1 key2,...` is the command to find sub-section or attributes in the REPL.
`showin config` , `showin defaults`, or just __showin__ which is the same as __show-all__.

For an Application layer, it is only necessary to provide a structure as desired, which
will be merged directly onto this structure.


## It's a Simple list processor.

This program is actually a very simple interpreter with an interactive REPL. 
Everything you want to do must be a python function which is registered in the
interpreter's symbol table. From there, everything is composable from symbol/words
from the interpreter's symbol table, ie, your symbols. Those composed symbols can 
also be added to the interpreter's symbol table to create increasingly
complex sets of processes, which are executed in order. These user
functions can also be defined in the YAML config file.

It has a really, really stupid parser. All it can do execute a list of symbols, or call
a special symbol with everything that follows. It does know the difference between
symbols, strings and numbers.

Basic symbol/functions should be functions done entirely for their side-effects.
They take no parameters and give no return. Special Symbols can take arguments.

At the lowest level the symbols/commands are directly connected to
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

Other commands are _save-config_, _load-config_, _msgbox_, _msgcli_,
_loglvl_, _log-info_, _showin_, etc.
    
Special symbols have an argument count which can be set. If positive the command will
be checked for compliance. Here is an example which
creates symbols for saving and loading configurations from a given filename.

    specials = [
        "Commands we want in the repl which can take arguments."
        ['save-config', save-config, 1,
        "Save the configuration; save-config 'filename'"]

        ['load-config', load-config, 1,
        "Load a configuration; save-config 'filename'"]
    ]
    

## Core: generic functionality

There are a few builtins which do 
special things. There is __wait__ which just waits for a device to come online 
with a timeout. There is pause which just sleeps for a few seconds as set in the 
configuration. The wifi function checks the wifi with linux's network manager, and
uses _nmcli_ to create a connection if one does not exist. Functionality is easy 
to add with a new function and an entry in the symbol table.

   * dialogs - There are some python dialog, and cli interface functionalities. 
   * wifi, - Uses network manager (nmcli) for linux. Non-functional on other platforms.
   * Waiting and handshaking.
        * __wait__ looks for the actual device path i/o event with a _timeout_.
        * __pause__ sleeps for _pause_time_. 
            Note: __wait__ for device is literally a poll to see if the device file exists.
            Once it appears there is some time before the udev rules make the file accessible
            by non-root users. A pause helps everything go smoothly. The next command will 
            actually have access to the device. So now I have a habit of following a __wait__ with
            a __pause__. 
        * __handshake__ does a blocking serial.read/readline for both the initial
        string, and the test results after. 


### Handshake function

This is a generic function that is a bit more complicated.  
It manages an interaction with a device. Everything _handshake_ 
does is defined in the configuration file. As with everything else, 
if anything fails, or doesn't match, an exception is raised.

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

  qqc = quelque chose = something. 
  
  In the config the do_qqc_function is set to _input-serial_,
  as an example. Input-serial prompts for a serial number, 
  validates it, and returns it.  This function must be listed in
  the symbol table as that is where _handshake()_ will
  look for it. Makes it easy to test. _serial-input_ at the
  _SPR:>_ prompt.
      
    



