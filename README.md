# Simple Process REPL

A YAML datastore, a config file, a namespace manager, and an interpreter walk 
into a bar...

I hope this document is not too annoying in it's repeating. I'm working on it.
It some ways it less important now since help is so good.
But I'd rather have too much than too little.

Trying very hard to keep this primitive so that it will only grow in necessary
and helpful ways.

I think, really, this would be better, if I just replaced the core repl with plysp.
But, I'm riding it out to see where it goes. 

At this point, I think it has enough that it should be used and evaluated for
the coding patterns needed to create solutions. It seems powerful enough, and
not annoying. 

The readme section of the app is one example, as it uses _with_, the _results_ stack,
automatic parameter binding, markdown, webviewer,
and webbrowser. Refactoring the particle board code to the emerging code patterns
is another step. 

Because of the _with_ stack, there is now stack and list capabilities. _With_
should be refactored to be written in spr instead of python. 
That would then cause the pop-with function to go away, as the regular
_pop_ could do it.  Maybe it already can since the internal with stack is
surfaced in the appstate. Need to check, ah, works already. Should be prettier.
See below.

```
SPR:> ls /
    config                        
    args                          
    defaults                      
    platform                      
    _with_                        
    _Root_                        
    device                        
    network                       
    markdown                      
    readme                        
    foo                           

SPR:> ls  /_with_
    {'path': '/', 'vv': []}       

SPR:> show  /_with_
/_with_
- path: /
  vv: []
  
  
SPR:> with foo

SPR:> with
/foo
-------------------------
    mymsg                         
    msg                           

SPR:> pop /_with_

SPR:> with
/
-------------------------
    config                        
    args                          
    defaults                      
    platform                      
    _with_                        
    _Root_                        
    device                        
    network                       
    markdown                      
    readme                        
    foo               
    
```


Python code is disappearing, after this last refactor I think the _markdown.py_ 
file can just go away. But it needs to be tested.

The way things work and read is a bit surprising. Here is basic use,
showing strings, path resolution.

There is also with, combined with YAML, and automatic parameter binding.

Here is some examples to show how things are working.

```
# stupid simple, give a message dialog window. 
SPR:> help cli/msg

SPR Help
=============================================

cli/msg(msg)        
----------------
Display a message on the cli and wait for input.

SPR:> cli/msg "Hello World"
"Hello World"
Press any key to continue;

SPR:> set /foo/mymsg "Hello World"
"Hello World"

SPR:> ls /foo
    mymsg                         

SPR:> show /foo
/foo
mymsg: '"Hello World"'


SPR:> cli/msg /foo/mymsg
"Hello World"
Press any key to continue;

SPR:> with /foo

SPR:> with
/foo
-------------------------
    mymsg                         

SPR:> '
YAML...>msg: This is another message to say hello.
YAML...>

SPR:> with
/foo
-------------------------
    mymsg                         
    msg                           

SPR:> ls /foo
    mymsg                         
    msg                           

SPR:> show /foo
/foo
msg: This is another message to say hello.
mymsg: '"Hello World"'


SPR:> cli/msg
This is another message to say hello.
Press any key to continue;

SPR:> with
/foo
-------------------------
    mymsg                         
    msg                           

```

#### The With Stack.

Here is the continuation of that session, to show the _with_ stack
and how it works.


```
SPR:> with
/foo
-------------------------
    mymsg                         
    msg                           

SPR:> help with

SPR Help
=============================================

 with                
--------------
"Set or show the current with path."
    Type: partial
    Source: [as/-with]

  --- Derived from: ---

    as/-with(path=None) 
    ----------------
    
    Show the current 'With' path or if a path is given,
    Push a Yaml datastore path onto the 'with' stack.

    If it is not yet there, it will appear when someone sets something.
    

SPR:> ls as

as         Simple_Process_REPL.appstate: 
---------------------------------------------
"Application State functionality"
   -print-stack()                
   -show-with()                  
   -with(path=None)              
   archive-log(new_name)         
   eval-default-process()        
   help()                        
   load-config(filename)         
   load-pkg-resource(package, filename)
   load-yaml(yaml_file)          
   merge-yaml(y)                 
   pop(path, destination=None)   
   pop-with()                    
   push(set_path, fromv)         
   reset-device()                
   save-config(filename)         
   set(set_path, fromv)          
   set-in(*keys)                 
   show(pathname='/')            
   sync-functions()              

SPR:> as/-print-stack
/foo
/readme
/

SPR:> as/-show-with
/foo
----------------------
/foo
msg: This is another message to say hello.
mymsg: '"Hello World"'


SPR:> with
/foo
-------------------------
    mymsg                         
    msg                           

SPR:> ls /foo
    mymsg                         
    msg                           

SPR:> as/-print-stack
/foo
/readme
/

SPR:> pop-with

SPR:> as/-print-stack
/readme
/

SPR:> with
/readme
-------------------------
    package                       
    filename                      
    url                           
    title                         
    results                       
    markdown                      
    html                          

SPR:> pop-with

SPR:> as/-print-stack
/

SPR:> with
/
-------------------------
    config                        
    args                          
    defaults                      
    platform                      
    _with_                        
    _Root_                        
    device                        
    network                       
    markdown                      
    readme                        
    foo                           

SPR:> ls foo
Unkown Symbol: foo
'NoneType' object is not subscriptable

SPR:> ls /foo
    mymsg                         
    msg                           

SPR:> show /foo
/foo
msg: This is another message to say hello.
mymsg: '"Hello World"'

```

These latest changes have altered things dramatically, to the point that earlier
design patterns have gone away, and the necessity for python code is disappearing.

I did add variable resolution only to remove it. There is still no scope or stack,
paths allow for pointer like behavior. __With__ means you probably will
never care if variables in the common sense exist.

Data structures are easy to make with inline YAML which automatically merges into
the system.

The results stack is an example of both a path which moves, and a list/stack.
Data can be pushed and popped to their locations. Lists are created automatically
as needed. popping a non-stack will behave as if it was one.

The code patterns are still emerging and changing. but currently something like this,
is showing up. 

 * Point at some path in the application data store using _with_.
 * set __value__ and __codetype__ in that location using YAML syntax.
 * Call the bar code generation function `bq/gen` which uses the values in _with_.
 * pop the last result from the results stack and put it in __code__.


#### A current, simple code pattern:

```
with foo
'
url: someurlsomewhere
msg: some message.

cli/msg
web/browse

pop-with
```

#### A real example.

```
with /mystuff/barcode

'
value : ABC
codetype : barcode
# codetype : QR-code


bq/gen

pop results code

pop-with
```

#### A more complex code pattern.
This is from _core.spr_ and is what configures and creates
the readme functionality in SPR. The steps it takes are:

  * Create and move to a new path called _/readme_ 
  * Use Yaml to define the data needed by **as/load-pkg-resource**.
  * Call **load-pkg-resource** 
  * move the result of that to _/readme/markdown_ with the 
  `pop results markdown` command.
  * Call **md/html** to convert the markdown to html
  * move the result of that to _/readme/html_ with the 
  `pop results html` command.
  * Define two new commands to view/browse the readme.
  
If this is as common as it seems it will be, a _partial_ for 
`pop results` would be nice.

A function to add a function's parameter map to a path would be nice
to have. 


```
# Set up readme folder with stuff,
# then load the readme and convert to html.
with /readme

'
package: Simple_Process_REPL
filename: README.md
url: https://github.com/EricGebhart/Simple_Process_REPL/blob/main/README.md
title: "The SPR README!!!"


# load the resource at readme. 
# works because, 'with', readme has vars which match the function signature.
as/load-pkg-resource

# pop the last result to markdown.
pop results markdown

# convert the markdown to html.
md/html

# move the last result to html.
pop results html

# view-with and browse-with are handy to have. - they can point where they want.
# view and browse use the current 'with'...
def view-doc "Display the Readme documentation in an html viewer."
    web/view-with readme

def browse-doc "Display the Readme documentation in a browser window."
    web/browse-with readme
```

The _with_ concept works really well, and the results stack which moves
around with the _with_, `pop results to/somewhere`

The parameter bindings do their best when calling python functions.
If some parameters but not all are given, the current _with_ will fill
in the rest if it can find matches to the parameters.

Paths without a leading / are relative to the setting of the _with_.

#### Possible pattern

I can see that it could be super beneficial to make it so that _with_ can 
be initialized from another data tree or trees.  So that a configuration
could be set up, then copied and used when anyone wanted to do that thing.

This is possible already using set. the following would create tree1 as needed
from a merge of tree1 and tree2 and tree3, it then moves to tree1 and
adds some yaml which will also be merged into tree1.

```
Set tree1 /config/tree2
Set tree1 /config/tree3
with tree1
'
some: yaml
```



### Creating functions.

This is just some of the entertaining things that come about. it turns out,
that because eval knows how to process a list of commands, and because we
can easily create lists, we can then easily create a sequence of things to
be done and do them.  Our code is data, our data is code.

This session creates a dataspace/folder/dictionary at /foo and pushes it
on the with stack. 
It then creates entries for msg, bar, and baz. 
Notice that bar is spr code, and baz is a yaml list of spr code.

__with__ and __show__ show what is there.

Then we get a bunch of messages, in different ways.
De-referencing and executing the data.

```
SPR:> with /foo

SPR:> '
YAML...>msg: this is my message. Hello.
YAML...>bar: cli/msg /foo/msg
YAML...>baz:
YAML...>- cli/msg /foo/msg
YAML...>- cli/msg Hello from the middle
YAML...>- cli/msg /foo/msg
YAML...>- cli/msg Goodbye.
YAML...>

SPR:> with
/foo
-------------------------
    msg                           
    bar                           
    baz                           

SPR:> ls /
    config                        
    args                          
    defaults                      
    platform                      
    _with_                        
    _Root_                        
    device                        
    network                       
    markdown                      
    readme                        
    foo       

SPR:> show /foo
/foo
bar: cli/msg /foo/msg
baz:
- cli/msg /foo/msg
- cli/msg Hello
- cli/msg /foo/msg
- cli/msg Goodbye.
msg: this is my message.


SPR:> cli/msg /foo/msg
this is my message.
Press any key to continue;

SPR:> eval /foo/bar
this is my message.
Press any key to continue;

SPR:> eval /foo/baz
this is my message. 
Press any key to continue;
Hello
Press any key to continue;
this is my message.
Press any key to continue;
Goodbye.
Press any key to continue;
```



I could probably chop this down to 

 * pip install, 
 * `SPR -r`
 * read, think, type, repeat.
 
 Short-cuts: 
  * Jump to the learn by example section. - Do it. - play, read.
  * `new-spr-extension-project myproj.` - look at the code.
  * Read all the help for all the namespaces.

### What is it?

The original need, was a process to interact with a particle board
and a person, in order to do a variety of steps that would register, 
test and flash a particle.io based device, to it's completed state. 
To be able to do that process once, or interactively over and over.

That purpose came with a variety of requirements, that come with many 
applications. It should be Documented, configurable, easy to maintain, 
use and adapt. It needed wifi, and dialog windows, and a way to execute
shell commands. Possibly ssh, and barcode reading and writing. 
The ability to easily update to a new process remotely.

The ideal that has been held in mind in SPR's creation, which was
born of the initial shell script, is to create an easy to use tool 
that will enable the creation of
repeatable processes which are easily configured. The processes
could be interactive or not, dialog and a cli interface are
provided for that.

Text translation was always a possibility, so all messages should be
configurable.

It needed to also be self documenting, such that it could be easily 
understood and reasoned about.

It should be easy to import and use python code and
leverage the abilities of python and libraries with a glue 
that is easy to understand and compose. 

In a way, it feels like python did in 1995. It was the glue that was
easy to use to put things together with. Python hasn't lost it's abilities,
but it's not that simple glue anymore, and it's not what I consider 
a high level language at this point. Python feels much closer to C, to me,
than it used to. Probably because I've been ruined by programming in
clojure and haskell.  I don't want to have to write a list comprehension
every time I want to do anything.  I'm accustomed to a simple one liner,
map/reduce/select/filter, walk, update-in, not a python list comprehension. 

I like to think about what I'm doing not the syntax for the language that
I'm trying to do it in.

SPR is a fun to use tool to create applications which do processes.
It's just stupid enough to be transparent and easy, and just smart
enough to not be too annoying. 

This is a tool that can be used to interactively create a run 
a process as if it is an application. Possibly with nothing but a configuration
file.

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

And it's a nice way to make a new tool, that has all the power of Python
behind it.

And the next time I need something, and I can make a cool thing in a small
amount of time, using this fun thing to make it, that's a win.

So far, I like it's simplicity, but can't help but wonder if that's a red 
herring in a way. If I took the appstate piece and core and combined it
with plysp that would be super powerful, but then perhaps daunting to
someone that would be comfortable with the way PBR or SPR work 
in their, non-lispless way.

It's been eating it's self lately, I find that super exciting.
I think I have successfully avoided having variables per se.
Adding partials felt like pandora's box. And now a _with_ stack, 
_result_ stacks, and smarter dynamic binding, it's getting interesting.

So still no variables, added them, took them out, don't miss them.

The appstate feels like a configuration and data tree maker / navigator.
It feels like this is the real innovation here. The repl is super primitive, 
and I like that. It keeps the complexity in the python.

It makes it easy to create, manipulate configuration and runtime data, 
It enables the repl to ask for bindings and gives it a place to push results.
In a lisp, appstate wouldn't exist. it would be the environment stack.
Instead we have a tree and you can shine the light on any part of it by pushing
it on the 'with' stack. Yaml, set, etc will then operate as if you are located at
that path location in the data tree.

Even if I were to plug in a lisp interpreter, the appstate is still super useful
and interesting. I am really curious how far it will go if I stay away
from that and only create higher order functions.

I've written other languages, my tagset language for SAS, 
and a couple of lisps among other things.  This wasn't really intentional,
and it comes with a strong desire to keep it from becoming a real turing
complete language. But it seems to be happening anyway.

I like the idea of keeping it syntaxless.  I think that is a nice
limitation that keeps it from changing too quickly. I have to be
really thoughtful about the naming and doing of things.
but I also want to try plugging in a different repl. 

What will happen? I don't know ! I suppose that's why it's fun.
It is already doing a great job at making handy self documenting 
scripts quickly.

So it's useful and it's fun. I want to smash it together with plysp and
see what happens. But I'm also curious about where the SPR ouroboros will 
stop. And what it might become.


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
the old version 1 of SPR. The same could be done with SPR 2, as the mechanisms
used by PBR to extend SPR are still there.

I built the REPL first and started converting all my functionality to
python. This particle board process also needed wifi, the concept of a device, 
usb handshaking, device waiting and dialog prompts among other things.

So in the end, it was really nice, and it did what was needed relatively easily.
Actually creating a working process from the parts took very little time.

Then I added barcodes. which prompted namespaces, importing, better help,
paths... And now there is SPR 2.

But it's job and purpose are really to provide a simple interface which can
configure a process that can be built by writing a little bit of python.
With the infrastructure taken care of the python code is simple 
and the gratification of building an application
that can be given to anyone is really high.

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

It's got some really handy extensions for making processes, and extensions
are easy to make from a bit of python code. It will even create an
extension project template for you. That's one of it's many commands.

All with nice configuration and yaml datastore management, logging,
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

Just a big yaml datastore Tree and
python functions. Failures are expected.
It's easy to get and put things into the yaml datastore 
which is represented as a big tree of Yaml. 

## The parts.
  * The Interpreter/Repl
  * Namespaces
  * yaml datastore data structure
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

Both the module's yaml datastore and spr code are shown in the help
if they exist.

The **ls** command will navigate both the Namespaces of SPR and the
yaml datastore. Any path that starts with a / looks in the yaml datastore. 
Anything that does not start with a / is looked up in the Namespaces.

The interpreter does it's best to call the
python functions you tell it to.  It recognizes, words, strings and numbers.
ie. `foo "this is a string" 10`, it understands functions with various 
signatures including variable arguments, but not keywords. Which aren't
valid in it's non-existent syntax anyway.

Well almost non existant syntax.
 * ' by itself to read the YAML that follows, terminated with two blank lines.
 * # in the first character of the line is a comment.

A single quote on a line by it's self, followed by yaml,
and another **2 Blank lines** will cause the interpreter to
switch parsers and merge the yaml it finds there into the yaml datastore.

Here is an example from bar_qr.spr:
```
'
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


def input-code
    "Dialog to get a string to encode to a bar or QR code"
    ui/input-string-to bar-QR value

def print-codes
    "Dialogs to get a string, encode it, and print it as some number of Bar or QR codes."
    bq/input-code ui/print-bcqr

```

The REPL is fun to use. It makes it super easy to
interactively create/execute a process step by step. 
`help` at the REPL prompt. 

On startup, there are only a dozen or so commands imported directly into
the repl. The rest of the initialization is done by _core.spr_ which
imports the rest of the extensions into their namespaces.


### Namespaces

A namespace is a structure that holds some stuff, and a list of symbols.
Think of it as a folder of commands. That really is about the extent of it.

When a namespace is created the python functions are imported directly 
into it, The module's spr code is also run, and the yaml code associated 
with the import module will be integrated into the yaml datastore tree.

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


### yaml datastore 

The yaml datastore, is actually just a merge, of all the yaml's defined
by the various modules, and by the core.yaml.

It is a data structure that was originally the configuration loaded
from a YAML file. It still is. But it's also where processes and extensions
can put stateful data that they are keeping track of or using.
So config, is for stuff you want to define in a file, and you mostly don't change.
and next to config, you can see them with `ls /` is lots of other stuff. 

You can save this config and change it, and load it to change the ways that
different modules behave, or even how SPR behaves. It's prompt was one of the first
options to go into the config section.

The yaml datastore is first built from the core of SPR, and then with each import
that SPR makes.  If you import _mymodule.foo_, spr will also merge _mymodule.foo.yaml.
into the yaml datastore, and will then execute foo.spr
It is also possible to embed the yaml in the the spr file with a **'**
on a line by itself just before the YAML. The YAML should be followed by
two blank lines, that tells the SPR parser to stop parsing YAML and
go back to normal.

Truthfully it's probably a waste of time writing this, 
The easiest way to see what is there is to go look.
Just go into the REPL and have a look around. Use `ls /<path>` and `show <path>`.

A complete configuration file can be generated at any time by saving it with
_save-config_. Note that this is only the **config** section of the data tree.

The configuration file should be named SPRConfig.yaml and will automatically loaded
from the runtime directory if it exists. A different name can be specified with
the `-c` option.  Or the name can be changed in the default section of the configuration.

There are other things in the yaml datastore, each SPR extension can
also add a structure to the root of the tree to hold the information that
it cares about.  This is the _state_ part of the structure. The yaml datastore
is defined by collecting all of the extension modules yaml file and
merging them together as they are imported.

Yaml files can also be merged directly into the yaml datastore config with load-config.

    `load-config foo.yaml`

Yaml files can be merged directly into the **Root** of the yaml datastore. 
with load-yaml.

    `load-yaml foo.yaml`
    
Or the last way, just code them like this, in spr.
```
'
foo: 
   bar: 10
   baz: 20
   
   
```
 
#### Paths
 
The entire system is held in this data tree. Think of it like a filesystem on
your computer. Lots of folders in a big tree. Pathnames are used to get things
and put things and look at things.

Paths are just like filesystem paths in Unix/Linux.  The namespaces can be 
thought of as one tree, built from imported python code, 
and the yaml datastore as another tree that is built from YAML.

 * `ls` navigates both trees using paths.
 * `set` uses paths like variable names. getting and putting values in them.
 * `show` uses paths to find what to show.
 * `-with` and `-from` and `-to` functions use paths to find and put their data.

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

#### Path symbols.

Symbols can be defined to represent paths. Those symbols can 
then be used in other commands, when accessed they will resolve
to their value.  Here is a sample session which creates some
yaml, then a path to that yaml, showing how the *show* command
works with the new symbol.

Then it gets interesting. mybar is define as `show foo`. Now,
at the prompt, mybar --> show foo --> as/show /foo


SPR:> '
YAML...>foo:
YAML...>   bar: show /foo/baz
YAML...>   baz: 110
YAML...>

SPR:> show foo
bar: show /foo/baz
baz: 110

SPR:> def sbaz "foobaz" /foo/baz

SPR:> sbaz
Unkown Symbol: 110

SPR:> def showbaz "foobaz" /foo/bar

SPR:> showbaz
110

SPR:> set /foo/bar show /foo

SPR:> showbaz
bar: show /foo
baz: 110
...

### With /Some/path

It is also possible to push a path onto the _with_ stack.
Here is an example session showing _with_. 

```
SPR:> as/-with foo

SPR:> '
YAML...>bar: 10
YAML...>baz: 100
YAML...>

SPR:> show foo
bar: 10
baz: 100

SPR:> as/-show-with
/foo
----------------------
bar: 10
baz: 100

SPR:> as/-print-stack
/foo
/

SPR:> as/pop-with

SPR:> as/-print-stack
/

SPR:> as/-with
/
-------------------------
    config
    args
    defaults
    platform
    _with_
    _Root_
    device
    network
    bar-QR
    markdown
    readme
    foo

SPR:> show foo
bar: 10
baz: 100


SPR:> ls /
    config
    args
    defaults
    platform
    _with_
    _Root_
    device
    network
    bar-QR
    markdown
    readme
    foo

SPR:> ls /foo
    bar
    baz

SPR:> as/-with
/
-------------------------
    config
    args
    defaults
    platform
    _with_
    _Root_
    device
    network
    bar-QR
    markdown
    readme
    foo

SPR:> as/-with foo

SPR:> as/-with
/foo
-------------------------
    bar
    baz

SPR:> as/-show-with
/foo
----------------------
bar: 10
baz: 100
'

SPR:> '
YAML...>foobar: this is foobar
YAML...>

SPR:> as/-show-with
/foo
----------------------
bar: 10
baz: 100
foobar: this is foobar


```
    

### SPR/Python extensions

** changing again, because of WITH. **

An SPR library/module is a Python module with a python file, a yaml file and
an spr file. An SPR library project can be created with the
    `new-spr-extension-project` command.
    
    `new-spr-extension-project path/to/my/new/library/foo` 

To install, `python setup.py install` will install your project into
your local python environment / site-packages. 

Once the new module is available on the Python path SPR can import it with
a command like this. 
    ```
    namespace foo "my foo namespace" 
        foo.core 
        function1 function2 
    ```
    
This will create a _namespace foo_ within SPR with all the functions listed, 
as well as whatever is defined in `foo/core.spr`.  The yaml datastore 
will merge in what ever structure is defined in `foo/core.yaml`. 



#### How to do it.
* Make a python extension with the 
`new-spr-extension-project path/to/project` command.
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
* Retrieve their configuration data from the yaml datastore, 
* Do something, 
* Save the result back into their part of the yaml datastore as needed.

To that end, the template created has example _-to_, _-from_ and _-with_ 
functions to be used.


#### Yaml Data Structure
Additionally, an extension can define a yaml file which import will integrate
into the yaml datastore. It can also be included in the spr file instead using
the quote syntax.
Configuration settings and whatever data structure needed by the extension 
are defined here.

Here is how the bar/QR code module defines it's yaml datastore structure
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

The above method of defining the data structure still works, but it can
now be within the spr code. A single quote **'** on a line by it's self 
Followed by yaml code, and ending with 2 blank lines, will allow everything to
exist together.

This is where more Libraries can be imported and new symbols and partial functions 
can be defined.  As well as the YAML if desired.

The Bar/QR extension is a good example of all of this. It only provides 3 public
functions and it has state, configuration, and a couple of SPR symbol definitions,
The files in the repo are: *bar_qr.py* and *bar_qr.spr* which has both spr and yaml
combined.

Here is the spr contents of *bar_qr.spr*. Notice it makes a new command `input-code`
which is actually a dialog window in the _ui_ namespace. The value vector given
is for _bar-QR/value_. So that is where the input dialog will put it's result.

The second function uses the newly defined `bq/input-code` along with another
command ui/print-bcqr to create what appears to be a 2 step process called
`print-codes`.

```
'
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


def input-code
    "Dialog to get a string to encode to a bar or QR code"
    ui/input-string-to bar-QR value

def print-codes
    "Dialogs to get a string, encode it, and print it as some number of Bar or QR codes."
    bq/input-code ui/print-bcqr
```

### The syntax. 

It's just a list of things with whitespace. words, strings and numbers.
**#'s** at the beginning of a line are comments
A **'** on a line by itselfs indicates that YAML follows until 2 blank lines
are encountered.

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
    do 
    rm 
    sleep

namespace log "logger controls and messages"
    Simple_Process_REPL.logs
    level 
    info 
    warning 
    error 
    critical 
    debug

namespace dev "Device interaction, waiting for, handshaking."
    Simple_Process_REPL.device
    wait 
    handshake 
    pause

namespace nw "Networking stuff, Wifi"
    Simple_Process_REPL.network 
    connect_wifi
    connect_tunnel 
    create_tunnel 
    sendlog

namespace bq "Bar and QR code generation and printing"
    Simple_Process_REPL.bar_qr
    gen 
    save 
    read_barcode_from_camera

in-ns

import Simple_Process_REPL.mkext new_spr_extension_project

```

Here is an example of using a message box and creating a new command
that does the same thing. First is the using a msg box. Then defining
a new command mymsg, then using the new command.
This is how it started. Just a nice list of functions and strings.
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
* appstate - yaml datastore - All the YAML, config etc.
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
And it's super cool to recompose old things into new processes. 

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
  * Load module config - SPR-Defaults

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
 * _partial_ bar "foo show too" as/show foo
 * _help_ foo
 * _help_ bar
 * _foo_ 
 * _bar_
 * _foo_ bar
 * _bar_ bar
 * _set_ /foo/bar 10
 * _set-from_ foo/foo /foo/bar
 * _foo_
 * ui/msg "hello"
 * def mymsg "my msg help" ui/msg "hello"
 * _'_           --- Start entering Yaml.
 * _stuff:_
 * _    mine: 10_
 * _    yours: 20_
 *_ _            --- Finish entering Yaml.
 * show /stuff

Once in the REPL at the prompt; __SPR:>,
_help_ shows all the commands known with their documentation. 

## A bit of internals in case more explanation is necessary

### Symbol types:
 * namespaces.
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
Note: They do not currently use pythons func.partial(), 
    they work in simpler SPR sort of way.

_partial_ commands are built from _fptr_ commands.
_partial_ commands are like dolist commands. 
Except that the first symbol in
the list is an fptr symbol, and the list is not everything the fptr function needs.
when using a partial, they act just like fptr functions, you just have to leave off
some or all of the first arguments. A partial acts like an alias for a function
if no arguments are given.  This is how SPR creates _show_, which is really _as/show_.

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
      

### Evolution Notes.

The basic idea is to only change something if it makes sense and it's simple.
It must be simple and elegant.

The goals of the project are to make it easy to create a very configurable
and repeatable process which is python code at it's heart.
Processes should be able to fail gracefully, and report what they know.


For me, it is very interesting to see how the solutions refine themselves
under such limited abilities. I'm interested how the _-from_, _-to_ and _-with_
stuff will affect the creation of stuff in the data tree. I think with those
constructs there will not be as much need for special data spots. The way
I was originally thinking when I added the markdown stuff. That'll change in 
a minute.. markdown will be like the new ones soon.

Because of the restrictions of the appstate, or thinking of it as an app state, 
and configuration instead of just namespace, things changed 
dramatically with that change of point of view.  
Now, set-in is making variables, we are just stashing them in a big global tree.  

It's feeling lot like a language...

Set_in, get_in and showin, were originally modeled after clojure's
_update-in_, and _get-in_. But now they use paths instead. Now it feels
much more intuitive to wander around the system space with **ls** and
**show**. The interface to values also became simple.


The python representation changed like so.
`[foo bar baz]` Became: `foo/bar/baz`.  

And the evolution of set evolved from set-in
and a dorky set-in-from

```
set-in foo bar baz 10
set-in-from foo baz from: foo bar baz
```

to this, - just set:

```
set foo bar baz 10

set foo baz from: foo bar baz
```

to this:

```
`set foo/bar/baz 10`
`set foo/baz  /foo/bar/baz`
```

The idea of **-from** and **-to** changed things too, those are essentially all that
is needed within a module for it to get the stuff to and from other module's,
yaml datastore, or where ever you are putting your stuff.

But that led to **-with** variants, so now, we give a path full of stuff to a 
function and it goes and gets what it wants _with_ what you have there.

So, I'm not sure where that's headed, but it seems like that could boil away too.
A _with_ function, and the lower level python code in every module goes away.

But the interpreter really hasn't changed, and it's way more stupid than the 
dumbest of lisp interpreters. And they can be pretty stupid too.

I added barcodes to SPR because that was a requirement for a thing I made for someone.
When I did that, I decided to add simple namespaces, which led to just changing
everything from the stupid simple and obvious symbol tables to a more elegant import
system. 

Because of namespaces and import, instead of a big ol YAML, 
each module could keep it's own little piece.
Simpler and Simpler.

These things changed everything, but the language, if you can call it that, 
It's only syntax is whitespace, and I guess we can count the */'s* in the paths.
hasn't changed.

And despite it's growing capabilities it's doing it with less code. That's cool.

I sort of want to give a choice of repl's so more fun could be had that way.
And why not have a repl server and an emacs mode so I can run spr code in emacs. 
And I'd like to see this with plysp as it's REPL.

So, endless fun. Why not.

Ok, so comments, and inline Yaml.  These are nice things.

**With** is coming, it's in my head swimming around.

With is here, almost. it works in appstate. the repl needs to bind with it.
Adding push and pop so we have stacks and lists. so with is implemented with SPR. cool.

Result stacks,....

Working!!!!
