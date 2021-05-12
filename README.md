# Simple Process REPL

Get your favorite python libraries that do things, and start 
scripting process applications that do composeable things out of them.

This is also a fun thing to embed in your application and wire it up. like you would
lua or python in a C project. Only it's SPR in your python.

Or maybe this is just a process you need to do a lot.  Program/test a particle
board, scan a bar or QR code, generate and print a bar or QR code, run a series
of shell commands, popup some dialogs, do some stuff.


    pip install Simple_Process_REPL
    
This is a stupid simple, configurable, Extensible, application interface.
You will need to install dialog. tkinter is coming probably.

on Arch Linux
    sudo pacman -S dialog

or on Apple
    brew install dialog


To start the REPL;

    SPR -r



[The Particle Board REPL](https://github.com/ericgebhart/Particle_Board_REPL.git)
is an application built from the previous version of SPR. PBR is now a standalone
application that embodies the old version 1 of SPR.

## What is it, really ?

This is a really stupid interpreter, connected to a configuration and application state
which is a big tree of Yaml.  Throw in a module of python functions and  you've got an 
application with a Read Eval Print loop.

SPR code is really simple. SPR only knows words, strings and numbers.
If you give it a list, it will try to look up what you gave it and 
execute it.  So you can make lists and give them names, and make lists of lists,
all of which turns into a process which will try to do it's thing, and if any
step fails, the whole process fails.

SPR has a configuration file, which, can have spr functions defined within it.
SPR can read spr files and execute them.

An SPR library/module is a Python module with a python file, a yaml file and
an spr file. An SPR library project can be created with the
    `new-spr-extension-project` command.

Once the new module is available on the Python path SPR can import it with
a command like this.
    `namespace foo "my foo namespace" foo.core function1 function2...`
    
This will create a namespace foo with all the functions listed, and with
whatever is defined in `foo.core.spr`.  The application state will merge 
in what ever structure is defined in `foo.core.yaml`. 

Here is how the bar/QR code module defines it's application state structure
and it's configuration settings in `bar_qr.yaml`.

``` code=YAML
bar-QR:
    src: Null
    value: ''
    QR_code:
        code: Null
        saved: ''
    barcode:
        code: Null
        saved: ''

config:
    QR_code:
        filename_suffix: 'QR'
        prefix: 'K1'
        suffix: 'A'
        save_path: 'qrcodes'
        font: DejaVuSans.ttf
        font_size: 18
    barcode:
        filename_suffix: 'BC'
        prefix: ''
        suffix: ''
        save_path: 'barcodes'
        save_options:
            module_height: 8
            text_distance: 2
```

## SPR code.

So it's stupid.  It's a list of things. If you put it in a file,
each command must be separated by a blank line.  A command can be 
formatted however you like, but the lines must be contiguous. A blank
line results in the command being executed. Here is a sample from
`core.py`

```
namespace sh "Subprocesses, shell etc."
    Simple_Process_REPL.subcmd
    do rm sleep

namespace log "logger controls and messages"
    Simple_Process_REPL.logs
    level info warning error critical debug

namespace dev "Device interaction, waiting for, handshaking."
    Simple_Process_REPL.device
    wait handshake pause

namespace nw "Networking stuff, Wifi"
    Simple_Process_REPL.network connect_wifi
    connect_tunnel create_tunnel sendlog

namespace bq "Bar and QR code generation and printing"
    Simple_Process_REPL.bar_qr
    gen save read_barcode_from_camera

in-ns

import Simple_Process_REPL.mkext new_spr_extension_project

```


## libraries

There are a few libraries included within SPR, they are imported by SPR
into their various namespaces by `core.spr`

* logs  - logging level and messaging.
* appstate - Application state - All the YAML, config etc.
* dialog_cli - dialog, and cli, stuff for the ui.
* network - Networking. wifi, ssh, etc.
* device  - Basic usb device interaction 
* particle_main  - Particle.io Board interaction.
* subcmd - shell commands etc.
* Bar_qr - a bar and QR code reader, generater, and printer
* mkext  - A function and files to create a sample SPR extension library project.


### Creating SPR extension modules

A new Python/SPR extension module named foo can be created with the SPR command
```
    new-spr-extension-project path/to/foo.
```

The module will have an appropriate `setup.py` with some *fix_mes*. There will
be 3 files, core.py, core.yaml, and core.spr.  Only the core.py is necessary.
So it is actually possible to import any python module in order to use it's 
functions within SPR.

SPR is stupid however, and does not understand keywords and other things.

The core.yaml file enables the module to add in it's data structures and 
configuration to the Application state upon import.

The core.spr file enables non python symbols and partials to be defined in
which ever namespaces are desired. By default, in it's own namespace.

The Application state, is actually just a merge, of all the yaml's defined
by the various modules, and by the core.yaml.

A complete configuration file can be generated at any time by saving it.

The configuration should be named SPRConfig.yaml and will automatically loaded
from the runtime directory if it exists.

It can also be specified on the command line along with an spr file to execute.

## Modes of running
  * Run Autoexec once
  * Run the Autoexec in an intractive loop
  * Run a repl
  * Run command line args once
  * Run command line args in an intractive loop

### Examples - mix and match.
  * `SPR -i` Run in a loop doing a process over and over 
  * `SPR` Run a process once 
  * `SPR cmd1 cmd2` Run a list of command/symbols from the command line 
  * `SPR -f foo.spr` Run an SPR file.
  * `SPR -r` Run as an interactive REPL 
  
## Order of execution  
  * core.py

  * The Startup Hook defined in the configuration will run first

  * The file given with -f will run next.

  * Run with a REPL, 
    * Commands on the command line will execute on startup.
  
  * Run the Automatic Exec once or in a loop. 
    * Commands given on the command line will replace the autoexec 
    defined in the configuration file.

  * The Shutdown Hook defined in the configuration will run last

  
__In any case, if any step fails, the process will fail.__ 
if in interactive loop mode, _-i_, The failure and continue dialogs will catch the 
fail for the next loop.


## The default process
In the configuration there is an __autoexec__ attribute. This should be a
symbol name or list of symbol names to run as the default process. This
is the process that will run when running cli in interactive loop mode,
or when run once.
  
If symbols are given on the cli after the option then that list is executed once 
automatically instead of the symbol in autoexec. 

# Invoking help.
Two different kinds of help are built in.
    * `SPR -h`
    * `SPR help`

Help with the symbols which are available for programming 
in the REPL is obtained with the help symbol/function.
 `SPR help` 

# Just do it.
The easiest way to understand this is system is by using the REPL. 
It will show you how it works. `SPR -r` 
 
Then type these commands and read as you go.
 * _ls-ns_ 
 * _ns-tree_ 
 * _help_ 
 * _help sh_
 * _help sh/do_
 * _help nw_
 * _help as_
 * _help ui_
 * _help bq_
 * _help device_
 * _showin_ 
 * _showin_ device
 * _showin_ foo
 * _set_ foo bar 10
 * _set-from_ foo foo from: foo bar
 * _showin_ foo
 * msgbox "hello"
 * def mymsg "my msg help" msgbox "hello"

Once in the REPL at the prompt; __SPR:>,
_help_ shows all the commands known with their documentation. 

## Symbols/Commands/functions

There are several kinds.

 * Symbols which point at directly at parameter-less functions, _voidfptr_
 * Symbols which are lists of symbols, _dolist_s.
 * Symbols which point at functions which take parameters. _fptr_
 * Symbols which point at list of symbols, but which resolve to partially completed 
   fptr commands, these are called _partial_s.

### symbol/functions.
These commands are just python functions, whatever it is they do.
Usually, manipulate the application state, and/or interact with something.

### dolist commands

_dolist_ commands are commands defined outside of python code. They are strings which
can be parsed and evaluated by the REPL/interpreter.

_dolist_ commands can be built from other _dolist_ commands and _fptr_ commands.
_dolist_ commands can be defined in yaml, in python code, or interactively in the REPL.

### Partial commands

_partial_ commands are built from _fptr_ commands.
_partial_ commands are like dolist commands. Except that the first symbol in
the list is an fptr symbol, and the list is not everything the fptr function needs.
when using a partial, they act just like fptr functions, you just have to leave off
some or all of the first arguments.

_partial_ commands can only be defined in SPR code.

## The REPL

The REPL is very convenient as it saves state, and can be used to
interactively create/execute a process step by step. 
`help` at the REPL prompt. 

 * Builtins __help__
 * __showin__, __ls-ns__, __ns-tree__ are quite handy.
 * REPL prompt: persistent history and tab completion. 
 * The __log/level__ command can change the logging level interactively.
 * Defining a symbol of a special works. - Super cool.
    * `ui/msgbox "Hello World"` 
    * `def mymsg "my special msg" ui/msgbox "Hello World"`
 * __log/info__ and __log/debug__ allow sending of arbitrary messages to the log.
 * __sh/do__ for running shell commands. - There are known bugs.

## The Application State
 * config is the place where is the merged yaml configurations should go.
 * args is the resolved command line
 * device is an imaginary device. Which we can wait for and handshake with.
 * bar-QR is the state managed by the bar/QR code module
 * device is used by core, and by particle.
 
 It's really best to just explore it with `showin`.

The command: **as** in the REPL will give it to you in yaml.
**help** will give you the documentation for every command you can do, even the ones you just created. 
The easiest way to access it is `showin device` or `showin config serial`
with `showin key1 key2,...` is the command to find sub-section or attributes in the REPL.
`showin config` , `showin defaults`, or just __showin__ 


## It's a Simple list processor.

This program is actually a very simple interpreter with an interactive REPL. 
Everything you want to do must be a python function imported into the repl.
From there, everything is composable from symbol/words
These user functions can also be defined in an spr file or even the YAML config file.

It has a really, really stupid parser. All it can do execute a list of symbols, or call
a special symbol with everything that follows. It does know the difference between
symbols, strings and numbers.
It does some introspection of the python function signtures, so it's not completely
stupid, but some care should be taken.


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
      
    



