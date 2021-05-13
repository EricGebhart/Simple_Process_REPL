# Simple Process REPL

### What is it?

It's a fun to use tool to create applications which do processes.
It's just stupid enough to be transparent and easy, and just smart
enough to not be too annoying. 

This program is actually a very simple interpreter with an interactive REPL. 

SPR code is really simple. SPR only knows words, strings and numbers.
If you give it a list, it will try to look up what you gave it and 
execute it.  So you can make lists and give them names, and make lists of lists,
all of which turns into a process which will try to do it's thing, and if any
step fails, the whole process fails. All with nice error handling, logging,
dialogs, configuration, integrated help, self introspection, a REPL, along 
with various methods of execution.

## Installation

    pip install Simple_Process_REPL
    
You will also need to install dialog. tkinter is coming probably.

on Arch Linux

    sudo pacman -S dialog

or on Apple

    brew install dialog


To start the REPL;

    SPR -r


## Why ?
This started out as a project to identify, test, and flash a particle.io
board. The boards and services are finicky, and the ability to be able
to create repeatable snippets of processes was the way to go. Two pieces
might work individually and not one after the other, or the device would
disconnect for a moment. It was a pull your hair out kind of experience.

The original python version 1 of SPR now lives on as 
[The Particle Board REPL](https://github.com/ericgebhart/Particle_Board_REPL.git).
PBR is an application layer built on top of the previous version of SPR. 
PBR is now a standalone application that embodies the old version 1 of SPR.

This particle board process also needed wifi, the concept of a device, 
usb handshaking, device waiting and dialog prompts among other things.

Composeability and an interactive REPL were necessary to efficiently create a
successful process of some complexity. 
It naturally evolved out of the first version of this code which was a _zsh_ script.
I had added a prompt to the script out of frustration so that I could run it's 
functions interactively.

But, then, between all the error trapping, and io redirection It was decided to
switch to python. I built the prompt first, and started feeding it functions as
I built the process. It was a list processor from the very beginning. 
It worked fantastically. Creating that finicky process was actually kind of fun.


----------

## Make something!

Get your favorite python libraries that do things, and start 
composing process applications that do more complicated things out of them.

So you have something you know you can code up in python. It's got some data
to keep track of, logging to do, it's got configuration settings, 
it does some things, communicates with a device or generates some
barcodes or flashes and tests an IoT device, 
or maybe it downloads an image and creates a bootable
sdcard with all the steps required... etc.

SPR handles the foundation, It can import python modules, it has namespaces,
It manages logging and yaml configurations. As well as Stateful data.
It has integrated help, and can be fully introspected within it's self.

It can be configured to run as an application, which will execute once, or
in a loop over and over with the `-i, --interactive` option. Help is fully 
configurable to complete the illusion. At the same time it has extensive internal help.

When run as a REPL SPR has history, tab completion, and complete access to
all functionality within your application.

SPR gives you YAML as a way to define your own tree of data to hold everything you 
could want. 

All of this allows you to write simple functions which set and get their configuration 
and stateful data in the tree, and/or interact with other things. 
There is a notion of devices, there are simple dialogs and cli prompts,

## To sum up.
This is a really stupid interpreter, think of it as a stupid layer on top of python.
All with nice configuration and application state management
But stupid, no syntax, no variables, no logic, it just calls functions.
It's easy to get and put things into the Application state 
which is represented as a big tree of Yaml. 

A module of python functions to do the complicated bits fills out the functionality. 
Then it's time to start playing with the parts and put something together.
Once it's done, with just a configuration file you could have an
application that does a repeatable process with a builtin REPL. 

## The parts.
  * The Interpreter/Repl
  * Namespaces
  * Application state data structure
  * SPR/Python extensions that are built in.

   
### The interpreter/REPL

This is defined in `repl.py`. It has `help`, persistent history,
and tab completion. 
It has the idea of namespaces and it knows how to import python modules. 

**help** will give you the documentation for every namespace and command available, 
even the ones you just created. 

It does it's best to call the
python functions you tell it to.  It recognizes, words, strings and numbers.
ie. `foo "this is a string" 10`, it understands functions with various 
signatures including variable arguments, but not keywords. Which aren't
valid in it's non-existent syntax anyway.

The REPL is very convenient as it saves state, and can be used to
interactively create/execute a process step by step. 
`help` at the REPL prompt. 

On startup, there are only a dozen or so commands imported directly into
the repl. The rest of the initialization is done by _core.spr_ which
imports the rest of the extensions into their namespaces.


## It's a Simple list processor.

Everything you want to do must be a python function imported into the repl.
From there, everything is composable from symbol/words
These user functions can also be defined in an spr file or even in the YAML config file.

It has a really, really stupid parser. All it can do execute a list of symbols, or call
a special symbol with everything that follows. It does know the difference between
symbols, strings and numbers.
It does some introspection of the python function signtures, so it's not completely
stupid, but some care should be taken.


### Namespaces

A namespace is a structure that holds some stuff, and a list of symbols.
Think of it as a folder of commands. That really is about the extent of it.

When a namespace is created the python functions are imported directly 
into it, The module's spr code is also run, and the yaml code associated 
with the import module will be integrated into the Application State tree.

It is encouraged that the modules imported into the namespace have a _help()_
function. The `new-spr-extension-project` creates a nice template accordingly.

At a minimum, creating a namespace requires a documentation string. If a help
function exists in the namespace that help will be integrated into the namespace
help formatting.

`ls-ns` will list all the namespaces. 
`ls-ns name` will list the contents of that namespace. 
`ns-tree` will list all the namespaces with their contents. 

Creating a namespace called foo from a python module _foo.core_ looks like this:
```
    namespace foo "my foo namespace that does bar" 
        foo.core 
        function1 function2 ...`
```

after a namespace command, the interpreter will remain in that namespace
until it is changed with the `in-ns` command.

While in a namespace it is also possible to do an import of a python module
like this, which is actually how SPR gets the *new_spr_extension_project* command,
into it's root namespace. `in-ns` with no name will take the you to the root
namespace.

```
    in-ns
    
    import Simple_Process_REPL.mkext new_spr_extension_project
```

SPR files can be loaded with load-file.

    `load-file foo.spr`


### Application State Data Structure

There is this big data structure referred to as the Application State.
It has a config tree which can be grown as needed by any SPR extensions
that need it. 

Some of the data trees at the root of the Application state are the following. 
 * config is the place where the configurations should go.
 * args is the resolved command line
 * device is an imaginary device. Which we can wait for and handshake with.
 * bar-QR is the state managed by the bar/QR code module
 * device is used by core, and by particle.
 
It's really easiest to just explore SPR and it's application state with `showin` 
in the REPL.
 
The command: **showin** in the REPL will give the Application state to you in yaml.
The easiest way to access it is `showin device` or `showin config serial`
with `showin key1 key2,...` is the command to find sub-section or attributes in the REPL.
`showin config` , `showin defaults`, or just __showin__ 

The Application state, is actually just a merge, of all the yaml's defined
by the various modules, and by the core.yaml.

A complete configuration file can be generated at any time by saving it with
_save-config_. This is the first step in creating an application.

The configuration file should be named SPRConfig.yaml and will automatically loaded
from the runtime directory if it exists. A different name can be specified with
the `-c` option.

There are other things in the Application state, each SPR extension can
also add a structure to the root of the tree to hold the information that
it cares about.  This is the _state_ part of the structure. The Application
state is defined by collecting all of the extension modules yaml file and
merging them together as they are imported.

Yaml files can be merged directly into the application state config with load-config.

    `load-config foo.yaml`

Yaml files can be merged directly into the **Root** of the application 
state with load-yaml.

    `load-yaml foo.yaml`


### SPR/Python extensions

An SPR library/module is a Python module with a python file, a yaml file and
an spr file. An SPR library project can be created with the
    `new-spr-extension-project` command.
    
    `new-spr-extension-project <path/to/my/new/library/foo` 

To install, `python setup.py install` will install your project into
your local python environment / site-packages. 

Once the new module is available on the Python path SPR can import it with
a command like this. 
    `namespace foo "my foo namespace" foo.core function1 function2...`
    
This will create a _namespace foo_ within SPR with all the functions listed, 
as well as whatever is defined in `foo/core.spr`.  The application state 
will merge in what ever structure is defined in `foo/core.yaml`. 



#### How to do it.
* Make a python extension with the 
`SPR new-spr-extension-project path/to/project` command.
* Define some data structure/YAML.
* Add in some python code. - the stuff you really want to do. 
* Write some spr code if you need it.

Interact in the Repl, `SPR -r` to start creating new commands which are lists of other
commands. Test and play with your code, and create a new process.

#### Make one.
A picture is worth a million words. use the _new-spr-extension-project_ to
make a project and go look at it. looking at the help for a namespace may
also be enlightening. There are three core files to an SPR extension.
A python module, a yaml file and an spr file. Only the python
is necessary. All of the builtin extensions follow this same model.
_bar_qr_ in the repo is a good example if you want to read the source. 

Here is the result of `new-spr-extension-project foo`.

```
foo
├── foo
│   ├── core.py
│   ├── core.spr
│   ├── core.yaml
│   └── __init__.py
├── README.md
└── setup.py
```

#### Python code
SPR can just import a python module and make those functions available,
in the interpreter.  However, there is usually some sort of wrapping up
to make life easier in SPR. It is fairly easy to make an extension made
from example snippets gleaned from StackOverflow.

The python functions for use as an SPR extension are generally very simple, 
* Retrieve their configuration data from the Application state, 
* Do something, 
* Save the result back into their part of the application state as needed.

#### Help, Please.
It is recommended that one function be named `help` and that it prints
Text which explains the extensions usage. There is a nice template in
the extension project.

#### Yaml Data Structure
Additionally, an extension can define a yaml file which import will integrate
into the Application state. Configuration settings and whatever data structure
needed by the extension are defined here.

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


#### SPR code
This is where more Libraries can be imported and new symbols and partial functions 
can be defined. 

The Bar/QR extension is a good example of all of this. It only provides 3 public
functions and it has state, configuration, and a couple of SPR symbol definitions,
The files in the repo are: *bar_qr.py* *bar_qr.yaml* and *bar_qr.spr*

Here is the contents of *bar_qr.spr*. Notice it makes a new command `input-code`
which is actually a dialog window in the _ui_ namespace. The value vector given
is for _bar-QR/value_. So that is where the input dialog will put it's result.

The second function uses the newly defined `bq/input-code` along with another
command ui/print-bcqr to create what appears to be a 2 step process called
`print-codes`.

```
def input-code
    "Dialog to get a string to encode to a bar or QR code"
    ui/input-string-to bar-QR value

def print-codes
    "Dialogs to get a string, encode it, and print it as some number of Bar or QR codes."
    bq/input-code ui/print-bcqr
```



### Some core commands.
* namespace - create a namespace and import a SPR/python extension.
* ls-ns - List the namespaces.
* ns-tree - List the namespaces and their contents.
* ns - which namespace am I in.
* in-ns - change to a namespace
* import - import a SPR/python extension into the current namespace.
* def - Define a new command
* partial - Define a new command that is a partial of another.
* showin - show the Application state in YAML form.
* help - get help, help <name|ns|ns/name>


### The syntax. 

It's just a list of things with whitespace. words, strings and numbers.
If the first thing is a python function with arguments the rest of the list
is the arguments. If it isn't, then it's a list of commands and each is done
in turn. But each command, can be a list of things.

If you put spr in a file, each list must be separated by a blank line.  
A command list can be formatted however you like, but the lines must be 
contiguous. A blank line results in the command being executed. Here is a sample from

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

Here is an example of using a message box and creating a new command
that does the same thing. First is the using a msg box. Then defining
a new command mymsg, then using the new command.
```
    ui/msg "Hello World" 

    def mymsg "my special msg" ui/msgbox "Hello World"

    mymsg 
```


That's it. words strings and numbers separated by spaces. Commands
are separated by a blank line and can be formatted with whitespace in
any way, as long as the lines are contiguous.

#### Oh, well almost.
There is this thing, the *from* commands take a `from:` keyword.
so `as/set-in-from foo bar from: foo baz`
Will copy the contents from foo/baz to foo/bar in the Application state.

Slashes '/' are valid characters in names. It's not special in the grammar, 
but it is when looking up SPR symbols. The / is what denotes the namespace 
path for the functions. So if we want to use _msg_ in the _ui_ namespace we 
would write it like this. 

`ui/msg "hello"`

A complication of this, is that namespaces are still stupid, they don't know
where they are, and therefore the namespace must always be specified 
on commands even when inside the namespace.  It's a pain point, 
but it's not bad. The thing that nags me is that the namespace name 
can be arbitrary. Therefore, this is brittle.


## A few batteries included so far.

There are a few core libraries included within SPR, they are imported by SPR
into their various namespaces by `core.spr`

* log  - logging level and messaging.
* appstate - Application state - All the YAML, config etc.
* dialog - dialog windows for the user interface.
* cli - cli stuff for the user interface.
* network - Networking. wifi, ssh, etc.
* device  - Basic usb device interaction 
* particle_main  - Particle.io Board interaction.
* subcmd - shell commands etc.
* Bar_qr - a bar and QR code reader, generater, and printer
* mkext  - A function and files to create a sample SPR extension library project.
* os  - Some functions from python OS
* shutil  - Some functions from python shutil


#### Reusable parts to make stuff with.

So instead of a run it once kind of application, this is a tool that can be
used to interactively create a run it once kind of application.

The idea was to keep it as simple to use and code as possible, even if a bit
painful.  Everything had to be configurable, and new process pieces needed to
be easy to make.

So here it is. It's a language, but there are only variables in a big tree.
It can run python functions, and it can make partials of them if they take
arguments.  It's only syntax is words, strings, numbers and whitespace.

It has namespaces, primarily for organization. It has built in help.
You have to fill in your doc strings!  

It has no scope, no understanding of if I'm in this Namespace things have
shorter names.

But it's pretty nice for creating little processes that document themselves.
And it's super cool to recompose old things into new processes. It's a fun
little tool here.


## Execution

### The default process

In the configuration there is an __exec/autoexec__ attribute. This should be a
symbol name or list of symbol names to run as the default process. This
is the process that will run when running in interactive loop mode,
or when run once.
  
If symbols are given on the cli after the option then that list 
takes the place of the autoexec for that execution.


### Modes of running
  * Run Autoexec once
  * Run the Autoexec in an intractive loop
  * Run a repl
  * Run command line args once
  * Run command line args in an intractive loop
  * Run command line args once and start the repl

### Examples - mix and match.
  * `SPR -i` Run in a loop doing a process over and over 
  * `SPR` Run a process once 
  * `SPR cmd1 cmd2` Run a list of command/symbols from the command line 
  * `SPR -f foo.spr` Run an SPR file.
  * `SPR -r` Run as an interactive REPL 
  * `SPR -r cmds` Run as an interactive REPL, executing cmds on startup.
  * `SPR -rf foo.spr cmds` Run as an interactive REPL, loading a file and
  executing cmds on startup.

### Sources:
When run with no Arguments, SPR will try to do whatever is set as the
_autoexec_ in the configuration file. This setting should be a list of
words understood by the interpreter.

With `-f` a file can be given for SPR to run on startup before the
autoexec or repl is started. 

The configuration file can also hold SPR code in the `functions:` section.

Additionally there are hooks which can be defined in the configuration 
to do what you like, at particular steps of the process.

  
### Order of execution  
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


## Learning by example.
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
 * _def foo "foo show" showin foo
 * _partial_ bar "foo show" showin foo
 * _help_ foo
 * _help_ bar
 * foo
 * bar
 * _set_ foo bar 10
 * _foo_ 
 * _bar_
 * _foo_ bar
 * _bar_ bar
 * _set-from_ foo foo from: foo bar
 * _foo_
 * ui/msg "hello"
 * def mymsg "my msg help" ui/msg "hello"

Once in the REPL at the prompt; __SPR:>,
_help_ shows all the commands known with their documentation. 

## In case more explanation is necessary, Symbols/Commands/functions

There are several kinds.

 * lists of symbols, _dolist_s.
 * python functions, _fptr_s.
 * lists of symbols, but which resolve to partially completed 
   fptr commands, these are called _partial_s.

### dolist commands

_dolist_ commands are commands defined in spr or the configuration. 
They are strings which can be parsed and evaluated by the REPL/interpreter.

_dolist_ commands can be built from other _dolist_ commands and _fptr_ commands.
_dolist_ commands can be defined in yaml, in python code, or interactively in the REPL.

### function pointers
_fptr_s can only be created with the repl's import and namespace commands through
the process of importing a python library into SPR.


### Partial commands

_partial_ commands are built from _fptr_ commands.
_partial_ commands are like dolist commands. Except that the first symbol in
the list is an fptr symbol, and the list is not everything the fptr function needs.
when using a partial, they act just like fptr functions, you just have to leave off
some or all of the first arguments.

_partial_ commands can only be defined in SPR code, and interactively.

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
      
