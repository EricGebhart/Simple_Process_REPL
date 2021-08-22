# Simple Process REPL

A YAML datastore, a config file, a namespace manager, and an interpreter walk 
into a bar...

This has been changing a lot, the wiki is a bit chaotic.
Important concepts are: 
 * datastore/appstate in the _as_ namepace
 * The _With_ stack.
 * The _results_ stack.

 Short-cuts: 
  * [Read the Wiki](https://github.com/EricGebhart/Simple_Process_REPL/wiki)
  * Read all the help for all the namespaces.
  

## Installation

    pip install Simple_Process_REPL
    
You will also need to install dialog. tkinter is coming probably.

on Arch Linux

    sudo pacman -S dialog

or on Apple

    brew install dialog


To start the REPL;

    SPR -r

read, think, type, repeat.
  
  
### zbar requirement.

At the moment there is a requirement for zbar in order to detect 
bar and QR codes with the camera. This will need to be installed manually.
Instructions can be found in the
    [pyzbar documentation.](https://pypi.org/project/pyzbar/)
    
    
### What is it?

Many things.

In a way, SPR feels like python did in 1995. It was the glue that was
easy to use to put things together with. Python hasn't lost it's abilities,
but it's not that simple glue anymore, and it's not what I consider 
a high level language at this point. Python feels much closer to C, to me,
than it used to. Probably because I've been ruined by programming in
clojure and haskell. 

SPR is a fun to use tool to create applications which do processes.
It's simple enough to be transparent and easy, and smart
enough to be a pleasure. Anything serious and there is always python
right there.

SPR can be used to interactively create and run 
a process as if it is an application. Possibly with nothing but a configuration
file.

SPR is actually a very simple interpreter with an interactive REPL. 

The code is data, and the data is code.
But it keeps code and data separate in a nice way. Function parameters are
automatically bound if they are needed and can be found.

SPR code is really simple. SPR only knows YAML, words, strings and numbers.
If you give it a list, it will try to look up what you gave it and 
execute it.  So you can make lists and give them names, and make lists of lists,
all of which turns into a process which will try to do it's thing, and if any
step fails, the whole process fails. All with nice error handling, logging,
dialogs, configuration, integrated help, self introspection, a REPL, along 
with various methods of execution.


## To sum up.

This is a really simple interpreter, with a really short list of commands, 
think of it as a stupid/smart layer on top of python.

It's got some really handy extensions for making processes, and extensions
are easy to make from a bit of python code. It will even create an
extension project template for you. That's one of it's many commands.

All with nice configuration and yaml datastore management, logging,
and error handling. It runs like an application once it has a process,
and it can repeat it interactively, reporting failures.
And it has a REPL. So you can play with it interactively, building things.


Just a big yaml datastore Tree and
python functions. Failures are expected.
It's easy to get and put things into the yaml datastore 
which is represented as a big tree of Yaml. 

## The parts.
  * The Interpreter/Repl
  * Namespaces
  * appstate/ _as_ ie. the datastore.
  * a with stack
  * results stacks.
  * yaml datastore data structure, configuration, state, etc...
  * SPR/Python extensions that are built in.
  * Any python module you care to import.


## Status

At this point, I think it has enough that it should be used and evaluated for
the coding patterns needed to create solutions. It's actually quite powerful,
and I'm looking forward to what happens next with it.

existing processes:

* particle test flash   - Particle board programmer, flasher, tester, environment.
* print-codes - print bar and QR codes.
* internal readme viewer code




