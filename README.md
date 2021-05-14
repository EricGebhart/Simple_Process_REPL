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
Well, at this point it's kind of fun. It's been really interesting to see
how it evolves. And why is it evolving? Well, because it's fun.

It's been eating it's self lately, I find that super exciting.

I've written other languages, my tagset language for SAS, 
and a couple of lisps among other things.  This wasn't really intentional,
and it comes with a strong desire to keep it from becoming a real turing
complete language. But it seems to be happening anyway.

What will happen? I don't know !

The basic idea is to only change something if it makes sense and it's simple.
It must be simple and elegant. 
Now the interesting thing is the complexity of the things 
you can build with such simple things, if you build your simple things correctly.

That has changed so much here. Because of the restrictions of the appstate, or
thinking of it as an app state, instead of just namespace, things changed 
dramatically with that change of point of view.  Now, set-in is making variables,
we are just stashing them in a big global tree.  Then it went from value vectors,

The python representation changed like so.
`[foo bar baz]` Became: `foo/bar/baz`.  

And the evolution of set evolved from

`set-in foo bar baz 10`
`set-from foo baz from: foo bar baz`

to this:

`set foo bar baz 10`
`set foo baz from: foo bar baz`

to this:

`set foo/bar/baz 10`
`set foo/baz  /foo/bar/baz`


They've been through a lot of change over time.
They are modeled after clojure's _update-in_, and _get-in_. But now they use
paths instead. It feels much more intuitive to wander around the system space
with **ls** and **show**.

The idea of **-from** and **-to** changed things too, those are essentially all that
is needed within a module for it to get the stuff to and from other module's,
application state, or where ever you are putting your stuff.

But that led to **-with** variants, so now, we give a path full of stuff to a 
function and it goes and gets what it wants _with_ what you have there.

So, I'm not sure where that's headed, but it seems like that could boil away too.
A _with_ function, and the lower level python code in every module goes away.

But the interpreter really hasn't changed, and it's way more stupid than the 
dumbest of lisp interpreters. And they can be pretty stupid too.

The symbols have gotten more complex over time. 
It's really interesting see something blow up into something big and 
then refactor into something smaller and more capable than the original. 
I like watching the architecture become more elegant.

I wrote exercism's "100 Bottles of Beer" exercise 21 different times in clojure 
alone.  Just to see how it boiled down. I had 3 basic flavors in the end, that
were more elegant, concise and readable than all the rest.

I added barcodes, because that was a requirement for a thing I made for someone.
When I did that, I decided to add simple namespaces, which led to just changing
everything from stupid simple and obvious symbol tables, to a more elegant import
system. Oh, so instead of that hardcoded symbol table, I had to make code to 
figure out python function signatures and do the right thing. 

Then, instead of a big ol YAML, each module could keep it's own
pieces. 

These things changed everything, but the language, if you can call it that, 
It's only syntax is whitespace, and I guess we can count the */'s* in the paths.
But, then, once I had namespaces, and imports and

And despite it's growing capabilities its doing it with less code. That's cool.

I sort of want to give a choice of repl's so more fun could be had that way.
And why not have a repl server and an emacs mode so I can run spr code in emacs. 

So, endless fun. Why not.


## History
This started out as a zsh script to identify, test, and flash a particle.io
board. The script can be found in the repo.

The option parsing of the script turned into a REPL out of frustration
with developing the process.

The boards and services are finicky, and the ability to be able
to create repeatable snippets of processes was the way to go. Two pieces
might work individually and not one after the other, or the device would
disconnect for a moment. It was a pull your hair out kind of experience.

It then turned into Python.

The original python version 1 of SPR now lives on as 
[The Particle Board REPL](https://github.com/ericgebhart/Particle_Board_REPL.git).
PBR is an application layer built on top of the previous version of SPR, which
was a bit of a pain to extend. PBR is now a standalone application that embodies 
the old version 1 of SPR.

I built the REPL first and started converting all my functionality to
python. This particle board process also needed wifi, the concept of a device, 
usb handshaking, device waiting and dialog prompts among other things.

So in the end, it was really nice, and it did what was needed relatively easily.
Actually creating a working process from the parts took very little time.

Then I added barcodes. which prompted namespaces, importing, better help,
paths... And now there is SPR 2.

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

This is a really simple interpreter, with a really short list of commands, 
think of it as a stupid/smart layer on top of python.

All with nice configuration and application state management, logging,
and error handling. It runs like an application once it has a process,
and it can repeat it interactively, reporting failures.
And it has a REPL. So you can play with it interactively, building things.

All with no syntax beyond this snippet, newlines and indention are optional, 
blank lines are not.

```    
    ui/msg "hello"

    def mymsg "This says hello" 
        ui/msg "hello"

    mymsg

SPR:> set /foo/bar 10

SPR:> show foo
bar: 10

SPR:> set /foo/baz /foo/bar

SPR:> show foo
bar: 10
baz: 10

```

no logic, Just a big Application State Tree and
python functions.
It's easy to get and put things into the Application state 
which is represented as a big tree of Yaml. 

If you build a process, 

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

There are two help systems. SPR's and python's. They have two different
presentations of the same thing, both are very useful.
**help** and **pyhelp** will give you the documentation for every 
namespace and command available, even the ones you just created. 

 * `help` will show a short summary, followed by an _ls_
 * `help /` will show full namespace help for the Root namespace. 
 * `help ns` will show full namespace help for the ns namespace. 
 * `help ns/name` will show full function help for the ns/name function. 

The same rules apply to the **pyhelp** command, but what it shows is different. 

Additionally each SPR module can have it's own help function which 
can be invoked as any other function, and which will be used by namespace
help if it exists. Extensions use a template which contains a help 
template showing SPR information in a pretty way.

Both the module's Application state and spr code are shown in the help
if they exist.

The **ls** command will navigate both the Namespaces of SPR and the
Application state. Any path that starts with a / looks in the Application
state. Anything that does not start with a / is looked up in the Namespaces.

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

 * `ls` will list all the namespaces. 
 * `ls name` will list the contents of that namespace. 
 * `help name` will show the namespace help, which includes the YAML, and spr code.
    As well as the SPR help for each symbol.
 * `pyhelp name` will show the python module help for the module 
    imported into that namespace on it's creation. 
 * `ns-tree` will list all the namespaces with their contents. 
 * `import` will import a python module
 * `ns` will tell you which namespace you are in.
 * `in-ns` will move you to another namespace. - which only matters for 
    _def, partial_, and _import_.

Creating a namespace called foo from a python module _foo.core_ looks like this:
```
    namespace foo "my foo namespace that does bar" 
        foo.core 
        function1 function2 ...`
```

After a namespace command, the interpreter will remain in that namespace
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

#### Introspection

If the code patterns are adhered to, ie. The module defines
it's yaml like so. Perhaps we should make a modules space.
It's getting cluttered in /.

```code=YAML
    mymodulename:
        mystuff1: "foo"
        mystuff2: "bar"
    config:
        mymodulename:
            mytitle: "sometitle I guess."
```

Given that. A namespace can be explored with the following
SPR commands, where <ns> is the name of the namespace: 

 * `ls <ns>` to see a summary of the namespace.

 * `help <ns>` to get help for the namespace.
 * `help <ns>/<function>` to get help for a function in the namespace.

 * `pyhelp <ns>` to get python help for the namespace.
 * `pyhelp <ns>/<function>` to get python help for a function in the namespace.

 * `show <ns>` to see the Stateful data used by the namespace.
 * `show /config/<ns>` to see the configuration data used by the device namespace


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
 
#### Paths
 
The entire system is held in this tree. so think of it like a filesystem on
your computer. Lots of folders in a big tree. Pathnames are used to get things
and put things and look at things.

Paths are just like filesystem paths in Unix/Linux.  The namespaces can be 
thought of as one tree, built from imported python code, 
and the Application state as another that is built from YAML.

`ls` navigates both trees.
`set` uses paths like variable names. getting and putting values in them.
`show` uses paths to find what to show.
`-with` and `-from` and `-to` functions use them to find and put their data.

```
    SPR:> set foo/bar 10

    SPR:> show foo
    bar: 10


    SPR:> set foo/baz /foo/bar

    SPR:> show foo
    bar: 10
    baz: 10

    SPR:> ls /foo
    bar                           
    baz
```


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

To that end, the template created has example _-to_, _-from_ and _-with_ 
functions to be used.


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

    def mymsg "my special msg" 
        ui/msgbox "Hello World"

    mymsg 
```


That's it. words strings and numbers separated by spaces. Commands
are separated by a blank line and can be formatted with whitespace in
any way, as long as the lines are contiguous.


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
* web  - View HTML or URL, Browse a URL.
* markdown  - Convert Markdown to HTML.


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
 * _ls_ 
 * _ls /_ 
 * _ls bq_
 * _ls /bar-QR_
 * _show /bar-QR_
 * _show bar-QR_
 * _show_ or _show /_ --- is big. 
 * _ls /config_
 * _ns-tree_ 
 * _help_ 
 * _pyhelp_ 
 * _help def_
 * _pyhelp def_
 * _help sh_
 * _pyhelp sh_
 * _help sh/do_
 * _pyhelp sh/do_
 * _ls_
 * _show_ 
 * _show_ device
 * _show_ foo
 * _def foo "foo show" as/show foo
 * _partial_ bar "foo show" as/show foo
 * _help_ foo
 * _help_ bar
 * foo
 * bar
 * _set_ /foo/bar 10
 * _foo_ 
 * _bar_
 * _foo_ bar
 * _bar_ bar
 * _set-from_ foo/foo foo/bar
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
They are created with the `def` command.

_dolist_ commands can be built from other _dolist_ commands and _fptr_ commands.
_dolist_ commands can be defined in yaml, in python code, or interactively in the REPL.

### function pointers
_fptr_s can only be created with the repl's import and namespace commands through
the process of importing a python library into SPR.


### Partial commands

_partial_s are created with the `partial` command.

_partial_ commands are built from _fptr_ commands.
_partial_ commands are like dolist commands. Except that the first symbol in
the list is an fptr symbol, and the list is not everything the fptr function needs.
when using a partial, they act just like fptr functions, you just have to leave off
some or all of the first arguments.

_partial_ commands can only be defined in SPR code, and interactively.


### Handshake function

Keeping this here, so it is findable in multiple ways.

The handshake function is defined in the device module which
is imported into the _dev_ namespace. Therefore, more help
is available like this.

See also: 
 * `help dev` to get help for the dev namespace, which
 has imported the device extension module.
 * `show device` to see the Stateful data used by the device namespace
 * `show config/device` to see the configuration data used by the device namespace

Handshake is a generic function that is a bit more complicated.  
It manages an interaction with a device. Everything _handshake_ 
does is defined in the configuration file. As with everything else, 
if anything fails, or doesn't match, an exception is raised.

Here are the steps that _handshake()_ does.

  * Wait for the specified device path to appear.
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
      
