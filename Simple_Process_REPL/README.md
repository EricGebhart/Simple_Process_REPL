# Simple Process REPL

[Read the wiki](https://github.com/EricGebhart/Simple_Process_REPL/wiki)


### What is it?

It's a fun to use tool to create applications which do processes.
It's just simple enough to be transparent and easy, and just smart
enough to not be too annoying. 

This program is actually a very simple interpreter with an interactive REPL,
and a data store that can be easily setup and manipulated. Any python library
can be imported an used directly. Think of it as glue code for python libraries.

SPR code is really simple. SPR only knows words, strings and numbers.
If you give it a list, it will try to look up what you gave it and 
execute it. It handles failures nicely, and can run a process once, in a loop
with start and end dialogs, or interactively in the REPL.

This started as a simple script and a yaml config file. All that was needed
was to setup the data then try to run a list of commands using that data.
It has since eaten it's self quite a bit. Lots of python code is gone as it
is mostly unnecessary to write any.

Now, it is less and more than that. It is a data store tree which is built
up from yaml data in the SPR files or modules that are imported. It has name 
spaces which can import python libraries and Spr code. Keeping things as
simple as possible has been a priority. No features unless it's easy and
a real pain point.

SPR is not scoping language, but scope is built manually using the _with_ construct.
The _with_ stack is a list of paths in the data store.  Parameters are
automatically bound to python functions, if they are not given and they are found.  
The values are looked for in the locations held by the with stack.  The data is 
YAML, and the language is also yaml. 
The lines between data and code are very blurred if they exist at all.

Any project can exist as a single SPR file.  The only python that might be needed
is mostly simple wrappers to provide better API's.

## Installation

    pip install Simple_Process_REPL
    
You will also need to install dialog and zbar for the qrcode and barcode library.
If you desire particle.io functionalities you will also need to install the
particle.io cli.

on Arch Linux

    sudo pacman -S dialog

or on Apple

    brew install dialog

For Zbar follow the instructions [here.](https://pypi.org/project/pyzbar/)

For particle.io functionalities follow the instructions 
[here.](https://docs.particle.io/tutorials/developer-tools/cli/#installing)

## Start the REPL

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


## Start in the REPL 

`SPR -r`

Explore the namespace functionalities you might want to use. Use
__help__, __pyhelp__ and __ls__ to see the functions, their signatures, and their
source code.
Explore the data using __show__ to see the data they use. 
Another way is to actualy call their __with__ or initialize functions, 
and then explore the __with stack__ they create.

Start with creating a YAML data tree of all the data you need, to start
calling functions. Modules which need things also provide functions which 
setup the _with stack_. The current with stack data can be shown with __as/show-with__.

List the namespaces you want to use, if they need it, there will be functions that
will create a _with stack_ for that set of functionalities so that it easy to see what
that namespace needs for data. build up the default _with stack_ and everything should
work. Then add your own space to the stack and start adding or redefining what you
need.

### After the with stack is set.

If you have all the data from the modules you want to use in your _with stack_
you should be good to go and start calling functions. 

Place an empty space on the with as the last thing. Any values that need to be
changed can be defined here. A flattened version of the with stack can be seen
with _as/flat-with_.

Build up the steps to the process in the REPL until you have them working. 
Make functions out of logical grouping of functionality. keep building.

Everything boils down to a python function, parameters are
automatically bound from the _with stack_. But can also be provided directly as 
needed.  The value at a path can be passed with a __~__ prefix on the path.

After a function call, the local results stack can be popped to any location 
in the datastore so that other functions might find the last value.

SPR can be configured to run as an application, which will execute once, or
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
This is a really simple interpreter, think of it as a glue layer on top of python.
All with nice configuration and application state management
It's easy to get and put things into the data store
which is represented as a big tree of Yaml. 

A chain of functions to do the complicated bits.

Once it's done, with just a configuration file you could have an
application that does a repeatable process with a builtin REPL. 

